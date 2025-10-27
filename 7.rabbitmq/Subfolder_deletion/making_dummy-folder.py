import os

BASE_DIR = r"C:\Users\Pankhuri Priyadarshi\Desktop\xbiz-Projects\rabbitmq\dummy_data"

structure = {
    "folder1": {
        "files": ["file1.txt", "file2.log"],
        "subfolders": {
            "sub1": {
                "files": ["sub1_file1.txt", "sub1_file2.txt"],
                "subfolders": {
                    "deep1": {
                        "files": ["deepfile1.txt"],
                        "subfolders": {}
                    }
                }
            },
            "sub2": {
                "files": ["sub2_file1.txt"],
                "subfolders": {}
            }
        }
    },
    "folder2": {
        "files": ["data.csv", "readme.md"],
        "subfolders": {
            "inner": {
                "files": ["inner_log.txt"],
                "subfolders": {
                    "deep_inner": {
                        "files": ["verydeep.txt"],
                        "subfolders": {}
                    }
                }
            }
        }
    }
}


def create_structure(base_path, structure):
    for folder, content in structure.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        for file in content.get("files", []):
            file_path = os.path.join(folder_path, file)
            with open(file_path, "w") as f:
                f.write(f"This is {file}\n")

        for subfolder, subcontent in content.get("subfolders", {}).items():
            create_structure(folder_path, {subfolder: subcontent})


if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    create_structure(BASE_DIR, structure)
    print(f"Dummy 3-layer folder structure created at: {BASE_DIR}")
