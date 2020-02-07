import os
import logging
import subprocess
import shutil

from pathlib import Path

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


class PathHelper(object):
    @staticmethod
    def delete_m2():
        import ipdb; ipdb.set_trace()
        setup_logger()
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


class Process(object):
    def __init__(self):
        self.is_build_full = False
        self.is_clean_m2 = False
        self.is_to_reset = False
        self.is_skip_menu = False
        self.build_branch = Const.BUILD_BRANCH


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
