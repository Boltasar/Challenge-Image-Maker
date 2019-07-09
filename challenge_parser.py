# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:20:22 2019

@author: nxf52810
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QTextEdit
from PyQt5.QtWidgets import QPushButton, QMessageBox, QSizePolicy
from challenge_data import challengeEntry


class challengeDialog(QDialog):
    def __init__(self, parent=None, importer=False, title='Popup'):
        super().__init__(parent=parent)

        self.setWindowTitle(title)
        self.setFixedSize(630, 400)
        self.setWindowModality(True)

        layout = QGridLayout()

        self.post = QTextEdit()
        self.post.setAcceptRichText(False)
        layout.addWidget(self.post, 0, 0, 1, 2)
        layout.setRowStretch(0, 255)

        if importer:
            self.post.setPlaceholderText('Paste the challenge code here.')
            importer = QPushButton('Import')
            importer.clicked.connect(self.import_event)
            layout.addWidget(importer, 1, 0, Qt.AlignCenter)

            cancel = QPushButton('Cancel')
            cancel.clicked.connect(self.reject)
            layout.addWidget(cancel, 1, 1, Qt.AlignCenter)

        self.setLayout(layout)

    @classmethod
    def importer(cls, parent=None):
        return cls(parent=parent, importer=True, title='Import Challenge Code')

    def import_event(self):
        text = self.post.toPlainText().split('\n')
        name = None
        while True:
            try:
                line = text.pop(0)
                if line[:1] == '#':
                    name = line.split('__')[1]
                    name = name.rstrip(' Challenge')
                    break
                elif line[:7] == '__Genre':
                    name = line.split('__')[1]
                    name = name.lstrip('Genre Challenge: ')
                    break
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
        self.output['entryNumbers'] = []
        self.output['entries'] = {}
        while text:
            line = text.pop(0)
            index = line.split('.')[0]
            number = ''
            if index[:5] == 'Bonus':
                try:
                    number = 'B' + index.split()[1]
                except IndexError:
                    number = 'B1'
            else:
                try:
                    int(index)
                    number = index.zfill(2)
                except ValueError:
                    continue
            self.output['entryNumbers'].append(number)
            entryName = name + ' ' + number
            try:
                entryData = {'requirement': line.split('__')[1],
                             'number': number.lstrip('0')}
            except IndexError:
                entryData = {'requirement': '',
                             'number': number.lstrip('0')}
            self.output['entries'].update({entryName: entryData})
        self.accept()


def challenge_code_decompiler():
    pass
