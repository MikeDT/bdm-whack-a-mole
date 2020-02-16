# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 13:23:25 2019

@author: DZLR3
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import random
import sys
from os import listdir
from wam.game import GameManager
import pygame
from time import time



class QT_GUI(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # File locations
        self.ui_file_loc = 'ui\\QT_Screen.ui'
        self.intro_text_file_loc = 'text\\Introduction.txt'
        self.disclaimer_text_file_loc = 'text\\Disclaimer.txt'
        self.instruct_text_file_loc = 'text\\Instructions.txt'
        self.debrief_text_file_loc = 'text\\Debrief.txt'

        # Import the QT designer UI and name the window
        self.window = uic.loadUi(self.ui_file_loc, self)
        self.setWindowTitle('BDM Whack-A-Mole')

        # Import images & set front screen image
        self.pixmap_dict = {}
        self.set_image_dict()
        self.window.front_screen.setPixmap(self.pixmap_dict["Front_Screen"])

        # Adjust the combobox content to support the valid values
        self.set_gender_types()
        self.set_edu_types()

        # Connect the buttons and tabs to the relevant functions
        self.window.back_btn.clicked.connect(self.back_button_clicked)
        self.window.next_btn.clicked.connect(self.next_button_clicked)
        self.window.launch_btn.clicked.connect(self.launch_button_clicked)
        self.window.save_btn.clicked.connect(self.save_button_clicked)
        self.window.tabs.currentChanged.connect(self.refresh_nav_buttons)
        self.window.tabs.currentChanged.connect(self.check_disclaimer_nav)
        
        # Open the 'database' table, set relevant file loc
        self.csv_user_log_db = open('logs\\csv_user_log_db.csv', 'a')

        # Import all the text from external sources (simplifies future changes)
        # adjust with the appropriate text and fill the text boxes
        # and set to read only to prevent user edits
        self.get_set_text()

        # Set the default visibility for the nav buttons and show the screen
        self.launched = False
        self.window.back_btn.hide()
        self.window.launch_btn.hide()
        self.window.save_btn.hide()
        self.window.error_textbox.hide()
        self.window.show()

    def set_image_dict(self):
        """
        Import and set the images for the urns into the pixmap_dict dictionary
        for importing into the gui.
        """
        files = listdir('images')
        for file in files:
            if file == 'Front_Screen.png':
                pixmap = QPixmap('images\\' + file)
                pixmap = pixmap.scaled(1001, 811,
                                       Qt.KeepAspectRatio,
                                       Qt.SmoothTransformation)
                self.pixmap_dict['Front_Screen'] = pixmap
            else:
                print('FYI - Non png file detected in image folder - ', file)

    def set_gender_types(self):
        """
        Sets the gender types for the combobox.  Presumed to be relatively
        static, but could be altered to support imports for more non-code
        adjustability
        """
        gender_list = ['', 'Prefer Not To Say', 'Female', 'Male', 'Other']
        for gender in gender_list:
            self.window.gender_combobox.addItem(gender)

    def set_edu_types(self):
        """
        Sets the education types for the combobox.  Presumed to be relatively
        static, but could be altered to support imports for more non-code
        adjustability
        """
        education_list = ['', 'High School', 'Bachelors', 'Masters', 'PhD',
                          'Other']
        for education in education_list:
            self.window.edu_combobox.addItem(education)

    def set_cond_all(self):
        """
        tbc
        """
        pass

    def back_button_clicked(self):
        """
        Dictates the actions for clicking the back button on a given screen
        using the screen_fxn_dict dictionary that houses the screen dispay
        functions
        """
        self.window.tabs.setCurrentIndex(self.window.tabs.currentIndex() - 1)
        self.window.next_btn.show()
        self.window.back_btn.show()
        self.window.launch_btn.hide()
        if self.window.tabs.currentIndex() == 0:
            self.window.back_btn.hide()

    def next_button_clicked(self):
        """
        Dictates the actions for clicking the next button on a given screen
        using the screen_fxn_dict dictionary that houses the screen dispay
        functions
        """
        self.window.tabs.setCurrentIndex(self.window.tabs.currentIndex() + 1)
        self.window.next_btn.show()
        self.window.back_btn.show()
        if self.window.tabs.currentIndex() == 3:
            self.window.next_btn.hide()
            self.show_launch_check()
        if self.window.tabs.currentIndex() == 4:
            self.window.next_btn.hide()
            self.show_save_check()

    def check_disclaimer_nav(self):
        """
        Ensures navigation cannot happen past the  disclaimer screen unless
        consent has been provided via the consent_checkbox
        """
        if self.window.consent_checkbox.isChecked() is False:
            if self.window.tabs.currentIndex() > 1:
                self.window.tabs.setCurrentIndex(1)
                self.window.launch_btn.hide()
                self.window.back_btn.show()
                self.window.next_btn.show()
                self.refresh_nav_buttons()
            else:
                self.refresh_nav_buttons()
        else:
            self.refresh_nav_buttons()

    def refresh_nav_buttons(self):
        """
        Refreshs the navigation buttons upon tab clicks to ensure only the
        relevant buttons are shown
        """
        if self.window.tabs.currentIndex() == 0:
            self.window.launch_btn.hide()
            self.window.back_btn.hide()
        elif self.window.tabs.currentIndex() == 3:
            self.show_launch_check()
            self.window.next_btn.hide()
            self.window.back_btn.show()
        else:
            self.window.next_btn.show()
            self.window.back_btn.show()
            self.show_debrief_check()
            self.window.launch_btn.hide()

    def check_task_complete(self):
        """
        Checks all activities, demographics etc have been submitted prior to
        allowing the participant to save and exit.  Should tasks not be
        complete an error message will be supplied to the user detailing
        the issue(s)
        """
        complete = True
        error_message = 'The following errors are preventing saving: '

        # Check all the required attributes have been captured
        if len(self.window.username_textbox.text()) > 0:
            complete *= True
        else:
            complete *= False
            error_message += 'username is blank, '
        if self.window.consent_checkbox.isChecked():
            complete *= True
        else:
            complete *= False
            error_message += 'consent was not provided, '
        if self.window.age_spinbox.value() > 17:
            complete *= True
        else:
            complete *= False
            error_message += 'must be an adult (18+) to participate, '
        if str(self.window.edu_combobox.currentText()) != '':
            complete *= True
        else:
            complete *= False
            error_message += 'education level was not provided, '
            print(self.window.edu_combobox.currentText())
        if str(self.window.gender_combobox.currentText()) != '':
            complete *= True
        else:
            complete *= False
            error_message += 'gender was not provided, '
            print(self.window.gender_combobox.currentText())

        return (complete, error_message)

    def get_save_details(self):
        """
        Get the all the details from the experiment (incl. demographics and
        consent), and cast them into a csv ready string, then return the
        content as a list
        """
        self.username = str(self.window.username_textbox.text())
        self.consent = str(self.window.consent_checkbox.isChecked())
        self.age = str(self.window.age_spinbox.value())
        self.education = str(self.window.edu_combobox.currentText())
        self.gender = str(self.window.gender_combobox.currentText())
        save_details = [(self.username + ', ' +
                         self.consent + ', ' +
                         self.age + ', ' +
                         self.education + ', ' +
                         self.gender)]
        return save_details

    def show_launch_check(self):
        """
        Check whether the save button should be shown, based upon the
        completion of all the relevant criteria (consent, demographics, test)
        """
        if self.window.consent_checkbox.isChecked():
            self.window.launch_btn.show()
        else:
            self.window.launch_btn.hide()

    def show_save_check(self):
        """
        Check whether the save button should be shown, based upon the
        completion of all the relevant criteria (consent, demographics, test)
        """
        if (self.window.consent_checkbox.isChecked() * self.launched):
            self.window.save_btn.show()
        else:
            self.window.save_btn.hide()

    def show_debrief_check(self):
        """
        Check whether the save button should be shown, based upon the
        completion of all the relevant criteria (consent, demographics, test)
        """
        if (self.window.consent_checkbox.isChecked() * self.launched):
            self.window.debrief_textbox.setText(self.debrief_text)

    def launch_button_clicked(self):
        """
        Saves the demographics to csv, closes the csv, sets the remaining
        random conditions in the batch and exits the application
        """
        self.launched = True
        self.launch_btn.hide()
        self.next_btn.show()
        self.launch_game()

    def launch_game(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.init()
        usr_timestamp = (str(self.window.username_textbox.text()) + '_' +
                         str(time()))
        # Run the main loop
        my_game = GameManager(usr_timestamp)
        my_game.play_game()
        # Exit the game if the main loop ends
        pygame.quit()

    def save_button_clicked(self):
        """
        Saves the demographics to csv, closes the csv, sets the remaining
        random conditions in the batch and exits the application
        """
        results = self.get_save_details()
        (validity, error_message) = self.check_task_complete()
        if validity:
            for result in results:
                self.csv_user_log_db.write(result)
                self.csv_user_log_db.write('\n')
            self.csv_user_log_db.close()
            sys.exit(QtWidgets.QApplication([]).exec_())
        else:
            self.window.error_textbox.show()
            self.window.error_textbox.setText(error_message)
            self.window.error_textbox.setReadOnly(True)

    def get_set_text(self):
        """
        Gets the text from the file locations and embeds it into the gui
        text boxs (made read only to prevent user edits)
        """
        self.intro_text = open(self.intro_text_file_loc, 'r').read()
        self.window.intro_textbox.setText(self.intro_text)
        self.window.intro_textbox.setReadOnly(True)
        self.disclaimer_text = open(self.disclaimer_text_file_loc, 'r').read()
        self.window.disclaimer_textbox.setText(self.disclaimer_text)
        self.window.disclaimer_textbox.setReadOnly(True)
        self.instruction_text = open(self.instruct_text_file_loc, 'r').read()
        self.window.instr_textbox.setText(self.instruction_text)
        self.window.instr_textbox.setReadOnly(True)
        self.debrief_text = open(self.debrief_text_file_loc, 'r').read()
        self.window.debrief_textbox.setText('Experiment not yet complete...')
        self.window.instr_textbox.setReadOnly(True)
