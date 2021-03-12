
# python
import os

def _dir_to_pgo_dir(path):
    return os.path.join(os.path.dirname(path), '.pgo-' + os.path.basename(path))
    