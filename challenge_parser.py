# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:20:22 2019

@author: nxf52810
"""

from PyQt5.QtWidgets import QDialog, QListWidget, QGridLayout, QTextEdit
from PyQt5.QtWidgets import QPushButton,QLineEdit


class challengeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.post_entry = QTextEdit()
        accept = QPushButton('Ok')
        accept.clicked.connect(self.accept_event)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancel_event)

        self.name_line = QLineEdit()
        self.entry_line = QLineEdit()

        layout = QGridLayout()

        self.setLayout(layout)

    pass


def challenge_code_decompiler():
    pass
