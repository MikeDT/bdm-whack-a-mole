# -*- coding: utf-8 -*-
"""
main
====

Typical main.py functionality, initiates the pyqt wrapper to support
demographic info collection

Attributes:
    na
C:\\Users\\miketaylor\\Documents\\GitHub\\bdm-whack-a-mole\\bdm-whack-a-mole\\config
Todo:
    * na

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: DZLR3
"""

from PyQt5 import QtWidgets
from QT import QT_Config

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    wizard = QT_Config()
    wizard.setWindowTitle('BDM Whack A Mole Configuration Handler')
    wizard.show()
    app.exec_()
