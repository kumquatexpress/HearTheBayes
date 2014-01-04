import pickle_util as putil
import echonest.remix.audio as audio
import numpy
import math
import utils

SECONDS_PER_MIN = 60


class Learner(object):

    PITCH_DICTIONARY = {
        0: "C",
        1: "C+",
        2: "D",
        3: "D+",
        4: "E",
        5: "F",
        6: "F+",
        7: "G",
        8: "G+",
        9: "A",
        10: "A+",
        11: "B"
    }

    def __init__(self, filenames):
        self.files = filenames
        self.songs = []
        self.note_list = []
        self.rhythm_list = []
        self.notes = {}

        for f in filenames:
            audio = putil.load_pickle(f)
            if not audio:
                audio = putil.load_pickle(putil.make_pickle_audio(f))
            self.songs.append({"data": audio, "bpm": audio.analysis.tempo,
                               "time": audio.analysis.time_signature,
                               "file": f})

        self.find_pitch_sequences()
        self.combine_same_pitch_for_length()

    def find_pitch_sequences(self):
        """
        Populates the learner with information about the individual segments
        of the song, including the most likely identified pitch and how long
        the segment lasted for in terms of note-length.
        """
        for song in self.songs:
            bpm = song["bpm"]["value"]
            data = song["data"]
            time = song["time"]["value"]
            temp_song_segs = []

            for seg in data.analysis.segments:
                rhythm = utils.round_note_length_base2(
                    float(seg.duration) / bpm * SECONDS_PER_MIN)

                pitches = [(self.PITCH_DICTIONARY[a[0]], a[1]) for a in sorted(
                    enumerate(seg.mean_pitches()),
                    key=lambda x: x[1], reverse=True)]

                temp_song_segs.append({"count": seg.absolute_context()[0],
                                       "rhythm": rhythm, "pitches": pitches,
                                       "amplitude": seg.mean_loudness()})

            self.notes[song["file"]] = temp_song_segs

    def combine_same_pitch_for_length(self):
        """
        Given a list of note segments such as
        [{rhythm: 32, pitches: C}, {rhythm: 32, pitches: C}],
        combines them into a single {rhythm: 16, pitches: C} because
        the note found spans more than a single segment.
        """
        last_encountered = ""
        sum_rhythm = 0

        for note in self.notes:
            for n in self.notes[note]:
                curr_note, curr_rhythm = n["pitches"][0][0], n["rhythm"]
                if last_encountered is not "" and curr_note is not last_encountered:
                    print curr_note
                    print last_encountered
                    print sum_rhythm
                    self.note_list.append((last_encountered, sum_rhythm))
                    self.rhythm_list.append(sum_rhythm)
                    sum_rhythm = curr_rhythm
                else:
                    if not sum_rhythm:
                        sum_rhythm = curr_rhythm
                    else:
                        sum_rhythm = 1 / \
                            (float(sum_rhythm + curr_rhythm)
                             / (sum_rhythm * curr_rhythm))
                last_encountered = curr_note

            self.note_list.append((last_encountered, sum_rhythm))
            self.rhythm_list.append(sum_rhythm)
