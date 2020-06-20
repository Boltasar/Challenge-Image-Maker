# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 13:20:22 2019

@author: nxf52810
"""

from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QTextEdit
from PyQt5.QtWidgets import QPushButton, QMessageBox

class challengeDialog(QDialog):
    def __init__(self, parent=None, mode='', title='Popup', data=None):
        super().__init__(parent=parent)

        self.setWindowTitle(title)
        self.setFixedSize(630, 400)
        self.setWindowModality(True)

        layout = QGridLayout()

        self.post = QTextEdit()
        self.post.setAcceptRichText(False)
        layout.addWidget(self.post, 0, 0, 1, 2)
        layout.setRowStretch(0, 255)

        if mode == 'Importer':
            self.post.setPlaceholderText('Paste the challenge code here.')
            importer = QPushButton('Import')
            importer.clicked.connect(self.import_event)
            layout.addWidget(importer, 1, 0, Qt.AlignCenter)

            cancel = QPushButton('Cancel')
            cancel.clicked.connect(self.reject)
            layout.addWidget(cancel, 1, 1, Qt.AlignCenter)
        elif mode == 'Exporter':
            self.post.setPlainText(self.build_post_from_data(data))

        self.setLayout(layout)

    @classmethod
    def importer(cls, parent=None):
        return cls(parent=parent, mode='Importer', title='Import Challenge Code')

    @classmethod
    def exporter(cls, parent=None, data=None):
        if data is None:
            data = {}
        return cls(parent=parent, mode='Exporter',
                   title='Export Forum Post', data=data)

    def import_event(self):
        text = self.post.toPlainText().split('\n')
        name = None
        while True:
            try:
                line = text.pop(0)
                if line[:1] == '#':
                    name = line.split('__')[1]
                    name = name[:-10]
                    break
                elif line[:7] == '__Genre':
                    name = line.split('__')[1]
                    name = name[17:]
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
            if len(line[:10].split('.')) > 1:
                index = line.split('.')[0]
            elif len(line[:10].split(')')) > 1:
                index = line.split(')')[0]
            else:
                continue
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
                requirement = line.split('__')[1]
            except IndexError:
                requirement = ''
            animeID = line.split('(')[1].split('/')[4]
            entryData = {'animeID': animeID,
                         'requirement': requirement,
                         'number': number.lstrip('0')}
            self.output['entries'].update({entryName: entryData})
        self.accept()

    def build_post_from_data(self, data):
        if data['startDate'].split('/')[2] == datetime.now().strftime("%Y"):
            startdate = data['startDate'][:-5]
            completedate = datetime.now().strftime("%d/%m")
        else:
            startdate = data['startDate']
            completedate = datetime.now().strftime("%d/%m/%Y")
        text = r"""#<center>__{0} Challenge__
<center>
Challenge Start Date: {1}
Challenge Finish Date: {2}

Progress {3}/{4}

✔️ = Completed | ▶️ = Currenty Watching | ❌ = Not Started | ❔ = Undecided
""".format(data['name'], startdate, completedate, data['completed'], data['total'])
        post_formatting = ""
        if data['easyEntries']:
            text += '<hr>\nEasy\n~!'
            post_formatting += '<hr>Easy\n'
            for entry in data['easyEntries']:
                text += image_format(entry, data)
                post_formatting += text_format(entry)
            text += '!~'
        if data['normalEntries']:
            text += '\n<hr>\nNormal\n~!'
            post_formatting += '<hr>Normal\n'
            for entry in data['normalEntries']:
                text += image_format(entry, data)
                post_formatting += text_format(entry)
            text += '!~'
        if data['hardEntries']:
            text += '\n<hr>\nHard\n~!'
            post_formatting += '<hr>Hard\n'
            for entry in data['hardEntries']:
                text += image_format(entry, data)
                post_formatting += text_format(entry)
            text += '!~'
        if data['entries']:
            text += '\n<hr>\n'
            post_formatting += '<hr>\n'
            for entry in data['entries']:
                text += image_format(entry, data)
                post_formatting += text_format(entry)
        text += '\n</center>' + post_formatting
        text += '<hr><center>Special Notes:\n'
        return text
    
def image_format(entry, data):
    image_format = (r"[<img src = 'insertlink{0}{1}'"
    + r" width = 20%>]({2})").format(data['name'].replace(" ",""), entry['number'],
                                  entry['link'])
    return(image_format)
def text_format(entry):
    if not entry["requirement"]:
        entry['requirement'] = " "
    text_format = ('{0}) Start: {1} Finish: {2} __{3}__ [{4}]({5})\n'.format(
        entry['number'].zfill(2), format_date_string(entry['startDate']),
        format_date_string(entry['completeDate']), entry['requirement'],
        entry['title'], entry['link']))
    return(text_format)
        
def format_date_string(datestring):
    dates = datestring.split('/')
    date_return = ''
    try:
        date_return += dates[0].zfill(2)
    except IndexError:
        return('??/??')
    date_return += '/' + dates[1].zfill(2)
    try:
        return(date_return + '/' + dates[2].zfill(4))
    except IndexError:
        return(date_return)