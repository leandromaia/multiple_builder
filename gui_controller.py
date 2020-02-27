from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from main_gui import Ui_MainWindow
from core import Const, HandlerProcess
from models import Process


class MainGuiController(QtWidgets.QMainWindow):

    def __init__(self, process, repositories):
        super(MainGuiController, self).__init__()

        self._process = process
        self._repositories = repositories
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._create_checkBox_from_repositories()
        self.ui.comboBoxBuild.addItems(Const.BUILD_CMDS.values())

        self.ui.pushButtonExecute.clicked.connect(self.execute_process)
        self.ui.pushButtonClose.clicked.connect(self._close)

    def _close(self):
        self.close()

    def _create_checkBox_from_repositories(self):
        index = 1
        for repo in self._repositories:
            check_box = QtWidgets.QCheckBox(self.ui.formLayoutWidget)
            check_box.setObjectName(f"checkBox_{index}")
            check_box.setText(repo.repo_initial)
            self.ui.formLayoutRepos.setWidget(index, \
                            QtWidgets.QFormLayout.LabelRole, check_box)
            index += 1

    def execute_process(self):
        self._process.build_branch = self.ui.lineEditBranch.text()
        self._process.is_clean_m2 = self.ui.checkBoxDeleteM2.isChecked()
        self._process.is_to_reset = self.ui.checkBoxGitReset.isChecked()

        handler = HandlerProcess(self._process)
        handler.start_process(self._repositories)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("The build has finished successfully!!")
        msg.setWindowTitle("Success!!!")
        msg.exec()
