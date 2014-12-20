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
        if yaml_output is None:
            pass
        else:
            self.name = yaml_output['repo']
            self.priority = yaml_output['priority']

class Config(YAMLBase):
    def __init__(self):
        super().__init__()

        self.options = None

        # Auto parse the repo file, and fill in the fields
        yaml_output = FileHelper.OpenYAMLFile('etc/wpkgman.yml')
        # TODO: Add auto downloading of the repo files if possible.
        if yaml_output is None:
            print("Creating config file at {ef}".format(ef=FileHelper.GetEffectiveRoot() + 'etc/wpkgman.cfg'))
            content = """# wpkgman master config file
# edit carefully, if the YAML formatting breaks wpkgman will error

options:
    - color: true
    - noconfirm: false # only enable this if you hate yourself

mirrors:
    - http://sundwarf.me/pkg/ # Will autocomplete $repo/$arch/$pkg

repos:
    stable:
        loc: var/wpkgman/repos/stable.yml
        priority: -1
    testing:
        loc: var/wpkgman/repos/testing.yml
        priority: 0
    extra:
        loc: var/wpkgman/repos/extra.yml
        priority: -1


ignore_package:
    - dummypackage # added to make YAML not complain
    # Add packages you wish to ignore here
    # - gcc

upgrade_first:
    # if any of these packages are installed, and have an update, will upgrade before anything else
    - dummypackage
    - wpkgman
    - wsystem
"""
            f = FileHelper.OpenFileForWritingText('etc/wpkgman.yml')
            f.write(content)
        else:
            self.options = (yaml_output['options'][0]['color'], yaml_output['options'][1]['noconfirm'])
            self.mirrors = yaml_output['mirrors']
            self.repos = yaml_output['repos']
            self.ignore_package = yaml_output['ignore_package']
            self.upgrade_first = yaml_output['upgrade_first']