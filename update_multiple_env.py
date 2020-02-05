#!/usr/bin/env python
import argparse
import os
import logging
import subprocess
import shutil
from pathlib import Path
from PyQt5 import QtWidgets
from main_window import Ui_MainWindow

logger = None

def setup_logger():
    global logger
    logFormatter = '> %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatter, level=logging.DEBUG)
    logger = logging.getLogger(__name__)


class Const(object):
    PULL_UPDATED = "Already up to date"                   
    MAVEN_COMMAND = ['mvn', 'clean','install']
    PULL_UPDATED = "Already up to date"
    
    # M2_PATH = ".m2/repository/"
    # REPO_PATHS = ('sample_1',
    #                 'sample_2',                    
    #                     'sample_3',
    #                         'sample_4',
    #                             'sample_5',
    #                                 'sample_6')

    M2_PATH = ".m2/repository/com/ericsson/bss"
   
    REPO_PATHS = ('com.ericsson.bss.ael.aep', 
                    'com.ericsson.bss.ael.aep.plugins',
                        'com.ericsson.bss.ael.bae',
                            'com.ericsson.bss.ael.dae',
                                'com.ericsson.bss.ael.jive',
                                    'com.ericsson.bss.ael.aep.sdk')


    BUILD_CMDS = {
        1: 'gradlew clean build',
        2: 'gradlew clean build -x test -x check -x javadoc',
        3: 'gradlew clean jar',
        4: 'gradlew clean install'
    }
    BUILD_BRANCH = 'master'
    BUILD_BRANCH_OPT = 'M'


class HandlerProcess(object):

    def __init__(self, process):
        self._process = process

    def start_process(self, repositories):
        self._clean_m2_project_folder()

        for repo in repositories:
            pull_result = self._update_repository(repo._absolute_path)
            
            if Const.PULL_UPDATED not in pull_result \
                        or self._process.is_clean_m2 \
                            or self._process.is_skip_menu:
                self._wrapper_run_process(repo.build_command, \
                                                repo._absolute_path)
            else:
                logger.info(\
                    f'The {repo.repo_initial} its already up to date!')

    def _clean_m2_project_folder(self):
        if self._process.is_clean_m2:
            PathHelper.delete_m2()

    def _update_repository(self, repo_path):
        if self._process.is_to_reset:
            self._update_with_reset(repo_path)
        else:
            args_checkout = ['git', 'checkout', self._process.build_branch]
            self._wrapper_run_process(args_checkout, repo_path)
        
        args_pull = ['git', 'pull']
        return self._wrapper_run_process(args_pull, repo_path)

    def _update_with_reset(self, repo_path):
        args_reset = ['yes', 'y', '|', 'git', 'clean', '-fxd']
        self._wrapper_run_process(args_reset, repo_path)

        args_checkout = ['git', 'checkout', 'master']
        self._wrapper_run_process(args_checkout, repo_path)

        args_reset = ['git', 'reset', '--hard', 'origin/master']
        self._wrapper_run_process(args_reset, repo_path)

    def _wrapper_run_process(self, command, path):
        process = subprocess.run(command, shell=True, check=True, \
                                    stdout=subprocess.PIPE, cwd=path, \
                                        universal_newlines=True)
        logger.info(f'The command: {command} to repository: {path} '+\
                                                'has executed successfully')
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
        #TODO Replace the structure below to with
        if os.path.isdir(absolute_path):
            self._absolute_path = absolute_path
            self._build_initial_value()
        else:
            logger.error(f"The directory {absolute_path} doesn't exist!!!")
            raise OSError(f"The directory {absolute_path} doesn't exist!!!")

    def _build_initial_value(self):
        self._initial = self._absolute_path.split('.')[-1].upper()

    @property
    def repo_initial(self):
        if not self._initial:
            self._build_initial_value()
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
    def delete_m2():
        absolute_m2_path = Path.joinpath(Path.home(), Const.M2_PATH)
        
        if absolute_m2_path.is_dir():
            try:
                shutil.rmtree(absolute_m2_path)
                logger.info(f"The m2 folder: {absolute_m2_path} "+\
                                            "has deleted sucessfully")
            except OSError:
                logger.error(f'Process to delete folders and files from ' + \
                                        f'{absolute_m2_path} has failed.')
        else:
            logger.warning(f'Is not possible to clean the M2 project. ' +\
                    f'The path {absolute_m2_path} is not a valid directory')
    
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
                'using "git reset --hard <<branch name >>":\n'+\
                    '1 - Yes\n2 - No\nR: '
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

    def ask_wich_build_branch(self):
        user_awser = input("Which branch all the repositories should to "+ \
                    "build?\nType only M to default branch master ou type"+ \
                    " the desired branch name:\nR: ")
        return Const.BUILD_BRANCH \
                    if user_awser.upper() == Const.BUILD_BRANCH_OPT \
                        else user_awser

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
            logger.error(f'Invalid choice: {awser}. ' +\
                                    'Please choose a valid option')
            return False
        return True


class Process(object):
    def __init__(self):
        self.is_build_full = False
        self.is_clean_m2 = False
        self.is_to_reset = False
        self.is_skip_menu = False
        self.build_branch = Const.BUILD_BRANCH


class SetupApp(QtWidgets.QMainWindow):

    def __init__(self):
        super(SetupApp, self).__init__()
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect up the button.
    #     self.ui.pushButton_Calcular.clicked.connect(self.calcular_imc)

    # def calcular_imc(self):
    #     altura = eval(self.ui.altura_le.text())
    #     peso = eval(self.ui.peso_le.text())
    #     imc = peso / (altura * altura)
    #     self.ui.imc_lb.setText(f'self.ui.imc_lb.text(): {str(imc)}')


if __name__ == "__main__":
    
    setup_logger()

    cmd_args_proc = CommandArgsProcessor()

    process = Process()
    process.is_build_full = cmd_args_proc.is_build_full()
    process.is_clean_m2 = cmd_args_proc.is_to_clean_m2()
    process.is_skip_menu = cmd_args_proc.is_to_skip_menu()

    repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

    list_repo = [Repository(r) for r in repo_paths]

    if len(repo_paths) > 0:
        gradle_cmd = None

        if not process.is_skip_menu:
            cli = CliInterface()
            list_repo = cli.ask_desired_repos(list_repo)
            process.is_to_reset = cli.ask_is_to_reset()
            process.build_branch = cli.ask_wich_build_branch()

            if not process.is_build_full:
                gradle_cmd = cli.ask_type_gradle_build()
        else:
            import ipdb; ipdb.set_trace()
            import sys
            app = QtWidgets.QApplication(sys.argv)
            av = SetupApp()
            av.show()
            sys.exit(app.exec_())

    #     if not gradle_cmd:
    #         gradle_cmd = Const.BUILD_CMDS.get(1)

    #     for r in list_repo:
    #         r.build_command = gradle_cmd

    #     handler = HandlerProcess(process)
    #     handler.start_process(list_repo)
    else:
        logger.error(f'Failed to read the repositories directories. '+\
            'Please make sure you had cloned all the repositories')
