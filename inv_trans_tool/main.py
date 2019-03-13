#!/usr/bin/env python3
# encoding=utf-8

""" Main module of the inverse transparency tool """

import sys
# pylint: disable-msg=no-name-in-module
from PySide2.QtWidgets import QMainWindow, QApplication, QStatusBar, QMessageBox, QMenuBar, QMenu, QAction, QTableWidget, QWidget
from PySide2.QtCore import QFile, QAbstractTableModel
from PySide2.QtUiTools import QUiLoader

from gui.main_ui import Ui_MainWindow


VERSION = 0.1


class MonitorTool(QMainWindow): # type: ignore
	def __init__(self, ui):
		super(MonitorTool, self).__init__()

		self.ui:Ui_MainWindow = ui
		self.ui.setupUi(self)

		# TODO auto sign-in?
		self.ui.screens.setCurrentIndex(0)

		# Add an "About" menu bar
		menu:QMenu = self.ui.menubar.addMenu("About")
		action:QAction = menu.addAction("Monitor tool v {}".format(VERSION))
		action.setDisabled(True)

		self.ui.sign_in_button.clicked.connect(self.sign_in)
		self.ui.statusbar.showMessage("Ready")


	def sign_in(self):
		# TODO actual sign in!
		user_id = self.ui.id_edit.text()
		user_pwd = self.ui.pwd_edit.text()
		if user_pwd != "admin":
			QMessageBox.warning(None, "Sign in failed", "Could not sign in!\nPlease check your details.")
			return

		self.i_just("Successfully signed in as " + user_id)
		self.load_monitor_screen(user_id=user_id)


	def load_monitor_screen(self, user_id:str):
		""" Switch to the monitor screen and populate its fields. """

		self.ui.screens.setCurrentIndex(1)
		self.ui.signed_in_as_label.setText(user_id)
		self.ui.activity_table.setColumnCount(5)

		x:QTableWidget
		x.item


	def i_just(self, did:str) -> None:
		self.ui.statusbar.showMessage(did, msecs=3000)


if __name__ == "__main__":
	try:
		app = QApplication(sys.argv)
		main_window = MonitorTool(ui=Ui_MainWindow())
		main_window.show()

		exit_code = app.exec_()
		sys.exit(exit_code)
	except KeyboardInterrupt:
		sys.exit(130)
