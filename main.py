# -*- coding: utf-8 -*-
"""
Created on Wed May 22 09:12:31 2019

Small program that helps generate the images used in several AWC submission posts

@author: Bram Hermsen
"""

#Import PyQt for the GUI, sys for
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL.ImageQt import ImageQt
import os
import sys
import requests
import math
import datetime
import qdarkstyle
import anilistAPI


resourcesImagePath = os.getcwd() + '\\resources\\images\\'
resourcesFontPath = os.getcwd() + '\\resources\\fonts\\'
saveImagePath = os.getcwd() + '\\exports\\'

statusDictionary = {'Complete': [True, False, 'Green'], 'Watching': [True, False, 'Blue'], 
                    'Decided': [True, False, 'Red'], 'Undecided': [True, True, 'White'],
                    'Previously_Watched': [True, False, 'Orange'], 'Rewatch': [False, False, None]}
imageLayers = ['base', 'glow', 'border', 'image', 'icons', 'number', 'tier', 'challenge', 'title', 'dates', 'duration']

class window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_screen()
        self.home()

    def main_screen(self):
        self.setFixedSize(900, 650)
        self.setWindowTitle('AWC Image Maker')
        self.setWindowIcon(QtGui.QIcon(resourcesImagePath + 'awc.ico'))
        self.center_screen()

        #Create a universal statusbar
        self.myStatusBar = myStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.setSizeGripEnabled(False)

        #Create a universal menubar
        mainMenu = self.menuBar()

        #Primary filemenu with basic actions like closing, opening and saving.
        fileMenu = mainMenu.addMenu('&File')
        #Action to initiate a closing sequence
        quitAction = QtWidgets.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Close the application')
        quitAction.triggered.connect(self.closeEvent)
        fileMenu.addAction(quitAction)
        #Action to initiate a forced closing sequence
        forcedQuitAction = QtWidgets.QAction('Quit - No Save', self)
        forcedQuitAction.setShortcut('Ctrl+Shift+Q')
        forcedQuitAction.setStatusTip('Close the application without save prompt')
        forcedQuitAction.triggered.connect(sys.exit)
        fileMenu.addAction(forcedQuitAction)
        #End of main body functions
###################################################################################################

    def home(self):
        self.newChallengeName = QtWidgets.QLineEdit('New Challenge', self)
        self.newChallengeName.setMaximumSize(170, 22)

        self.addChallenge = QtWidgets.QPushButton('Add Challenge', self)
        self.addChallenge.setMaximumSize(82, 24)
        self.addChallenge.setMinimumSize(82, 24)

        self.challengeList = QtWidgets.QListWidget(self)
        self.challengeList.setDragDropMode(4)
        self.challengeList.DropIndicatorPosition = QtWidgets.QAbstractItemView.BelowItem
        self.challengeList.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        self.challengeList.setMaximumWidth(250)
        self.challengeList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.username = myLineEdit()
        self.username.setPlaceholderText("Input your username here")

        self.rightSide = {}
        self.populate_right_side(self.rightSide)

        #Create the main dictionary
        mainGrid = {}
        #Create the the main grid layout
        mainGrid['layout'] = QtWidgets.QGridLayout()
        mainGrid['layout'].addWidget(self.username, 0, 0, 1, 2)
        mainGrid['layout'].addWidget(self.challengeList, 1, 0, 1, 2)
        mainGrid['layout'].addWidget(self.newChallengeName, 2, 0)
        mainGrid['layout'].addWidget(self.addChallenge, 2, 1)
        mainGrid['layout'].addWidget(self.rightSide['container'], 0, 2, 3, 1)

        build_layout(mainGrid, 'widget', 'layout', 0, 2)

        self.setCentralWidget(mainGrid['widget'])

        self.connect_signals()

        self.show()
        self.activateWindow()
        #End of home body functions
###################################################################################################

    def populate_right_side(self, rightSide):
        #Add a text input field for the user to define the anime id
        self.animeInput = {}
        self.animeInput['widget'] = myLineEdit()
        self.animeInput['widget'].setPlaceholderText("Type the link to the anime page or its ID")
        self.animeInput['label'] = QtWidgets.QLabel('AnimeID')
        self.animeInput['layout'] = QtWidgets.QVBoxLayout()
        self.animeInput['layout'].addWidget(self.animeInput['label'])
        self.animeInput['layout'].addWidget(self.animeInput['widget'])
        build_layout(self.animeInput, 'container', 'layout')

        #Building the groupbox
        self.status = buttonGroup('Status')
        self.status.batch_buttons(statusDictionary)

        #Building the tier dropbox
        self.tierChoice = {}
        self.tierChoice['widget'] = QtWidgets.QComboBox()
        for tier in [['', ''], ['Easy', 'green'], ['Normal', 'blue'], ['Hard', 'red']]:
            self.tierChoice['widget'].addItem(tier[0], tier[1])
        self.tierChoice['label'] = QtWidgets.QLabel('Tier')
        self.tierChoice['layout'] = QtWidgets.QVBoxLayout()
        self.tierChoice['layout'].addWidget(self.tierChoice['label'])
        self.tierChoice['layout'].addWidget(self.tierChoice['widget'])
        self.tierChoice['layout'].insertStretch(-1, 255)
        
        #Build challenge number entry line
        self.challengeNumber = {}
        self.challengeNumber['widget'] = myLineEdit()
        self.challengeNumber['widget'].setValidator(QtGui.QIntValidator(0,255))
        self.challengeNumber['widget'].setPlaceholderText('#')
        self.challengeNumber['widget'].setMaximumWidth(25)
        self.challengeNumber['label'] = QtWidgets.QLabel('Number:')
        self.challengeNumber['layout'] = QtWidgets.QHBoxLayout()
        self.challengeNumber['layout'].addWidget(self.challengeNumber['label'], -1, QtCore.Qt.AlignRight)
        self.challengeNumber['layout'].addWidget(self.challengeNumber['widget'])

        statusTier = {}
        statusTier['layout'] = QtWidgets.QGridLayout()
        statusTier['layout'].addWidget(self.status.box['container'], 0, 0, 2, 1)
        statusTier['layout'].addLayout(self.tierChoice['layout'], 0, 1)
        statusTier['layout'].addLayout(self.challengeNumber['layout'], 1, 1)
        build_layout(statusTier, 'container', 'layout', 2)
        
        #Build the minimum time entry box
        self.minimumTime = {}
        self.minimumTime['widget'] = myLineEdit()
        self.minimumTime['widget'].setValidator(QtGui.QIntValidator(0,9999))
        self.minimumTime['label'] = QtWidgets.QLabel('Minimum time:')

        #Build challenge text entry box
        self.challengeData = {}
        self.challengeData['widget'] = myTextEdit()
        self.challengeData['widget'].setAcceptRichText(False)
        self.challengeData['widget'].setPlaceholderText("Type the challenge requirements")
        self.challengeData['label'] = QtWidgets.QLabel('Challenge Data')
        self.challengeData['layout'] = QtWidgets.QGridLayout()
        self.challengeData['layout'].addWidget(self.challengeData['label'], 0, 0)
        self.challengeData['layout'].addWidget(QtWidgets.QWidget(), 0, 1)
        self.challengeData['layout'].setColumnStretch(1, 255)
        self.challengeData['layout'].addWidget(self.minimumTime['label'], 0, 2)
        self.challengeData['layout'].addWidget(self.minimumTime['widget'], 0, 3)
        self.challengeData['layout'].addWidget(self.challengeData['widget'], 1, 0, 1, 4)

        build_layout(self.challengeData, 'container', 'layout', [5,2], 0)

        #Build the button to import the data from anilist
        self.importAnidata = {}
        self.importAnidata['widget'] = QtWidgets.QPushButton('Import AniData')

        #Build the button to export the final image
        self.exportPNG = {}
        self.exportPNG['widget'] = QtWidgets.QPushButton('Export PNG')

        #Placeholder image to give a feel for the eventual frame
        self.imageViewer = {'grid': QtWidgets.QGridLayout()}
        for item in imageLayers:
            self.imageViewer[item] = QtWidgets.QLabel()
            self.imageViewer[item].setFixedSize(310, 540)
            self.imageViewer['grid'].addWidget(self.imageViewer[item], 0, 0, QtCore.Qt.AlignCenter)
        build_layout(self.imageViewer, 'viewer', 'grid', 0, 0)
        self.imageViewer['viewer'].setStyleSheet('''
                            QWidget {
                              background: transparent;
                              border: 0px solid #32414B;
                              }
                        	''')
        self.imageViewer['line'] = QtWidgets.QVBoxLayout()
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
        self.imageViewer['layout'] = QtWidgets.QGridLayout()
        self.imageViewer['layout'].addWidget(self.imageViewer['box'], 1, 1, QtCore.Qt.AlignCenter)
        build_layout(self.imageViewer, 'container', 'layout')

        #Build a container widget for the right side of the program
        rightSide['layout'] = QtWidgets.QGridLayout()
        rightSide['layout'].addWidget(self.animeInput['container'], 0, 0)
        rightSide['layout'].addWidget(self.importAnidata['widget'], 0, 1, QtCore.Qt.AlignBottom)
        rightSide['layout'].addWidget(self.exportPNG['widget'], 0, 2, QtCore.Qt.AlignBottom)
        rightSide['layout'].addWidget(statusTier['container'], 1, 0, 1, 1)
        rightSide['layout'].addWidget(self.challengeData['container'], 2, 0, 1, 1)
        rightSide['layout'].setRowStretch(2, 255)
        rightSide['layout'].addWidget(self.imageViewer['container'], 1, 1, 3, 3)

        build_layout(rightSide, 'container', 'layout', 5, [2, 0, 0, 0])
        rightSide['container'].setEnabled(False)

    #Connecting Signals with Events
###################################################################################################
    def connect_signals(self):
        self.addChallenge.clicked.connect(self.new_list_item)
        self.challengeList.currentItemChanged.connect(self.load_item)
        self.challengeList.keyPressEvent = self.challengeList_key_events

        self.animeInput['widget'].editingFinished.connect(self.anime_id_update)
        
        self.challengeData['widget'].textChanged.connect(self.challenge_update)
        
        self.challengeNumber['widget'].editingFinished.connect(self.number_update)
        
        self.tierChoice['widget'].currentIndexChanged.connect(self.tier_update)
        
        self.minimumTime['widget'].editingFinished.connect(self.minimum_time_update)

        self.importAnidata['widget'].clicked.connect(self.import_aniData)
        
        for key, item in self.status.buttons.items():
            item.toggled.connect(lambda state, name=key, button=item: self.change_status(name, state, button))

        self.exportPNG['widget'].clicked.connect(self.export_image)

        #Events
###################################################################################################
    def export_image(self):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        data.image.build_full_image()

    def new_list_item(self):
        k = self.challengeList.count()
        name = self.newChallengeName.text()
        item = QtWidgets.QListWidgetItem(name)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        item.setData(QtCore.Qt.UserRole, challenge())
        self.challengeList.insertItem(k, item)
        self.challengeList.setCurrentRow(k)
        self.challengeList.setFocus(True)

    def load_item(self, currentItem):
        if not currentItem:
            return
        self.rightSide['container'].setEnabled(True)
        data = currentItem.data(QtCore.Qt.UserRole)
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

    def import_aniData(self):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        if data.get_info_from_id(self.username.text()):
            for item in ['image', 'title', 'dates', 'duration']:
                self.change_image(data, item)
        else:
            self.wrong_id()

    def change_image(self, data, key):
        self.imageViewer[key].image = getattr(data.image, key, data.image.empty)
        self.imageViewer[key].Qt = ImageQt(self.imageViewer[key].image)
        self.imageViewer[key].pixmap = QtGui.QPixmap.fromImage(self.imageViewer[key].Qt)
        self.imageViewer[key].setPixmap(self.imageViewer[key].pixmap)

    def change_status(self, name, state, button):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        data.status[name] = state
        if type(button) == type(QtWidgets.QRadioButton()):
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
            data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
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
        self.challengeList.currentItem().setData(QtCore.Qt.UserRole, data)

    def wrong_id(self):
        pass

    def number_update(self):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        if self.challengeNumber['widget'].text():
            data.number = int(self.challengeNumber['widget'].text())
        data.image.write_challenge_number(str(data.number), 15)
        self.change_image(data, 'number')
        
    def tier_update(self, index):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        data.tierIndex = index
        tier = self.tierChoice['widget'].currentText()
        color = self.tierChoice['widget'].currentData()
        data.image.write_challenge_tier(tier, color = color)
        self.change_image(data, 'tier')
    
    def challenge_update(self):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        data.challenge = self.challengeData['widget'].toPlainText()
        data.image.write_challenge_text(data.challenge, 15)
        self.change_image(data, 'challenge')
    
    def minimum_time_update(self):
        data = self.challengeList.currentItem().data(QtCore.Qt.UserRole)
        if self.minimumTime['widget'].text():
            data.minimumTime = int(self.minimumTime['widget'].text())
        data.image.write_duration_text(data.minimumTime, data.episodeCount, data.episodeDuration, 15)
        self.change_image(data, 'duration')

    def challengeList_key_events(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.rightSide['container'].setEnabled(False)
            row = self.challengeList.currentRow()
            self.challengeList.takeItem(row)
            row = max([0, row - 1])
            self.challengeList.setCurrentRow(row)

    #Exit Application
    def closeEvent(self, event):
        choice = QtWidgets.QMessageBox.question(self,
                                            'Close Application',
                                            'You sure you want to quit?',
                                            QtWidgets.QMessageBox.Yes |
                                            QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
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
###################################################################################################
    def center_screen(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(
                QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    #Custom Widget Classes
###################################################################################################
#Class to universalize the statusgroup widget
class buttonGroup():
    def __init__(self, boxName, buttonSpacing = [2, 2], buttonMargins = 2, boxSpacing = 2, boxMargins = 0):
        self.buttons = {}
        self.labels = {}
        self.box = {}
        self.box['box'] = QtWidgets.QGroupBox()
        self.box['box'].setStyleSheet('''
                  QGroupBox {
                  font-weight: bold;
                  border: 1px solid #32414B;
                  border-radius: 4px;
                  padding: 2px;
                  margin-top: 0px;
                  }''')
        self.box['grid'] = QtWidgets.QGridLayout()
        build_layout(self.box, 'box', 'grid', buttonSpacing, buttonMargins)
        self.box['label'] = QtWidgets.QLabel(boxName)
        self.box['layout'] = QtWidgets.QVBoxLayout()
        self.box['layout'].addWidget(self.box['label'])
        self.box['layout'].addWidget(self.box['box'])
        build_layout(self.box, 'container', 'layout', boxSpacing, boxMargins)

    def add_button(self, name, exclusive = False, checked = False, color = None):
        column = len(self.buttons)
        if exclusive:
            self.buttons[name] = QtWidgets.QRadioButton()
        else:
            self.buttons[name] = QtWidgets.QCheckBox()
        self.buttons[name].glowColor = color
        self.labels[name] = QtWidgets.QLabel(name[0:3])
        self.box['grid'].addWidget(self.buttons[name], 0, column, QtCore.Qt.AlignCenter)
        self.box['grid'].addWidget(self.labels[name], 1, column, QtCore.Qt.AlignCenter)

    def batch_buttons(self, buttonsDictionary = {}):
        for key, typelist in buttonsDictionary.items():
            self.add_button(key, typelist[0], typelist[1], typelist [2])

class myLineEdit(QtWidgets.QLineEdit):
    lostFocus = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent=parent)

    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusOutEvent(e)
    
class myTextEdit(QtWidgets.QTextEdit):
    lostFocus = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        super().__init__(parent=parent)
        
    def focusOutEvent(self, e):
        self.lostFocus.emit()
        super().focusOutEvent(e)

#Specialized statusBar
class myStatusBar(QtWidgets.QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    @QtCore.pyqtSlot()
    def clearMessage(self):
        self.setStyleSheet('color: white')
        super().clearMessage()
        
class timeOutWorker(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    #Data storage classes
###################################################################################################
#Class to store the image information in
class challenge:
    def __init__(self):
        self.image = animeImage((31, 35, 35, 255), (95, 104, 117, 255))
        self.animeID = None
        self.status = {}
        for key, item in statusDictionary.items():
            self.status[key] = item[1]
        self.number = 0
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
        self.full.save(saveImagePath + 'test.png', 'png')
        self.full.show()

#Global functions
###################################################################################################
#A method of universalizing the building of a widget around a layout
def build_layout(target, containerKey, layoutKey, spacings=0, margins=0):
    if containerKey not in target:
        target[containerKey] = QtWidgets.QWidget()
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
            draw.multiline_text((x + shift, y + (flow - abs(shift))), text, font=font, fill=shadowColor, align = alignment)
            draw.multiline_text((x + shift, y - (flow - abs(shift))), text, font=font, fill=shadowColor, align = alignment)
    
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
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Gui = window()
    app.exec_()

def test_image():
    test = challenge()
    test.animeID = 1010
    test.get_info_from_id('bolt')
    test.image.build_glow('green', 8)
    test.image.add_icon('Complete', (35,35))
    test.image.write_challenge_tier('Normal', color = 'blue', fontSize = 20)
    test.image.build_full_image()