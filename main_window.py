# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 513)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(230, 10, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 40, 291, 161))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayoutRepos = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayoutRepos.setContentsMargins(0, 0, 0, 0)
        self.formLayoutRepos.setObjectName("formLayoutRepos")
        self.checkBox_1 = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBox_1.setObjectName("checkBox_1")
        self.formLayoutRepos.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.checkBox_1)
        self.pushButtonExecute = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonExecute.setGeometry(QtCore.QRect(600, 470, 75, 23))
        self.pushButtonExecute.setObjectName("pushButtonExecute")
        self.pushButtonClose = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonClose.setGeometry(QtCore.QRect(500, 470, 75, 23))
        self.pushButtonClose.setObjectName("pushButtonClose")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Update Multiple Environments"))
        self.label_title.setText(_translate("MainWindow", "Update Multiple Environments"))
        self.checkBox_1.setText(_translate("MainWindow", "CheckBox"))
        self.pushButtonExecute.setText(_translate("MainWindow", "Execute"))
        self.pushButtonClose.setText(_translate("MainWindow", "Close"))
