#!/usr/bin/env python
import argparse
import subprocess
import shutil
import os
from pathlib import Path


repo_paths = ('sample_1', 
                'sample_2',
                    'sample_3')

M2_PATH = ".m2/"


class HandlerProcess(object):
    PULL_UPDATED = "Already up to date"

    def __init__(self, repo_paths):
        self.repo_paths = repo_paths

    def start_process(self, build_full=False):
        for repo in self.repo_paths:
            if os.path.isdir(repo):
                pull_result = self.execute_pull(repo)
                
                if self.PULL_UPDATED not in pull_result:
                    self.execute_gradle_build(repo, build_full)
                else:
                    print(f'The {repo} its already up to date!')
            else:
                print(f"The directory {repo} doesn't exist!!!")

    def execute_pull(self, repo_path):
        print(f"********* Starting pull: {repo_path} *****************")
        args = ['git', 'pull']
        process = subprocess.run(args, check=True, cwd=repo_path, \
                            stdout=subprocess.PIPE, universal_newlines=True)
        return process.stdout

    def execute_gradle_build(self, repo_path, build_full):
        print(f"********* Starting gradle clean build: {repo_path} *********")
        
        args = ['gradlew', 'clean', 'build']
        if not build_full:
            args = args + ['-x', 'test', '-x', 'check']
        
        subprocess.run(args, shell=True, check=True, \
                                    cwd=repo_path, universal_newlines=True)
        print("********* Updating finished successfully!!! *****************")


class CommandArgsProcessor(object):

    def __init__(self):
        parser = argparse.ArgumentParser(\
                                    description='Options to build projects!')
        parser.add_argument('-b', \
                        '--build-full', \
                        action='store_true', \
                        help="Execute the full gradlew clean build process")

        parser.add_argument('-c', \
                        '--clean-bss-m2', \
                        action='store_true', \
                        help="Delete all files from m2 folder")
        self._parsed_args = parser.parse_args()
    
    def is_build_full(self):
        return self._parsed_args.build_full

    def delete_m2(self, m2_path):
        print("Start deleting ......")
        if self._parsed_args.clean_bss_m2:
            absolute_m2_path = Path.joinpath(Path.home(), m2_path)

            if absolute_m2_path.is_dir():
                print(f'Deleting the M2 files: {absolute_m2_path}')
                try:
                    shutil.rmtree(absolute_m2_path)
                except OSError:
                    print(f'Error: process to delete folders and files from \
                            {absolute_m2_path} has failed.')
            else:
                print(f'The path {absolute_m2_path} is not a valid directory')


if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    
    cmd_args_proc = CommandArgsProcessor()
    cmd_args_proc.delete_m2(M2_PATH)

    handler = HandlerProcess(repo_paths)
    handler.start_process(cmd_args_proc.is_build_full)
