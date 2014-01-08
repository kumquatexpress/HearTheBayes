#!/usr/bin/python
#
# HearBayes.py
# Boyang Niu
# 1-5-2014
# boyang.niu@gmail.com
#
# This is the main method for song generation using Generator and Learner.
#

import Generator as g
import Learner as l
import sys
import pickle_util as putil


def main():
    if "--help" in sys.argv:
        print """
        Usage: ./HearBayes.py [audiofile_out]
        [length of generation in seconds][audiofiles_in or Learner pickle
        file, ..., ]

        #TODO optional: --bpm=[number], --key=[C-B,+ for sharp, - for flat]
                --time_sig=[number 1-4, only common time sigs allowed here]

        In place of [audiofiles_in] as the last argument, you can also
        specify a pickle file with extension ".pickle" to use as the Learner
        if it has already been trained.
        """
        return 0
    arguments = sys.argv

    file_out = arguments[1]
    length = int(arguments[2])
    files_in = arguments[3:]

    if len(files_in) == 1 and "pickle" in files_in[0].split("."):
        print "Loading learner from pickle..."
        learner = putil.load_pickle(files_in[0])
    else:
        learner = l.Learner(list(files_in))
        print "Learning songs..."
        learner.populate_fields()
        learner.save(files_in[0] + ".learner")
        print("%d progressions learned" % len(learner.note_list))

    print "Generating new audio..."
    generator = g.Generator(learner, file_out)

    generator.write_music(length, bpm=120, initial_key="D+")
    print "Finished!"

    # Debugging information about target statistics to more accurately
    # set the ngram length.
    print("hit notes: %d" % generator.FOUND_NOTE)
    print("missed notes: %d" % generator.NOT_FOUND_NOTE)
    print("hit rhythms: %d" % generator.FOUND_RHYTHM)
    print("missed rhythms: %d" % generator.NOT_FOUND_RHYTHM)
    print("not in key: %d" % generator.NOT_IN_KEY)

    return 0

if __name__ == "__main__":
    main()
