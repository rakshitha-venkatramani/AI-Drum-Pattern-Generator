import os
for root, dirs, files in os.walk('data/raw/'):
    print(f"ROOT: {root}")
    print(f"DIRS: {dirs}")
    print(f"FILES: {files}")
