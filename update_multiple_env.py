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
    MAVEN_COMMAND = ['mvn', 'clean','install']
    GRADLE_FULL = ['gradlew', 'clean', 'build']
    GRADLE_SKIP = GRADLE_FULL + \
                        ['-x', 'test', '-x', 'check', '-x', 'javadoc']


class HandlerProcess(object):

    def __init__(self, repositories):
        self._repositories = repositories

    def start_process(self, has_deleted_m2, \
                                build_full=False, is_to_reset=False):
        for repo in self._repositories:
            pull_result = self._update_repository(\
                                        repo._absolute_path, is_to_reset)
            
            if Const.PULL_UPDATED not in pull_result or has_deleted_m2:
                self._build_repository(repo, build_full)
            else:
                print(f'The {repo.repo_initial} its already up to date!')

    def _update_repository(self, repo_path, is_to_reset):
        if is_to_reset:
            print('************ Reset repository ****************')
            args_reset = ['git', 'reset', '--hard', 'origin/master']
            self._wrapper_run_process(args_reset, repo_path)
        
        print('************ Checkout to branch MASTER ****************')
        args_checkout = ['git', 'checkout', 'master']
        self._wrapper_run_process(args_checkout, repo_path)
        
        print(f"********* Starting pull: {repo_path} *****************")
        args_pull = ['git', 'pull']
        return self._wrapper_run_process(args_pull, repo_path)

    def _build_repository(self, repo, build_full):
        print(f"********* Starting build: {repo._absolute_path} *********")
        
        build_command = repo.get_build_command(build_full)
        self._wrapper_run_process(build_command, repo._absolute_path)
        print("********* Build finished successfully!!! *****************")

    def _wrapper_run_process(self, command, path):
        process = subprocess.run(command, shell=True, check=True, \
                                    stdout=subprocess.PIPE, cwd=path, \
                                        universal_newlines=True)
        print(f'The command: {command} to repository: {path} has executed successfully')
        return process.stdout



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
    _maven_types = ('JIVE', )

    def __init__(self, absolute_path):
        if os.path.isdir(absolute_path):
            self._absolute_path = absolute_path
        else:
            print(f"The directory {absolute_path} doesn't exist!!!")
            raise OSError(f"The directory {absolute_path} doesn't exist!!!")

    @property
    def repo_initial(self):
        if not self._initial:
            self._initial = self._absolute_path.split('.')[-1].upper()
        return self._initial

    def get_build_command(self, is_build_full):
        if self._initial in self._maven_types:
            return Const.MAVEN_COMMAND

        if is_build_full:
            return Const.GRADLE_FULL
        else:
            return Const.GRADLE_SKIP 
    
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
        if not root_path:
            root_path = os.getcwd()

        all = [f.path for f in os.scandir(root_path) if f.is_dir()]
        valid_paths = [a for a in all \
                            for r in Const.REPO_PATHS if a.endswith(r)]
        return valid_paths


class CliInterface(object):

    def ask_desired_repos(self, list_repo):
        names = [r.repo_initial for r in list_repo]

        menu = str()
        indexes = list()
        for i in range(0, len(names)):
            index = str(i + 1)
            menu = menu + f'{index} - {names[i]}\n'
            indexes.append(index)
        else:
            menu = menu + 'R: '

        user_awser = self._show_repo_menu(menu, indexes)

        choices = set([m for r in user_awser \
                        for m in menu.split('\n') if r in m])

        return [repo for repo in list_repo \
                        for c in choices \
                            if c.endswith(repo.repo_initial)]

    def _show_repo_menu(self, menu, indexes):
        is_to_ask = True       
        print('#########################################################')
        print('########## Build Repos - Choice Your Options ############')
        print('#########################################################')
        while is_to_ask:
            print(\
                'You can select more than one options adding space between them:')
            user_awser = input(menu).split()

            for awser in user_awser:
                if awser not in indexes:
                    print(f">>>>> Invalid choice: {awser} <<<<<<\
                                \n\tPlease choose a valid option\n")
                    break
            else:
                is_to_ask = False
        return user_awser
    
    def ask_is_to_reset(self):
        while True:
            user_awser = input('Do you want to reset your repositories branch, '+\
                                'using "git reset --hard <<branch name >>":\n1 - Yes\n2 - No\n'+\
                                    '>>>>>> WARNING: Your stash will be also be cleaned.\nR: ')
            if user_awser == "1":
                return True
            elif user_awser == "2":
                return False
            else:
                print(f"\n>>>>> Invalid choice: {user_awser} <<<<<<\n")


if __name__ == "__main__":
    print("********* Starting Repo Update *****************")
    
    cmd_args_proc = CommandArgsProcessor()
    
    is_build_full = cmd_args_proc.is_build_full()
    is_clean_m2 = cmd_args_proc.is_to_clean_m2()
    is_show_menu = cmd_args_proc.is_to_show_menu()
    
    if is_clean_m2:
        PathHelper.delete_m2(Const.M2_PATH)

    repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

    list_repo = [Repository(r) for r in repo_paths]

    if len(repo_paths) > 0:
        if is_show_menu:
            cli = CliInterface()
            list_repo = cli.ask_desired_repos(list_repo)
            is_to_reset = cli.ask_is_to_reset()

        handler = HandlerProcess(list_repo)
        handler.start_process(is_clean_m2, is_build_full, is_to_reset)
    else:
        print(">>>>>> Failed to read the repositories directories.\n"+
                ">>>>>> Please make sure you had cloned all the repositories")
