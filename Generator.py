from numpy import linspace, sin, pi, float32
import numpy as np
import scikits.audiolab
import Utils
import random


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
        format = scikits.audiolab.Format()
        self.output = scikits.audiolab.Sndfile(
            filename, format=format, mode='w',
            channels=1, samplerate=self.RATE)

    def generate_notes(self, bigrams, initial, count):
        output = []
        current = initial
        while len(output) < count:
            # Check if current is a rare ending only note
            if current not in bigrams:
                num = random.randint(0, len(bigrams) - 1)
                current = bigrams.keys()[num]

            next = Utils.get_result_from_distribution(
                bigrams[current])
            output.append(next)
            current = next
        return output

    def generate_rhythms(self, bigrams, initial, bpm, time):
        output = []
        current = initial

        while sum(output) < (float(time) / 60 * bpm):
            # Check if current is a rare ending only rhythm
            if current not in bigrams:
                num = random.randint(0, len(bigrams) - 1)
                current = bigrams.keys()[num]

            next = Utils.get_result_from_distribution(
                bigrams[current])
            output.append(next)
            current = next
        return output

    def make_note_sound(self, freq, time, amplitude=1):
        """
        Generates the numpy array for a single note
        with length [time] and loudness [amplitude] at
        the given frequency.
        """
        note = sin(2 * pi * freq * amplitude *
                   linspace(0, time, time * self.RATE))
        print freq, time, amplitude, len(note)
        if note:
            return note/np.max(np.abs(note), axis=0)     # Normalize the note

    def write_note(self, note):
        """
        Writes the given note numpy array to the generator's
        file, then forces an os sync to save.
        """
        self.output.write_frames(note)
        self.output.sync()

    def write_music(self, length, bpm=120, note_initial="C",
                    rhythm_initial="0.25"):
        rhythms = self.generate_rhythms(
            self.learner.bigrams["rhythms"], rhythm_initial, bpm, length)
        notes = self.generate_notes(
            self.learner.bigrams["notes"], note_initial, len(rhythms))

        rhythms = map(lambda x: float(60) / bpm * x, rhythms)
        notes = map(lambda x: self.FREQUENCY_MAP[x], notes)

        for i, n in enumerate(notes):
            self.write_note(self.make_note_sound(notes[i], rhythms[i]))
