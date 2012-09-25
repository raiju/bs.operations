from bs.operations.base import OperationPlugin  # import the base class to build your plugin
import os, random


# some information for the plugins
meta = {'version' : "1.0.0",
        'author' : "Yohan Jarosz",
        'contact' : "webmaster-bbcf@epfl.ch"}



class Simple(OperationPlugin):

    info = {
        'title' : 'SIMPLE',                             # The title of your operation
        'description' : 'A minimal example',          # Describe the operation's goal
        'path' : ['Tests', 'Examples', 'Simple'],    # Under which category the operation will be set
        # Must be unique across all plugins
        # First in the list mean higher category
        'in' : [{'id' : 'input', 'type' : 'text', 'required' : True}],    # All input parameters
        'out' : [{'id' : 'output', 'type' : 'file'}],                     # All output parameters
        'meta' : meta,                                # Meta information (authors, version, ...)
    }

    def __call__(self, *args, **kw):
        text = kw.get('input', '')                    # get the parameter back

        path = self.temporary_path()                  # get a temporary path
        with open(path, 'w') as f:                    # open a file & write the input
            f.write(text)
        self.new_file(path, 'output')                 # add a file to the result

        return 1


