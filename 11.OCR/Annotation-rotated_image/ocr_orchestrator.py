import os
import time
from os import listdir
from os.path import isfile, join
import threading
import yaml
import shutil

# pyinstaller --onefile --console --clean --add-data "./paddle_config.yaml;." "./ocr_orchestrator.py"
# pyinstaller --onefile --console --clean --add-data "./paddle_config.yaml;." --collect-all "paddlepaddle-gpu" --collect-all "paddleocr" --collect-all "paddlepaddle" --collect-all "paddle" --collect-all "cv2" --collect-all "google" --collect-all "future" --collect-all "subprocess" --collect-all "openpyxl" --collect-all "numpy" --collect-all "frozen" --collect-all "shapely" --collect-all "skimage" "./thread.py"
INPUT_JSON_PATH = ""
OUTPUT_JSON_PATH = ""
THREAD = ""
curr_dir = os.getcwd()


def init_yaml():
    global INPUT_JSON_PATH, OUTPUT_JSON_PATH, THREAD
    stream = open("xbiz_ocr_config.yaml", 'r')
    dictionary = yaml.safe_load(stream)
    INPUT_JSON_PATH = dictionary["INPUT_JSON_PATH"]
    OUTPUT_JSON_PATH = dictionary["OUTPUT_JSON_PATH"]
    THREAD = dictionary["THREAD"]


def create_folders():
    os.makedirs(os.path.join(curr_dir, INPUT_JSON_PATH), exist_ok=True)
    os.makedirs(os.path.join(curr_dir, OUTPUT_JSON_PATH), exist_ok=True)
    for i in range(int(THREAD)):
        os.makedirs(os.path.join(curr_dir, INPUT_JSON_PATH + "_" + str(i + 1)), exist_ok=True)


def process(thread):
    try:
        os.system("python \"" + curr_dir + "\\thread.py\" " + thread)
        os.system("\"" + curr_dir + "\\thread.exe\" " + thread)
        print(thread)
    except Exception as e:
        print(e)


def start_thread():
    threads = []
    for i in range(int(THREAD)):
        threads.append(threading.Thread(target=process, args=(str(i + 1),)))
    for thread in threads:
        thread.start()


def get_lowest_load_thread():
    loads = []
    for i in range(int(THREAD)):
        loads.append(len([f for f in listdir(join(curr_dir, INPUT_JSON_PATH + "_" + str(i + 1))) if
                          isfile(join(join(curr_dir, INPUT_JSON_PATH + "_" + str(i + 1)), f))]))
    return loads.index(min(loads))


def filter_files(files):
    new_files = []
    for file in files:
        if file.lower().endswith(".json"):
            new_files.append(file)
    return new_files


def start_process():
    while True:
        files = filter_files([f for f in listdir(join(curr_dir, INPUT_JSON_PATH) + "\\") if
                              isfile(join(join(curr_dir, INPUT_JSON_PATH), f))])
        if len(files) > 0:
            for file in files:
                try:
                    lowest_load_thread = get_lowest_load_thread()
                    shutil.copy(join(join(curr_dir, INPUT_JSON_PATH), file),
                                join(join(curr_dir, INPUT_JSON_PATH + "_" + str(lowest_load_thread + 1)), file))
                    os.remove(join(join(curr_dir, INPUT_JSON_PATH), file))
                except Exception as e:
                    pass
        else:
            time.sleep(1)


init_yaml()
create_folders()
start_thread()
start_process()
