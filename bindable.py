#!/usr/bin/env python

import sys

i
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QLineEdit, QTextEdit, QCheckBox, QFormLayout, QApplication


def bind(objectName, propertyName, type):
    def getter(self):
        return type(self.findChild(QObject, objectName).property(propertyName).toPyObject())

    def setter(self, value):
        self.findChild(QObject, objectName).setProperty(propertyName, QVariant(value))

    return property(getter, setter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
