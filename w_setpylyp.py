import os
import pylyppath

print("Path setting of pylyp_parser.py")
print("...")
pylyppath.setpath()

print("Installing pyinstaller")
print("...")
os.system("pip install pyinstaller")

print("Creating pylyp.exe")
os.system("pyinstaller --onefile --exclude-module _bootlocale pylyp.py")
