from numpy import linspace, sin, pi, float32
import numpy as np
import scikits.audiolab


class Generator(object):

    RATE = 44100    # Generate audio stream at 44.1Khz

    def __init__(self, learner, filename):
        self.learner = learner
        format = scikits.audiolab.Format()
        self.output = scikits.audiolab.Sndfile(
            filename, format=format, mode='w',
            channels=1, samplerate=self.RATE)

    def generate_note(self, freq, time, amplitude=1):
        """
        Generates the numpy array for a single note
        with length [time] and loudness [amplitude] at
        the given frequency.
        """
        note = sin(2 * pi * freq * amplitude *
                   linspace(0, time, time * self.RATE))
        return np.max(np.abs(note), axis=0)     # Normalize the note

    def write_note(self, note):
        """
        Writes the given note numpy array to the generator's
        file, then forces an os sync to save.
        """
        self.output.write_frames(note)
        self.output.sync()
