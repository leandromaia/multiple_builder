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
    BUILD_CMDS = {
        1: 'gradlew clean build',
        2: 'gradlew clean build -x test -x check -x javadoc',
        3: 'gradlew clean jar',
        4: 'gradlew clean install'
    }


class HandlerProcess(object):

    def __init__(self, repositories):
        self._repositories = repositories

    def start_process(self, has_deleted_m2, build_full=False, \
                                    is_to_reset=False, from_menu=False):
        import pdb; pdb.set_trace()
        # for repo in self._repositories:
        #     pull_result = self._update_repository(\
        #                                 repo._absolute_path, is_to_reset)
            
        #     if Const.PULL_UPDATED not in pull_result \
        #                         or has_deleted_m2 or from_menu:
        #         self._build_repository(repo, build_full)
        #     else:
        #         print(f'The {repo.repo_initial} its already up to date!')

    def _update_repository(self, repo_path, is_to_reset):
        if is_to_reset:
            self._update_with_reset(repo_path)
        else:
            print('************ Checkout to branch MASTER ****************')
            args_checkout = ['git', 'checkout', 'master']
            self._wrapper_run_process(args_checkout, repo_path)
        
        print(f"********* Starting pull: {repo_path} *****************")
        args_pull = ['git', 'pull']
        return self._wrapper_run_process(args_pull, repo_path)

    def _update_with_reset(self, repo_path):
        print('************ Clean repository ****************')
        args_reset = ['yes', 'y', '|', 'git', 'clean', '-fxd']
        self._wrapper_run_process(args_reset, repo_path)

        print('************ Checkout to branch MASTER ****************')
        args_checkout = ['git', 'checkout', 'master']
        self._wrapper_run_process(args_checkout, repo_path)
        
        print('************ Reset repository ****************')
        args_reset = ['git', 'reset', '--hard', 'origin/master']
        self._wrapper_run_process(args_reset, repo_path)

    def _build_repository(self, repo, build_full):
        print(f"********* Starting build: {repo._absolute_path} *********")
        self._wrapper_run_process(repo.build_command, repo._absolute_path)
        print("********* Build finished successfully!!! *****************")

    def _wrapper_run_process(self, command, path):
        process = subprocess.run(command, shell=True, check=True, \
                                    stdout=subprocess.PIPE, cwd=path, \
                                        universal_newlines=True)
        print(f'The command: {command} to repository: {path} has executed successfully')
        return process.stdout


class CommandArgsProcessor(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description=\
                        '>>>>> Options to update and build projects! <<<<<')
        parser.add_argument('-b', \
                        '--build-full', \
                        action='store_true', \
                        help="Execute the full gradlew clean build process. \
                            This option also skip the menu to select the \
                            others gradle options.")

        parser.add_argument('-c', \
                        '--clean-m2', \
                        action='store_true', \
                        help="Delete all folders and files from project \
                            m2 folder.")

        parser.add_argument('-d', \
                        '--repos-directory', \
                        help='Add your repositories absolute path. If this \
                            parameter is not passed the script absolute path \
                            will be consider as the root path to find the \
                            repositories folder.')

        parser.add_argument('-sm', \
                        '--skip-menu', \
                        action='store_true', \
                        help='Skip visualization of the CLI User Menu. \
                            Passing this option all the found repositories \
                            will be update and build automatically.')
        self._parsed_args = parser.parse_args()
    
    def is_build_full(self):
        return self._parsed_args.build_full

    def is_to_clean_m2(self):
        return self._parsed_args.clean_m2

    def is_to_skip_menu(self):
        return self._parsed_args.skip_menu

    @property
    def repos_directory(self):
        return self._parsed_args.repos_directory


class Repository(object):
    _initial = None
    _maven_types = ('JIVE', )
    __build_command = None

    def __init__(self, absolute_path):
        if os.path.isdir(absolute_path):
            self._absolute_path = absolute_path
            self.build_initial_value()
        else:
            print(f"The directory {absolute_path} doesn't exist!!!")
            raise OSError(f"The directory {absolute_path} doesn't exist!!!")

    def build_initial_value(self):
        self._initial = self._absolute_path.split('.')[-1].upper()

    @property
    def repo_initial(self):
        if not self._initial:
            self.build_initial_value()
        return self._initial

    @property
    def build_command(self):
        if self.__build_command:
            return self.__build_command
        else:
            return Const.BUILD_CMDS.get(1)

    @build_command.setter
    def build_command(self, cmd):
        if self._initial in self._maven_types:
            self.__build_command = Const.MAVEN_COMMAND
        else:
            self.__build_command = cmd
    
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
    MENU_OPTIONS_TO_RESET_ENV = [1, 2]
    POSITIVE_OPTION_TO_RESET = 1

    def ask_desired_repos(self, list_repo):
        names = [r.repo_initial for r in list_repo]

        menu, indexes = self._build_menu_options(names)

        user_awser = self._show_repo_menu(menu, indexes)

        choices = set([m for r in user_awser \
                        for m in menu.split('\n') if r in m])
        return [repo for repo in list_repo \
                        for c in choices \
                            if c.endswith(repo.repo_initial)]

    def ask_is_to_reset(self):
        menu = 'Do you want to reset your repositories branch, '+\
                'using "git reset --hard <<branch name >>":\n1 - Yes\n2 - No\nR:'
        user_awser = self._get_only_one_awser(\
                                        menu, self.MENU_OPTIONS_TO_RESET_ENV)

        return True \
                if int(user_awser) == self.POSITIVE_OPTION_TO_RESET \
                    else False

    def ask_type_gradle_build(self):
        cmds = list(Const.BUILD_CMDS.values())
        key_indexes = list(Const.BUILD_CMDS.keys())

        menu, indexes = self._build_menu_options(cmds, key_indexes)
        
        user_awser = int(self._get_only_one_awser(menu, indexes))
        return Const.BUILD_CMDS.get(user_awser)

    def _build_menu_options(self, raw_options, indexes=None):
        menu = str()
        list_index = None
        if indexes:
            list_index = indexes
        else:
            list_index = [* range(1, len(raw_options) + 1)]

        for i in range(len(raw_options)):
            menu = menu + f'{list_index[i]} - {raw_options[i]}\n'
        else:
            menu = menu + 'R: '
        return menu, list_index

    def _show_repo_menu(self, menu, indexes):      
        print('#########################################################')
        print('########## Build Repos - Choice Your Options ############')
        print('#########################################################')
        while True:
            print(\
                'You can select more than one options adding space between them:')
            raw_awser = input(menu).split()

            for awser in raw_awser:
                if not self._is_valid_awser_by_indexes(awser, indexes):
                    break
            else:
                return raw_awser
           
    def _get_only_one_awser(self, menu, indexes):
        user_awser = None
        while True:
            user_awser = input(menu)
            if self._is_valid_awser_by_indexes(user_awser, indexes):
                break
        return user_awser
    
    def _is_valid_awser_by_indexes(self, awser, indexes):
        try:
            if int(awser) not in indexes:
                raise ValueError("Failed - Not a valid index.")
        except ValueError:
            print(f">>>>> Invalid choice: {awser} <<<<<<\
                            \n\tPlease choose a valid option\n")
            return False
        return True


if __name__ == "__main__":
    cmd_args_proc = CommandArgsProcessor()    
    is_build_full = cmd_args_proc.is_build_full()
    is_clean_m2 = cmd_args_proc.is_to_clean_m2()
    is_skip_menu = cmd_args_proc.is_to_skip_menu()

    repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

    list_repo = [Repository(r) for r in repo_paths]

    if len(repo_paths) > 0:
        is_to_reset = False
        gradle_cmd = None

        if not is_skip_menu:
            cli = CliInterface()
            list_repo = cli.ask_desired_repos(list_repo)
            is_to_reset = cli.ask_is_to_reset()
            if not is_build_full:
                gradle_cmd = cli.ask_type_gradle_build()
            
        if not gradle_cmd:
            gradle_cmd = Const.BUILD_CMDS.get(1)

        for r in list_repo:
            r.build_command = gradle_cmd

        if is_clean_m2:
            PathHelper.delete_m2(Const.M2_PATH)

        handler = HandlerProcess(list_repo)
        handler.start_process(is_clean_m2, is_build_full, \
                                        is_to_reset, is_skip_menu)
    else:
        print(">>>>>> Failed to read the repositories directories.\n"+
                ">>>>>> Please make sure you had cloned all the repositories")
