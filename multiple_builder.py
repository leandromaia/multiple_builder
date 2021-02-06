#!/usr/bin/env python
import argparse
import os
import logging
import subprocess
import shutil
from pathlib import Path

logger = None


class BuilderProcessException(Exception):
    "Raise a found error during the Multiple Builder process executing"
    pass


class Const:
    PULL_UPDATED = "Already up to date"
    
    M2_PATH = ".m2/repository/"

    REPO_PATHS = ('sample_1',
                    'sample_2',                    
                        'sample_3',
                            'sample_4',
                                'sample_5',
                                    'sample_6')

    BUILD_CMDS = {
        1: 'mvn clean install',
        2: 'mvn clean install -T 4',
        3: 'mvn clean install -T 4 -DskipTests',
        4: 'mvn clean install -T 4 -DskipTests -Dmaven.javadoc.skip=true',
        5: 'mvn clean isntall -T 4 -DskipTests -Dmaven.javadoc.skip=true -Dmaven.source.skip=true'
    }
    BUILD_BRANCH = 'master'
    BUILD_BRANCH_OPT = 'M'


class ProcessHandler:

    def __init__(self, process):
        self._process = process

    def start_process(self, repositories):
        self._clean_m2_project_folder()
        is_to_build = self._check_is_process_to_build()

        for repo in repositories:
            pull_result = str()

            if self._process.is_to_update:
                pull_result = self._update_repository(repo._absolute_path)

            if is_to_build or Const.PULL_UPDATED not in pull_result:
                self._wrapper_run_process(repo.build_command, \
                                                    repo._absolute_path)
            else:
                logger.info(f'The {repo.repo_initial} has not been built!')

    def _check_is_process_to_build(self):
        return True \
            if self._process.is_build_all or self._process.is_clean_m2 or\
                                                self._process.is_skip_menu\
            else False

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
        args_checkout = ['git', 'checkout', 'master']
        args_reset = ['git', 'reset', '--hard', 'origin/master']

        self._wrapper_run_process(args_reset, repo_path)
        self._wrapper_run_process(args_checkout, repo_path)
        self._wrapper_run_process(args_reset, repo_path)

    def _wrapper_run_process(self, command, path):
        try:
            process = subprocess.run(command, shell=True, check=True, \
                                        stdout=subprocess.PIPE, cwd=path, \
                                            universal_newlines=True)
            logger.info(f'The command: "{command}" to the repository: {path} '+\
                            f'has executed successfully')
            return process.stdout
        except subprocess.CalledProcessError as e:
            raise BuilderProcessException(\
                f'Failed executing the command: "{command}". '+\
                                f'to the repository {path} '+\
                                    f'Exception: {e}')





class Repository:
    _initial = None
    _build_command = None

    def __init__(self, absolute_path):
        if os.path.isdir(absolute_path):
            self._absolute_path = absolute_path
            self._build_initial_value()
        else:
            # FIXME the log below is ambiguous
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
        if self._build_command:
            return self._build_command
        else:
            return Const.BUILD_CMDS.get(1)

    @build_command.setter
    def build_command(self, cmd):
        if cmd in Const.BUILD_CMDS.values():
            self._build_command = cmd
        else:
            raise ValueError(f"The '{cmd}' is not a valid Maven command.")

    def __str__(self):
        return self._initial


class PathHelper:

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


class CliInterface:
    MENU_OPTIONS_TO_ONE_ANSWER = (1, 2)
    POSITIVE_OPTION_TO_ONE_ANSWER = 1

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
                'using "git reset --hard <<branch name >>?":\n'+\
                    '1 - Yes\n2 - No\nR: '
        user_awser = self._get_only_one_answer(\
                                        menu, self.MENU_OPTIONS_TO_ONE_ANSWER)
        return True \
                if int(user_awser) == self.POSITIVE_OPTION_TO_ONE_ANSWER \
                    else False

    def ask_is_to_update(self):
        menu = 'Do you want to update all your repositories branch, '+\
                'using "git pull":\n'+\
                    '1 - Yes\n2 - No\nR: '
        user_awser = self._get_only_one_answer(\
                                        menu, self.MENU_OPTIONS_TO_ONE_ANSWER)
        return True \
                if int(user_awser) == self.POSITIVE_OPTION_TO_ONE_ANSWER \
                    else False

    def ask_is_to_build_all(self):
        menu = 'Do you want build all your repositories or just that'+\
            ' has been updated?\n1 - All.\n2 - Just the updated.\nR: '
        user_awser = self._get_only_one_answer(\
                                        menu, self.MENU_OPTIONS_TO_ONE_ANSWER)
        return True \
                if int(user_awser) == self.POSITIVE_OPTION_TO_ONE_ANSWER \
                    else False

    def ask_type_command_build(self):
        cmds = list(Const.BUILD_CMDS.values())
        key_indexes = list(Const.BUILD_CMDS.keys())

        menu, indexes = self._build_menu_options(cmds, key_indexes)        
        menu = f"Which Maven command should to use in build process:\n{menu}"

        user_awser = int(self._get_only_one_answer(menu, indexes))
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
        print('######## Multiple Builder - Choice Your Options #########')
        print('#########################################################')
        while True:
            print(\
                'You can select more than one options adding space between them:')
            raw_awser = input(menu).split()

            for awser in raw_awser:
                if not self._is_valid_answer_by_indexes(awser, indexes):
                    break
            else:
                return raw_awser
           
    def _get_only_one_answer(self, menu, indexes):
        user_awser = None
        while True:
            user_awser = input(menu)
            if self._is_valid_answer_by_indexes(user_awser, indexes):
                break
        return user_awser
    
    def _is_valid_answer_by_indexes(self, answer, indexes):
        try:
            if int(answer) not in indexes:
                raise ValueError("Failed - Not a valid index.")
        except ValueError:
            logger.warning(f'Invalid choice: {answer}. ' +\
                                    'Please choose a valid option')
            return False
        return True


class Process:
    def __init__(self):
        self.is_build_full = False
        self.is_clean_m2 = False
        self.is_to_reset = False
        self.is_to_update = False
        self.is_skip_menu = False
        self.is_build_all = False
        self.build_branch = Const.BUILD_BRANCH


class BuildProcessInputs:

    def __init__(self, cli, command_processor, repo_paths):
        self._cli = cli
        self._command_processor = command_processor
        self._build_repositories(repo_paths)

    def build_process(self):
        self._initiate_process()

        if not self._process.is_skip_menu:
            self._process.is_to_reset = self._cli.ask_is_to_reset()
            self._process.is_to_update = self._cli.ask_is_to_update()

            if self._process.is_to_update:
                self._process.is_build_all = self._cli.ask_is_to_build_all()

            self._process.build_branch = self._cli.ask_wich_build_branch()

            self._format_repositories()

    def _initiate_process(self):
        self._process = Process()
        self._process.is_build_full = self._command_processor.is_build_full()
        self._process.is_clean_m2 = self._command_processor.is_to_clean_m2()
        self._process.is_skip_menu = self._command_processor.is_to_skip_menu()

    def _build_repositories(self, repo_paths):
        self._list_repo = [Repository(r) for r in repo_paths]
        self._list_repo = self._cli.ask_desired_repos(self._list_repo)

    def _format_repositories(self):
        if not self._process.is_build_full and not self._process.is_skip_menu:
            build_cmd = self._cli.ask_type_command_build()
        else:
            build_cmd = Const.BUILD_CMDS.get(1)

        for r in self._list_repo:
            r.build_command = build_cmd        

    @property
    def repositories(self):
        if self._list_repo:
            return self._list_repo



from typing import TypedDict, Text


class CommandArgument(TypedDict):
    """A command argument for the Command Args Processor.

    Attributes:
        flag: The flag identify of the CommandArgument.
        name: The body of the CommandArgument, also used as a command
                method identify.
        action: The action for the CommandArgument.
        help: Text description that helps the usage for th command.
    """
    flag: Text
    name: Text
    action: Text
    help: Text




#FIXME See: https://github.com/zedr/clean-code-python
class CommandArgsProcessor:

    def __init__(self):
        parser = argparse.ArgumentParser(description=\
                        '>>>>> Options to update and build projects! <<<<<')
        parser.add_argument('-b', \
                        '--build-full', \
                        action='store_true', \
                        help="Execute the full build command: "+\
                            f"'{Const.BUILD_CMDS.get(1)}'. " +\
                            "This option also skip the menu to select the \
                            others Maven options.")

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


def setup_logger():
    global logger
    logFormatter = '> %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatter, level=logging.DEBUG)
    logger = logging.getLogger(__name__)


def start_build():
    try:
        setup_logger()

        cmd_args_proc = CommandArgsProcessor()

        repo_paths = PathHelper.fetch_repo_paths(cmd_args_proc.repos_directory)

        if len(repo_paths) > 0:
            cli = CliInterface()
            build_inputs = BuildProcessInputs(cli, cmd_args_proc, repo_paths)

            handler = ProcessHandler(build_inputs.build_process())
            handler.start_process(build_inputs.repositories)
        else:
            raise BuilderProcessException(\
                f'Failed to read the repositories directories.'+\
                    'Please make sure you had cloned the GIT repositories.')

    except KeyboardInterrupt:
        logger.info(f'The process has finished by CTRL+C.')
        logger.info("Exiting! Have a nice day!!!")
    except EOFError:
        logger.info(f'The process has finished by CTRL+Z.')
        logger.info("Exiting! Have a nice day!!!")
    except BuilderProcessException as e:
        logger.error(e)


if __name__ == "__main__":
    start_build()
