from . import FileHelper
class YAMLBase(object):
    def __init__(self):
        pass

class Repo(YAMLBase):
    def __init__(self, file):
        super().__init__()
        self.name = None
        self.priority = 0
        # Auto parse the repo file, and fill in the fields
        yaml_output = FileHelper.OpenYAMLFile('var/wpkgman/repos/' + file + '.yml')
        # TODO: Add auto downloading of the repo files if possible.
        if yaml_output is None:
            print("Creating repo file {f} at {ef}".format(f=file,
                                                          ef=FileHelper.GetEffectiveRoot() + 'var/wpkgman/repos'))
            content = {
                'repo': file,
                'priority': 0
            }
            FileHelper.WriteYAMLFile('var/wpkgman/repos' + file + '.yml', content)
        else:
            self.name = yaml_output['name']
            self.priority = yaml_output['priority']