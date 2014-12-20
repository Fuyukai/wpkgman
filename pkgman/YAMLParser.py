import yaml

class YAMLBase(object):
    def __init__(self):
        pass

class Repo(YAMLBase):
    def __init__(self, name):
        super().__init__()
        self.name = name