from bs.operations.base import OperationPlugin  # import the base class to build your plugin
import os, random


# some information for the plugins
meta = {'version' : "1.0.0",
        'author' : "Yohan Jarosz",
        'contact' : "webmaster-bbcf@epfl.ch"}



class ReadFile(OperationPlugin):

    info = {
        'title' : 'ReadFile',
        'description' : "Read the file to find the number of characters and write the result in an output file. "
                        "If randomize is checked, the result is between 0 and the file's number of characters ",
        'path' : ['Tests', 'Examples', 'Read a file'],
        'in' : [{'id' : 'fname', 'label' : 'File Name', 'type' : 'text'},
                {'id' : 'input', 'label' : 'File input', 'type' : 'file', 'required' : True},
                {'id' : 'randomize', 'label' : 'Randomize', 'type' : 'boolean'}
        ],
        'out' : [{'id' : 'output', 'type' : 'file'}],
        'meta' : meta,
        }

    def __call__(self, *args, **kw):
        # get parameters
        fin = kw.get('input')
        fname = kw.get('fname', '')
        if fname == '' : fname = os.path.split(fin)[1]
        randomize = kw.get('randomize', False)
        # read the input file
        nchar = 0
        with open(fin, 'r') as rin:
            for line in rin:
                nchar += len(line)
                # randomize if checked
        if randomize:
            nchar = random.randint(0, nchar - 1)
            # take a temporary path where to write the file
        fout = self.temporary_path(fname)
        print fout
        # write the result
        with open(fout, 'w') as wout:
            wout.write(str(nchar))
            # add the file to the result
        self.new_file(fout, 'output')
