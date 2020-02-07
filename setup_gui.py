from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from main_window import Ui_MainWindow
from util import Const, HandlerProcess, Process


class SetupApp(QtWidgets.QMainWindow):

    def __init__(self, repositories):
        super(SetupApp, self).__init__()
        self.repositories = repositories
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._create_checkBox_from_repositories(self.repositories)
        self.ui.comboBoxBuild.addItems(Const.BUILD_CMDS.values())

        self.ui.pushButtonExecute.clicked.connect(self.execute_process)

    def _create_checkBox_from_repositories(self, repositories):
        index = 1
        for repo in repositories:
            check_box = QtWidgets.QCheckBox(self.ui.formLayoutWidget)
            check_box.setObjectName(f"checkBox_{index}")
            check_box.setText(repo.repo_initial)
            self.ui.formLayoutRepos.setWidget(index, \
                            QtWidgets.QFormLayout.LabelRole, check_box)
            index += 1

    def execute_process(self):
        process = Process()
        process.build_branch = self.ui.lineEditBranch.text()
        process.is_clean_m2 = self.ui.checkBoxDeleteM2.isChecked()
        process.is_to_reset = self.ui.checkBoxGitReset.isChecked()

        handler = HandlerProcess(process)
        handler.start_process(self.repositories)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("The build has finished successfully!!")
        msg.setWindowTitle("Success!!!")
        msg.exec()
