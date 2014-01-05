#
# Utils.py
#
# Boyang Niu
# 1-04-2014
# boyang.niu@gmail.com
#
# Contains utilities used in the learner and generator for HearBayes
#
import math


def round_note_length_base2(frac):
    """
    Numbers will come in as something like 1/17.55, we want to
    round them to 1/16 for 16th notes, etc.

    This function returns the denominator of the note length, i.e.
    1 for whole note, 2 for half, ... , 128 for 128th note.
    """
    denominator = float(1) / frac
    return float(1)/(2 ** round(math.log(denominator) / math.log(2), 0))
