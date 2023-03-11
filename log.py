import os
import time

class Log(object):
    
    def __init__(self):
        # Create file
        self.file_name = time.strftime('%Y-%m-%d.%H.%M.%S')
        folder = os.path.exists("./log")
        if not folder:
            os.makedirs("./log")
        open(f"./log/{self.file_name}.txt", "a")
        self.file_path = f"./log/{self.file_name}.txt"
    
    def write_string(self, string):
        with open(self.file_path, "a") as f:
            f.write(string)
            f.write("\n")
    
    def write_object(self, list_dict):
        with open(self.file_path, "a") as f:
            for i, dict1 in enumerate(list_dict):
                for key, value in dict1.items():
                    f.write(f"The {i}-th object: {key}: {value}")
                f.write("\n")
    def write_list(self, list_):
        with open(self.file_path, "a") as f:
            for element in list_:
                f.write(f"{element} ")
            f.write("\n")

