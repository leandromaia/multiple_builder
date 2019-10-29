#!/usr/bin/env python
import os
import argparse
import subprocess
import shutil
from pathlib import Path


repo_paths = ('sample_1', 
                'sample_2',
                    'sample_3')

PULL_UPDATED = "Already up to date"
M2_PATH = ".m2/"

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

    parser.add_argument('--clean-bss-m2', \
                        '-c', \
                        action='store_true', \
                        help="Delete all files from m2 folder")
    return parser.parse_args()


def delete_bss_m2():
    bss_m2_path = Path.joinpath(Path.home(), M2_PATH)

    if bss_m2_path.is_dir():
        try:
            shutil.rmtree(bss_m2_path)
        except OSError:
            print(f'Error: process to delete folders and files from \
                    {bss_m2_path} has failed.')


if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    args = get_command_args()
    if args.clean_bss_m2:
        delete_bss_m2()

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