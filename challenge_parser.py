# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:20:22 2019

@author: nxf52810
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QTextEdit
from PyQt5.QtWidgets import QPushButton, QMessageBox

from challenge_data import challengeEntry

class challengeDialog(QDialog):
    def __init__(self, parent=None, importer=False, title='Popup'):
        super().__init__(parent=parent)

        layout = QGridLayout()

        self.post = QTextEdit()
        self.post.setAcceptRichText(False)
        layout.addWidget(self.post, 0, 0, 1, 2, Qt.AlignCenter)

        if importer:
            importer = QPushButton('Import')
            importer.clicked.connect(self.import_event)
            layout.addWidget(importer, 1, 0, Qt.AlignCenter)

            cancel = QPushButton('Cancel')
            cancel.clicked.connect(self.close)
            layout.addWidget(cancel, 1, 1, Qt.AlignCenter)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setWindowModality(True)
        self.exec_()

    @classmethod
    def importer(cls, parent=None):
        return cls(parent=parent, importer=True, title='Import Challenge Code')

    def import_event(self):
        text = self.post.text().split('\n')
        while True:
            try:
                line = text.pop(0)
                if line[0] == '#':
                    name = line.split('__')[1]
                    name.rstrip(' Challenge')
                elif line[0:7] == '__Genre':
                    name = line.split('__')[1]
                    name.lstrip('Genre Challenge: ')
            except IndexError:
                break
        if not name:
            choice = QMessageBox.question(
                    self, 'Failed Import',
                    "Couldn't find the name in this challenge code\n"
                    + "Try new code?", QMessageBox.Yes | QMessageBox.Quit)
            if choice == QMessageBox.Yes:
                return
            else:
                self.close()
        challenge_entries = []
        while text:
            line = text.pop(0)
            index = line.split('.')[0]
            number = ''
            if index[0:5] == 'Bonus':
                try:
                    number = 'b' + index.split()[1]
                except IndexError:
                    number = 'b1'
            else:
                try:
                    int(index)
                    number = index
                except ValueError:
                    continue
            entry = challengeEntry(number)

        self.close()


def challenge_code_decompiler():
    pass
