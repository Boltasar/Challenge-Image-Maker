# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 16:37:25 2019

@author: nxf52810
"""

import math
import datetime
# Import PIL for the image editing
from PIL import Image, ImageDraw, ImageFilter, ImageFont
# Import requests for internet access
import requests
# Local module for interacting with the anilist API.
import anilistAPI
from config import RESOURCES_FONT_PATH, RESOURCES_IMAGE_PATH, STATUS_DICTIONARY


# Class to store the image information in
class challengeEntry:
    """
    Class to save and manipulate the data of a challenge entry.

    Attributes:
        image (animeImage): An object holding all the imagedata and methods.
        animeID (int): The id of the anime.
        status (dict): A dictionary of the state of completion status.
        number (str): The number of the challenge entry.
        tierIndex (int): The index of the tier.
        title (str): The title of the anime.
        imageLink (str): The link to the anime's picture on anilist.
        requirement (str): The challenge entry's goal.
        startDate (dict): The year, month, day that the anime was started.
        completedDate (dict): The year, month, day that the anime was completed.
        minimumTime (int): The minimum time requirement for the challenge entry.
        episodeCount (int): The number of episodes of the anime.
        epidoseDuration (int): The duration of the anime's episodes.
    """

    # Class variables
    savedAttributesList = [
        'link', 'animeID', 'status', 'number', 'tierIndex', 'title',
        'imageLink', 'requirement', 'startDate', 'completeDate',
        'episodeCount', 'episodeDuration'
    ]

    def __init__(self, number='0'):
        """
        The construct for challengeEntry class.

        Args:
            number (int) default=0: Number of the challenge entry.

        Returns
        -------
        None.
        """
        self.image = animeImage((31, 35, 35, 255), (95, 104, 117, 255))
        self.animeID = None
        self.link = 'https://anilist.co/anime'
        self.status = {}
        for key, item in STATUS_DICTIONARY.items():
            self.status[key] = item[1]
        self.number = number
        self.tierIndex = 0
        self.title = None
        self.imageLink = None
        self.requirement = ''
        self.startDate = None
        self.completeDate = None
        self.minimumTime = 0
        self.episodeCount = 0
        self.episodeDuration = 0
        self.progress = 0

    def get_id_from_link(self, link):
        # Split the link into parts seperated by /
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
        except ValueError:
            return(False)

    def get_info_from_id(self, username=None):
        # Retrieves Anilist info with the ID
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
        self.image.write_duration_text(self.minimumTime, self.episodeCount,
                                       self.episodeDuration, 15)
        self.startDate = {'year': None, 'month': None, 'day': None}
        self.completeDate = {'year': None, 'month': None, 'day': None}
        self.progress = 0
        if username:
            userdata = anilistAPI.get_user_data(self.animeID, username)
            if userdata:
                self.startDate = userdata['startedAt']
                self.completeDate = userdata['completedAt']
                self.progress = userdata['progress']
        self.image.write_dates_text(self.startDate, self.completeDate, 15)
        return True

    def load_savedata(self, savedata, app):
        # Builds the image layers based on savedata
        for key in savedata:
            setattr(self, key, savedata[key])
        self.image.write_entry_number(self.number)
        tier = app.tierChoice['widget'].itemText(self.tierIndex)
        tierColor = app.tierChoice['widget'].itemData(self.tierIndex)
        self.image.write_entry_tier(tier, tierColor)
        self.image.write_entry_requirement(self.requirement)
        if self.title:
            self.image.write_title_text(self.title)
            self.image.open_image(self.imageLink)
            self.image.write_duration_text(self.minimumTime, self.episodeCount,
                                           self.episodeDuration, 15)
            self.image.write_dates_text(self.startDate, self.completeDate, 15)


class animeImage:
    # A class to save and work all the image part of the data.
    def __init__(self, baseColor, borderColor):
        self.empty = Image.new('RGBA', (310, 540), (0, 0, 0, 0))
        self.base = round_rectangle((310, 540), 10, baseColor)
        self.glowfill = self.empty.copy()
        self.glow = self.empty.copy()
        self.build_border(borderColor, baseColor)
        self.image = self.empty.copy()
        self.icons = self.empty.copy()
        # Location of the font files for the text based imagelayers
        self.fontPath = RESOURCES_FONT_PATH + 'Proxima\\Regular.otf'
        self.fontPathBold = RESOURCES_FONT_PATH + 'Proxima\\Bold.otf'
        # Text based imagelayers
        self.number = self.empty.copy()
        self.tier = self.empty.copy()
        self.requirement = self.empty.copy()
        self.title = self.empty.copy()
        self.dates = self.empty.copy()
        self.duration = self.empty.copy()

    def open_image(self, url):
        # Loads the image from the anilist server
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
        # Builds a border around the anime image
        border = round_rectangle((240, 330), 5, borderColor)
        fill = Image.new('RGBA', (230, 320), fillColor)
        self.border = self.empty.copy()
        self.border.paste(border, (35, 35), border)
        self.border.paste(fill, (40, 40))

    def build_glow(self, color,  radius):
        # Builds a glow around the border
        alpha = self.empty.copy()
        radiusHalved = radius//2
        box = round_rectangle((240 + radius, 330 + radius),
                              5 + radiusHalved, 'green')
        alpha.paste(box, (35 - radiusHalved, 35 - radiusHalved))
        blur = alpha.filter(ImageFilter.GaussianBlur(radiusHalved))
        alpha = blur.split()[-1]
        self.glow = Image.new('RGBA', alpha.size, (color))
        self.glow
        self.glow.putalpha(alpha)

    def add_icon(self, name, position):
        # Adds an icon at the requested position
        newIcon = Image.open(RESOURCES_IMAGE_PATH + name.lower() + '.png')
        newIcon = newIcon.resize((30, 30))
        self.icons.paste(newIcon, position)

    def write_entry_number(self, number, fontSize=20):
        # Builds the number layer
        self.number = self.empty.copy()
        font = ImageFont.truetype(self.fontPathBold, fontSize)
        textSize = font.getsize(number)
        x = 40 - textSize[0]//2
        y = 358 - textSize[1]//2
        self.number = draw_text(self.number, number, x, y, font, outline=3)

    def write_entry_tier(self, tier, color='white', fontSize=20):
        # Builds the tier layer
        self.tier = self.empty.copy()
        if tier == '':
            return
        font = ImageFont.truetype(self.fontPathBold, fontSize)
        # Get text size with a margin of 3 pixels in all directions
        textSize = tuple(map(sum, zip(font.getsize(tier), (6, 6))))
        txtimg = Image.new('RGBA', textSize, (0, 0, 0, 0))
        txtimg = draw_text(txtimg, tier, 3, 3, font,
                           textColor=color, outline=3)
        txtimg = txtimg.rotate(30, resample=Image.BICUBIC, expand=1)
        x = 265 - txtimg.size[0]//2
        y = 350 - txtimg.size[1]//2
        self.tier.paste(txtimg, (x, y), txtimg)

    def write_entry_requirement(self, text, fontSize=15):
        # Builds the requirement layer
        self.requirement = self.empty.copy()
        maxWidth = 270
        maxHeight = 40
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath=self.fontPathBold)
        textSize = font.getsize_multiline(text, spacing=0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 385
        self.requirement = draw_text(
            self.requirement, text, x, y, alignment='center', outline=1,
            font=font, textColor='white', shadowColor='black')

    def write_title_text(self, text, fontSize=20):
        # Builds the title text layer
        self.title = self.empty.copy()
        maxWidth = 270
        maxHeight = 40
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath=self.fontPathBold)
        textSize = font.getsize_multiline(text, spacing=0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 435 + (maxHeight - textSize[1])//2
        self.title = draw_text(
            self.title, text, x, y, alignment='center', outline=2,
            font=font, textColor='white', shadowColor='black')

    def write_dates_text(self, startDate, completeDate, fontSize=15):
        # Builds the dates layer
        start = 'Start: {day}/{month}/{year}'
        if startDate['day']:
            if datetime.datetime.now().year == startDate['year']:
                startDate['year'] = ''
                # Omits the year if the show was started this year.
        else:
            startDate['day'] = startDate['month'] = '??'
            startDate['year'] = ''
        start = start.format(**startDate).rstrip('/') + '   '

        end = 'End: {day}/{month}/{year}'
        if completeDate['day']:
            if (
                startDate['year'] == ''
                and datetime.datetime.now().year == completeDate['year']
            ):  # Only omit year we omitted start year and it's current year.
                completeDate['year'] = ''
        else:
            completeDate['day'] = completeDate['month'] = '??'
            completeDate['year'] = ''
        end = end.format(**completeDate).rstrip('/')
        text = start + end

        self.dates = self.empty.copy()

        # Set geometry
        maxWidth = 270
        maxHeight = 15
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath=self.fontPath)
        textSize = font.getsize_multiline(text, spacing=0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 485 + (maxHeight - textSize[1])//2
        # Write text
        self.dates = draw_text(self.dates, text, x, y, alignment='center',
                               outline=0, font=font, textColor='white',
                               shadowColor='black')

    def write_duration_text(self, minTime, epCount, epDuration, fontSize=15):
        # Builds the duration layer
        # Clear previous text
        self.duration = self.empty.copy()
        # Build text
        text = ''
        if minTime:
            text = 'Min: {} | '.format(minTime)
        text += 'Total: '
        if epCount and epCount > 1:
            text += '{}x'.format(epCount)
        if epDuration:
            text += '{} mins'.format(epDuration)
        # Set geometry
        maxWidth = 270
        maxHeight = 15
        text, font = text_fitter(maxWidth, maxHeight, text, fontSize,
                                 fontPath=self.fontPath)
        textSize = font.getsize_multiline(text, spacing=0)
        x = 20 + (maxWidth - textSize[0])//2
        y = 505 + (maxHeight - textSize[1])//2
        # Write text
        self.duration = draw_text(self.duration, text, x, y,
                                  alignment='center', outline=0, font=font,
                                  textColor='white', shadowColor='black')

    def build_full_image(self):
        # Pastes all layers into a final image and returns it.
        full = Image.alpha_composite(self.base, self.glow)
        full.paste(self.border, (0, 0), self.border)
        full.paste(self.image, (0, 0), self.image)
        full.paste(self.icons, (0, 0), self.icons)
        full.paste(self.number, (0, 0), self.number)
        full.paste(self.tier, (0, 0), self.tier)
        full.paste(self.requirement, (0, 0), self.requirement)
        full.paste(self.title, (0, 0), self.title)
        full.paste(self.dates, (0, 0), self.dates)
        full.paste(self.duration, (0, 0), self.duration)
        return(full)


def text_fitter(maxWidth, maxHeight, text, fontSize, fontPath, spacing=0):
    # Resizes a text until it fits the requested width and height
    font = ImageFont.truetype(fontPath, fontSize)
    textsize = font.getsize_multiline(text, spacing=spacing)
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
                return text_fitter(maxWidth, maxHeight, text,
                                   fontSize - 1, fontPath)
            line = line.strip()
            lines += line + '\n'
            line = word + ' '
            lineWidth = wordWidth
    text = lines + line.strip()
    return text, font


def draw_text(image, text, x, y, font, textColor='white', shadowColor='black',
              outline=0, alignment='left', spacing=0):
    # Draws the text on the image with a potential outline
    draw = ImageDraw.Draw(image)

    for flow in range(outline, outline+1):
        for shift in range(-flow, flow+1):
            draw.multiline_text((x+shift, y+(flow-abs(shift))), text,
                                font=font, fill=shadowColor, align=alignment)
            draw.multiline_text((x+shift, y-(flow-abs(shift))), text,
                                font=font, fill=shadowColor, align=alignment)

    draw.multiline_text((x, y), text, font=font, fill=textColor, align=alignment)

    return(image)


def round_corner(radius, fill):
    # Draws a round corner
    corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rectangle(size, radius, fill):
    # Draws a rounded rectangle
    width, height = size
    rectangle = Image.new('RGBA', size, fill)
    corner = round_corner(radius, fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle