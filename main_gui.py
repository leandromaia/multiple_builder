# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/source_ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(351, 412)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(50, 10, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 40, 311, 161))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayoutRepos = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayoutRepos.setContentsMargins(0, 0, 0, 0)
        self.formLayoutRepos.setObjectName("formLayoutRepos")
        self.groupBoxRepositories = QtWidgets.QGroupBox(self.formLayoutWidget)
        self.groupBoxRepositories.setObjectName("groupBoxRepositories")
        self.formLayoutRepos.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.groupBoxRepositories)
        self.pushButtonExecute = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonExecute.setGeometry(QtCore.QRect(250, 370, 75, 23))
        self.pushButtonExecute.setObjectName("pushButtonExecute")
        self.pushButtonClose = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonClose.setGeometry(QtCore.QRect(20, 370, 75, 23))
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(20, 210, 311, 141))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayoutOptions = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayoutOptions.setContentsMargins(0, 0, 0, 0)
        self.formLayoutOptions.setObjectName("formLayoutOptions")
        self.labelBranch = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.labelBranch.setObjectName("labelBranch")
        self.formLayoutOptions.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labelBranch)
        self.lineEditBranch = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.lineEditBranch.setObjectName("lineEditBranch")
        self.formLayoutOptions.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEditBranch)
        self.labelBuild = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.labelBuild.setObjectName("labelBuild")
        self.formLayoutOptions.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelBuild)
        self.comboBoxBuild = QtWidgets.QComboBox(self.formLayoutWidget_2)
        self.comboBoxBuild.setObjectName("comboBoxBuild")
        self.formLayoutOptions.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBoxBuild)
        self.checkBoxDeleteM2 = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.checkBoxDeleteM2.setChecked(True)
        self.checkBoxDeleteM2.setObjectName("checkBoxDeleteM2")
        self.formLayoutOptions.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.checkBoxDeleteM2)
        self.checkBoxGitReset = QtWidgets.QCheckBox(self.formLayoutWidget_2)
        self.checkBoxGitReset.setObjectName("checkBoxGitReset")
        self.formLayoutOptions.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.checkBoxGitReset)
        self.groupBoxOptions = QtWidgets.QGroupBox(self.formLayoutWidget_2)
        self.groupBoxOptions.setObjectName("groupBoxOptions")
        self.formLayoutOptions.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.groupBoxOptions)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Update Multiple Environments"))
        self.label_title.setText(_translate("MainWindow", "Update Multiple Environments"))
        self.groupBoxRepositories.setTitle(_translate("MainWindow", "Repositories:"))
        self.pushButtonExecute.setText(_translate("MainWindow", "Execute"))
        self.pushButtonClose.setText(_translate("MainWindow", "Close"))
        self.labelBranch.setText(_translate("MainWindow", "Branch:"))
        self.lineEditBranch.setText(_translate("MainWindow", "master"))
        self.labelBuild.setText(_translate("MainWindow", "Build:"))
        self.checkBoxDeleteM2.setText(_translate("MainWindow", "Delete m2 foder"))
        self.checkBoxGitReset.setText(_translate("MainWindow", "Reset branch"))
        self.groupBoxOptions.setTitle(_translate("MainWindow", "Build Options"))
