# -*- coding: utf-8 -*-
"""
Started on Wed May 20 09:12:31 2019

Small program that helps generate the images used in several AWC submission posts

@author: Bram Hermsen
"""

import os
import sys
import math
import datetime
import pickle
#Import PyQt for the GUI
from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QIcon, QIntValidator, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QAction, QComboBox, QFileDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QErrorMessage
from PyQt5.QtWidgets import QRadioButton, QMessageBox, QApplication, QCheckBox
from PyQt5.QtWidgets import QTextEdit, QStatusBar
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox
import qdarkstyle
#Import PIL for the image editing
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL.ImageQt import ImageQt
#Import requests for internet access
import requests
#Local module for interacting with the anilist API.
import anilistAPI


resourcesImagePath = os.getcwd() + '\\resources\\images\\'
resourcesFontPath = os.getcwd() + '\\resources\\fonts\\'
saveImagePath = os.getcwd() + '\\exports\\'

statusDictionary = {
    'Complete': [True, False, 'Green'], 'Watching': [True, False, 'Blue'], 
    'Decided': [True, False, 'Red'], 'Undecided': [True, True, 'White'],
    'Previously_Watched': [True, False, 'Orange'], 'Rewatch': [False, False, None]
    }
imageLayers = [
    'base', 'glow', 'border', 'image', 'icons', 'number', 'tier','challenge',
    'title', 'dates', 'duration'
    ]

class window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.imageSavePath = saveImagePath
        self.challengeSavePath = saveImagePath
        self.fileName = None
        
        self.main_screen()
        self.home()

    def main_screen(self):
        self.setFixedSize(900, 650)
        self.setWindowTitle('Anime Watching Challenge Image Maker')
        self.setWindowIcon(QIcon(resourcesImagePath + 'awc.ico'))
        self.center_screen()

        #Create a universal statusbar
        self.myStatusBar = myStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.setSizeGripEnabled(False)

        #Create a universal menubar
        mainMenu = self.menuBar()
        #Primary filemenu with basic actions like closing, opening and saving.
        fileMenu = mainMenu.addMenu('&File')
        
        #Action to load a list
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open list')
        openAction.triggered.connect(self.load_list_items)
        fileMenu.addAction(openAction)
        #Action to save a list
        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save list')
        saveAction.triggered.connect(self.save_list_items)
        fileMenu.addAction(saveAction)
        #Action to initiate a closing sequence
        quitAction = QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Close the application')
        quitAction.triggered.connect(self.closeEvent)
        fileMenu.addAction(quitAction)
        #Action to initiate a forced closing sequence
        fQuitAction = QAction('Quit - No Save', self)
        fQuitAction.setShortcut('Ctrl+Shift+Q')
        fQuitAction.setStatusTip('Close the application without save prompt')
        fQuitAction.triggered.connect(sys.exit)
        fileMenu.addAction(fQuitAction)
        #End of main body functions
##############################################################################

    def home(self):
        self.challengeName = QLineEdit('New Challenge', self)
        self.challengeName.setMaximumSize(170, 22)

        self.addChallenge = QPushButton('Add entry', self)
        self.addChallenge.setFixedSize(82, 24)

        self.challengeList = QListWidget(self)
        self.challengeList.setSortingEnabled(True)
        self.challengeList.setMaximumWidth(250)
        self.challengeList.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Input your username here")

        self.rightSide = {}
        self.populate_right_side(self.rightSide)

        #Create the main dictionary
        mainGrid = {}
        #Create the the main grid layout
        mainGrid['layout'] = QGridLayout()
        mainGrid['layout'].addWidget(self.username, 0, 0, 1, 2)
        mainGrid['layout'].addWidget(self.challengeList, 1, 0, 1, 2)
        mainGrid['layout'].addWidget(self.challengeName, 2, 0)
        mainGrid['layout'].addWidget(self.addChallenge, 2, 1)
        mainGrid['layout'].addWidget(self.rightSide['container'], 0, 2, 3, 1)

        build_layout(mainGrid, 'widget', 'layout', 0, 2)

        self.setCentralWidget(mainGrid['widget'])

        self.connect_signals()

        self.show()
        self.activateWindow()
        #End of home body functions
##############################################################################

    def populate_right_side(self, rightSide):
        #Add a text input field for the user to define the anime id
        self.animeInput = {}
        self.animeInput['widget'] = QLineEdit()
        self.animeInput['widget'].setPlaceholderText("Type the link to the anime page or its ID")
        self.animeInput['label'] = QLabel('AnimeID')
        self.animeInput['layout'] = QVBoxLayout()
        self.animeInput['layout'].addWidget(self.animeInput['label'])
        self.animeInput['layout'].addWidget(self.animeInput['widget'])
        build_layout(self.animeInput, 'container', 'layout')

        #Building the groupbox
        self.status = buttonGroup('Status')
        self.status.batch_buttons(statusDictionary)

        #Building the tier dropbox
        self.tierChoice = {}
        self.tierChoice['widget'] = QComboBox()
        for tier in [['', ''], ['Easy', 'green'], ['Normal', 'blue'], ['Hard', 'red']]:
            self.tierChoice['widget'].addItem(tier[0], tier[1])
        self.tierChoice['label'] = QLabel('Tier')
        self.tierChoice['layout'] = QVBoxLayout()
        self.tierChoice['layout'].addWidget(self.tierChoice['label'])
        self.tierChoice['layout'].addWidget(self.tierChoice['widget'])
        self.tierChoice['layout'].insertStretch(-1, 255)
        
        #Build challenge number entry line
        self.challengeNumber = {}
        self.challengeNumber['widget'] = QLineEdit()
        self.challengeNumber['widget'].setValidator(QIntValidator(0,255))
        self.challengeNumber['widget'].setPlaceholderText('#')
        self.challengeNumber['widget'].setMaximumWidth(25)
        self.challengeNumber['label'] = QLabel('Number:')
        self.challengeNumber['layout'] = QHBoxLayout()
        self.challengeNumber['layout'].addWidget(self.challengeNumber['label'], -1, Qt.AlignRight)
        self.challengeNumber['layout'].addWidget(self.challengeNumber['widget'])

        statusTier = {}
        statusTier['layout'] = QGridLayout()
        statusTier['layout'].addWidget(self.status.box['container'], 0, 0, 2, 1)
        statusTier['layout'].addLayout(self.tierChoice['layout'], 0, 1)
        statusTier['layout'].addLayout(self.challengeNumber['layout'], 1, 1)
        build_layout(statusTier, 'container', 'layout', 2)
        
        #Build the minimum time entry box
        self.minimumTime = {}
        self.minimumTime['widget'] = QLineEdit()
        self.minimumTime['widget'].setValidator(QIntValidator(0,9999))
        self.minimumTime['label'] = QLabel('Minimum time:')

        #Build challenge text entry box
        self.challengeData = {}
        self.challengeData['widget'] = QTextEdit()
        self.challengeData['widget'].setAcceptRichText(False)
        self.challengeData['widget'].setPlaceholderText("Type the challenge requirements")
        self.challengeData['timer'] = QTimer()
        self.challengeData['timer'].setSingleShot(True)
        self.challengeData['label'] = QLabel('Challenge Data')
        self.challengeData['layout'] = QGridLayout()
        self.challengeData['layout'].addWidget(self.challengeData['label'], 0, 0)
        self.challengeData['layout'].addWidget(QWidget(), 0, 1)
        self.challengeData['layout'].setColumnStretch(1, 255)
        self.challengeData['layout'].addWidget(self.minimumTime['label'], 0, 2)
        self.challengeData['layout'].addWidget(self.minimumTime['widget'], 0, 3)
        self.challengeData['layout'].addWidget(self.challengeData['widget'], 1, 0, 1, 4)

        build_layout(self.challengeData, 'container', 'layout', [5,2], 0)

        #Build the buttons
        self.buttons = {}
        #The button to import the data from anilist
        self.buttons['import'] = QPushButton('Import AniData')
        #The button to export the image
        self.buttons['export'] = QPushButton('Export PNG')
        #The button to force a save as dialog
        self.buttons['exportas'] = QPushButton('Export PNG As')

        #Placeholder image to give a feel for the eventual frame
        self.imageViewer = {'grid': QGridLayout()}
        for item in imageLayers:
            self.imageViewer[item] = QLabel()
            self.imageViewer[item].setFixedSize(310, 540)
            self.imageViewer['grid'].addWidget(self.imageViewer[item], 0, 0, Qt.AlignCenter)
        build_layout(self.imageViewer, 'viewer', 'grid', 0, 0)
        self.imageViewer['viewer'].setStyleSheet('''
                            QWidget {
                              background: transparent;
                              border: 0px solid #32414B;
                              }
                        	''')
        self.imageViewer['line'] = QVBoxLayout()
        self.imageViewer['line'].addWidget(self.imageViewer['viewer'])
        build_layout(self.imageViewer, 'box', 'line', 0, 5)
        self.imageViewer['box'].setStyleSheet('''
                            QWidget {
                              background-color: #FFFFFF;
                              border: 5px solid #32414B;
                              padding: 0px;
                              }
                        	''')
        self.imageViewer['box'].setFixedSize(320, 550)
        self.imageViewer['layout'] = QGridLayout()
        self.imageViewer['layout'].addWidget(self.imageViewer['box'], 1, 1, Qt.AlignCenter)
        build_layout(self.imageViewer, 'container', 'layout')

        #Build a container widget for the right side of the program
        rightSide['layout'] = QGridLayout()
        rightSide['layout'].addWidget(self.animeInput['container'], 0, 0)
        rightSide['layout'].addWidget(self.buttons['import'], 0, 1, Qt.AlignBottom)
        rightSide['layout'].addWidget(self.buttons['export'], 0, 2, Qt.AlignBottom)
        rightSide['layout'].addWidget(self.buttons['exportas'], 0, 3, Qt.AlignBottom)
        rightSide['layout'].addWidget(statusTier['container'], 1, 0, 1, 1)
        rightSide['layout'].addWidget(self.challengeData['container'], 2, 0, 1, 1)
        rightSide['layout'].setRowStretch(2, 255)
        rightSide['layout'].addWidget(self.imageViewer['container'], 1, 1, 3, 3)

        build_layout(rightSide, 'container', 'layout', 5, [2, 0, 0, 0])
        rightSide['container'].setEnabled(False)

    #Connecting Signals with Events
##############################################################################
    def connect_signals(self):
        self.addChallenge.clicked.connect(self.new_list_item)
        self.challengeList.currentItemChanged.connect(self.load_item)
        self.challengeList.keyPressEvent = self.challengeList_key_events
        self.challengeName.editingFinished.connect(self.challenge_name_update)

        self.animeInput['widget'].editingFinished.connect(self.anime_id_update)
        
        self.challengeData['widget'].textChanged.connect(self.challenge_text_update)
        self.challengeData['timer'].timeout.connect(self.challenge_text_image_update)
        
        self.challengeNumber['widget'].editingFinished.connect(self.number_update)
        
        self.tierChoice['widget'].currentIndexChanged.connect(self.tier_update)
        
        self.minimumTime['widget'].editingFinished.connect(self.minimum_time_update)
        
        for key, item in self.status.buttons.items():
            item.toggled.connect(lambda state, name=key, button=item: self.change_status(name, state, button))

        self.buttons['import'].clicked.connect(self.import_aniData)
        self.buttons['export'].clicked.connect(self.export_image)
        self.buttons['exportas'].clicked.connect(self.export_image)

        #Events
##############################################################################
    def export_image(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        if not data.fileName:
            return self.export_image_as()
        data.image.build_full_image()
        data.image.full.save(data.fileName, 'png')

    def export_image_as(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        data.image.build_full_image()
        fileName = QFileDialog().getSaveFileName(self, 'Save image', self.imageSavePath, 'PNG(*.png)')[0]
        if not fileName:
            return
        data.fileName = fileName
        self.imageSavePath = data.fileName.rstrip(data.fileName.split('\\')[-1])
        data.image.full.save(data.fileName, 'png')
        
    def new_list_item(self):
        total = self.challengeList.count()
        name = self.challengeName.text() + ' ' + str(total+1).zfill(2)
        item = QListWidgetItem(name)
        data = challenge(number = total+1, name = name)
        data.image.write_challenge_number(str(total+1))
        item.setData(Qt.UserRole, data)
        self.challengeList.insertItem(total, item)
        self.challengeList.setCurrentRow(total)
        self.challengeList.setFocus(True)

    def load_item(self, currentItem):
        if not currentItem:
            return
        self.rightSide['container'].setEnabled(True)
        data = currentItem.data(Qt.UserRole)
        if data.animeID is None:
            self.animeInput['widget'].setText('')
        else:
            self.animeInput['widget'].setText(str(data.animeID))
        for key, item in data.status.items():
            if self.status.buttons[key].autoExclusive():
                self.status.buttons[key].setAutoExclusive(False)
                self.status.buttons[key].setChecked(False)
                self.status.buttons[key].setAutoExclusive(True)
            self.status.buttons[key].setChecked(item)
        self.challengeNumber['widget'].setText(str(data.number))
        self.tierChoice['widget'].setCurrentIndex(data.tierIndex)
        self.challengeData['widget'].setPlainText(data.challenge)
        self.minimumTime['widget'].setText(str(data.minimumTime))
        for item in imageLayers:
            self.change_image(data, item)
            
    def save_list_items(self):
        fileName = QFileDialog().getSaveFileName(self, 'Save challenge list', self.challengeSavePath, 'ACLO(*.aclo)')[0]
        if not fileName:
            return False
        self.challengeSavePath = fileName.rstrip(fileName.split('\\')[-1])
        challengeList = []
        for k in range(0, self.challengeList.count()):
            name = self.challengeList.item(k).text()
            data = self.challengeList.item(k).data(Qt.UserRole)
            challengeList.append([name, data])
        with open(fileName, 'wb') as f:
            pickle.dump(challengeList, f)
        return True
        
    
    def load_list_items(self):
        fileName = QFileDialog().getOpenFileName(self, 'Load challenge list', self.challengeSavePath, 'ACLO(*.aclo)')[0]
        if not fileName:
            return
        try:
            with open(fileName, 'rb') as f:
                dataList = pickle.load(f)
        except:
            QErrorMessage().showMessage("Couldn't open file!")
            return
        self.challengeList.clear()
        for k, data in enumerate(dataList):
            item = QListWidgetItem(data[0])
            item.setData(Qt.UserRole, data[1])
            self.challengeList.insertItem(k, item)
        self.challengeList.setCurrentRow(k)
        self.challengeList.setFocus(True)
        self.recentlyLoaded = True
           
    def challenge_name_update(self):
        name = self.challengeName.text()
        for k in range(0, self.challengeList.count()):
            number = self.challengeList.item(k).data(Qt.UserRole).number
            text = name + ' ' + str(number).zfill(2)
            self.challengeList.item(k).setText(text)
        
    def import_aniData(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        if data.get_info_from_id(self.username.text()):
            for item in ['image', 'title', 'dates', 'duration']:
                self.change_image(data, item)
        else:
            self.wrong_id()

    def change_image(self, data, key):
        self.imageViewer[key].image = getattr(data.image, key, data.image.empty)
        self.imageViewer[key].Qt = ImageQt(self.imageViewer[key].image)
        self.imageViewer[key].pixmap = QPixmap.fromImage(self.imageViewer[key].Qt)
        self.imageViewer[key].setPixmap(self.imageViewer[key].pixmap)

    def change_status(self, name, state, button):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        data.status[name] = state
        if type(button) == type(QRadioButton()):
            if(state):
                position = (35, 35)
                data.image.add_icon(name, position)
                self.change_image(data, 'icons')
        else:
            if(not state):
                name = 'empty'
            position = (245,35)
            data.image.add_icon(name, position)
            self.change_image(data, 'icons')
        if(button.glowColor):
            if(state):
                data.image.build_glow(button.glowColor, 8)
                self.change_image(data, 'glow')

    def anime_id_update(self, data = False):
        if not data:
            data = self.challengeList.currentItem().data(Qt.UserRole)
        text = self.animeInput['widget'].text()
        try:
            data.animeID = int(text)
        except ValueError:
            if data.get_id_from_link(text):
                self.animeInput['widget'].setText(str(data.animeID))
            else:
                self.myStatusBar.setStyleSheet('color: red')
                self.myStatusBar.showMessage('Invalid input', 1000)
                return
        self.myStatusBar.showMessage('Updated ID', 1000)
        self.challengeList.currentItem().setData(Qt.UserRole, data)

    def wrong_id(self):
        pass

    def number_update(self):
        number = self.challengeNumber['widget'].text()
        currentItem = self.challengeList.currentItem()
        text = currentItem.text()
        text = text.strip(text.split()[-1]) + number.zfill(2)
        currentItem.setText(text)
        data = currentItem.data(Qt.UserRole)
        data.number = int(number)
        data.image.write_challenge_number(str(data.number), 15)
        self.change_image(data, 'number')
        
    def tier_update(self, index):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        data.tierIndex = index
        tier = self.tierChoice['widget'].currentText()
        color = self.tierChoice['widget'].currentData()
        data.image.write_challenge_tier(tier, color = color)
        self.change_image(data, 'tier')
    
    def challenge_text_update(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        data.challenge = self.challengeData['widget'].toPlainText()
        self.challengeData['timer'].start(500)
        
    def challenge_text_image_update(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        data.image.write_challenge_text(data.challenge, 15)
        self.change_image(data, 'challenge')
    
    def minimum_time_update(self):
        data = self.challengeList.currentItem().data(Qt.UserRole)
        if self.minimumTime['widget'].text():
            data.minimumTime = int(self.minimumTime['widget'].text())
        data.image.write_duration_text(data.minimumTime, data.episodeCount,
                                       data.episodeDuration, 15)
        self.change_image(data, 'duration')

    def challengeList_key_events(self, event):
        if event.key() == Qt.Key_Delete:
            self.rightSide['container'].setEnabled(False)
            row = self.challengeList.currentRow()
            self.challengeList.takeItem(row)
            row = max([0, row - 1])
            self.challengeList.setCurrentRow(row)

    #Exit Application
    def closeEvent(self, event):
        choice = QMessageBox.question(self,
                        'Close Application',
                        'Would you like to save your current challenge?',
                        QMessageBox.Yes |
                        QMessageBox.No |
                        QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            try:
                if self.save_list_items():
                    event.accept()
                else:
                    event.ignore()
            except AttributeError:
                sys.exit()
        elif choice == QMessageBox.No:
            try:
                event.accept()
            except AttributeError:
                sys.exit()
        else:
            try:
                event.ignore()
            except AttributeError:
                pass

    #Screen positioning methods
##############################################################################
    def center_screen(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
                QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    #Custom Widget Classes
##############################################################################
#Class to universalize the statusgroup widget
class buttonGroup():
    def __init__(
            self, boxName, buttonSpacing = [2, 2], buttonMargins = 2,
            boxSpacing = 2, boxMargins = 0):
        self.buttons = {}
        self.labels = {}
        self.box = {}
        self.box['box'] = QGroupBox()
        self.box['box'].setStyleSheet('''
                  QGroupBox {
                  font-weight: bold;
                  border: 1px solid #32414B;
                  border-radius: 4px;
                  padding: 2px;
                  margin-top: 0px;
                  }''')
        self.box['grid'] = QGridLayout()
        build_layout(self.box, 'box', 'grid', buttonSpacing, buttonMargins)
        self.box['label'] = QLabel(boxName)
        self.box['layout'] = QVBoxLayout()
        self.box['layout'].addWidget(self.box['label'])
        self.box['layout'].addWidget(self.box['box'])
        build_layout(self.box, 'container', 'layout', boxSpacing, boxMargins)

    def add_button(
            self, name, exclusive = False, checked = False, color = None):
        column = len(self.buttons)
        if exclusive:
            self.buttons[name] = QRadioButton()
        else:
            self.buttons[name] = QCheckBox()
        self.buttons[name].glowColor = color
        self.labels[name] = QLabel(name[0:3])
        self.box['grid'].addWidget(self.buttons[name], 0, column, Qt.AlignCenter)
        self.box['grid'].addWidget(self.labels[name], 1, column, Qt.AlignCenter)

    def batch_buttons(self, buttonsDictionary = {}):
        for key, typelist in buttonsDictionary.items():
            self.add_button(key, typelist[0], typelist[1], typelist [2])

#Specialized statusBar
class myStatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    @pyqtSlot()
    def clearMessage(self):
        self.setStyleSheet('color: white')
        super().clearMessage()
    #Data storage classes
##############################################################################
#Class to store the image information in
class challenge:
    def __init__(self, name = '', number = 0):
        self.name = name
        self.image = animeImage((31, 35, 35, 255), (95, 104, 117, 255))
        self.animeID = None
        self.status = {}
        for key, item in statusDictionary.items():
            self.status[key] = item[1]
        self.number = number
        self.tierIndex = 0
        self.title = None
        self.imageLink = None
        self.challenge = None
        self.startDate = None
        self.completeDate = None
        self.minimumTime = 0
        self.episodeCount = 0
        self.episodeDuration = 0

    def get_id_from_link(self, link):
        #Split the link into parts seperated by /
        words = link.split('/')
        if words[0] == 'http:' or words[0] == 'https:':
            pos = 4
        elif words[0] == 'anilist.co':
            pos = 3
        else:
            return(False)
        try:
            self.animeID = int(words[pos])
            self.link = link
            return(True)
        except:
            return(False)

    def get_info_from_id(self, username = None):
        anime = anilistAPI.get_anime_data(self.animeID)
        if not anime:
            return False
        self.link = 'https://anilist.co/anime' + str(self.animeID) + '/'
        self.title = anime['title']['userPreferred']
        self.image.write_title_text(self.title)
        self.imageLink = anime['coverImage']['large']
        self.image.open_image(self.imageLink)
        self.episodeCount = anime['episodes']
        self.episodeDuration = anime['duration']
        self.image.write_duration_text(self.minimumTime, self.episodeCount, self.episodeDuration, 15)
        self.startDate = {'year': None, 'month': None, 'day': None}
        self.completeDate = {'year': None, 'month': None, 'day': None}
        if username:
            user = anilistAPI.get_user_data(self.animeID, username)
            if user:
                self.startDate = user['startedAt']
                self.completeDate = user['completedAt']
        self.image.write_dates_text(self.startDate, self.completeDate, 15)
        return True

    def build_all_image_layers(self):
        pass

class animeImage:
    def __init__(self, baseColor, borderColor):
        self.empty = Image.new('RGBA',(310, 540), (0,0,0,0))
        self.base = round_rectangle((310, 540), 10, baseColor)
        self.glowfill = self.empty.copy()
        self.glow = self.empty.copy()
        self.build_border(borderColor, baseColor)
        self.image = self.empty.copy()
        self.icons = self.empty.copy()
        #Text based entries, starting with the font path
        self.fontPath = resourcesFontPath + 'Proxima\\Regular.otf'
        self.fontPathBold = resourcesFontPath + 'Proxima\\Bold.otf'
        self.number = self.empty.copy()
        self.tier = self.empty.copy()
        self.challenge = self.empty.copy()
        self.title = self.empty.copy()
        self.dates = self.empty.copy()
        self.duration = self.empty.copy()

    def open_image(self, url):
        image = Image.open(requests.get(url, stream=True).raw)
        width = 230
        height = 320
        if image.size[0] != width:
            ratio = width / image.size[0]
            newHeight = int(math.ceil(ratio * image.size[1]))
            image = image.resize((width, newHeight), Image.BICUBIC)
        if image.size[1] > height:
            toCrop = image.size[1] - height
            left = 0
            right = width
            top = toCrop//2
            bottom = top + height
            image = image.crop((left, top, right, bottom))
        croppedHeight = image.size[1]
        self.image = self.empty.copy()
        self.image.paste(image, (40, (height - croppedHeight) // 2 + 40))

    def build_border(self, borderColor, fillColor):
        border = round_rectangle((240, 330), 5, borderColor)
        fill = Image.new('RGBA', (230, 320), fillColor)
        self.border = self.empty.copy()
        self.border.paste(border, (35, 35), border)
        self.border.paste(fill, (40, 40))

    def build_glow(self, color,  radius):
        alpha = self.empty.copy()
        radiusHalved = radius//2
        box = round_rectangle((240 + radius, 330 + radius), 5 + radiusHalved, 'green')
        alpha.paste(box, (35 - radiusHalved, 35 - radiusHalved))
        blur = alpha.filter(ImageFilter.GaussianBlur(radiusHalved))
        alpha = blur.split()[-1]
        self.glow = Image.new('RGBA', alpha.size, (color))
        self.glow
        self.glow.putalpha(alpha)

    def add_icon(self, name, position):
        newIcon = Image.open(resourcesImagePath + name.lower() + '.png')
        newIcon = newIcon.resize((30,30))
        self.icons.paste(newIcon, position)

    def write_challenge_number(self, number, fontSize = 20):
        self.number = self.empty.copy()
        font = ImageFont.truetype(self.fontPathBold, fontSize)
        textSize = font.getsize(number)
        x = 40 - textSize[0]//2
        y = 358 - textSize[1]//2
        self.number = draw_text(self.number, number, x, y, font, outline = 3)
        
    def write_challenge_tier(self, tier, color = 'white', fontSize = 20):
        self.tier = self.empty.copy()
        if tier == '':
            return
        font = ImageFont.truetype(self.fontPathBold, fontSize)
        textSize = tuple(map(sum,zip(font.getsize(tier), (6,6))))
        txtimg = Image.new('RGBA', textSize, (0,0,0,0))
        txtimg = draw_text(txtimg, tier, 3, 3, font, textColor = color, outline = 3)
        txtimg = txtimg.rotate(30, resample=Image.BICUBIC, expand=1)
        x = 265 - txtimg.size[0]//2
        y = 350 - txtimg.size[1]//2
        self.tier.paste(txtimg, (x, y), txtimg)
        
    def write_challenge_text(self, text, fontSize = 15):
        self.challenge = self.empty.copy()
        maxWidth = 270
        maxHeight = 40
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath = self.fontPathBold)
        textSize = font.getsize_multiline(text, spacing = 0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 385
        self.challenge = draw_text(self.challenge, text, x, y, alignment = 'center', outline = 1,
                                  font = font, textColor = 'white', shadowColor = 'black')

    def write_title_text(self, text, fontSize = 20):
        self.title = self.empty.copy()
        maxWidth = 270
        maxHeight = 40
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath = self.fontPathBold)
        textSize = font.getsize_multiline(text, spacing = 0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 435 + (maxHeight - textSize[1])//2
        self.title = draw_text(self.title, text, x, y, alignment = 'center', outline = 2,
                                  font = font, textColor = 'white', shadowColor = 'black')

    def write_dates_text(self, startDate, completeDate, fontSize = 15):
        start = 'Start: {day}/{month}/{year}'
        if startDate['day']:
            if datetime.datetime.now().year == startDate['year']:
                startDate['year'] = ''
        else:
            startDate['day'] = startDate['month'] = '??'
            startDate['year'] = ''
        start = start.format(**startDate).strip('/') + '   '
        
        end = 'End: {day}/{month}/{year}'
        if completeDate['day']:
            if datetime.datetime.now().year == completeDate['year'] and startDate['year'] == '':
                completeDate['year'] = ''
        else:
            completeDate['day'] = completeDate['month'] = '??'
            completeDate['year'] = ''
        end = end.format(**completeDate).strip('/')
        text = start + end
        
        self.dates = self.empty.copy()
        
        #Set geometry
        maxWidth = 270
        maxHeight = 15
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath = self.fontPath)
        textSize = font.getsize_multiline(text, spacing = 0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 485 + (maxHeight - textSize[1])//2
        #Write text
        self.dates = draw_text(self.dates, text, x, y, alignment = 'center', outline = 0,
                                  font = font, textColor = 'white', shadowColor = 'black')
        
    
    def write_duration_text(self, minTime, epCount, epDuration, fontSize = 15):
        #Clear previous text
        self.duration = self.empty.copy()
        #Build text
        text = ''
        if minTime:
            text = 'Min: {} | '.format(minTime)
        text += 'Total: '
        if epCount and epCount > 1:
            text += '{}x'.format(epCount)
        if epDuration:
            text += '{} mins'.format(epDuration)
        #Set geometry
        maxWidth = 270
        maxHeight = 15
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath = self.fontPath)
        textSize = font.getsize_multiline(text, spacing = 0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 505 + (maxHeight - textSize[1])//2
        #Write text
        self.duration = draw_text(self.duration, text, x, y, alignment = 'center', outline = 0,
                                  font = font, textColor = 'white', shadowColor = 'black')
        

    def build_full_image(self):
        self.full = Image.alpha_composite(self.base, self.glow)
        self.full.paste(self.border, (0, 0), self.border)
        self.full.paste(self.image, (0, 0), self.image)
        self.full.paste(self.icons, (0, 0), self.icons)
        self.full.paste(self.number, (0,0), self.number)
        self.full.paste(self.tier, (0,0), self.tier)
        self.full.paste(self.challenge, (0,0), self.challenge)
        self.full.paste(self.title, (0,0), self.title)
        self.full.paste(self.dates, (0,0), self.dates)
        self.full.paste(self.duration, (0,0), self.duration)

#Global functions
##############################################################################
#A method of universalizing the building of a widget around a layout
def build_layout(target, containerKey, layoutKey, spacings=0, margins=0):
    if containerKey not in target:
        target[containerKey] = QWidget()
    target[containerKey].setLayout(target[layoutKey])
    if type(spacings) == type([]):
        target[layoutKey].setHorizontalSpacing(spacings[0])
        target[layoutKey].setVerticalSpacing(spacings[1])
    else:
        target[layoutKey].setSpacing(spacings)
    if type(margins) == type([]):
        target[layoutKey].setContentsMargins(margins[0], margins[1], margins[2], margins[3])
    else:
        target[layoutKey].setContentsMargins(margins, margins, margins, margins)

def text_fitter(maxWidth, maxHeight, text, fontSize, fontPath, spacing = 0):
    font = ImageFont.truetype(fontPath, fontSize)
    textsize = font.getsize_multiline(text, spacing = spacing)
    if textsize[0] < maxWidth and textsize[1] < maxHeight:
        return text, font
    maxLines = maxHeight // fontSize
    if textsize[0] // maxLines > maxWidth:
        return text_fitter(maxWidth, maxHeight, text, fontSize - 1, fontPath)
    lines = line = ''
    lineWidth = 0
    lineCount = 1
    spaceWidth = font.getsize(' ')[0]
    for word in text.split():
        wordWidth = font.getsize(word)[0]
        if (lineWidth + wordWidth) < maxWidth:
            line += word + ' '
            lineWidth += wordWidth + spaceWidth
        else:
            lineCount += 1
            if lineCount > maxLines:
                return text_fitter(maxWidth, maxHeight, text, fontSize - 1, fontPath)
            line = line.strip()
            lines += line + '\n'
            line = word + ' '
            lineWidth = wordWidth
    text = lines + line.strip()
    return text, font
           
def draw_text(image, text, x, y, font, textColor = 'white', shadowColor = 'black', outline = 0, alignment = 'left', spacing = 0):
    draw = ImageDraw.Draw(image)
    
    for flow in range(outline,outline+1):
        for shift in range(-flow, flow+1):
            draw.multiline_text((x+shift, y+(flow-abs(shift))), text,
                                font=font, fill=shadowColor, align = alignment)
            draw.multiline_text((x+shift, y-(flow-abs(shift))), text,
                                font=font, fill=shadowColor, align = alignment)
    
    draw.multiline_text((x, y), text, font=font, fill=textColor, align = alignment)
    
    return(image)
 
def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner

def round_rectangle(size, radius, fill):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image.new('RGBA', size, fill)
    corner = round_corner(radius, fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius)) # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle

def run():
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Gui = window()
    app.exec_()