#!/usr/bin/env python3
# encoding=utf-8

""" Main module of the inverse transparency tool """

import sys
# pylint: disable-msg=no-name-in-module
from PyQt5.QtWidgets import QMainWindow, QApplication, QStatusBar, QMessageBox, QMenuBar, QMenu, QAction
from PyQt5 import uic

VERSION = 0.1

qtCreatorFile = "gui/main.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MonitorTool(QMainWindow, Ui_MainWindow): # type: ignore
	def __init__(self):
		super(MonitorTool, self).__init__()
		self.setupUi(self)

		# TODO auto sign-in?
		self.screens.setCurrentIndex(0)

		# Add an "About" menu bar
		menu:QMenu = self.menubar.addMenu("About")
		action:QAction = menu.addAction("Monitor tool v {}".format(VERSION))
		action.setDisabled(True)

		self.sign_in_button.clicked.connect(self.sign_in)
		self.statusbar.showMessage("Ready")


	def sign_in(self):
		# TODO actual sign in!
		user_id = self.id_edit.text()
		user_pwd = self.pwd_edit.text()
		if user_pwd != "admin":
			QMessageBox.warning(None, "Sign in failed", "Could not sign in!\nPlease check your details.")
			return

		self.i_just("Successfully signed in as " + user_id)
		self.load_monitor_screen(user_id=user_id)


	def load_monitor_screen(self, user_id:str):
		""" Switch to the monitor screen and populate its fields. """

		self.screens.setCurrentIndex(1)
		self.signed_in_as_label.setText(user_id)
		self.activity_table.setColumnCount(5)


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
