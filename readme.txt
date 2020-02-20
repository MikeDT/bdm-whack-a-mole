Instructions
============

Open the main.py script and execute in a IDE, or use a python3.7 version to execute i.e. from the 
command line type 'python37 main.py' (assuming python37 is linked to your python 3.7 environment)

The programme has been developed to avoid the need to alter the raw code, with configuration possible for most tasks
by adjusting the offline configuration (see file and folder structure etc. below for more detail)

Files
=====

1. main.py: the main python file that supports execution of the programme

2. Primary_GUI: the moduile that contains the Primary_GUI class (the bulk of the code)

3. readme.txt: this file

4. .gitattributes: ignore, only relevant for github interaction

Folder Structure
================

1. __pycache__: ui cache, should be ignored

2. config: contains both the 'config.txt' file which dictates the maximum and required number of trials per participant
 to enable adjustment of the experiment process without altering the code (e.g. if you want to support a second marble
selection to see if people adjust their expectations of the urns with new information.  Also contains the 
'condition_combo_file_master.txt' file which contains all the condition combinations.  Should an experimenter want to
alter the conditions and extend this file would be amended.  The format is

(random urn side i.e. 0 or 1, urn marble count, red marbles, blue marbles) e.g.
(0, 2, 2, 0) denotes a left random urn, with 2 marbles, both of which are red

checks exist within the code to ensure the total marble count is valid, should a new combo be added a new image would
also be required

3. current_state: contains the file 'condition_combo_file_dynamic.txt' which governs the current state of the trial, 
i.e. which condition (2/10/100 marbles) and where the random urn should be (left/0 or right/1)

4. images: contains the .png image files for the gui front/splash screen and the grey/colour urn images.  NB if adding
new images for the urns they must be .png and should be of the name scheme below -

    colour/grey + _ + 5050/random + _ + condition(i.e. number of marbles).  e.g. colour_5050_100.png

5. results: contains the results csv database file, 'csv_results_db.csv'

6. text: contains teh raw text for the introduction, disclaimer, instructions and debrief screen

7. ui: contains the Qt Designer developed 'Screen.ui' file

8. pptx: powerpoint slides with the relevant images, to enable a user to extend the images base as required