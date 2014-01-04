import pickle_util as putil
import echonest.remix.audio as audio


class Learner(object):

    def __init__(self, filenames):
        self.files = filenames
        self.analyses = []
        for f in filenames:
            audio = putil.load_pickle(f)
            if not audio:
                audio = putil.load_pickle(putil.make_pickle_audio(f))
            self.analyses.append(audio)
