#!/usr/bin/env python
import os
import argparse
import subprocess


repo_paths = ('com.ericsson.bss.ael.aep', 
                'com.ericsson.bss.ael.aep.plugins',
                    'com.ericsson.bss.ael.bae')

PULL_UPDATED = "Already up to date"

def execute_pull(repo_path):
    print(f"********* Starting pull: {repo_path} *****************")
    args = ['git', 'pull']
    process = subprocess.run(args, check=True, cwd=repo_path, \
                            stdout=subprocess.PIPE, universal_newlines=True)
    return process.stdout


def execute_gradle_build(repo_path, build_full):
    print(f"********* Starting gradle clean build: {repo_path} *************")
    
    args = ['gradlew', 'clean', 'build']
    if not build_full:
        args = args + ['-x', 'test', '-x', 'check']
    
    subprocess.run(args, shell=True, check=True, \
                                cwd=repo_path, universal_newlines=True)
    print('Process finished successfully.')


def get_command_args():
    parser = argparse.ArgumentParser(description='Options to build projects!')
    parser.add_argument('--build-full', \
                        '-b', \
                        action='store_true', \
                        help="Execute the full gradlew clean build process")
    return parser.parse_args()


if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    args = get_command_args()

    for repo in repo_paths:
        if os.path.isdir(repo):
            pull_result = execute_pull(repo)
            
            if PULL_UPDATED not in pull_result:
                execute_gradle_build(repo, args.build_full)
            else:
                print(f'The {repo} its already up to date!')
        else:
            print(f"The directory {repo} doesn't exist!!!")

    print("********* Updating finished successfully!!! *****************")