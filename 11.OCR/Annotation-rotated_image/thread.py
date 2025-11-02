import os, re, io, sys, math, time, json, shutil, tempfile
from os import listdir
from os.path import isfile, join
from paddleocr import PaddleOCR
import yaml, openpyxl
import numpy as np
from PIL import Image
import cv2

# ------------- GLOBAL CONFIG -------------
INPUT_JSON_PATH = ""
OUTPUT_JSON_PATH = ""
SOURCE = ""
PATH = ""
SKIP_COUNT = 2
thread = sys.argv[1]
curr_dir = os.getcwd()
use_gpu = False


# ------------- BASIC HELPERS -------------

def myFunc(e):
    return (e["VERTICES"][0]["Y"] + e["VERTICES"][3]["Y"]) / 2


def filter_raw(string):
    return re.sub("[^\u0000-\u007F]", "", string)


def filter_raw_v2(raw_list):
    res_list = []
    for raw_l in raw_list:
        text = filter_raw(raw_l.get("TEXT", "")).strip()
        if len(text) > 0:
            if len(re.compile(r'[a-zA-Z0-9]').findall(text)) > 0:
                raw_l["TEXT"] = text
                res_list.append(raw_l)
    return res_list


def update_height(raw_text_hl_line):
    res = []
    for hl in raw_text_hl_line:
        height = max(p["Y"] for p in hl["VERTICES"]) - min(p["Y"] for p in hl["VERTICES"])
        text_len = len(hl["TEXT"].split("\n"))
        if text_len > 0:
            height /= text_len
        if height > 6:
            res.append(hl)
    return res


def update_vertices(para):
    final_para = []
    for p in para:
        xs = [v["X"] for v in p["VERTICES"]]
        ys = [v["Y"] for v in p["VERTICES"]]
        p["VERTICES"] = {"x": min(xs), "x1": max(xs), "y": min(ys), "y1": max(ys)}
        final_para.append(p)
    return final_para


def update_sorted(my_lists):
    if not my_lists or not isinstance(my_lists, list):
        return "", "", ""
    valid = [x for x in my_lists if x.get("TEXT") and x.get("VERTICES")]
    if not valid:
        return "", "", ""

    my_lists = sorted(valid, key=lambda x: x["VERTICES"][0]["Y"])
    grouped_lines, current_group = [], [my_lists[0]]

    for i in range(1, len(my_lists)):
        prev_y, curr_y = my_lists[i - 1]["VERTICES"][0]["Y"], my_lists[i]["VERTICES"][0]["Y"]
        if abs(curr_y - prev_y) < 25:
            current_group.append(my_lists[i])
        else:
            grouped_lines.append(current_group)
            current_group = [my_lists[i]]
    grouped_lines.append(current_group)

    for g in grouped_lines:
        g.sort(key=lambda x: x["VERTICES"][0]["X"])

    sorted_v1 = "\n".join([w["TEXT"] for g in grouped_lines for w in g])
    sorted_v2 = "\n".join([" ".join([w["TEXT"] for w in g]) for g in grouped_lines])
    sorted_v3 = ""
    for g in grouped_lines:
        line = "<TAB>".join([w["TEXT"] for w in g])
        sorted_v3 += line + "\n"
    return sorted_v1.strip(), sorted_v2.strip(), sorted_v3.strip()


# ------------- DESKEW FUNCTION -------------

def deskew_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated


# ------------- MAPPING FUNCTION -------------

def map_point_from_rotated_to_original(pt, orig_w, orig_h, rotation_deg):
    x_r, y_r = float(pt[0]), float(pt[1])
    rot = rotation_deg % 360
    if abs(rot) < 1e-3 or abs(rot - 360) < 1e-3:
        return {"X": int(round(x_r)), "Y": int(round(y_r))}

    cx, cy = orig_w / 2.0, orig_h / 2.0
    theta = math.radians(-rotation_deg)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    x0, y0 = x_r - cx, y_r - cy
    x_orig = x0 * cos_t - y0 * sin_t + cx
    y_orig = x0 * sin_t + y0 * cos_t + cy
    return {"X": int(round(x_orig)), "Y": int(round(y_orig))}


# ------------- OCR RUNNER -------------

def run_paddle_and_map(image_path, rotation_deg, ocr, apply_deskew=False):
    orig = cv2.imread(image_path)
    if orig is None:
        raise FileNotFoundError(image_path)
    orig_h, orig_w = orig.shape[:2]

    if abs(rotation_deg) < 1e-6:
        img_for_ocr = orig.copy()
    else:
        M = cv2.getRotationMatrix2D((orig_w // 2, orig_h // 2), rotation_deg, 1.0)
        img_for_ocr = cv2.warpAffine(orig, M, (orig_w, orig_h),
                                     flags=cv2.INTER_CUBIC,
                                     borderMode=cv2.BORDER_REPLICATE)

    if apply_deskew:
        try:
            img_for_ocr = deskew_image(img_for_ocr)
        except Exception:
            pass

    gray = cv2.cvtColor(img_for_ocr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
    proc_for_ocr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    tmp_dir = tempfile.mkdtemp(prefix="ocr_run_")
    tmp_file = os.path.join(tmp_dir, "tmp_img.jpg")
    cv2.imwrite(tmp_file, proc_for_ocr)

    res = ocr.ocr(tmp_file, cls=True)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    mapped = []
    if not res or not res[0]:
        return mapped

    for line in res[0]:
        pts = np.array(line[0], dtype=np.float32)
        text = line[1][0]
        conf = line[1][1] if len(line[1]) > 1 else 0.0
        box_pts = [map_point_from_rotated_to_original(p, orig_w, orig_h, rotation_deg) for p in pts.tolist()]
        mapped.append({"TEXT": text, "VERTICES": box_pts, "CONF": float(conf)})

    return mapped


# ------------- ANNOTATION FUNCTION -------------

def generate_ocr_image_visual(txn_id, original_image_path, ocr_hl_line_path, base_path):
    try:
        ocr_image_dir = os.path.join(base_path, "OCR_IMAGE")
        os.makedirs(ocr_image_dir, exist_ok=True)
        annotated_path = os.path.join(ocr_image_dir, os.path.basename(original_image_path))

        img = cv2.imread(original_image_path)
        if img is None:
            print(f"[ERROR] Could not open image: {original_image_path}")
            return
        h, w = img.shape[:2]

        with open(ocr_hl_line_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
        if not ocr_data:
            print(f"[WARN] Empty OCR data: {ocr_hl_line_path}")
            return

        annotated = img.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.45, min(0.9, w / 1600.0))
        thickness = 1

        for entry in ocr_data:
            text = entry.get("TEXT", "").strip()
            verts = entry.get("VERTICES", [])
            if not text or not verts:
                continue

            pts = np.array([[v["X"], v["Y"]] for v in verts], np.int32)
            pts[:, 0] = np.clip(pts[:, 0], 0, w - 1)
            pts[:, 1] = np.clip(pts[:, 1], 0, h - 1)
            cv2.polylines(annotated, [pts], True, (0, 255, 0), 2)

            x_min, y_min = np.min(pts[:, 0]), np.min(pts[:, 1])
            x_max, y_max = np.max(pts[:, 0]), np.max(pts[:, 1])
            box_height = y_max - y_min
            (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness + 1)
            y_text = max(15, int(y_min - max(text_h, 0.4 * box_height)))
            cv2.putText(annotated, text, (int(x_min), int(y_text)),
                        font, font_scale, (0, 0, 255), thickness + 1, cv2.LINE_AA)

        cv2.imwrite(annotated_path, annotated)
        print(f"[OCR_IMAGE] Annotated image saved: {annotated_path}")

    except Exception as e:
        print(f"[ERROR] generate_ocr_image_visual failed: {e}")


# ------------- DETECT TEXT -------------

def detect_text(path, source, annotated_save_path=None):
    print(f"\n[INFO] Running full OCR for: {path}")

    temp_dir = os.path.join(os.getcwd(), "TEMP_IMAGES")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, os.path.basename(path))
    shutil.copy2(path, temp_path)

    orig = cv2.imread(temp_path)
    if orig is None:
        print(f"[ERROR] Could not open {temp_path}")
        return "NA", "[]", "[]", "NA", "[]"

    h, w = orig.shape[:2]
    parts = [orig]

    # --- Auto split if Aadhaar front/back in one frame ---
    if h > 1.5 * w:
        print("[INFO] Image looks like both Aadhaar sides together — splitting into halves...")
        top = orig[0:int(h/2), :]
        bottom = orig[int(h/2):, :]
        parts = [top, bottom]
    else:
        print("[INFO] Single-side card detected.")

    all_detections = []
    for idx, part in enumerate(parts):
        part_path = os.path.join(temp_dir, f"part_{idx}.jpg")
        cv2.imwrite(part_path, part)
        ph, pw = part.shape[:2]

        # Decide rotations
        rotations = [0, 90, 270] if ph > pw else [0, 2, -2]

        best = {"rotation": 0, "mapped": [], "score": 0.0}
        for rot in rotations:
            try:
                mapped = run_paddle_and_map(part_path, rot, ocr)
                score = len(mapped) + 0.001 * sum(d.get("CONF", 0.0) for d in mapped)
                print(f"[CHECK] Part {idx} → Rotation {rot}° → {len(mapped)} words (score={score:.2f})")
                if score > best["score"]:
                    best = {"rotation": rot, "mapped": mapped, "score": score}
            except Exception as e:
                print(f"[WARN] Rotation {rot} failed for part {idx}: {e}")

        # Add offset for bottom half coordinates
        offset_y = int(h/2 * idx) if len(parts) > 1 else 0
        for d in best["mapped"]:
            for v in d["VERTICES"]:
                v["Y"] += offset_y
        all_detections.extend(best["mapped"])

    detections = all_detections
    print(f"[INFO] Total words detected: {len(detections)}")

    if not detections:
        print("[WARN] No detections found.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return "NA", "[]", "[]", "NA", "[]"

    # Save annotation
    if annotated_save_path:
        try:
            json_path = annotated_save_path.replace(".jpg", "_hl_line.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(detections, f, indent=4, ensure_ascii=False)
            txn_id = os.path.basename(os.path.dirname(os.path.dirname(annotated_save_path)))
            generate_ocr_image_visual(txn_id, path, json_path, os.path.dirname(os.path.dirname(annotated_save_path)))
        except Exception as e:
            print(f"[WARN] Failed to generate annotation: {e}")

    combined_text = "\n".join(d["TEXT"] for d in detections)
    raw_text = filter_raw(combined_text)
    hl_para = filter_raw_v2(detections)
    hl_line = filter_raw_v2(detections)
    if source == "ISV_IN_V2":
        hl_line = update_height(hl_line)
    hl_para.sort(key=myFunc)
    hl_line.sort(key=myFunc)
    hl_para_v2 = update_vertices(json.loads(json.dumps(hl_para)))

    shutil.rmtree(temp_dir, ignore_errors=True)
    sorted_text = "\n".join([d["TEXT"].strip() for d in hl_line if d["TEXT"].strip()])
    return raw_text, json.dumps(hl_para, indent=4), json.dumps(hl_line, indent=4), sorted_text, json.dumps(hl_para_v2, indent=4)

# ------------- MAIN PROCESS -------------

def detect_ocr_main_process(request):
    try:
        txn_id = request["TXN_ID"]
        source = request["SOURCE"].upper()
        files = request["DATA"]

        folders = [
            "OCR", "OCR_HL_PARA", "OCR_HL_LINE", "OCR_SORTED",
            "OCR_HL_PARA_V2", "OCR_SORTED_V2", "OCR_SORTED_V3",
            "OCR_SORTED_V4", "OCR_ANNOTATED", "OCR_IMAGE"
        ]
        base_paths = {f: os.path.join(PATH, txn_id, f) for f in folders}
        [os.makedirs(p, exist_ok=True) for p in base_paths.values()]

        response = []
        for file in files:
            name = os.path.splitext(os.path.basename(file))[0]
            annotated = os.path.join(base_paths["OCR_ANNOTATED"], f"{name}_annotated.jpg")

            print(f"[INFO] Processing: {file}")
            raw_text, raw_para, raw_line, raw_sorted, raw_para_v2 = detect_text(file, source, annotated)

            paths = {
                "OCR": f"{base_paths['OCR']}/{name}.txt",
                "HL_PARA": f"{base_paths['OCR_HL_PARA']}/{name}.txt",
                "HL_LINE": f"{base_paths['OCR_HL_LINE']}/{name}.txt",
                "PARA_V2": f"{base_paths['OCR_HL_PARA_V2']}/{name}.txt",
            }
            with open(paths["OCR"], "w", encoding="utf-8") as f: f.write(raw_text)
            with open(paths["HL_PARA"], "w", encoding="utf-8") as f: f.write(raw_para)
            with open(paths["HL_LINE"], "w", encoding="utf-8") as f: f.write(raw_line)
            with open(paths["PARA_V2"], "w", encoding="utf-8") as f: f.write(raw_para_v2)

            try:
                v1, v2, v3 = update_sorted(json.loads(raw_line))
                with open(os.path.join(base_paths["OCR_SORTED"], f"{name}.txt"), "w", encoding="utf-8") as f: f.write(v1)
                with open(os.path.join(base_paths["OCR_SORTED_V2"], f"{name}.txt"), "w", encoding="utf-8") as f: f.write(v2)
                wb = openpyxl.Workbook()
                sheet = wb.active
                for line in v3.splitlines():
                    sheet.append(line.split("<TAB>"))
                wb.save(os.path.join(base_paths["OCR_SORTED_V3"], f"{name}.xlsx"))
            except Exception as e:
                print(f"[WARN] SORTED failed: {e}")

            response.append(paths["OCR"].replace(PATH, SOURCE))

        print(f"\n[DONE]  OCR Completed for TXN_ID: {txn_id}")
        return response

    except Exception as e:
        print(f"[ERROR] detect_ocr_main_process: {e}")
        return str(e)


# ------------- CONFIG + MAIN LOOP -------------

def init_yaml():
    global INPUT_JSON_PATH, OUTPUT_JSON_PATH, SOURCE, PATH, use_gpu, SKIP_COUNT
    with open("xbiz_ocr_config.yaml", "r") as stream:
        d = yaml.safe_load(stream)
    INPUT_JSON_PATH = d["INPUT_JSON_PATH"]
    OUTPUT_JSON_PATH = d["OUTPUT_JSON_PATH"]
    SOURCE = d["SOURCE"]
    PATH = d["PATH"]
    use_gpu = d.get("GPU", "FALSE") == "TRUE"


def filter_files(files):
    return [f for f in files if f.lower().endswith(".json")]


def read_json(json_file_path):
    with open(json_file_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


init_yaml()
ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=use_gpu)

while True:
    files = filter_files([f for f in listdir(join(curr_dir, INPUT_JSON_PATH + "_" + thread))
                          if isfile(join(curr_dir, INPUT_JSON_PATH + "_" + thread, f))])
    if files:
        for file in files:
            try:
                print(f"[RUN] Processing {file}")
                request = read_json(join(curr_dir, INPUT_JSON_PATH + "_" + thread, file))
                txn_id = request.get("TXN_ID", "")
                request["DATA"] = [i.replace(SOURCE, PATH) for i in request["DATA"]]
                results = detect_ocr_main_process(request)
                out_json = {
                    "STATUS": True,
                    "CODE": 200,
                    "TXN_ID": txn_id,
                    "MESSAGE": "SUCCESS",
                    "DATA": results
                }
                with open(join(curr_dir, OUTPUT_JSON_PATH, file), "w", encoding="utf-8") as out:
                    json.dump(out_json, out, indent=4, ensure_ascii=False)
                os.remove(join(curr_dir, INPUT_JSON_PATH + "_" + thread, file))
            except Exception as e:
                print(f"[ERROR] {e}")
                try:
                    os.remove(join(curr_dir, INPUT_JSON_PATH + "_" + thread, file))
                except:
                    pass
    else:
        time.sleep(0.2)


