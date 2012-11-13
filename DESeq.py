from bs.operations import base
from bbcflib.bFlatMajor.stream import neighborhood, score_by_feature
from bbcflib.btrack import track
from bbcflib import genrep
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri as numpy2ri
import numpy
import os
import itertools


ftypes = [(0, 'genes bodies'), (1, 'gene promoters'), (2, 'exons'), (3, 'custom upload')]
prom_up_def = 1000
prom_down_def = 100

import tw2.forms as twf
import tw2.core as twc
import tw2.dynforms as twd


class QuantifyTableForm(base.BaseForm):

    signals = base.MultipleFileUpload(label='Signal: ',
        help_text='Select signal files (e.g. bedgraph)',
        validator=twf.FileValidator(required=True))
    child = twd.HidingTableLayout()
    feature_type = twd.HidingSingleSelectField(label='Feature type: ',
        options=ftypes, prompt_text=None,
        mapping={ftypes[-1][0]: ['features'],
                 1: ['upstream', 'downstream']},
        help_text='Choose a feature set or upload your own',
        validator=twc.Validator(required=True))
    features = twf.FileField(label='Custom feature set: ',
        help_text='Select a feature file (e.g. bed)',
        validator=twf.FileValidator())
    assembly = twf.SingleSelectField(label='Assembly: ',
        options=genrep.GenRep().assemblies_available(),
        help_text='Reference genome')
    upstream = twf.TextField(label='Promoter upstream distance: ',
        validator=twc.IntValidator(required=True),
        value=prom_up_def,
        help_text='Size of promoter upstream of TSS')
    downstream = twf.TextField(label='Promoter downstream distance: ',
        validator=twc.IntValidator(required=True),
        value=prom_down_def,
        help_text='Size of promoter downstream of TSS')
    submit = twf.SubmitButton(id="submit", value="Quantify")


meta = {'version': "1.0.0",
        'author': "BBCF",
        'contact': "webmaster-bbcf@epfl.ch"}

in_parameters = [
        {'id': 'feature_type', 'type': 'int'},
        {'id': 'upstream', 'type': 'int'},
        {'id': 'downstream', 'type': 'int'},
        {'id': 'assembly', 'type': 'assembly'},
        {'id': 'signals', 'type': 'track', 'required': True, 'multiple': True},
        {'id': 'features', 'type': 'track', 'required': True},
]
out_parameters = [{'id': 'differential_expression', 'type': 'file'}]


class DESeqPlugin(base.OperationPlugin):

    info = {
        'title': 'Differential expression analysis',
        'description': '''Gets the score associated to each feature in each sample and runs DESeq for differential analysis within them.''',
        'path': ['Signal', 'DESeq'],
        'output': QuantifyTableForm,
        'in': in_parameters,
        'out': out_parameters,
        'meta': meta,
        }

    # TEST (cd .../plugins/bs/plugins)
    # from bs.plugins.DESeq import DESeqPlugin; DESeqPlugin()(**{'signals':['tests/DESeq/signal1.bedGraph', 'tests/DESeq/signal2.bedGraph'], 'features':'tests/DESeq/features.bed', 'feature_type':3})

    def __call__(self, **kw):
        feature_type = int(kw.get('feature_type', 0))
        assembly_id = kw.get('assembly')
        chrmeta = "guess"
        if assembly_id:
            assembly = genrep.Assembly(assembly_id)
            chrmeta = assembly.chrmeta
            genes = assembly.gene_track
            exons = assembly.exon_track
        elif not(feature_type == 3):
            raise ValueError("Please specify an assembly")
        if feature_type == 0:
            features = genes
        elif feature_type == 1:
            prom_pars = {'before_start': int(kw.get('upstream') or prom_up_def),
                          'after_start': int(kw.get('downstream') or prom_down_def),
                          'on_strand': True}
            features = lambda c: neighborhood(genes(c), **prom_pars)
        elif feature_type == 2:
            features = exons
        elif feature_type == 3:
            assert os.path.exists(kw.get('features'))
            _t = track(kw.get('features'), chrmeta=chrmeta)
            chrmeta = _t.chrmeta
            features = _t.read
        else:
            return 2

        signals = []
        norm_factors = []
        for sig in kw.get('signals', []):
            assert os.path.exists(sig), "File not found: %s." % sig
            _t = track(sig, chrmeta=chrmeta)
            if 'normalization' in _t.info:
                _nf = float(_t.info['normalization'])
            elif 'nreads' in _t.info:
                _nf = float(_t.info['nreads']) * 1e-7 / float(_t.info.get('read_extension', 1))
            else:
                _nf = 1
            signals.append(_t)
            norm_factors.append(_nf)
        if len(signals) > 1:
            _f = ["score" + str(i) for i in range(len(signals))]
        else:
            _f = ["score"]
        de_list = []
        for chrom in chrmeta:
            sread = [sig.read(chrom) for sig in signals]
            mread = score_by_feature(sread, features(chrom), fn='sum')
            de_list.extend(list(mread))
        name_idx = mread.fields.index("name")
        # Turn all scores into integers
        de_matrix = numpy.asarray([[int(s * norm_factors[k] + .5) for s in x[-len(_f):]]
                                   for k, x in enumerate(de_list)], dtype=numpy.float)
        rownames = numpy.asarray([x[name_idx] for x in de_list])
        colnames = numpy.asarray([os.path.splitext(os.path.basename(s.path))[0]
                                  for s in signals])
        del de_list
        output = self.temporary_path(fname='DE')

        robjects.r.assign('Mdata', numpy2ri.numpy2ri(de_matrix))
        robjects.r.assign('row_names', numpy2ri.numpy2ri(rownames))
        robjects.r.assign('col_names', numpy2ri.numpy2ri(colnames))
        robjects.r("""
        Mdata <- as.data.frame(Mdata,row.names=row_names)
        conds <- unlist(strsplit(col_names,".",fixed=T))
        colnames(Mdata) <- conds
        groups <- unique(conds)
        couples <- combn(groups,2)

        # Still need to check that replicates are not identical - lfproc would fail
        if (any(table(conds)>1)){ method = 'normal' # if replicates
        } else { method = 'blind' }

        library(DESeq)
        cds <- newCountDataSet(Mdata, conds)
        cds <- estimateSizeFactors(cds)
        cds <- estimateVarianceFunctions(cds,method='blind')
        """)

        groups = list(set(colnames))
        couples = itertools.combinations(groups, 2)
        for c in couples:
            out = output + '_' + c[0] + '-' + c[1] + '.txt'
            print out
            r_cmd = """
            res <- nbinomTest(cds, '%s', '%s')
            res <- res[order(res[,8]),]
            write.table(res, '%s', row.names=F)
            """ % (c[0], c[1], out)
            robjects.r(r_cmd)
            self.new_file(out, 'differential_expression')
        return 1
