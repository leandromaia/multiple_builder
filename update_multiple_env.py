#!/usr/bin/env python
import os
import argparse
from subprocess import check_call, Popen, PIPE

repo_paths = ('sample_repo_1',
                'sample_repo_1',
                    'sample_repo_1')

def execute_pull(repo_path, password=None):
    print(f"********* Starting pull: {repo_path} *****************")
    proc = Popen(['git', 'pull'], stdin=PIPE)
    if password:
        proc.communicate(password)

def execute_gradle_build(repo_path):
    print(f"********* Starting gradle clean build: {repo_path} *****************")
    check_call('gradlew clean build', shell=True, cwd=repo_path)

def get_args():
    parser = argparse.ArgumentParser(description='Options to build projects!')
    parser.add_argument("--p", default=0, help="This is the Git passphrase!")

    args = parser.parse_args()
    return args.p

if __name__ == "__main__":
    print(f"********* Starting Repo Update *****************")
    pwd = get_args()

    for repo in repo_paths:
        if os.path.isdir(repo):
            if pwd != 0:
                execute_pull(repo, pwd)
            else:
                execute_pull(repo)
            execute_gradle_build(repo)
        else:
            print(f"The directory {repo} doesn't exist!!!")

    print(f"********* Updating finished successfully!!! *****************")