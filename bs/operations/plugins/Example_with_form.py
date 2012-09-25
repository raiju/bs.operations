from bs.operations import base  # import the base class to build your plugin
import os, random


# some information for the plugins
meta = {'version' : "1.0.0",
        'author' : "Yohan Jarosz",
        'contact' : "webmaster-bbcf@epfl.ch"}



# import toscawidget2 modules in order to build forms
import tw2.forms as twf

class OutputForm(base.BaseForm):
    # the parameter 'input'
    input = twf.FileField(label_text="My input", validator=twf.FileValidator(required=True))

    # the submit button
    submit = twf.SubmitButton(id="submit", value="Submit My job")



class WithForm(base.OperationPlugin):

    info = {
        'title' : 'Simple Form customization',
        'description' : 'See http://tw2core.readthedocs.org/en/latest/index.html for more information.',
        'path' : ['Tests', 'Examples', 'Simple form'],
        'in' : [{'id' : 'input', 'type' : 'text', 'required' : True}],
        'out' : [],
        'meta' : meta,
        'output' : OutputForm                         # Define the form you want to use
    }

    def __call__(self, *args, **kw):     # proceed as usual
        fin = kw.get('input', '')
        return 1
