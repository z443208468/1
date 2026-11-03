"""Launch one Windows child with its working directory and tool state on D:."""
import os
import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv)<4 or os.name!='nt':
        raise SystemExit('Windows: python d_child.py <D:/runtime-root> <D:/work-dir> <executable> [arguments...]')
    root, work=(Path(p).resolve() for p in sys.argv[1:3])
    if root.drive.upper()!='D:' or work.drive.upper()!='D:' or not work.is_dir():
        raise SystemExit('Runtime root and existing work directory must resolve to D:')
    env=os.environ.copy()
    groups={
        'temp':['TEMP','TMP','TMPDIR'], 'profile':['HOME','USERPROFILE'],
        'codex':['CODEX_HOME'], 'roaming':['APPDATA'], 'local':['LOCALAPPDATA'],
        'cache':['XDG_CACHE_HOME'], 'config':['XDG_CONFIG_HOME'], 'data':['XDG_DATA_HOME'],
        'npm':['NPM_CONFIG_CACHE'], 'browsers':['PLAYWRIGHT_BROWSERS_PATH'],
        'huggingface':['HF_HOME'], 'torch':['TORCH_HOME'], 'pycache':['PYTHONPYCACHEPREFIX']
    }
    for name,keys in groups.items():
        dest=root/name
        dest.mkdir(parents=True,exist_ok=True)
        if dest.resolve().drive.upper()!='D:':
            raise SystemExit('Reparse point leads away from D: '+str(dest))
        for key in keys:
            env[key]=str(dest)
    env['HOMEDRIVE']='D:'
    env['HOMEPATH']=str((root/'profile').relative_to('D:/'))
    env['HOMEPATH']='\\'+env['HOMEPATH']
    env['PYTHONDONTWRITEBYTECODE']='1'
    return subprocess.run(sys.argv[3:],env=env,cwd=work,check=False).returncode

if __name__=='__main__':
    sys.exit(main())
