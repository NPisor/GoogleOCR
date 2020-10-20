# -*- coding: utf-8 -*-

from __future__ import print_function
import cv2 as cv
import os
import numpy as np
from google.cloud import vision
import io
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter import Tk, Label
from tkinter import ttk
from tkinter import filedialog
import database

name = input("What is your username?: ")
password = input("What is your password?: ")

user = database.checkUser(name, password)
if user == False:
    createUser = input("User not recognized. Would you like to create a new user? (Admin Privileges Required)")
    if(createUser == "yes"):
        name = input("What is the admin password?: ")
        adminCheck = database.checkUser("admin", name)
        if adminCheck == False:
            print("Incorrect password. Exiting.")
            exit()
        elif adminCheck == True:
            name = input("What is your username?: ")
            password = input("What is your password?: ")
            database.addUser(name, password)
elif user == True:
    print("User authenticated. Access Granted.")



# Point to location of JSON file containing Google Authentication for Google Vision API

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googleauth.json"

def detect_document(path):

    # Initialize Google Vision client

    client = vision.ImageAnnotatorClient()
    print("Initializing Google Client:  " + str(client))

    # Take in image passed through detect_document function as path and pass to Numpy

    img = cv.imread(path)

    # Create dictionary of English to Japanese Language conversions

    translate = {'日':'a', '本':'b', 'c':'あ','d':'い','e':'う','f':'え', 'g':'お', 'h':'か', 'i':'き', 'j':'く', 'k':'け', 'l':'こ', 'm':'さ','n':'し','o':'す', 'p':'せ', 'q':'そ', 'r':'が','s':'ぎ',
                 't':'ぐ','u':'げ', 'w':'ご','x':'ぱ', 'y':'ぴ', 'z':'ぷ', '0':'高', '1':'金', '2':'手', '3': '市', '4':'力', '5':'米', '6':'合', '7':'二', '8':'下', '9':'八'}

    # Set font parameters for OpenCV text

    font_size = 36
    font_color = (0, 0, 0)

    # Convert passed image to numpy array to pass into OpenCV

    im = Image.fromarray(img)

    # Draw image to screen

    draw = ImageDraw.Draw(im)
    unicode_font = ImageFont.truetype("arial.ttf",font_size)
    english = ImageFont.truetype("PAPYRUS.ttf", font_size)

    # Open image in Google Vision client to prepare for processing

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Create response variable to signify handwriting detection module with Japanese Language Hint

    response = client.document_text_detection(image=image, image_context = {"language_hints": ["ja"]})

    # Loop through pages, blocks of text, paragraphs, and words to reach symbols(characters) for processing and display

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:

                        # Draw bounding box at given vertices as noted by Google Vision API

                        draw.rectangle(((symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[0].y),(symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[2].y)))

                        # Draw text at corresponding bounding box as found by GVAPI

                        draw.text((symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[0].y - 45),
                                  symbol.text, font=english, fill=font_color)

                        # Check to see if given character is either a key or value in "translate" dictionary and print to console conversion

                        if translate.__contains__(symbol.text):
                            original = symbol.text
                            symbol.text = translate[original]
                            print(original + " converted to: " + symbol.text)
                        elif symbol.text in translate.values():
                            symbol.text = list(translate.keys())[list(translate.values()).index(symbol.text)]
                            print(translate[symbol.text] + " converted to: " + symbol.text)

                        # Draw text for symbols designated as values in dictionary

                        draw.text((symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[0].y+75), symbol.text, font=unicode_font, fill=font_color)

    # Convert numpy array back to OpenCV format

    imcv = np.asarray(im)[:, :, ::-1].copy()

    # Write image to file for display in TKinter Window

    cv.imwrite("testComplete.jpg", imcv)
    cv.waitKey(0)


# -----------------------------------------------------------------------------------------------------------------------

class Root(Tk):

    # Create TKinter window with button to locate file to translate

    def __init__(self):
        super(Root, self).__init__()
        self.title("IST 440W OCR Cipher")
        self.minsize(1000, 900)

        self.labelFrame = ttk.LabelFrame(self, text = "Open File to Encrypt/Decrypt:")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)

        lmain = Label(self.labelFrame)
        lmain.grid()


        self.button()



    def button(self):
        self.button = ttk.Button(self.labelFrame, text = "Browse...",command = self.fileDialog)
        self.button.grid(column = 1, row = 1)


    # After choosing file, run detect_document function on given file and pass saved image to Tkinter for display

    def fileDialog(self):

        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("jpeg files","*.jpg"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 3)
        self.label.configure(text = self.filename)
        detect_document(self.filename)
        image = "testComplete.jpg"
        img = Image.open(image)
        img = img.resize((800, 800), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = Label(image=img)
        panel.image = img
        panel.place(relheight=1, relwidth=1, relx=0, rely=0)

root = Root()
root.mainloop()

