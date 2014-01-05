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


def main():
    if "--help" in sys.argv:
        print """
        Usage: ./HearBayes.py [audiofile_out]
        [length of generation in seconds][audiofiles_in, ..., ]

        #TODO optional: --bpm=[number], --key=[C-B,+ for sharp, - for flat]
                --time_sig=[number 1-4, only common time sigs allowed here]
        """
        return 0
    arguments = sys.argv

    file_out = arguments[1]
    length = int(arguments[2])
    files_in = arguments[3:]

    learner = l.Learner(list(files_in))

    print "Learning songs..."
    learner.populate_fields()
    print("%d progressions learned" % len(learner.note_list))

    print "Generating new audio..."
    generator = g.Generator(learner, file_out)

    generator.write_music(length)
    print "Finished!"

    # Debugging information about target statistics to more accurately
    # set the ngram length.
    print("hit notes: %d" % generator.FOUND_NOTE)
    print("missed notes: %d" % generator.NOT_FOUND_NOTE)
    print("hit rhythms: %d" % generator.FOUND_RHYTHM)
    print("missed rhythms: %d" % generator.NOT_FOUND_RHYTHM)

    return 0

if __name__ == "__main__":
    main()
