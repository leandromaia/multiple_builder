#!/usr/bin/env python
import argparse
import subprocess
import shutil
import os
from pathlib import Path


class Const(object):
    M2_PATH = ".m2/repository/com/ericsson/bss"
    PULL_UPDATED = "Already up to date"
    REPO_PATHS = ('com.ericsson.bss.ael.aep', 
                    'com.ericsson.bss.ael.aep.plugins',
                        'com.ericsson.bss.ael.bae',
                            'com.ericsson.bss.ael.dae',
                                'com.ericsson.bss.ael.jive',
                                    'com.ericsson.bss.ael.aep.sdk')


class HandlerProcess(object):

    def __init__(self, repo_paths):
        self.repo_paths = repo_paths

    def start_process(self, has_deleted_m2, build_full=False):
        for repo in self.repo_paths:
            if os.path.isdir(repo):
                pull_result = self.execute_pull(repo)
                
                if Const.PULL_UPDATED not in pull_result or has_deleted_m2:
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
            args = args + ['-x', 'test', '-x', 'check', '-x', '-javadoc']
        
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
                        '--clean-m2', \
                        action='store_true', \
                        help="Delete all files from m2 folder")

        parser.add_argument('-d', \
                        '--repos-directory', \
                        help='Add your repositories absolute path.')

        parser.add_argument('-m', \
                        '--show-menu', \
                        action='store_true', \
                        help='Show the CLI User Menu thats allow to choice '\
                            'wich repositories to update.')
        self._parsed_args = parser.parse_args()
    
    def is_build_full(self):
        return self._parsed_args.build_full

    def is_to_clean_m2(self):
        return self._parsed_args.clean_m2

    def is_to_show_menu(self):
        return self._parsed_args.show_menu

    @property
    def repos_directory(self):
        return self._parsed_args.repos_directory


class Repository(object):
    _initial = None

    def __init__(self, absolute_path):
        self._absolute_path = absolute_path

    @property
    def repo_initial(self):
        if not self._initial:
            self._initial = self._absolute_path.split('.')[-1].upper()
        return self._initial

    def __str__(self):
        return self._initial


class PathHelper(object):
    
    @staticmethod
    def delete_m2(m2_path):
        print("Start deleting ......")
        absolute_m2_path = Path.joinpath(Path.home(), m2_path)
        
        if absolute_m2_path.is_dir():
            print(f'Deleting the M2 files: {absolute_m2_path}')
            try:
                shutil.rmtree(absolute_m2_path)
                print("The m2 folder has deleted sucessfully")
            except OSError:
                print(f'Error: process to delete folders and files from \
                        {absolute_m2_path} has failed.')
        else:
            print(f'The path {absolute_m2_path} is not a valid directory')
    
    @staticmethod
    def fetch_repo_paths(root_path):
        if root_path:
            if os.path.isdir(root_path):
                all = [f.path for f in os.scandir(root_path) if f.is_dir()] 
                valid_paths = [a for a in all \
                                for r in Const.REPO_PATHS \
                                    if a.endswith(r)]
                return valid_paths
            else:
                print(f"Invalid path: {root_path}")
                return list()
        else:
            return Const.REPO_PATHS


class CliInterface(object):

    def _parse_repo_names(self, repo_paths):
        repo_names = [r.split('.')[-1].upper() for r in repo_paths]
        return repo_names

    def ask_desired_repos(self, list_repo):
        names = [r.repo_initial for r in list_repo]

        menu = str()
        for index in range(0, len(names)):
            menu = menu + f'{index + 1} - {names[index]}\n'
        else:
            menu = menu + 'R: '
        
        print('#########################################################')
        print('########## Build Repos - Choice Your Options ############')
        print('#########################################################')
        print(\
            'You can select more than one options adding space between them:')
        raw_resp = input(menu)

        choices = [m for r in raw_resp.split() \
                        for m in menu.split('\n') if r in m]
       
        repos_selected = [repo for repo in list_repo \
                                for c in choices \
                                    if c.endswith(repo.repo_initial)]
        
        return repos_selected


if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    
    cmd_args_proc = CommandArgsProcessor()
    
    is_build_full = cmd_args_proc.is_to_clean_m2()
    is_clean_m2 = cmd_args_proc.is_to_clean_m2()
    is_show_menu = cmd_args_proc.is_to_show_menu()
    
    if is_clean_m2:
        PathHelper.delete_m2(Const.M2_PATH)

    repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

    list_repo = [Repository(r) for r in repo_paths]

    if len(repo_paths) > 0:
        if is_show_menu:
            CliInterface().ask_desired_repos(list_repo)

        handler = HandlerProcess(repo_paths)
        handler.start_process(is_clean_m2, is_build_full)
    else:
        print(">>>>>> Failed to read the repositories directories.\n"+
                ">>>>>> Please make sure you had cloned all the repositories")
