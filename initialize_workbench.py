"""Initialize the project environment and only the default, checksum-verified model."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
CHECK = r'''
import hashlib, json
from pathlib import Path
import torch, spandrel, numpy, PIL, psutil
import denoise as dn
name = dn.MODELS['esrgan'][0]
model = Path.home() / '.cache' / 'gpt-anime-denoise' / name
assert model.is_file(), 'Default ESRGAN model is missing'
assert hashlib.sha256(model.read_bytes()).hexdigest() == dn.SHA256[name], 'Model checksum mismatch; file preserved'
device = dn.default_device()
print(json.dumps({'device': device, 'torch': torch.__version__, 'default_model': name}))
'''


def run(argv):
    return subprocess.run(list(map(str, argv)), cwd=ROOT, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not args.check:
        import setup_env
        if (ROOT / '.venv').exists() and not PYTHON.is_file():
            print('Existing .venv is incomplete; preserved for review.', file=sys.stderr)
            return 3
        if setup_env.detect()['kind'] == 'rocm' and PYTHON.exists() and setup_env.venv_version() != '3.12':
            print('Existing .venv needs a different Python; preserved for review.', file=sys.stderr)
            return 3
        if run([sys.executable, ROOT / 'setup_env.py', '--yes']):
            return 1
        if run([PYTHON, '-c', "from pathlib import Path; import denoise as dn; dn.fetch('esrgan', Path.home()/'.cache'/'gpt-anime-denoise')"]):
            return 1
    if not PYTHON.is_file():
        print('Project .venv is not initialized.', file=sys.stderr)
        return 1
    return run([PYTHON, '-c', CHECK])


if __name__ == '__main__':
    sys.exit(main())
