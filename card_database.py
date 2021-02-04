from guizero import App, Text
import numpy as np
import cv2
from mtgsdk import Card
import urllib
import _pickle as pickle
import os
import scanner

#region Card Database Summary

# This module creates a database of MTG card images and a .cbd
# file containing the data of each card, the hashes of each
# card's artwork, and the hash of an image of an empty tray as
# taken by the user before sorting.

# When initialized when no such file exists or prompted by
# the user, this module downloads an up to date list of cards
# using the mtgsdk module and then starts downloading each
# card image one by one from the wizards website and saving
# a hash of each card's artwork, assuming the artwork is
# spaced within the same dimensions [37:172, 20:204] on all
# cards. Artwork not limited by these dimensions such as full
# art, textless, and unhinged cards are ignored as accurately
# detecting the edges of these cards is not possible with the
# lighting conditions and overlapping edges of stacked cards.

# As this process takes an enormous amount of time, an index
# is saved within the .cdb file to keep track of where it left
# off so the next time this program is started, this process
# can be started again without needing to redownload any card
# images already added. Also, when updating this database
# to include new cards, all previously downloaded card images
# are used instead of redownloading them to further save time
# and bandwidth.

# Once this file is completed, this module can be used to find
# card data and to find the closest match by comparing artwork
# hashes. If the hamming distance, the number of bits different
# between both image hashes, between the artwork detected and
# any of the artworks within the database is less than or equal
# to 100, then the card with the shortest hamming distance is
# returned.

# Additionally, this same method of comparing hamming distances
# is used to detect an empty tray. Adjusting the camera or
# lighting can change the empty tray image hash. Thus, it is
# vitally important that the user retakes the empty picture
# before sorting cards to prevent an endless loop due to not
# detecting an empty tray.
#endregion


#region Constants and Variables

file_path = "data/CardDatabase.cdb"
card_art_max_distance = 100
empty_max_distance = 50
app_output = None
text_output = None
#endregion

#region Basic Functions

def app_print(output):
    # print to console
    print(output)

    # if outputs are valid, also change text and update app
    if app_output is App and text_output is Text:
        print("1")
        text_output.value = output
        app_output.update()
        print("2")

def dhash(image, hashSize=16):
    # convert the input image to grayscale then
    # resize it, adding a single column (width) so we
    # can compute the horizontal gradient
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(image, (hashSize + 1, hashSize))

    # compute the (relative) horizontal gradient between adjacent
    # column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

def hamming_dist(h1,h2):
    return bin(h1^h2).count('1')
#endregion


class CardDatabase:
    cards = None
    dictionary = {}
    di = None
    empty = None

    def __init__(self, app, text):
        app_output=app
        text_output=text

        # try to load Card Database file
        try:
            self = pickle.load(open(file_path, "rb"))

             # if dictionary index is None
            if self.di is None:
                # database is complete
                app_print("loaded card database")
            else:
                # continue download
                app_print("loaded incomplete card database")
                self.download()
        except:
            # if file doesn't load, take empty and start download
            self.save_empty()
            self.download()

    def download(self):
        # make data folder if it doesn't exist already
        os.makedirs("data", exist_ok=True)

        # if dictionary index is None, download Magic the Gathering card data
        if self.di is None:
            app_print("downloading cards...")
            self.cards = Card.all()
            print(".")
            self.di = 0
            pickle.dump(self, open(file_path, "wb"), -1)
            print(".")

        # loop through all cards
        app_print("downloading images and generating dictionary...")
        total = len(self.cards)
        while self.di < total:
            c = self.cards[self.di]
            out = "{}/{}: {}/{}".format(self.di, total, c.set, c.name)
            app_print(out)

            # make a folder for the current card's set if it doesn't exist already
            filename = "data/{}/{}{}.jpg".format(c.set, c.name, c.multiverse_id)
            if not os.path.exists(os.path.dirname(filename)):
                directory = os.path.dirname(filename)
                os.makedirs(directory, exist_ok=True)

            # if the card's image has already been downloaded, add it to the dictionary using its art's hash as a key
            if os.path.isfile(filename):
                app_print(out + " : file exists")
                image = cv2.imread(filename)
                self.dictionary[dhash(image[37:172, 20:204])] = self.di
                self.di += 1
                if self.di % 50 is 0:
                    pickle.dump(self, open(file_path, "wb"), -1)
                    app_print("saved card database")
                continue

            # if the card's image is not available, skip it
            if c.image_url is None:
                app_print(out + " : image N/A")
                self.di += 1
                continue

            # keep trying to download the card's image until successful, adding it to the dictionary using its art's
            # hash as a key when done and saving every 50 cards
            print_message = True
            while True:
                try:
                    urllib.request.urlretrieve(c.image_url, filename)
                    image = cv2.imread(filename)
                    self.dictionary[dhash(image[37:172, 20:204])] = self.di
                    self.di += 1
                    if self.di % 50 is 0:
                        pickle.dump(self, open(file_path, "wb"), -1)
                    break
                except:
                    if print_message:
                        print_message = False
                        app_print(out + " : retrying @ " + c.image_url)

        # set dictionary index to None to denote completion and then save everything
        self.di = None
        pickle.dump(self, open(file_path, "wb"), -1)
        app_print("saved dictionary")


    def save_empty(self):
        # take a picture of the empty tray and save it, then calculate
        # the hash value
        e = scanner.take_picture()
        cv2.imwrite("data/empty.jpg", e)
        self.empty = dhash(e)

        # save the database
        pickle.dump(self, open(file_path, "wb"), -1)

    def is_empty(self):
        # take a picture, then calculate the hash value, then find
        # the hamming difference between the current hash and the
        # saved hash of the empty tray
        p = scanner.take_picture()
        pic = dhash(p)
        distance = hamming_dist(self.empty, pic)

        # the tray is empty if the hamming distance is less than
        # the empty_max_distance
        return distance < empty_max_distance

    def get_card(self, image):
        # calculate the hash value of the card art
        hash = dhash(image)
        matches = []

        # search through the dictionary and add cards that have a
        # hamming distance less than the card_art_max_distance to
        # the list of matches
        for key, value in self.dictionary.items():
            d = hamming_dist(hash, key)
            if d <= card_art_max_distance:
                matches.append([d, value])

        # if there are matches, return the closest one
        if len(matches) > 0:
            matches.sort()
            return cards[matches[0][1]]

        return None
