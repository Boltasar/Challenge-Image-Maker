# -*- coding: utf-8 -*-
"""
Started on Wed May 20 09:12:31 2019

Small program that helps generate the images used in several AWC submission posts

@author: Bram Hermsen
"""

import os
import json
# Import PyQt for the GUI
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QAction, QComboBox, QFileDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QMessageBox
from PyQt5.QtWidgets import QRadioButton, QApplication, QCheckBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox
import qdarkstyle
# Import PIL for the image editing
from PIL.ImageQt import ImageQt
from challenge_data import challengeEntry
from challenge_parser import challengeDialog

PATH = os.getcwd()
RESOURCES_IMAGE_PATH = PATH + '\\resources\\images\\'
PREVIOUS_SESSION = PATH + '\\PREVIOUS-SESSION.aclo'


STATUS_DICTIONARY = {
    'Complete': [True, False, 'Green'], 'Watching': [True, False, 'Blue'],
    'Decided': [True, False, 'Red'], 'Undecided': [True, True, 'White'],
    'Previously_Watched': [True, False, 'Orange'],
    'Rewatch': [False, False, None]
    }
IMAGELAYERS = [
    'base', 'glow', 'border', 'image', 'icons', 'number', 'tier',
    'requirement', 'title', 'dates', 'duration'
    ]


class window(QMainWindow):
    # The class that contains all the gui code
    def __init__(self):
        # Initiates a few instance variables before building the rest
        super().__init__()
        self.challengePath = PATH
        self.fileName = None
        self.exportPath = PATH
        self.entryNumbers = []

        self.main_window()
        self.home()

        self.connect_signals()

        self.load_challenge(PREVIOUS_SESSION)

        self.show()
        self.activateWindow()
        # End of home body functions

    def main_window(self):
        # Builds the main window and menubar
        self.setFixedSize(900, 650)
        self.setWindowTitle('Anime Watching Challenge Image Maker')
        self.setWindowIcon(QIcon(RESOURCES_IMAGE_PATH + 'awc.ico'))
        center_screen(self)

        # Create the main statusbar
        self.statusBar()
        self.statusBar().setSizeGripEnabled(False)

        # Create the main menubar
        mainMenu = self.menuBar()

        def add_action(parent, name, shortcut, tip, function):
            action = QAction(name, parent)
            action.setShortcut(shortcut)
            action.setStatusTip(tip)
            action.triggered.connect(function)
            parent.addAction(action)

        # Primary filemenu with basic actions like closing, opening and saving.
        fileMenu = mainMenu.addMenu('&File')

        add_action(fileMenu, '&New', 'Ctrl+N',
                   'New challenge', self.new_challenge)
        add_action(fileMenu, '&Open', 'Ctrl+O',
                   'Open challenge', self.load_challenge)
        add_action(fileMenu, '&Save', 'Ctrl+S',
                   'Save challenge', self.save_challenge)
        fileMenu.addSeparator()
        add_action(fileMenu, '&Quit', 'Ctrl+Q',
                   'Close the application', self.closeEvent)

        porterMenu = mainMenu.addMenu('Im/Ex&port')

        add_action(porterMenu, '&Import challenge', 'Ctrl+I',
                   'Import challenge from challenge code',
                   lambda: challengeDialog.importer())
        # End of main body functions
##############################################################################

    def home(self):
        # Builds the left, challenge part of the program
        self.challengeName = QLineEdit(self)
        self.challengeName.setPlaceholderText(
            "Input the challenge's name here.")
        self.challengeName.setMaximumSize(170, 22)

        self.addEntry = QPushButton('Add entry', self)
        self.addEntry.setFixedSize(82, 24)

        self.challengeEntries = QListWidget(self)
        self.challengeEntries.setSortingEnabled(True)
        self.challengeEntries.setMaximumWidth(250)
        self.challengeEntries.setSelectionMode(QAbstractItemView.SingleSelection)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Input your username here")

        self.rightSide = {}
        self.populate_right_side(self.rightSide)

        # Create the main dictionary
        mainGrid = {}
        # Create the the main grid layout
        mainGrid['layout'] = QGridLayout()
        mainGrid['layout'].addWidget(self.username, 0, 0, 1, 2)
        mainGrid['layout'].addWidget(self.challengeName, 1, 0)
        mainGrid['layout'].addWidget(self.addEntry, 1, 1)
        mainGrid['layout'].addWidget(self.challengeEntries, 2, 0, 1, 2)
        mainGrid['layout'].addWidget(self.rightSide['container'], 0, 2, 3, 1)

        build_layout(mainGrid, 'widget', 'layout', 0, 2)

        self.setCentralWidget(mainGrid['widget'])
##############################################################################

    def populate_right_side(self, rightSide):
        # Add a text input field for the user to define the anime id
        self.animeIDInput = {}
        self.animeIDInput['widget'] = QLineEdit()
        self.animeIDInput['widget'].setPlaceholderText("Type the link to the anime page or its ID")
        self.animeIDInput['label'] = QLabel('AnimeID')
        self.animeIDInput['layout'] = QVBoxLayout()
        self.animeIDInput['layout'].addWidget(self.animeIDInput['label'])
        self.animeIDInput['layout'].addWidget(self.animeIDInput['widget'])
        build_layout(self.animeIDInput, 'container', 'layout')

        # Building the groupbox
        self.status = buttonGroup('Status')
        self.status.add_button_batch(STATUS_DICTIONARY)

        # Building the tier dropbox
        self.tierChoice = {}
        self.tierChoice['widget'] = QComboBox()
        for tier in [['', ''], ['Easy', 'green'],
                     ['Normal', 'blue'], ['Hard', 'red']]:
            self.tierChoice['widget'].addItem(tier[0], tier[1])
        self.tierChoice['label'] = QLabel('Tier')
        self.tierChoice['layout'] = QVBoxLayout()
        self.tierChoice['layout'].addWidget(self.tierChoice['label'])
        self.tierChoice['layout'].addWidget(self.tierChoice['widget'])
        self.tierChoice['layout'].insertStretch(-1, 255)

        # Build challenge number entry line
        self.entryNumber = {}
        self.entryNumber['widget'] = QLineEdit()
        self.entryNumber['widget'].setValidator(QIntValidator(1, 99))
        self.entryNumber['widget'].setPlaceholderText('#')
        self.entryNumber['widget'].setMaximumWidth(25)
        self.entryNumber['label'] = QLabel('Number:')
        self.entryNumber['layout'] = QHBoxLayout()
        self.entryNumber['layout'].addWidget(self.entryNumber['label'], -1, Qt.AlignRight)
        self.entryNumber['layout'].addWidget(self.entryNumber['widget'])

        statusTier = {}
        statusTier['layout'] = QGridLayout()
        statusTier['layout'].addWidget(self.status.box['container'], 0, 0, 2, 1)
        statusTier['layout'].addLayout(self.tierChoice['layout'], 0, 1)
        statusTier['layout'].addLayout(self.entryNumber['layout'], 1, 1)
        build_layout(statusTier, 'container', 'layout', 2)

        # Build the minimum time entry box
        self.minimumTime = {}
        self.minimumTime['widget'] = QLineEdit()
        self.minimumTime['widget'].setValidator(QIntValidator(0, 9999))
        self.minimumTime['label'] = QLabel('Minimum time:')

        # Build requirement text entry box
        self.entryRequirement = {}
        self.entryRequirement['widget'] = QTextEdit()
        self.entryRequirement['widget'].setAcceptRichText(False)
        self.entryRequirement['widget'].setPlaceholderText("Type the entry requirements")
        self.entryRequirement['timer'] = QTimer()
        self.entryRequirement['timer'].setSingleShot(True)
        self.entryRequirement['label'] = QLabel('Entry Data')
        self.entryRequirement['layout'] = QGridLayout()
        self.entryRequirement['layout'].addWidget(self.entryRequirement['label'], 0, 0)
        self.entryRequirement['layout'].addWidget(QWidget(), 0, 1)
        self.entryRequirement['layout'].setColumnStretch(1, 255)
        self.entryRequirement['layout'].addWidget(self.minimumTime['label'], 0, 2)
        self.entryRequirement['layout'].addWidget(self.minimumTime['widget'], 0, 3)
        self.entryRequirement['layout'].addWidget(self.entryRequirement['widget'], 1, 0, 1, 4)

        build_layout(self.entryRequirement, 'container', 'layout', [5, 2], 0)

        # Build the buttons
        self.buttons = {}
        # The button to import the data from anilist
        self.buttons['import'] = QPushButton('Import AniData')
        # The button to export the image
        self.buttons['export'] = QPushButton('Export PNG')
        # The button to force a save as dialog
        self.buttons['exportall'] = QPushButton('Export PNG All')

        # Placeholder image to give a feel for the eventual frame
        self.imageViewer = {'grid': QGridLayout()}
        for item in IMAGELAYERS:
            self.imageViewer[item] = QLabel()
            self.imageViewer[item].setFixedSize(310, 540)
            self.imageViewer['grid'].addWidget(self.imageViewer[item], 0, 0, Qt.AlignCenter)
        build_layout(self.imageViewer, 'viewer', 'grid', 0, 0)
        self.imageViewer['viewer'].setStyleSheet(
            """
            QWidget {
            background: transparent;
            border: 0px solid #32414B;
            }
            """)
        self.imageViewer['line'] = QVBoxLayout()
        self.imageViewer['line'].addWidget(self.imageViewer['viewer'])
        build_layout(self.imageViewer, 'box', 'line', 0, 5)
        self.imageViewer['box'].setStyleSheet(
            """
            QWidget {
            background-color: #FFFFFF;
            border: 5px solid #32414B;
            padding: 0px;
            }
            """)
        self.imageViewer['box'].setFixedSize(320, 550)
        self.imageViewer['layout'] = QGridLayout()
        self.imageViewer['layout'].addWidget(self.imageViewer['box'], 1, 1, Qt.AlignCenter)
        build_layout(self.imageViewer, 'container', 'layout')

        # Build a container widget for the right side of the program
        rightSide['layout'] = QGridLayout()
        rightSide['layout'].addWidget(self.animeIDInput['container'], 0, 0)
        rightSide['layout'].addWidget(self.buttons['import'], 0, 1, Qt.AlignBottom)
        rightSide['layout'].addWidget(self.buttons['export'], 0, 2, Qt.AlignBottom)
        rightSide['layout'].addWidget(self.buttons['exportall'], 0, 3, Qt.AlignBottom)
        rightSide['layout'].addWidget(statusTier['container'], 1, 0, 1, 1)
        rightSide['layout'].addWidget(self.entryRequirement['container'], 2, 0, 1, 1)
        rightSide['layout'].setRowStretch(2, 255)
        rightSide['layout'].addWidget(self.imageViewer['container'], 1, 1, 3, 3)

        build_layout(rightSide, 'container', 'layout', 5, [2, 0, 0, 0])
        rightSide['container'].setEnabled(False)

    # Connecting Signals with Events
##############################################################################
    def connect_signals(self):
        # Connects the signals.
        self.addEntry.clicked.connect(self.new_challenge_entry)
        self.challengeEntries.currentItemChanged.connect(self.load_entry)
        self.challengeEntries.keyPressEvent = self.challengeEntries_key_events
        self.challengeName.editingFinished.connect(self.challenge_name_update)

        self.animeIDInput['widget'].editingFinished.connect(self.anime_id_update)

        self.entryRequirement['widget'].textChanged.connect(self.entry_requirement_update)
        self.entryRequirement['timer'].timeout.connect(self.entry_requirement_image_update)

        self.entryNumber['widget'].editingFinished.connect(self.number_update)

        self.tierChoice['widget'].currentIndexChanged.connect(self.tier_update)

        self.minimumTime['widget'].editingFinished.connect(self.minimum_time_update)

        for key, item in self.status.buttons.items():
            item.toggled.connect(lambda state, name=key, button=item:
                                 self.change_status(name, state, button))

        self.buttons['import'].clicked.connect(self.import_aniData)
        self.buttons['export'].clicked.connect(self.export_image)
        self.buttons['exportall'].clicked.connect(self.export_all_images)

# Events
##############################################################################
    def export_image(self):
        # Asks for a save location and name and saves the current entry image.
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        fileName = QFileDialog().getSaveFileName(
            self, 'Save image', self.exportPath, 'PNG(*.png)')[0]
        if not fileName:
            return
        self.exportPath = fileName.rstrip(fileName.split('\\')[-1])
        image = data.image.build_full_image()
        image.save(fileName, 'png')

    def export_all_images(self):
        # Asks for a save directory and exports all entries images.
        fileName = QFileDialog().getExistingDirectory(
            self, 'Save all images', self.exportPath)
        if not fileName:
            return
        self.exportPath = fileName
        for k in range(0, self.challengeEntries.count()):
            data = self.challengeEntries.item(k).data(Qt.UserRole)
            name = self.challengeEntries.item(k).text()
            image = data.image.build_full_image()
            image.save(fileName + '\\' + name + '.png', 'png')

    def new_challenge_entry(self):
        # Builds a new entry and gives it the first missing positive integer.
        try:
            number = next(a for a, b in enumerate(self.entryNumbers, 1) if a != int(b))
        except StopIteration:
            number = len(self.entryNumbers) + 1
        self.entryNumbers.insert(number-1, str(number).zfill(2))
        name = self.challengeName.text() + ' ' + str(number).zfill(2)
        item = QListWidgetItem(name)
        data = challengeEntry(number=number, status_options=STATUS_DICTIONARY)
        data.image.write_entry_number(str(number))
        item.setData(Qt.UserRole, data)
        self.challengeEntries.addItem(item)
        self.challengeEntries.setCurrentRow(number-1)

    def load_entry(self, currentItem):
        # Loads in the visual information of the selected entry.
        if not currentItem:
            return
        self.rightSide['container'].setEnabled(True)
        data = currentItem.data(Qt.UserRole)
        if getattr(data, 'animeID', None) is None:
            self.animeIDInput['widget'].setText('')
        else:
            self.animeIDInput['widget'].setText(str(data.animeID))
        for key, item in data.status.items():
            if self.status.buttons[key].autoExclusive():
                self.status.buttons[key].setAutoExclusive(False)
                self.status.buttons[key].setChecked(False)
                self.status.buttons[key].setAutoExclusive(True)
            self.status.buttons[key].setChecked(item)
        self.entryNumber['widget'].setText(str(data.number))
        self.tierChoice['widget'].setCurrentIndex(data.tierIndex)
        self.entryRequirement['widget'].setPlainText(data.requirement)
        self.minimumTime['widget'].setText(str(data.minimumTime))
        for item in IMAGELAYERS:
            self.change_image(data, item)

    def new_challenge(self):
        # Clears the current challenge.
        if self.challengeEntries.count():
            choice = QMessageBox.question(
                self, 'Make new challenge',
                'Would you first like to save your current challenge?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.save_challenge()
            elif choice == QMessageBox.Cancel:
                return
        self.challengeEntries.clear()
        self.entryNumbers = []
        self.challengeName.setText('')
        self.rightSide['container'].setEnabled(False)

    def load_challenge(self, fileName=None):
        """
        Loads the challenge data from a json file.

        :fileName: pathname to the challenge that was previously open.
        :returns: None
        """
        if not fileName:
            fileName = QFileDialog().getOpenFileName(
                self, 'Load challenge list',
                self.challengePath, 'Anime Challenge List Object(*.aclo)')[0]
        if not fileName:
            return
        self.challengePath = fileName.rstrip(fileName.split('\\')[-1])
        # Open the file or show error in case of failure
        try:
            with open(fileName, 'rb') as f:
                savedata = json.load(f)
        except FileNotFoundError:
            if fileName == PREVIOUS_SESSION:
                return
            else:
                QMessageBox.warning(self, 'Warning', "Couldn't find file!")
                return

        self.statusBar().showMessage('Loading Anime Challenge List Object')
        self.challengeName.setText(savedata['name'])
        self.username.setText(savedata['username'])
        self.entryNumbers = savedata['entryNumbers']
        self.exportPath = savedata['exportPath']
        self.challengeEntries.clear()
        k = 0
        for name, entryRequirement in savedata['entries'].items():
            item = QListWidgetItem(name)
            data = challengeEntry()
            data.load_savedata(entryRequirement, self)
            item.setData(Qt.UserRole, data)
            self.challengeEntries.addItem(item)
            self.challengeEntries.setCurrentRow(k)
            self.challengeEntries.setFocus(True)
            k += 1
        self.statusBar().clearMessage()

    def save_challenge(self, fileName=None):
        # Saves the challenge data to a json file.
        if not fileName:
            fileName = QFileDialog().getSaveFileName(
                self, 'Save challenge', self.challengePath,
                'Anime Challenge List Object(*.aclo)')[0]
        if not fileName:
            return False
        self.challengePath = fileName.rstrip(fileName.split('\\')[-1])
        entries = {}
        for k in range(0, self.challengeEntries.count()):
            name = self.challengeEntries.item(k).text()
            data = self.challengeEntries.item(k).data(Qt.UserRole)
            challengeData = {}
            for attr in data.savedAttributesList:
                challengeData[attr] = getattr(data, attr, None)
            entries[name] = challengeData
        savedata = {
                'name': self.challengeName.text(),
                'username': self.username.text(),
                'entryNumbers': self.entryNumbers,
                'exportPath': self.exportPath,
                'entries': entries
                }
        with open(fileName, 'w') as f:
            json.dump(savedata, f, indent=4)
        return True

    def challenge_name_update(self):
        # Updates all entry names to the new challenge name.
        name = self.challengeName.text()
        self.challengeEntries.setSortingEnabled(False)
        for k in range(0, self.challengeEntries.count()):
            number = self.entryNumbers[k]
            text = name + ' ' + str(number).zfill(2)
            self.challengeEntries.item(k).setText(text)
        self.challengeEntries.setSortingEnabled(True)

    def anime_id_update(self):
        # Checks if the input is valid. Updates the data if it is.
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        text = self.animeIDInput['widget'].text()
        try:
            data.animeID = int(text)
        except ValueError:
            if data.get_id_from_link(text):
                self.animeIDInput['widget'].setText(str(data.animeID))
            else:
                self.animeIDInput['widget'].setText('')
                self.statusBar().showMessage('Invalid input', 1000)
        self.import_aniData()

    def import_aniData(self):
        # Imports the data from the internet.
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        data.get_info_from_id(self.username.text())
        for item in ['image', 'title', 'dates', 'duration']:
            self.change_image(data, item)

    def change_image(self, data, key):
        # Updates the requested image layer.
        self.imageViewer[key].image = getattr(data.image, key, data.image.empty)
        self.imageViewer[key].Qt = ImageQt(self.imageViewer[key].image)
        self.imageViewer[key].pixmap = QPixmap.fromImage(self.imageViewer[key].Qt)
        self.imageViewer[key].setPixmap(self.imageViewer[key].pixmap)

    def change_status(self, name, state, button):
        # Builds the icon and border glow according to selected check/radiobox
        entry = self.challengeEntries.currentItem()
        data = entry.data(Qt.UserRole)
        data.status[name] = state
        if isinstance(button, QRadioButton):
            if state:
                position = (35, 35)
                data.image.add_icon(name, position)
                self.change_image(data, 'icons')
        else:
            if not state:
                name = 'empty'
            position = (245, 35)
            data.image.add_icon(name, position)
            self.change_image(data, 'icons')
        if button.glowColor:
            if state:
                data.image.build_glow(button.glowColor, 8)
                self.change_image(data, 'glow')

    def number_update(self):
        """
        Updates the challenge number.

        Updates the number in all three tracking instances:
        self.entryNumbers: The list used for finding first missing positive integer.
        entry.text(): The name of the challenge entry.
        data.number: The data that's used for the image.
        """
        number = self.entryNumber['widget'].text().zfill(2)
        row = self.challengeEntries.currentRow()
        old = self.entryNumbers[row]
        self.entryNumbers[row] = number
        self.entryNumbers.sort()
        currentItem = self.challengeEntries.currentItem()
        text = currentItem.text()
        text = text.split()
        numberpos = max(i for i, e in enumerate(text) if e == old)
        text[numberpos] = number
        text = ' '.join(text)
        currentItem.setText(text)
        data = currentItem.data(Qt.UserRole)
        data.number = int(number)
        data.image.write_entry_number(number.lstrip('0'), 15)
        self.change_image(data, 'number')

    def tier_update(self, index):
        # Updates the tier text and image
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        data.tierIndex = index
        tier = self.tierChoice['widget'].currentText()
        color = self.tierChoice['widget'].currentData()
        data.image.write_entry_tier(tier, color=color)
        self.change_image(data, 'tier')

    def entry_requirement_update(self):
        # Updates the requirement text
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        data.requirement = self.entryRequirement['widget'].toPlainText()
        # Timer to put a delay on firing the resize code since it gets resource intensive otherwise.
        self.entryRequirement['timer'].start(250)

    def entry_requirement_image_update(self):
        # Updates the requirement image
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        data.image.write_entry_requirement(data.requirement, 15)
        self.change_image(data, 'requirement')

    def minimum_time_update(self):
        # Updates the minimum time and image.
        data = self.challengeEntries.currentItem().data(Qt.UserRole)
        if self.minimumTime['widget'].text():
            data.minimumTime = int(self.minimumTime['widget'].text())
        data.image.write_duration_text(data.minimumTime, data.episodeCount,
                                       data.episodeDuration, 15)
        self.change_image(data, 'duration')

    def challengeEntries_key_events(self, event):
        # Catches the delete key for challenge entry removal
        if event.key() == Qt.Key_Delete:
            if self.challengeEntries.count():
                self.rightSide['container'].setEnabled(False)
                row = self.challengeEntries.currentRow()
                self.challengeEntries.takeItem(row)
                self.entryNumbers.pop(row)
                row = max([0, row - 1])
                self.challengeEntries.setCurrentRow(row)

    # Exit Application
    def closeEvent(self, event):
        try:
            self.save_challenge(PREVIOUS_SESSION)
            event.accept()
        except AttributeError:
            pass

    # Screen positioning methods
##############################################################################


# Custom Widget Classes
##############################################################################
class buttonGroup():
    # Class to universalize the statusgroup widget
    def __init__(
            self, boxName, buttonSpacing=[2, 2], buttonMargins=2,
            boxSpacing=2, boxMargins=0):
        self.buttons = {}
        self.labels = {}
        self.box = {}
        self.box['box'] = QGroupBox()
        self.box['box'].setStyleSheet("""
            QGroupBox {
            font-weight: bold;
            border: 1px solid #32414B;
            border-radius: 4px;
            padding: 2px;
            margin-top: 0px;
            }""")
        self.box['grid'] = QGridLayout()
        build_layout(self.box, 'box', 'grid', buttonSpacing, buttonMargins)
        self.box['label'] = QLabel(boxName)
        self.box['layout'] = QVBoxLayout()
        self.box['layout'].addWidget(self.box['label'])
        self.box['layout'].addWidget(self.box['box'])
        build_layout(self.box, 'container', 'layout', boxSpacing, boxMargins)

    def add_button(self, name, exclusive=False, checked=False, color=None):
        # Adds a button to the button group
        column = len(self.buttons)
        if exclusive:
            self.buttons[name] = QRadioButton()
        else:
            self.buttons[name] = QCheckBox()
        self.buttons[name].glowColor = color
        self.labels[name] = QLabel(name[0:3])
        self.box['grid'].addWidget(
            self.buttons[name], 0, column, Qt.AlignCenter)
        self.box['grid'].addWidget(
            self.labels[name], 1, column, Qt.AlignCenter)

    def add_button_batch(self, buttonsDictionary={}):
        # Calls add button for every entry in the input dictionary
        for key, typelist in buttonsDictionary.items():
            self.add_button(key, typelist[0], typelist[1], typelist[2])


# Data storage classes
##############################################################################


# Global functions
##############################################################################
def center_screen(window):
    # Centers the window on the screen the mouse is on
    frameGm = window.frameGeometry()
    screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
    centerPoint = QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    window.move(frameGm.topLeft())


def build_layout(target, containerKey, layoutKey, spacings=0, margins=0):
    # Builds a widget around a layout
    if containerKey not in target:
        target[containerKey] = QWidget()
    target[containerKey].setLayout(target[layoutKey])
    if isinstance(spacings, list):
        target[layoutKey].setHorizontalSpacing(spacings[0])
        target[layoutKey].setVerticalSpacing(spacings[1])
    else:
        target[layoutKey].setSpacing(spacings)
    if isinstance(margins, list):
        target[layoutKey].setContentsMargins(margins[0], margins[1],
                                             margins[2], margins[3])
    else:
        target[layoutKey].setContentsMargins(margins, margins, margins, margins)


def run():
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Gui = window()
    app.exec_()
