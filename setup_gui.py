from PyQt5 import QtWidgets
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
        self.handlerProcess = HandlerProcess()

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
        altura = eval(self.ui.altura_le.text())
        peso = eval(self.ui.peso_le.text())
        imc = peso / (altura * altura)
        self.ui.imc_lb.setText(f'self.ui.imc_lb.text(): {str(imc)}')
