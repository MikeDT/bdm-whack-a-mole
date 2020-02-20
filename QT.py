# -*- coding: utf-8 -*-
"""
main
====

Typical GUI screen, adapted from prior pyqt work

Attributes:
    na

Todo:
    * clean up docstrings (ideally to sphinx format, but to numpy/scipy
    minimally)

Related projects:
    Adapted from initial toy project https://github.com/sonlexqt/whack-a-mole
    which is under MIT license

@author: DZLR3
"""

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import pickle
import sys
from os import listdir
from wam.game import GameManager
import pygame
from time import time


class QT_Basic(QtWidgets.QMainWindow):
    def __init__(self, ui_file_loc, *args, **kwargs):
        super().__init__(*args, **kwargs)        # QT GUI
        self.ui_file_loc = ui_file_loc
        self.window = uic.loadUi(self.ui_file_loc, self)

        self.tab_count = self.window.tabs.count()

        # Default button hide conditions (lists so appendable)
        self.next_btn_hide_tabs = [self.tab_count - 1]
        self.back_btn_hide_tabs = [0]

    def back_button_clicked(self):
        """
        Dictates the actions for clicking the back button on a given screen
        using the screen_fxn_dict dictionary that houses the screen dispay
        functions
        """
        self.window.tabs.setCurrentIndex(self.window.tabs.currentIndex() - 1)
        self.window.next_btn.show()
        self.window.back_btn.show()
        if self.window.tabs.currentIndex() in self.back_btn_hide_tabs:
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
        if self.window.tabs.currentIndex() in self.next_btn_hide_tabs:
            self.window.next_btn.hide()

    def refresh_nav_buttons(self):
        """
        Refreshs the navigation buttons upon tab clicks to ensure only the
        relevant buttons are shown
        """
        if self.window.tabs.currentIndex() in self.back_btn_hide_tabs:
            self.window.next_btn.show()
            self.window.back_btn.hide()
        elif self.window.tabs.currentIndex() in self.next_btn_hide_tabs:
            self.window.next_btn.hide()
            self.window.back_btn.show()
        else:
            self.window.next_btn.show()
            self.window.back_btn.show()

    def set_combo_types(self, combobox, valid_list):
        for item in valid_list:
            combobox.addItem(item)


class QT_Config(QT_Basic):

    def __init__(self, *args, **kwargs):
        QT_Basic.__init__(self, 'ui\\QT_Config.ui', *args, **kwargs)
        # Import the QT designer UI and name the window
        self.setWindowTitle('BDM Whack-A-Mole')
        self.file_config_loc = 'config\\master_dict.pkl'
        self.save_dict = {}

        # Connect the buttons and tabs to the relevant functions
        self.window.back_btn.clicked.connect(self.back_button_clicked)
        self.window.next_btn.clicked.connect(self.next_button_clicked)
        self.window.save_btn.clicked.connect(self.save_button_clicked)
        self.window.load_btn.clicked.connect(self.load_button_clicked)
        self.window.tabs.currentChanged.connect(self.refresh_nav_buttons)

        # Import the configuration
        self.set_config_dict()
        self.populate_main_game(self.master_dict['main_game'])

        # Set the default visibility for the nav buttons and show the screen
        self.window.back_btn.hide()
        self.window.error_textbox.hide()

        # Set the combo box valid values
        self.set_combo_types(self.window.score_type, ['Normal',
                                                      'lin_dist_skill',
                                                      'nonlin_dist_skill'])
        self.set_combo_types(self.window.adj_type, ['rnd_wlk_neg',
                                                    'rnd_wlk_pos',
                                                    'static', 'design'])
        self.set_combo_types(self.window.hit_type, ['Standard',
                                                    'Binomial'])
        self.set_combo_types(self.window.stage_type, ['Standard',
                                                      'Attempts'])
        self.set_combo_types(self.window.drift_type, ['static',
                                                      'dynamic'])
        self.window.show()

    def load_button_clicked(self):
        self.file_config_loc = self.window.cond_set_file_path.text()
        try:
            self.set_config_dict()
            self.populate_main_game(self.master_dict['main_game'])
        except IOError:
            print('File not found, make sure to use the format c:\\path\\..')

    def set_config_dict(self):
        self.master_dict = pickle.load(open(self.file_config_loc, 'rb'))

    def populate_conditions_meta(self, cond_meta_dict):
        # Screen Setup
        self.window.cond_set_name.setText(str(cond_meta_dict['cond_set_name']))
        self.window.cond_set_user.setText(str(cond_meta_dict['cond_set_user']))
        self.window.cond_set_notes.setText(str(cond_meta_dict[
                                            'cond_set_notes']))

    def populate_main_game(self, main_game_dict):
        # Screen Setup
        self.window.screen_width.setText(str(main_game_dict['SCREEN_WIDTH']))
        self.window.screen_height.setText(str(main_game_dict['SCREEN_HEIGHT']))
        self.window.comm_bar_height.setText(str(main_game_dict[
                                            'COMM_BAR_HEIGHT']))
        self.window.twobytwo_len.setText(str(main_game_dict['TWO_X_TWO_LEN']))
        self.window.twobytwo_x.setText(str(main_game_dict['TWO_X_TWO_LOC'][0]))
        self.window.twobytwo_y.setText(str(main_game_dict['TWO_X_TWO_LOC'][1]))
        self.window.font_size.setValue(main_game_dict['FONT_SIZE'])
        # Animation Setup
        self.window.fps.setValue(main_game_dict['FPS'])
        self.window.mole_width.setValue(main_game_dict['MOLE_WIDTH'])
        self.window.mole_height.setValue(main_game_dict['MOLE_HEIGHT'])
        self.window.post_whack_interval.setValue(main_game_dict[
                                                 'post_whack_interval'])
        self.window.mole_pause_interval.setValue(main_game_dict[
                                                 'mole_pause_interval'])
        self.window.animation_interval.setValue(main_game_dict[
                                                 'animation_interval'])
        self.window.mole_down_interval.setValue(main_game_dict[
                                                 'mole_down_interval'])
        # Stage setup
        self.window.stage_score_gap.setValue(main_game_dict['STAGE_SCORE_GAP'])
        self.window.stages.setValue(main_game_dict['stages'])
        self.window.stage_length.setValue(main_game_dict['stage_length'])
        self.window.stage_type.setCurrentText(main_game_dict['stage_type'])
        self.window.demo_2.setChecked(main_game_dict['demo'])
        self.window.demo_len.setValue(main_game_dict['demo_len'])
        self.window.update_delay.setValue(main_game_dict['update_delay'])
        self.window.feedback_limit.setValue(main_game_dict['feedback_limit'])
        self.window.feedback.setChecked(main_game_dict['FEEDBACK'])
        self.window.stage_time_change.setChecked(main_game_dict[
                                                 'stage_time_change'])
        # Mole hits and scoring
        self.window.mole_radius.setValue(main_game_dict['MOLE_RADIUS'])
        self.window.margin_start.setValue(main_game_dict['MARGIN_START'])
        self.window.drift_type.setCurrentText(main_game_dict['drift_type'])
        self.window.hit_type.setCurrentText(main_game_dict['hit_type'])
        self.window.adj_type.setCurrentText(main_game_dict['adj_type'])
        self.window.score_type.setCurrentText(main_game_dict['score_type'])

    @property
    def save_check(self):
        return True, 'No Errors'

    def save_button_clicked(self):
        self.fill_condition_meta_dict()
        self.fill_main_game_dict()
        can_save, errors = self.save_check
        if can_save:
            self.save()
        else:
            self.window.error_textbox.setText(errors)

    def save(self):
        file_path = (self.save_folder_path.text() + '\\' +
                     self.window.cond_set_name.text() +
                     '.pkl')
        with open(file_path, 'wb') as f:
            pickle.dump(self.save_dict, f)
            self.window.error_textbox.setText('File Saved Succesfully')

    def fill_condition_meta_dict(self):
        tmp = {'cond_set_name': (self.window.cond_set_name.text()),
               'cond_set_user': (self.window.cond_set_user.text()),
               'cond_set_notes': (self.window.cond_set_notes.toPlainText())}
        self.save_dict['conditions_meta'] = tmp

    def fill_main_game_dict(self):
        tmp = {  # Screen Setup
               'SCREEN_WIDTH': int(self.window.screen_width.text()),
               'SCREEN_HEIGHT':  int(self.window.screen_height.text()),
               'COMM_BAR_HEIGHT':  int(self.window.comm_bar_height.text()),
               'TWO_X_TWO_LEN':  int(self.window.twobytwo_len.text()),
               'TWO_X_TWO_LOC': (int(self.window.twobytwo_x.text()),
                                 int(self.window.twobytwo_y.text())),
               'FONT_SIZE': int(self.window.font_size.value()),
               # Animation Setup
               'FPS': self.window.fps.value(),
               'MOLE_WIDTH': self.window.mole_width.value(),
               'MOLE_HEIGHT': self.window.mole_height.value(),
               'post_whack_interval': self.window.post_whack_interval.value(),
               'mole_pause_interval': self.window.mole_pause_interval.value(),
               'animation_interval': self.window.animation_interval.value(),
               'mole_down_interval': self.window.mole_down_interval.value(),
               # Stage setup
               'STAGE_SCORE_GAP': self.window.stage_score_gap.value(),
               'stages': self.window.stages.value(),
               'stage_length': self.window.stage_length.value(),
               'stage_type': self.window.stage_type.currentText(),
               'demo': self.window.demo_2.isChecked(),
               'demo_len': self.window.demo_len.value(),
               'update_delay': self.window.update_delay.value(),
               'feedback_limit': self.window.feedback_limit.value(),
               'FEEDBACK': self.window.feedback.isChecked(),
               'stage_time_change': self.window.stage_time_change.isChecked(),
               # Mole hits and scoring
               'MOLE_RADIUS': self.window.mole_radius.value(),
               'MARGIN_START': self.window.margin_start.value(),
               'drift_type': self.window.drift_type.currentText(),
               'hit_type': self.window.hit_type.currentText(),
               'adj_type': self.window.adj_type.currentText(),
               'score_type': self.window.score_type.currentText()}
        self.save_dict['main_game'] = tmp


class QT_GUI(QT_Basic):

    def __init__(self, *args, **kwargs):
        QT_Basic.__init__(self, 'ui\\QT_Screen.ui', *args, **kwargs)

        # File locations
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
        self.set_combo_types(self.window.gender_combobox, ['',
                                                           'Prefer Not To Say',
                                                           'Female',
                                                           'Male',
                                                           'Other'])
        self.set_combo_types(self.window.edu_combobox, ['',
                                                        'High School',
                                                        'Bachelors',
                                                        'Masters',
                                                        'PhD',
                                                        'Other'])

        # Connect the buttons and tabs to the relevant functions
        self.window.back_btn.clicked.connect(self.back_button_clicked)
        self.window.next_btn.clicked.connect(self.next_button_clicked)
        self.window.next_btn.clicked.connect(self.show_launch_check)
        self.window.next_btn.clicked.connect(self.show_save_check)
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

    def set_cond_all(self):
        """
        tbc
        """
        pass

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
        if (
            self.window.consent_checkbox.isChecked() *
            (self.launched is False) *
            self.window.tabs.currentIndex() == 3
           ):
            self.window.launch_btn.show()
        else:
            self.window.launch_btn.hide()

    def show_save_check(self):
        """
        Check whether the save button should be shown, based upon the
        completion of all the relevant criteria (consent, demographics, test)
        """
        if (
            self.window.consent_checkbox.isChecked() *
            self.launched *
            self.window.tabs.currentIndex() == 4
           ):
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
