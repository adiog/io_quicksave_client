# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

import getpass

from PyQt5.QtWidgets import QApplication, QInputDialog


def succFunc(qd, output):
    value = qd.textValue()
    if value:
        output[0] = value


def failFunc(qd, output):
    pass


def qt_input(prompt, default_value, is_password):
    result = [default_value]
    app = QApplication([])
    qd = QInputDialog()
    qd.setLabelText(prompt)
    if is_password:
        qd.setTextEchoMode(2)
    qd.rejected.connect(lambda: failFunc(qd, result))
    qd.accepted.connect(lambda: succFunc(qd, result))
    qd.show()
    app.exec()
    return result[0]


def gui_credentials_prompt():
    user = getpass.getuser()
    username = qt_input('Username [%s]: ' % user, user, is_password=False)
    password = qt_input('Password: ', '', is_password=True)
    return username, password
