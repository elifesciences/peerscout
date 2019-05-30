class CachedDatasetLoader:
    def __init__(self, parent_loader):
        self.parent_loader = parent_loader
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        result = self.parent_loader[key]
        self.cache[key] = result
        return result

    def __getitem__(self, key):
        return self.get(key)
