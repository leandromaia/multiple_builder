import os

from util import  Const


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


class Process(object):
    def __init__(self):
        self.is_build_full = False
        self.is_clean_m2 = False
        self.is_to_reset = False
        self.build_branch = Const.BUILD_BRANCH
