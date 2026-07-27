import subprocess
import os

os.chdir('/home/Krishna-Singh/equityforge')

def run_git(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"$ {cmd}")
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())

run_git("git status")
