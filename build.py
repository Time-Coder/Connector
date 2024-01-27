import subprocess
import sys

subprocess.call([sys.executable, "setup.py", "sdist", "bdist_wheel"])