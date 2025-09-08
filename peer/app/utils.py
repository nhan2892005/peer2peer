import os
from typing import List, Dict

def list_shared_files(folder: str) -> List[Dict]:
    files = []
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            size = os.path.getsize(fpath)
            files.append({"name": fname, "size": size, "sha256": fname})
    return files
