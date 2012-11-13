from bs.operations import base  # import the base class to build your plugin

# common information for the two plugins
meta = {'version': "1.0.0",
        'author': "Yohan Jarosz",
        'contact': "webmaster-bbcf@epfl.ch"}



# PLUGIN ONE

# import toscawidget2 modules in order to build forms
import tw2.forms as twf


class OutputForm(base.BaseForm):
    # the parameter 'input'
    input = twf.FileField(label_text="My input", validator=twf.FileValidator(required=True))

    # the submit button
    submit = twf.SubmitButton(id="submit", value="Submit My job")


class WithForm(base.OperationPlugin):

    info = {
        'title': 'Simple Form customization',
        'description': 'See <a href="http://tw2core.readthedocs.org/en/latest/index.html">toscawidget documentation</a> for more information.',
        'path': ['Tests', 'Examples', 'Simple form'],
        'in': [{'id': 'input', 'type': 'text', 'required': True}],
        'out': [],
        'meta': meta,
        'output': OutputForm                         # Define the form you want to use
    }

    def __call__(self, *args, **kw):     # proceed as usual
        file_input = kw.get('input', '')
        return file_input


# PLUGIN TWO
import tw2.dynforms as twd  # import dynamic modules


class DynamicOutputForm(base.DynForm):
    method = twd.HidingSingleSelectField(label='Select method', options=('This is', 'a-demo'),
        mapping={
            'This is': ['one'],
            'a-demo': ['two', 'three'],
                })

    one = twf.TextField(label='One')
    two = twf.TextField(label='Two')
    three = twf.TextField(label='Three')

    # the submit button
    submit = twf.SubmitButton(id="submit", value="Submit My job")


class WithDynamicForm(base.OperationPlugin):

    info = {
        'title': 'Dynamic form',
        'description': 'See <a href="http://tw2core.readthedocs.org/en/latest/index.html">toscawidget documentation</a> for more information.',
        'path': ['Tests', 'Examples', 'Dynamic form'],
        'in': [{'id': 'input', 'type': 'text', 'required': True}],
        'out': [],
        'meta': meta,
        'output': DynamicOutputForm                         # Define the form you want to use
    }

    def __call__(self, *args, **kw):     # proceed as usual
        return 1
