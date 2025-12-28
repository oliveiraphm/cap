import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
print(f"Adding {root_dir} to sys.path")
sys.path.insert(0, root_dir)
