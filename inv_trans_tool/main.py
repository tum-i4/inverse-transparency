#!/usr/bin/env python3
# encoding=utf-8

""" Main module of the inverse transparency tool """

import sys
# pylint: disable-msg=no-name-in-module
from PyQt5.QtWidgets import QMainWindow, QApplication, QStatusBar, QMessageBox
from PyQt5 import uic

qtCreatorFile = "gui/main.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MonitorTool(QMainWindow, Ui_MainWindow): # type: ignore
	def __init__(self):
		super(MonitorTool, self).__init__()
		self.setupUi(self)

		# TODO auto sign-in?
		self.screens.setCurrentIndex(0)
		self.sign_in_button.clicked.connect(self.sign_in)
		self.statusbar.showMessage("Ready")


	def sign_in(self):
		# TODO actual sign in!
		user_id = self.id_edit.text()
		user_pwd = self.pwd_edit.text()
		if user_pwd != "admin":
			QMessageBox.warning(None, "Sign in failed", "Could not sign in!\nPlease check your details.")
			return

		self.screens.setCurrentIndex(1)
		self.signed_in_as_label.setText(user_id)
		self.i_just("Successfully signed in as " + user_id)


	def i_just(self, did:str) -> None:
		self.statusbar.showMessage(did, msecs=3000)


if __name__ == "__main__":
	try:
		app = QApplication(sys.argv)
		window = MonitorTool()
		window.show()
		exit_code = app.exec_()
		sys.exit(exit_code)
	except KeyboardInterrupt:
		sys.exit(130)
