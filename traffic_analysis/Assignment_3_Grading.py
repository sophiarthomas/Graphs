import subprocess
import os


directory_path = './'

# List all files and directories in the specified directory
files_and_dirs = os.listdir(directory_path)
files_and_dirs = sorted(files_and_dirs)

for f in files_and_dirs:
    if f.endswith('.py') and not f.endswith('Assignment_3_Grading.py'):
        print("---------------------")
        print(f)
        subprocess.run(["python", f,  "traffic.gml", "20", "0", "3", "--plot"])
