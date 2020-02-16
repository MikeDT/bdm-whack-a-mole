# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 18:05:19 2020

@author: DZLR3
"""

from PyQt5 import QtWidgets
from QT_GUI import QT_GUI

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    wizard = QT_GUI()
    wizard.setWindowTitle('BDM WAM PyQT Wrapper')
    wizard.show()
    app.exec_()
