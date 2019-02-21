import pandas as pd
import numpy as np
import string
import re
import os
import sys
import importlib

from functools import reduce

"""
Initally created by Stephen Lizcano. @stevelizcano on GitHub. 

MIT License.

This program loads the MIMICIII NOTEEVENTS and DIAGNOSES_ICD .csv files, extracts 'Discharge Summaries' from the Notes,
and matches them with the HADM_ID, or Hospital Admission ID, of the patients.

It drops any patient/note combos that have "NaNs" or missing data, or patients without an ICD9 diagnosis code.

It returns all three as a list that can then be used for Tokenization, etc.
"""


# Global vars
NOTE_LENGTHS = []
AVERAGE_NOTE_LENGTHS = 0
NUM_NOTES = 0

notes_filename = 'NOTEEVENTS.csv'
icd_filename = 'DIAGNOSES_ICD.csv'

def clean_note(note):
    '''
    This cleans the notes:
    1) uses translation to remove the punctuation, and replace it with nothing.
    2) the next part removes all new line carriages, tabs, and excess white space.
    3) returns cleaned string.

    ToDo: Examine replacing each [**First Name**] with fillers etc instead of removing brackets, creating uniformity
    '''

    if len(note.split()) < 5:
        print('PROBLEM: Low Length Note')
    NOTE_LENGTHS.append(len(note.split()))
    # Convert to lower case - do metrics and see what works?
    note = note.lower()
    translator = str.maketrans('', '', string.punctuation)
    note = note.translate(translator)

    #note = ' '.join(note.split())
    note = re.sub('\s+', ' ', note).strip()

    return note


def create_icd_array(discharge_notes, diag_icd):
    '''Create ICD Array: Creates list of icd codes, matched with a separate hospital admission id list
    Then looks through and creates a note list that can match and be tokenized later

    All three are then returned.

    '''
    # Items to be returned
    icd_list = []
    hadm_id_list = []
    notes_list = []

    # Create the df of discharge notes ***This used to have .dropna()!!!!
    df = discharge_notes['HADM_ID']
    print(len(df))

    prev_el = 1
    j = 0
    for el in df:

        icd_temp = []

        el = int(el)  # cast as int since notes for some reason has it as float
        df2 = diag_icd[diag_icd['HADM_ID'] == el]
        df2 = df2.dropna()

        # Get codes, save to hadm_list
        icd_temp = pd.Series.tolist(df2['ICD9_CODE'])
        #if len(icd_temp) == 0: print('length zero found' + str(el))

        # flag to check for duplicates
        if len(icd_temp) != 0 and prev_el != el and len(icd_temp) != 0:
            icd_list.append(icd_temp)
            hadm_id_list.append(el)
            #print('we good')

            # This needs to be investigated further. Some notes are returned as multi-dimensional lists
            notes_list.append(pd.Series.tolist(
                discharge_notes[discharge_notes['HADM_ID'] == el].TEXT)[0])

        elif len(icd_temp) == 0:

            #print("dupe id prev: " + str(el))
            #print("dupe id el: " + str(prev_el))
            print("***")
            print(el)
            # pass
            #print("dupe found?" + str(el))
        # We can't convert to int, they need to be one hot encoded after converting with SKlearn label-encoder
        #hadm_list = list(map(int, hadm_list))

        j += 1

        prev_el = el

    return icd_list, hadm_id_list, notes_list



# Load the Notes and ICD .CSV
notes_df = pd.read_csv(notes_filename)
diag_icd_df = pd.read_csv(icd_filename)

# Clean the notes.
notes_df['TEXT'] = notes_df['TEXT'].apply(clean_note)

# Statistics
NUM_NOTES = len(NOTE_LENGTHS)
AVERAGE_NOTE_LENGTHS = reduce(lambda x, y: x + y, NOTE_LENGTHS) / NUM_NOTES
print('Num Notes: ' + str(NUM_NOTES) +
      ' Avg. Note Length: ' + str(int(AVERAGE_NOTE_LENGTHS)))

# Call Array transformation function, create_icd_array
print('...Done')
icdList, hadmList, notesList = create_icd_array(notes_df, diag_icd_df)
