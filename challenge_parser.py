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
            cancel.clicked.connect(self.reject)
            layout.addWidget(cancel, 1, 1, Qt.AlignCenter)

        self.setLayout(layout)
        self.setWindowTitle(title)
        self.setFixedSize(900, 650)
        self.setWindowModality(True)

    @classmethod
    def importer(cls, parent=None):
        return cls(parent=parent, importer=True, title='Import Challenge Code')

    def import_event(self):
        text = self.post.toPlainText().split('\n')
        name = None
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
                    + "Try new code?", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                return
            else:
                self.reject()
                return
        self.output = {}
        self.output['name'] = name
        self.output['entries'] = []
        self.output['numbers'] = []
        while text:
            line = text.pop(0)
            index = line.split('.')[0]
            number = ''
            if index[0:5] == 'Bonus':
                try:
                    number = 'b' + index.split()[1]
                except IndexError:
                    number = 'b'
            else:
                try:
                    int(index)
                    number = index.zfill(2)
                except ValueError:
                    continue
            self.output['numbers'].append(number)
            entry = challengeEntry(number)
            entry.requirement = line.split('__')[1]
            self.output['entries'].append(entry)
        self.accept()


def challenge_code_decompiler():
    pass
