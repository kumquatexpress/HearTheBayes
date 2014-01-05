from numpy import linspace, sin, pi, float32
import numpy as np
import scikits.audiolab
import utils
import random
from collections import deque


class Generator(object):

    RATE = 44100    # Generate audio stream at 44.1Khz

    FREQUENCY_MAP = {
        "C": 261.63,
        "C+": 277.18,
        "D": 293.66,
        "D+": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F+": 369.99,
        "G": 392.00,
        "G+": 415.30,
        "A": 440.00,
        "A+": 466.16,
        "B": 493.88,
        "REST": 0.00
    }

    def __init__(self, learner, filename):
        self.learner = learner

        # Tracking statistics
        self.NOT_FOUND_NOTE = 0
        self.NOT_FOUND_RHYTHM = 0
        self.FOUND_NOTE = 0
        self.FOUND_RHYTHM = 0

        format = scikits.audiolab.Format()
        self.output = scikits.audiolab.Sndfile(
            filename, format=format, mode='w',
            channels=1, samplerate=self.RATE)

    def generate_notes(self, ngrams, initial, count):
        output = []
        current = deque(initial, maxlen=self.learner.NGRAM_LEN)
        while len(output) < count:
            # Check if current is a rare ending only note
            if tuple(current) not in ngrams:
                self.NOT_FOUND_NOTE += 1
                num = random.randint(0, len(ngrams) - 1)
                current = deque(ngrams.keys()[num],
                                maxlen=self.learner.NGRAM_LEN)
                if not output:
                    # This is the initial one, so we add
                    # the "random" choice into it to start off.
                    output += current
            else:
                self.FOUND_NOTE += 1
            next = utils.get_result_from_distribution(
                ngrams[tuple(current)])
            output.append(next)

            current.append(next)
        return output

    def generate_rhythms(self, ngrams, initial, bpm, time):
        output = []
        current = deque(initial, maxlen=self.learner.NGRAM_LEN)

        while sum(output) < (float(time) / 60 * bpm):
            # Check if current is a rare ending only rhythm
            if tuple(current) not in ngrams:
                self.NOT_FOUND_RHYTHM += 1
                num = random.randint(0, len(ngrams) - 1)
                current = deque(ngrams.keys()[num],
                                maxlen=self.learner.NGRAM_LEN)
                if not output:
                    # This is the initial one, so we add
                    # the "random" choice into it to start off.
                    output += current
            else:
                self.FOUND_RHYTHM += 1
            next = utils.get_result_from_distribution(
                ngrams[tuple(current)])
            output.append(next)

            current.append(next)
        return output

    def make_note_sound(self, freq, time, amplitude=1):
        """
        Generates the numpy array for a single note
        with length [time] and loudness [amplitude] at
        the given frequency.
        """
        note = sin(2 * pi * freq * amplitude *
                   linspace(0, time, time * self.RATE))
        freq = utils.reverse_dictionary(self.FREQUENCY_MAP)[freq]
        print freq, time, amplitude, len(note)
        return note / np.max(np.abs(note), axis=0)     # Normalize the note

    def write_note(self, note):
        """
        Writes the given note numpy array to the generator's
        file, then forces an os sync to save.
        """
        self.output.write_frames(note)
        self.output.sync()

    def write_music(self, length, bpm=75, note_initial="C",
                    rhythm_initial="0.25"):
        rhythms = self.generate_rhythms(
            self.learner.ngrams["rhythms"], rhythm_initial, bpm, length)
        notes = self.generate_notes(
            self.learner.ngrams["notes"], note_initial, len(rhythms))

        rhythms = map(lambda x: float(60) * x / bpm, rhythms)
        notes = map(lambda x: self.FREQUENCY_MAP[x], notes)

        for i, n in enumerate(notes):
            self.write_note(self.make_note_sound(notes[i], rhythms[i]))
