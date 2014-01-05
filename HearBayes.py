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
        """
        return 0
    file_out = sys.argv[1]
    length = int(sys.argv[2])
    files_in = sys.argv[3:]

    learner = l.Learner(list(files_in))

    print "Learning songs..."
    learner.populate_fields()
    print("%d progressions learned" % len(learner.note_list))

    print "Generating new audio..."
    generator = g.Generator(learner, file_out)

    generator.write_music(length)
    print "Finished!"
    return 0

main()
