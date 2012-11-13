from bs.operations import base
from bbcflib.btrack import convert
from bbcflib import genrep

format_list = ['bedgraph', 'wig', 'bed', 'sql', 'gff', 'sga', 'bigwig']


import tw2.forms as twf
import tw2.core as twc
import tw2.dynforms as twd


class ConvertForm(base.BaseForm):
    hover_help = True
    show_errors = True
    infile = twf.FileField(label='File: ', help_text='Select file.',
        validator=twf.FileValidator(required=True))
    child = twd.HidingTableLayout()
    to = twd.HidingSingleSelectField(label='Output format: ',
        options=format_list,  prompt_text=None,
        mapping={'sql': ['dtype', 'assembly'],
                 'bigwig': ['assembly']},
        validator=twc.Validator(required=True),
        help_text='Select the format of your result')
    dtype = twf.SingleSelectField(label='Output datatype: ', prompt_text=None,
        options=['quantitative', 'qualitative'],
        help_text='Choose sql data type attribute')
    assembly = twf.SingleSelectField(label_text='Assembly: ',
        options=genrep.GenRep().assemblies_available(),
        help_text='Reference genome')
    submit = twf.SubmitButton(id="submit", value="Convert")


meta = {'version': "1.0.0",
        'author': "BBCF",
        'contact': "webmaster-bbcf@epfl.ch"}

in_parameters = [{'id': 'infile', 'type': 'track', 'required': True},
        {'id': 'to', 'type': 'list'},
        {'id': 'dtype', 'type': 'list'},
        {'id': 'assembly', 'type': 'assembly'},
]

out_parameters = [{'id': 'converted_file', 'type': 'track'}]


class FileConvert(base.OperationPlugin):
    info = {
        'title': 'Convert file',
        'description': 'Convert a file to a different format',
        'path': ['Files', 'Convert'],
        'output': ConvertForm,
        'in': in_parameters,
        'out': out_parameters,
        'meta': meta,
        }

    def title(self):
        return 'Convert file'

    def path(self):
        return

    def output(self):
        return ConvertForm

    def description(self):
        return '''.'''

    def parameters(self):
        return {'in': ['infile', 'to', 'dtype', 'assembly'],
                'out': {'converted_file': 'track'}}

    def files(self):
        return ['infile']

    def meta(self):
        return {'version': "1.0.0",
                'author': "BBCF",
                'contact': "webmaster-bbcf@epfl.ch",
                'library': 'http://bbcf.epfl.ch/track'}

    def process(self, **kw):
        ext = kw.get('to') or 'sql'
        outfile = self.temporary_path(ext=ext)
        info = {'datatype': kw.get('datatype') or 'qualitative'}
        convert(kw.get('infile'), outfile,
                chrmeta=kw.get('assembly') or None, info=info)
        self.new_file(outfile, 'converted_file')
        return 1
