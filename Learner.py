import pickle_util as putil
import echonest.remix.audio as audio
import numpy
import math
from collections import defaultdict, deque
import utils

SECONDS_PER_MIN = 60


class Learner(object):

    # The threshold at which to call a segment a silence
    REST_THRESH = 1.6
    NGRAM_LEN = 25

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
        self.ngrams = defaultdict()

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

            for seg in data.analysis.beats:
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
                if n["amplitude"] < current_song["loudness"] * self.REST_THRESH:
                    curr_note = "REST"
                if last_encountered is not "" \
                        and curr_note is not last_encountered:
                    # A note change occurred, record the note and summed rhythm
                    self.note_list.append((last_encountered, sum_rhythm))
                    sum_rhythm = curr_rhythm
                else:
                    if not sum_rhythm:
                        sum_rhythm = curr_rhythm
                    else:
                        sum_rhythm = utils.round_note_length_base2(
                            sum_rhythm + curr_rhythm)
                last_encountered = curr_note

            self.note_list.append((last_encountered, sum_rhythm))

    def count_ngrams(self, inlist):
        ngrams_dict = defaultdict(dict)
        curr_note = ""
        prev_note = deque(maxlen=self.NGRAM_LEN)
        for note in inlist:
            if len(prev_note) < self.NGRAM_LEN:
                prev_note.append(note)
                continue
            if note not in ngrams_dict[tuple(prev_note)]:
                ngrams_dict[tuple(prev_note)][note] = 0

            ngrams_dict[tuple(prev_note)][note] += 1
            prev_note.append(note)
        return ngrams_dict

    def populate_fields(self):
        """
        This method does all of the work for the Learner, analyzing
        the audio and coming out with ngrams for generation.
        """
        for f in self.files:
            audio = putil.load_pickle(f)
            if not audio:
                audio = putil.load_pickle(putil.make_pickle_audio(f))
            self.songs.append({"data": audio, "bpm": audio.analysis.tempo,
                               "time": audio.analysis.time_signature,
                               "file": f})

        self.find_pitch_sequences()
        self.combine_same_pitch_for_length()

        # Populate the bigram structure
        self.ngrams["notes"] = self.count_ngrams(self.get_notes())
        self.ngrams["rhythms"] = self.count_ngrams(self.get_rhythms())

    def get_notes(self):
        return zip(*self.note_list)[0]

    def get_rhythms(self):
        return zip(*self.note_list)[1]
