#!/usr/bin/env python3
# encoding=utf-8

""" Main module of the inverse transparency tool """

import sys
# pylint: disable-msg=no-name-in-module
from PyQt5.QtWidgets import QMainWindow, QApplication, QStatusBar
from PyQt5 import uic

qtCreatorFile = "gui/main.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MonitorTool(QMainWindow, Ui_MainWindow): # type: ignore
	def __init__(self):
		super(MonitorTool, self).__init__()
		self.setupUi(self)
		self.sign_in_button.clicked.connect(self.sign_in)
		self.statusbar.showMessage("Ready")

	def sign_in(self):
		user_id = self.id_edit.text()
		user_pwd = self.pwd_edit.text()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MonitorTool()
	window.show()

sys.exit(app.exec_())
