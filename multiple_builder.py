#!/usr/bin/env python
import argparse
import os
import logging
import subprocess
import shutil

from pathlib import Path
from typing import TypedDict, Text


logger = None


class BuilderProcessException(Exception):
    "Raise a found error during the Multiple Builder process executing"
    pass


class Const:
    PULL_UPDATED = "Already up to date"
    
    M2_PATH = ".m2/repository/"

    REPO_PATHS = ('com.ericsson.bss.ael.aep', 
                'com.ericsson.bss.ael.aep.plugins',
                        'com.ericsson.bss.ael.bae',
                        'com.ericsson.bss.ael.dae',
                            'com.ericsson.bss.ael.jive',
                                    'com.ericsson.bss.ael.aep.sdk')

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

    def _check_is_process_to_build(self):
        return True \
            if self._process.is_build_all or self._process.is_clean_m2 or\
                                                self._process.is_skip_menu\
            else False

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
        """Delete all the folders and files from the Maven m2 folder"""
        m2_path = PathHelper._get_m2_path()

        PathHelper._validate_m2_path(m2_path)

        try:
            shutil.rmtree(m2_path)

            logger.info(f"The m2 folder: {m2_path} "+\
                                        "has been deleted successfully")
        except OSError:
            raise BuilderProcessException(\
                f'Process to delete folders and files from ' + \
                                f'{m2_path} has failed.')

    @staticmethod
    def _validate_m2_path(m2_path):
        if not m2_path.is_dir():
            raise BuilderProcessException(\
                f'Is not possible to clean the M2 project. The path '+\
                            f'{m2_path} is not a valid directory')

    @staticmethod
    def _get_m2_path():
        return Path.joinpath(Path.home(), Const.M2_PATH)

    @staticmethod
    def fetch_repo_paths(root_path):
        """Process the root path and extract all valid repository paths
        from the root path."""
        root_path = PathHelper._get_root_path(root_path)

        raw_paths = PathHelper._extract_directories_from_path(root_path)

        valid_repo_paths = PathHelper._extract_valid_repo_paths(raw_paths)

        PathHelper._check_has_valid_repo_paths(valid_repo_paths)

        return valid_repo_paths

    @staticmethod
    def _get_root_path(root_path):
        return os.getcwd() if not root_path else root_path

    @staticmethod
    def _extract_directories_from_path(root_path):
        return [f.path for f in os.scandir(root_path) if f.is_dir()]

    @staticmethod
    def _extract_valid_repo_paths(all_paths):
        return [a for a in all_paths \
                    for r in Const.REPO_PATHS if a.endswith(r)]

    @staticmethod
    def _check_has_valid_repo_paths(repo_paths):
        if len(repo_paths) == 0:
            raise BuilderProcessException(\
                f'Failed to read the repositories directories.'+\
                    'Please make sure you had cloned the GIT repositories.')


class CliInterface:
    CHOICE_REPO_MSG = \
            'You can select more than one options adding space between them:'
    HEADER_MSG = '#######################################################'\
                +'\n####### Multiple Builder - Choice Your Options ########'\
                +'\n#######################################################'
    MENU_OPTIONS_TO_ONE_RESPONSE = (1, 2)
    CORRECT_OPTION_TO_ONE_ANSWER = 1
    REQUEST_IS_TO_RESET_MSG = 'Do you want to reset your repositories branch, '\
                        +'using "git reset --hard <<branch name >>?":\n1'\
                        +' - Yes\n2 - No\nR: '
    REQUEST_IS_TO_UPDATE_MSG = 'Do you want to update all your repositories'\
                        +' branch, using "git pull":\n1 - Yes\n2 - No\nR: '
    REQUEST_WAY_BUILD_REPO_MSG = 'Do you want build all your repositories '\
                                    +'or just that has been updated?'\
                                    +'n1 - All.\n2 - Just the updated.\nR: '
    REQUEST_BUILD_CMD_MSG = 'Which Maven command should to use '\
                                    +'in build process:'

    REQUEST_BRANCH_TO_BUILD_MSG = 'Which branch all the repositories should '\
                            +'to build?\nType only M to default branch master'\
                            +' ou type the desired branch name:\nR: '

    @property
    def is_build_full(self):
        return self._is_build_full

    @property
    def is_clean_m2(self):
        return self._is_clean_m2

    @property
    def is_skip_menu(self):
        return self._is_skip_menu

    def request_desired_repos(self, list_repo):
        repo_names = self._extract_repo_names(list_repo)
        
        indexes = self._build_indexes(repo_names)
        menu = self._build_menu(indexes, repo_names)

        repos = self._request_repo_to_build(menu, indexes)
        repos = self._extract_valid_repo(menu, repos)

        return self._consolidate_valid_repos(list_repo, repos)

    def _extract_repo_names(self, list_repo):
        return [r.repo_initial for r in list_repo]

    def _build_indexes(self, options):
        return [* range(1, len(options) + 1)]

    def _build_menu(self, indexes, options):
        menu = str()

        for index, option in zip(indexes, options):
            menu = f'{menu}{index} - {option}\n'

        menu = menu + 'R: '
        return menu

    def _request_repo_to_build(self, menu, indexes):      
        self._show_message_to_user(self.HEADER_MSG)
        
        while True:
            user_responses = self._request_with_multiple_response(menu)

            for response in user_responses:
                if not self._is_valid_response_by_indexes(response, indexes):
                    break
            else:
                return user_responses

    def _show_message_to_user(self, message):
        print(message)

    def _request_user_response(self, message):
        return input(message)

    def _request_with_multiple_response(self, message):
        self._show_message_to_user(self.CHOICE_REPO_MSG)

        return self._request_user_response(message).split()

    def _is_valid_response_by_indexes(self, response, indexes):
        if int(response) not in indexes:
            logger.warning(f'Invalid choice: Failed - Not a valid index. ' +\
                                'Please choose a valid option')
            return False
        else:
            return True

    def _extract_valid_repo(self, menu, repos):
        return set([m for repo in repos \
                        for m in menu.split('\n') if repo in m])

    def _consolidate_valid_repos(self, list_repo, choices):
        return [repo for repo in list_repo \
                        for c in choices \
                            if c.endswith(repo.repo_initial)]

    def request_type_build_comands(self):
        commands = list(Const.BUILD_CMDS.values())
        commands_indexes = list(Const.BUILD_CMDS.keys())

        menu = self._build_menu(commands_indexes, commands)
        menu = self.REQUEST_BUILD_CMD_MSG + menu

        return self._handle_build_command_response(menu, commands_indexes)

    def _handle_build_command_response(self, menu, commands_indexes):
        response_index = self._request_only_one_response(\
                                                    menu, commands_indexes)
        
        return Const.BUILD_CMDS.get(int(response_index))

    def request_branch_to_build(self):
        user_response = self._request_user_response(\
                                            self.REQUEST_BRANCH_TO_BUILD_MSG)

        return Const.BUILD_BRANCH \
                    if user_response.upper() == Const.BUILD_BRANCH_OPT \
                        else user_response
    
    def request_is_to_reset(self):
        return self._handle_one_response(self.REQUEST_IS_TO_RESET_MSG)

    def request_is_to_update(self):
        return self._handle_one_response(self.REQUEST_IS_TO_UPDATE_MSG)

    def request_is_to_build_all(self):
        return self._handle_one_response(self.REQUEST_WAY_BUILD_REPO_MSG)

    def _handle_one_response(self, request_message):
        response = self._request_only_one_response(\
                                            request_message,\
                                            self.MENU_OPTIONS_TO_ONE_RESPONSE)
        return self._is_correct_response(response)

    def _request_only_one_response(self, menu, indexes):
        user_awser = None

        while True:
            user_awser = self._request_user_response(menu)
            if self._is_valid_response_by_indexes(user_awser, indexes):
                break

        return user_awser

    def _is_correct_response(self, response_value):
        return True if int(response_value) == \
                            self.CORRECT_OPTION_TO_ONE_ANSWER \
                                else False
 


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

    def __init__(self):
        self._cli = CliInterface()
        self._cmd_args_proc  = CommandArgsProcessor()      

    def build_repositories(self, process):
        repo_paths = PathHelper.fetch_repo_paths(\
                                        self._cmd_args_proc.repos_directory)

        self._list_repo = [Repository(r) for r in repo_paths]
        self._list_repo = self._cli.request_desired_repos(self._list_repo)
        return self._format_repositories(process)

    def _format_repositories(self, process):
        if not process.is_build_full and not process.is_skip_menu:
            build_cmd = self._cli.request_type_build_comands()
        else:
            build_cmd = Const.BUILD_CMDS.get(1)

        for r in self._list_repo:
            r.build_command = build_cmd
        
        return self._list_repo

    def build_process(self):
        process = self._initiate_process()

        if not process.is_skip_menu:
            process.is_to_reset = self._cli.request_is_to_reset()
            process.is_to_update = self._cli.request_is_to_update()

            if process.is_to_update:
                process.is_build_all = self._cli.is_build_full

            process.build_branch = self._cli.request_branch_to_build()

        return process

    def _initiate_process(self):
        process = Process()
        process.is_build_full = self._cmd_args_proc.is_build_full()
        process.is_clean_m2 = self._cmd_args_proc.is_to_clean_m2()
        process.is_skip_menu = self._cmd_args_proc.is_to_skip_menu()
        return process


class CommandArgument(TypedDict, total=False):
    """A command argument for the Command Args Processor.

    Attributes:
        flag: The flag identify of the CommandArgument.
        name: The body of the CommandArgument, also used as
                a command method identify.
        action: The action for the CommandArgument.
        help: Text description that helps the usage of the command.
    """
    flag: Text
    name: Text
    action: Text
    help: Text


class CommandArgsProcessor:
    ACTION_STORE_TRUE = "store_true"
    ARGUMENT_PARSER_DESCRIPTION = \
                        ">>>>> Options to update and build projects! <<<<<"

    BUILD_FLAG = "-b"
    BUILD_NAME = "--build-full"
    BUILD_HELP = "Execute the full build command: "+\
                    f"'{Const.BUILD_CMDS.get(1)}'. " +\
                    "This option also skip the menu to select the \
                    others Maven options."

    CLEAN_M2_FLAG = "-c"
    CLEAN_M2_NAME = "--clean-m2"
    CLEAN_M2_HELP = "Delete all folders and files from project m2 folder."

    REPOS_DIR_FLAG = "-d"
    REPOS_DIR_NAME = "--repos-directory"
    REPOS_DIR_HELP = "Add your repositories absolute path. If this \
                        parameter is not passed the script absolute path \
                        will be consider as the root path to find the \
                        repositories folder."

    SKIP_MENU_FLAG = "-sm"
    SKIP_MENU_NAME = "--skip-menu"
    SKIP_MENU_HELP = "Skip visualization of the CLI User Menu. \
                        Passing this option all the found repositories \
                        will be update and build automatically."

    def __init__(self):
        parser = self._initiate_parser()

        arg_list = self._create_arguments()

        self._populate_args(arg_list, parser)
        self._parsed_args = parser.parse_args()

    def _initiate_parser(self):
        return argparse.ArgumentParser(description=\
                                            self.ARGUMENT_PARSER_DESCRIPTION)
    
    def _create_arguments(self):
        arg_list = list()

        build_full = CommandArgument(
            flag = self.BUILD_FLAG,
            name = self.BUILD_NAME,
            action = self.ACTION_STORE_TRUE,
            help = self.BUILD_HELP
        )

        clean_m2 = CommandArgument(
            flag = self.CLEAN_M2_FLAG,
            name = self.CLEAN_M2_NAME,
            action = self.ACTION_STORE_TRUE,
            help = self.CLEAN_M2_HELP
        )

        repos_dir = CommandArgument(
            flag = self.REPOS_DIR_FLAG,
            name = self.REPOS_DIR_NAME,
            help = self.REPOS_DIR_HELP
        )

        skip_menu = CommandArgument(
            flag = self.SKIP_MENU_FLAG,
            name = self.SKIP_MENU_NAME,
            action = self.ACTION_STORE_TRUE,
            help = self.SKIP_MENU_HELP
        )

        arg_list.append(build_full)
        arg_list.append(clean_m2)
        arg_list.append(repos_dir)
        arg_list.append(skip_menu)

        return arg_list

    def _populate_args(self, arg_list, parser):
        for arg in arg_list:
            parser.add_argument(arg.get('flag'),
                        arg.get('name'),
                        action=arg.get('action', None),
                        help=arg.get('help'))
    
    def is_build_full(self):
        """Returns True if the build must be full or False is not."""
        return self._parsed_args.build_full

    def is_to_clean_m2(self):
        """Returns True for to clean the Maven m2 folder or False is not."""
        return self._parsed_args.clean_m2

    def is_to_skip_menu(self):
        """Returns True for to skip the menu or False is not."""
        return self._parsed_args.skip_menu

    @property
    def repos_directory(self):
        return self._parsed_args.repos_directory


def setup_logger():
    global logger
    logFormatter = '> %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatter, level=logging.DEBUG)
    logger = logging.getLogger(__name__)


def initiate_process(command_processor):
        process = Process()
        process.is_build_full = command_processor.is_build_full()
        process.is_clean_m2 = command_processor.is_to_clean_m2()
        process.is_skip_menu = command_processor.is_to_skip_menu()
        return process


def start_build():
    try:
        setup_logger()

        build_inputs = BuildProcessInputs()

        process = build_inputs.build_process()

        repositories = build_inputs.build_repositories(process)
              
        handler = ProcessHandler(process)
        handler.start_process(repositories)

    except KeyboardInterrupt:
        logger.info(f'The process has finished by CTRL+C.')
        logger.info("Exiting! Have a nice day!!!")
    except EOFError:
        logger.info(f'The process has finished by Caa TRL+Z.')
        logger.info("Exiting! Have a nice day!!!")
    except BuilderProcessException as e:
        logger.error(e, exc_info=True)


if __name__ == "__main__":
    start_build()
