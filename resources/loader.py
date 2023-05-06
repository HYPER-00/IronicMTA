import os
from typing import List

class ResourceLoader:
    def __init__(
        self,
        core_names: List[str],
        extensions: List[str],
        directory: str
    ) -> None:
        self.BASE_DIR = '\\'.join(__file__.split('\\')[:-1])
        directory = os.path.join(self.BASE_DIR, directory)
        self.core_names = core_names
        self.extensions = extensions
        self.resource_cores = []

        self.supported_exts = ['.json', '.xml']

        for index, ext in enumerate(extensions):
            if not ext.startswith('.'):
                extensions[index] = '.' + str(ext)
            

        self.get_dirs(directory)

        print(self.resource_cores)

    def get_dirs(self, directory):
        if os.path.isdir(directory):
            for dir in os.listdir(directory):
                print(type(dir))
                if (
                    dir.startswith('[')
                    and dir.endswith(']')
                    and dir.count('[') == 1
                    and dir.count(']') == 1
                ):
                    self.get_dirs(os.path.join(directory, dir))
                else:
                    if '.'.join(dir.split('.')[:-1]) in self.core_names: # Check if the filename in core names
                        if '.' + dir.split('.')[-1] in self.extensions:
                            print('ss')
                            self.resource_cores.append(
                                os.path.join(directory, dir))
        else:
            print('noo')



ResourceLoader(
    extensions=['json', '.xml'],
    core_names=['resource', 'res'],
    directory='ress'
)