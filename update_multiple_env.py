#!/usr/bin/env python
import argparse
import os
import logging


from PyQt5 import QtWidgets

from main_window import Ui_MainWindow
from setup_gui import SetupApp
from util import Const, PathHelper, HandlerProcess
from models import Repository, Process

logger = None


def setup_logger():
    global logger
    logFormatter = '> %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatter, level=logging.DEBUG)
    logger = logging.getLogger(__name__)


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


class CliInterface(object):
    MENU_OPTIONS_TO_RESET_ENV = [1, 2]
    POSITIVE_OPTION_TO_RESET = 1

    def ask_desired_repos(self, list_repo):
        names = [r.repo_initial for r in list_repo]

        menu, indexes = self._build_menu_options(names)

        user_anwser = self._show_repo_menu(menu, indexes)

        choices = set([m for r in user_anwser \
                        for m in menu.split('\n') if r in m])
        return [repo for repo in list_repo \
                        for c in choices \
                            if c.endswith(repo.repo_initial)]

    def ask_is_to_reset(self):
        menu = 'Do you want to reset your repositories branch, '+\
                'using "git reset --hard <<branch name >>":\n'+\
                    '1 - Yes\n2 - No\nR: '
        user_anwser = self._get_only_one_awser(\
                                        menu, self.MENU_OPTIONS_TO_RESET_ENV)
        return True \
                if int(user_anwser) == self.POSITIVE_OPTION_TO_RESET \
                    else False

    def ask_type_gradle_build(self):
        cmds = list(Const.BUILD_CMDS.values())
        key_indexes = list(Const.BUILD_CMDS.keys())

        menu, indexes = self._build_menu_options(cmds, key_indexes)
        
        user_anwser = int(self._get_only_one_awser(menu, indexes))
        return Const.BUILD_CMDS.get(user_anwser)

    def ask_wich_build_branch(self):
        user_anwser = input("Which branch all the repositories should to "+ \
                    "build?\nType only M to default branch master ou type"+ \
                    " the desired branch name:\nR: ")
        return Const.BUILD_BRANCH \
                    if user_anwser.upper() == Const.BUILD_BRANCH_OPT \
                        else user_anwser

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
        user_anwser = None
        while True:
            user_anwser = input(menu)
            if self._is_valid_awser_by_indexes(user_anwser, indexes):
                break
        return user_anwser
    
    def _is_valid_awser_by_indexes(self, awser, indexes):
        try:
            if int(awser) not in indexes:
                raise ValueError("Failed - Not a valid index.")
        except ValueError:
            logger.error(f'Invalid choice: {awser}. ' +\
                                    'Please choose a valid option')
            return False
        return True


class CliInterfaceControl(object):
    
    def __init__(self, process, list_repo):
        self._process = process
        self._list_repo = list_repo
        self._cli = CliInterface()

    def show(self):
        self._show_user_menus()
        self._execute_build()

    def _show_user_menus(self):
        self._list_repo = self._cli.ask_desired_repos(self._list_repo)
        
        self._process.is_to_reset = self._cli.ask_is_to_reset()
        self._process.build_branch = self._cli.ask_wich_build_branch()

        if self._process.is_build_full:
            build_command = Const.BUILD_CMDS.get(1)
        else:
            build_command = self._cli.ask_type_gradle_build()
        
        self._apply_select_build_command(build_command)

    def _execute_build(self):
        handler = HandlerProcess(self._process)
        handler.start_process(self._list_repo)
    
    def _apply_select_build_command(self, build_command):
        for repository in self._list_repo:
            repository.build_command = gradle_cmd


if __name__ == "__main__":    
    setup_logger()

    cmd_args_proc = CommandArgsProcessor()

    process = Process()
    process.is_build_full = cmd_args_proc.is_build_full()
    process.is_clean_m2 = cmd_args_proc.is_to_clean_m2()

    repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

    list_repo = [Repository(r) for r in repo_paths]

    if len(repo_paths) > 0:
        gradle_cmd = None

        if not cmd_args_proc.is_to_skip_menu():
            cli_control = CliInterfaceControl(process, list_repo)
            cli_control.show()
        else:
            import sys
            app = QtWidgets.QApplication(sys.argv)
            av = SetupApp(list_repo)
            av.show()
            sys.exit(app.exec_())
    else:
        logger.error(f'Failed to read the repositories directories. '+\
            'Please make sure you had cloned all the repositories')
