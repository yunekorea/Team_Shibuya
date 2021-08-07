# import module
import os
from encodings import utf_8

# folder path
path = r"C:\Users\anuuj\Desktop\PNU\Graduation project\docs\test_docs"

# change the directory
os.chdir(path)


# read text File


def read_text_file(file_path):
    with open(file_path, 'r', encoding="utf_8") as f:
        lines = f.read()
        title = lines.split('\n', 1)[0] # getting the first line and save it in title
        texts = lines.split('\n', 1)[1:] # rest of the lines are saved in the texts

#        print(f.read())
        print(title)
        print(texts)

# iterate through all file
for file in os.listdir():
    # check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{path}\{file}"

        # call read text file function
        read_text_file(file_path)