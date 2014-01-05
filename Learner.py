import pickle_util as putil
import echonest.remix.audio as audio
import numpy
import math
import Utils as utils

SECONDS_PER_MIN = 60


class Learner(object):

    # The threshold at which to call a segment a silence
    REST_THRESH = 1.6

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

            self.notes[song["file"]] = {
                "notes": temp_song_segs,
                "loudness": data.analysis.loudness
            }

    def combine_same_pitch_for_length(self):
        """
        Given a list of note segments such as
        [{rhythm: 1/32, pitches: C}, {rhythm: 1/32, pitches: C}],
        combines them into a single {rhythm: 1/16, pitches: C} because
        the note found spans more than a single segment.
        """
        last_encountered = ""
        sum_rhythm = 0

        for note in self.notes:
            current_song = self.notes[note]
            for n in current_song["notes"]:
                curr_note, curr_rhythm = n["pitches"][0][0], n["rhythm"]
                # Check if the segment is a series of rests or not
                # If so, treat it like a note change for mapping
                if n["amplitude"] < current_song["loudness"] \
                        * self.REST_THRESH or last_encountered is not "" \
                        and curr_note is not last_encountered:
                    # A note change occurred, record the note and summed rhythm
                    self.note_list.append((last_encountered, sum_rhythm))
                    self.rhythm_list.append(sum_rhythm)
                    sum_rhythm = curr_rhythm
                else:
                    if not sum_rhythm:
                        sum_rhythm = curr_rhythm
                    else:
                        sum_rhythm = sum_rhythm + curr_rhythm
                last_encountered = curr_note

            self.note_list.append((last_encountered, sum_rhythm))

    def get_notes(self):
        return zip(*self.note_list)[0]

    def get_rhythms(self):
        return zip(*self.note_list)[1]
