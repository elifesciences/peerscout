import pandas as pd


class PickleDatasetLoader:
    def __init__(self, pickle_path):
        self.pickle_path = pickle_path

    def get_pickle(self, filename):
        df = pd.read_pickle(self.pickle_path + "/" + filename)
        print("df {} shape {}".format(filename, df.shape))
        return df

    def __getitem__(self, key):
        return self.get_pickle(key + '.pickle')
