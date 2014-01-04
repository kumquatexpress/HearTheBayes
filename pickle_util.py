import pickle
import echonest.remix.audio as audio
import os.path


def pickle_filename(filename):
    return filename + ".pickle"


def file_to_analysis(filename):
    a = audio.LocalAudioFile(filename)
    if a:
        return a


def pickle_analysis(analysis, f):
    if analysis and f:
        pickle.dump(analysis, f)


def make_pickle_audio(filename):
    p_filename = pickle_filename(filename)

    pickle_file = open(p_filename, 'w')
    pickle_analysis(file_to_analysis(filename), pickle_file)
    return p_filename


def make_pickle(ob, pickle_file=None):
    if not pickle_file:
        pickle_file = open("default.pickle", 'w')
    pickle.dump(ob, open(pickle_file))


def load_pickle(filename=None):
    if not "pickle" == filename.split(".")[-1]:
        filename = pickle_filename(filename)
    if not os.path.exists(filename):
        return None
    return pickle.load(open(filename))
