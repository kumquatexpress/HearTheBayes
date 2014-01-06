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
import random


def round_note_length_base2(frac):
    """
    Numbers will come in as something like 1/17.55, we want to
    round them to 1/16 for 16th notes, etc.

    This function returns the denominator of the note length, i.e.
    1 for whole note, 2 for half, ... , 128 for 128th note.
    """
    denominator = float(1) / frac
    return float(1) / (2 ** round(math.log(denominator) / math.log(2), 0))


def get_result_from_distribution(dist, filt=None):
    """
    Given a dictionary of counts {a:1, b:2, etc}, generates a random
    number and returns a key from the dictionary probabalistically.

    Optional filt is a filter of letters
    ["C", "D", "E",..."B"] that corresponds to the current key.
    Apply the key filter to the possible next values to change the
    key to something that works.
    """
    sum_dist = {}
    temp_val = 0

    # This is not accurate because it blocks everything not in the key.
    # Commented out because sometimes it results in the empty {}
    # if filt:
    #    dist = {k: v for k, v in dist.iteritems() if k in filt}

    # Create the summation of the distribution
    # that we will select from later.
    for key in dist:
        temp_val += dist[key]
        sum_dist[key] = temp_val
    sum_dist = sorted(list(sum_dist.iteritems()), key=lambda x: x[1])
    num = random.randint(sum_dist[0][1], temp_val)

    for key, value in sum_dist:
        if num < value:
            return key

    return sum_dist[0][0]


def reverse_dictionary(d):
    return {v: k for k, v in d.iteritems()}


def filter_by_key_major():
    """
    Given a number, 0 = C, 2 = C+, ..., 11 = B, as a major key,
    returns a list of corresponding numbers to tones in that key.
    """
    return [0, 2, 4, 5, 7, 9, 11]
