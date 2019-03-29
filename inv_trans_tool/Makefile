.PHONY: gui

gui:
	pipenv run pyside2-uic gui/main.ui > gui/main_ui.py
	@echo "Done"

test:
	pipenv run pytest
