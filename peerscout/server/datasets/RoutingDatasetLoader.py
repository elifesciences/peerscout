class RoutingDatasetLoader:
    def __init__(self, routes, default_loader):
        self.routes = routes
        self.default_loader = default_loader

    def get(self, key):
        if key in self.routes:
            return self.routes[key][key]
        return self.default_loader[key]

    def __getitem__(self, key):
        return self.get(key)
