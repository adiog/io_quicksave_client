# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

import getpass

from PyQt5.QtWidgets import QApplication, QInputDialog


class MutableWrapper(object):
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


def qt_input_accepted(dialog, output):
    value = dialog.textValue()
    if value:
        output.set(value)


def qt_input_rejected(dialog, output):
    pass


def qt_input(prompt, default_value, is_password):
    result = MutableWrapper(default_value)
    app = QApplication([])
    dialog = QInputDialog(flags=None)
    dialog.setLabelText(prompt)
    if is_password:
        dialog.setTextEchoMode(2)
    dialog.accepted.connect(lambda: qt_input_accepted(dialog, result))
    dialog.rejected.connect(lambda: qt_input_rejected(dialog, result))
    dialog.show()
    app.exec()
    return result.get()


def credentials_prompt_gui():
    user = getpass.getuser()
    username = qt_input(f'Username [{user}]: ', user, is_password=False)
    password = qt_input('Password: ', '', is_password=True)
    return username, password
