import numpy as np
import cv2
from mtgsdk import Card
import urllib
import _pickle as pickle
import os
import scanner

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

file_path = "data/CardDatabase.cdb"

class CardDatabase:
    cards = None
    dictionary = None
    di = None
    card_art_max_distance = 100
    empty = None
    empty_max_distance = 50

    def __init__(self, app_output=None, text_output=None):
        try:
            self = pickle.load(open(file_path, "rb"))
            if self.di is None:
                print("loaded card database")
            else:
                self.download(app=app_output, text=text_output)
        except:
            self.save_empty()
            self.download(text=text_output)

    def download(self, app=None, text=None):
        # make data folder if it doesn't exist already
        os.makedirs("data", exist_ok=True)

        # if dictionary index is None, download Magic the Gathering card data
        if self.di is None:
                if text is not None and app is not None:
                    text.value = "downloading cards..."
                    app.update()
                print("downloading cards...")
                self.cards = Card.all()
                self.di = 0
                self.dictionary = {}
                pickle.dump(self, open(file_path, "wb"), -1)

        # loop through all cards
        if text is not None and app is not None:
            text.value = "downloading images and generating dictionary..."
            app.update()
        print("downloading images and generating dictionary...")
        total = len(self.cards)
        while self.di < total:
            c = self.cards[self.di]
            if text is not None and app is not None:
                text.value = "{}/{}: {}/{}".format(self.di, total, c.set, c.name)
                app.update()
            print("{}/{}: {}/{}".format(self.di, total, c.set, c.name))

            # make a folder for the current card's set if it doesn't exist already
            filename = "data/{}/{}{}.jpg".format(c.set, c.name, c.multiverse_id)
            if not os.path.exists(os.path.dirname(filename)):
                directory = os.path.dirname(filename)
                os.makedirs(directory, exist_ok=True)

            # if the card's image has already been downloaded, add it to the dictionary using its art's hash as a key
            if os.path.isfile(filename):
                if text is not None and app is not None:
                    text.value += " : file exists"
                    app.update()
                print("  file exists")
                image = cv2.imread(filename)
                self.dictionary[dhash(image[37:172, 20:204])] = self.di
                self.di += 1
                if self.di % 50 is 0:
                    pickle.dump(self, open(file_path, "wb"), -1)
                continue

            # if the card's image is not available, skip it
            if c.image_url is None:
                if text is not None and app is not None:
                    text.value += " : image N/A"
                    app.update()
                print("  image N/A")
                self.di += 1
                continue

            # keep trying to download the card's image until successful, adding it to the dictionary using its art's
            # hash as a key when done
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
                        if text is not None and app is not None:
                            text.value += " : retrying @ " + c.image_url
                            app.update()
                        print("  " + c.image_url)
                        print("  retrying...")

        # set di to None to denote completion and then save everything
        self.di = None
        pickle.dump(self, open(file_path, "wb"), -1)
        if text is not None and app is not None:
            text.value = "saved dictionary"
            app.update()
        print("saved dictionary")


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
        return distance < self.empty_max_distance

    def get_card(self, image):
        # calculate the hash value of the card art
        hash = dhash(image)
        matches = []

        # search through the dictionary and add cards that have a
        # hamming distance less than the card_art_max_distance to
        # the list of matches
        for key, value in self.dictionary.items():
            if hamming_dist(hash, key) <= self.card_art_max_distance:
                matches.append((d, cards[value]))

        # if there are matches, return the closest one
        if len(matches) > 0:
            matches.sort()
            return matches[0]

        return None