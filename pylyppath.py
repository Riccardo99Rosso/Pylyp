import os
import fileinput

def setpath():
    current_path = os.getcwd()
    pylyp_parser = current_path + "\pylyp_parser.py"
    with open("pylyp.py") as f:
        lines = f.read()
    lines = lines.split("\n")
    lines[0] = "pylyp_parser = " + "r\"" + pylyp_parser + "\""
    lines = "\n".join(lines)
    with open("pylyp.py", "w") as f:
        f.write(lines) 