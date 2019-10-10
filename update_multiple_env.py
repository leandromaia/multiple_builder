#!/usr/bin/env python
import os
import argparse
from subprocess import check_call, Popen, PIPE, check_output

repo_paths = ('c:/AEL/repositories/com.ericsson.bss.ael.aep.plugins', )
                # 'sample_repo_1',
                #     'sample_repo_1')

PULL_UPDATED = "Already up to date"

def execute_pull(repo_path, password=None):
    print(f"********* Starting pull: {repo_path} *****************")
    args = ['git', 'pull']
    # if password:
    #     args.append('-input')
    #     args.append(password)

    return str(check_output(args, stdin=PIPE))
    
def execute_gradle_build(repo_path):
    print("********* Starting gradle clean build: {repo_path} *****************")
    check_call('gradlew clean build', shell=True, cwd=repo_path)

def get_args():
    parser = argparse.ArgumentParser(description='Options to build projects!')
    parser.add_argument("--p", default=0, help="This is the Git passphrase!")

    args = parser.parse_args()
    return args.p

if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    pwd = get_args()

    for repo in repo_paths:
        if os.path.isdir(repo):
            pull_result = str()
            if pwd != 0:
                pull_result = execute_pull(repo, pwd)
            else:
                pull_result = execute_pull(repo)
            
            if PULL_UPDATED not in pull_result:
                execute_gradle_build(repo)
        else:
            print(f"The directory {repo} doesn't exist!!!")

    print("********* Updating finished successfully!!! *****************")