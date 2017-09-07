#!/usr/bin/env python3
# This file is a part of quicksave project.
# Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.


from PyQt5.QtWidgets import QApplication, QInputDialog
import sys, time


def succFunc(qd):
    sys.stdout.write(qd.textValue())
    sys.stdout.flush()
    exit(0)


def failFunc(qd):
    exit(1)


def main():
    app = QApplication(sys.argv)
    qd = QInputDialog()
    # QLineEdit.Password
    qd.setLabelText("Enter password:")
    qd.setTextEchoMode(2)
    qd.rejected.connect(lambda: failFunc(qd))
    qd.accepted.connect(lambda: succFunc(qd))
    qd.show()
    app.exec()


if __name__ == '__main__':
    main()
