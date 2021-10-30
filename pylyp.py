pylyp_parser = r"C:\Users\Utente\Desktop\UNI\Stage\cpython\Pylyp\pylyp_parser.py"
#don't touch the line above

import sys
import os

if len(sys.argv) != 2:
    print("This script needs a file.py as an argument")
    sys.exit(0)

os.system("python " + pylyp_parser + " " + sys.argv[1])
