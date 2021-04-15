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


class ProcessNotValid(Exception):
    "Raise a warning indicating an invalid rule for execute a process"
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


class ProcessBuildFull:
    GIT_CHECKOUT_CMD = 'git checkout '
    GIT_CHECKOUT_MASTER_CMD = 'git checkout master'
    GIT_CLEAN_CMD = 'yes y | git clean -fxd'
    GIT_RESET_HARD_MASTER_CMD = 'git reset --hard origin/master'
    GIT_PULL_CMD = 'git pull'

    def __init__(self):
        self.is_clean_m2 = False
        self.is_to_reset = True
        self.is_to_update = True
        self.is_build_all = True
        self.build_branch = Const.BUILD_BRANCH
        self.build_command = None
        self.repositories = list()

    def execute_build_process(self, repositories):
        self._clean_m2_project_folder()

        for repository in repositories:
            repository_path = repository._absolute_path

            self._prepare_repository(repository_path)

            pull_result = self._update_repository(repository._absolute_path)

            self._execute_build_process(repository, pull_result)

    def _clean_m2_project_folder(self):
        if self.is_clean_m2:
            PathHelper.delete_m2()

    def _prepare_repository(self, repository_path):
        self._run_process_command(self.GIT_CLEAN_CMD, repository_path)
        
        command = self.GIT_CHECKOUT_CMD + self.build_branch
        self._run_process_command(command, repository_path)

        self._run_process_command(self.GIT_RESET_HARD_MASTER_CMD, \
                                                        repository_path)

    def _update_repository(self, repository_path):
        if self.is_to_update:
            return self._run_process_command(self.GIT_PULL_CMD, \
                                                            repository_path)

    def _execute_build_process(self, repository, pull_result):
        try:
            self._is_process_to_build(pull_result, repository.initial)

            self._run_process_command(repository.build_command, \
                                                    repository._absolute_path)
        except ProcessNotValid as e:
            logger.info(e)

    def _is_process_to_build(self, pull_result, initial):
        if (not self.is_build_all or not self.is_clean_m2) \
                and Const.PULL_UPDATED in pull_result:
            raise ProcessNotValid(f'The {initial} has not been built!')

    def _run_process_command(self, command, path):
        try:
            # process = subprocess.run(command, shell=True, check=True, \
            #                             stdout=subprocess.PIPE, cwd=path, \
            #                                 universal_newlines=True)

            logger.info(f'The command: "{command}" to the repository: ' +\
                                        f'{path} has executed successfully')
            return 'process.stdout'
        except subprocess.CalledProcessError as e:
            raise BuilderProcessException(\
                f'Failed executing the command: "{command}". '+\
                                f'to the repository {path} '+\
                                    f'Exception: {e}')


class ProcessPersonalized(ProcessBuildFull):

    def __init__(self):
        super().__init__()
        self.is_to_reset = False
        self.is_to_update = False
        self.is_build_all = False
   

class ProcessSkipMenu(ProcessBuildFull):
    pass


class Repository:
    _initial = None
    _build_command = None

    def __init__(self, absolute_path):
        self._is_valid_absolute_path(absolute_path)        
        self._absolute_path = absolute_path        
        self._build_initial_value()

    def _is_valid_absolute_path(self, absolute_path):
        if not os.path.isdir(absolute_path):
            raise BuilderProcessException(\
                            f"The directory {absolute_path} doesn't exist!!!")

    def _build_initial_value(self):
        self._initial = self._absolute_path.split('.')[-1].upper()

    @property
    def initial(self):
        return self._initial \
            if self._initial \
                else self._build_initial_value()       

    @property
    def build_command(self):
        return self._build_command \
            if self._build_command \
                else Const.BUILD_CMDS.get(1)

    @build_command.setter
    def build_command(self, command):
        if command in Const.BUILD_CMDS.values():
            self._build_command = command
        else:
            raise BuilderProcessException(\
                            f"The '{command}' is not a valid Maven command.")

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
    def _get_m2_path():
        return Path.joinpath(Path.home(), Const.M2_PATH)

    @staticmethod
    def _validate_m2_path(m2_path):
        if not m2_path.is_dir():
            raise BuilderProcessException(\
                f'Is not possible to clean the M2 project. The path '+\
                            f'{m2_path} is not a valid directory')

    @staticmethod
    def fetch_repo_paths(root_path):
        """Process the root path and extract all valid repository paths
        from the root path."""
        root_path = PathHelper._get_valid_root_path(root_path)

        absolute_paths = PathHelper.\
                        _extract_all_absolute_paths_from_root_path(root_path)

        repo_paths = PathHelper._extract_repo_paths(absolute_paths)

        PathHelper._has_valid_repo_paths(repo_paths)

        return repo_paths

    @staticmethod
    def _get_valid_root_path(root_path):
        return root_path if root_path else os.getcwd()

    @staticmethod
    def _extract_all_absolute_paths_from_root_path(root_path):
        return [f.path for f in os.scandir(root_path) if f.is_dir()]

    @staticmethod
    def _extract_repo_paths(absolute_paths):
        return [a for a in absolute_paths \
                    for r in Const.REPO_PATHS if a.endswith(r)]

    @staticmethod
    def _has_valid_repo_paths(repo_paths):
        if len(repo_paths) == 0:
            raise BuilderProcessException(\
                f'Failed to read the repositories directories.'+\
                    'Please make sure you had cloned the GIT repositories.')


class MultipleBuilderCLI:
    CHOICE_REPO_MSG = \
            'You can select more than one options adding space between them:'
    HEADER_MSG = '#######################################################'\
                +'\n####### Multiple Builder - Choice Your Options ########'\
                +'\n#######################################################'
    MENU_OPTIONS_TO_ONE_RESPONSE = (1, 2)
    CORRECT_OPTION_TO_ONE_ANSWER = 1
    REQUEST_IS_TO_RESET_MSG = 'Do you want to reset your repositories branch,'\
                        +' using "git reset --hard <<branch name >>?":\n1'\
                        +' - Yes\n2 - No\nR: '
    REQUEST_IS_TO_UPDATE_MSG = 'Do you want to update all your repositories'\
                        +' branch, using "git pull":\n1 - Yes\n2 - No\nR: '
    REQUEST_WAY_BUILD_REPO_MSG = 'Do you want build all your repositories '\
                                    +'or just that has been updated?'\
                                    +'\n1 - All.\n2 - Just the updated.\nR: '
    REQUEST_BUILD_CMD_MSG = 'Which Maven command should to use '\
                                    +'in build process:\n'

    REQUEST_BRANCH_TO_BUILD_MSG = 'Which branch all the repositories should '\
                            +'to build?\nType only M to default branch master'\
                            +' ou type the desired branch name:\nR: '

    def request_user_repositories(self, initials):        
        indexes = self._build_indexes(initials)
        menu = self._build_menu(indexes, initials)

        repos = self._request_repo_to_build(menu, indexes)

        return self._extract_valid_repo(menu, repos)

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
                try:
                    self._is_valid_response_by_indexes(response, indexes)
                except ProcessNotValid as e:
                    logger.warning(e)
                    break
            else:
                return user_responses

    def _show_message_to_user(self, message):
        print(message)

    def _request_with_multiple_response(self, message):
        self._show_message_to_user(self.CHOICE_REPO_MSG)

        return self._request_user_response(message).split()

    def _request_user_response(self, message):
        return input(message)

    def _is_valid_response_by_indexes(self, response, indexes):
        if int(response) not in indexes:
            raise ProcessNotValid(f'Invalid choice: Failed - Not a ' +\
                                f'valid index. Please choose a valid option')

    def _extract_valid_repo(self, menu, repos):
        return set([m for repo in repos \
                        for m in menu.split('\n') if repo in m])

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
            try:
                user_awser = self._request_user_response(menu)

                self._is_valid_response_by_indexes(user_awser, indexes)
                break
            except ProcessNotValid as e:
                logger.warning(e)

        return user_awser

    def _is_correct_response(self, response_value):
        return True if int(response_value) == \
                            self.CORRECT_OPTION_TO_ONE_ANSWER \
                                else False


class MultipleBuilderCLIController:

    def __init__(self):
        self._cli = MultipleBuilderCLI()
        self._command_args  = CommandArgsProcessor()
        self._process = None

    def build_process(self, repositories):
        process = None

        if self._command_args.is_build_full():
            process = ProcessBuildFull()
            process.repositories = repositories
        elif self._command_args.is_to_skip_menu():
            process = ProcessSkipMenu()
            self._setup_personalized_repository(process, repositories)
        else:
            process = ProcessPersonalized()
            self._setup_personalized_repository(process, repositories)
            self._set_personalized_process_values(process)

        process.is_clean_m2 = self._command_args.is_to_clean_m2()

        return process

    def _setup_personalized_repository(self, process, repositories):
        repositories_initial = self._get_repositories_initial(repositories)
        
        user_response = self._cli.request_user_repositories(\
                                                    repositories_initial)
        
        process.repositories = self._filter_repositories_user_response(\
                                                        user_response, \
                                                            repositories)

    def _get_repositories_initial(self, repositories):
        return [r.initial for r in repositories]

    def _filter_repositories_user_response(self, choices, repositories):
        return [repository for repository in repositories \
                        for choice in choices \
                            if choice.endswith(repository.initial)]
    
    def _set_personalized_process_values(self, process):
        process.build_command = self._cli.request_type_build_comands()

        process.is_to_reset = self._cli.request_is_to_reset()
        process.is_to_update = self._cli.request_is_to_update()
        process.build_branch = self._cli.request_branch_to_build()

        self._set_is_to_build_all(process)   
    
    def _set_is_to_build_all(self, process):
        if process.is_to_update:
            process.is_build_all = self._cli.request_is_to_build_all()

    def build_repositories(self):
        repositories_paths = self._get_repositories_paths()

        return self._initiate_repositories(repositories_paths)
   
    def _get_repositories_paths(self):
        paths_from_command_args = self._command_args.repos_directory

        return PathHelper.fetch_repo_paths(paths_from_command_args)

    def _initiate_repositories(self, repositories_paths):
        repositories = list()

        for path in repositories_paths:
            try:
                repositories.append(Repository(path))
            except BuilderProcessException as e:
                logger.warning(e)
        
        return repositories
   


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
                    "Passing this option all the found repositories \
                    will be update and build automatically\
                    and the menu is skipped."

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
    SKIP_MENU_HELP = "This option allow to select which repository must be \
                    updated, but all the others menu questions is skipped."

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

        skip_menu = CommandArgument(
            flag = self.SKIP_MENU_FLAG,
            name = self.SKIP_MENU_NAME,
            action = self.ACTION_STORE_TRUE,
            help = self.SKIP_MENU_HELP
        )

        repos_dir = CommandArgument(
            flag = self.REPOS_DIR_FLAG,
            name = self.REPOS_DIR_NAME,
            help = self.REPOS_DIR_HELP
        )

        arg_list.append(build_full)
        arg_list.append(clean_m2)
        arg_list.append(skip_menu)
        arg_list.append(repos_dir)

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


def start_build():
    try:
        setup_logger()

        cli_controller = MultipleBuilderCLIController()

        repositories = cli_controller.build_repositories()
        
        process = cli_controller.build_process(repositories)

        process.execute_build_process(repositories)

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
