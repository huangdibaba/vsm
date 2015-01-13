import unittest2 as unittest
import numpy as np

from vsm.corpus import Corpus
from vsm.corpus.util.corpusbuilders import random_corpus
from vsm.model.ldacgsseq import *


class TestLdaCgsSeq(unittest.TestCase):

    def setUp(self):
        pass

    ##TODO: write actual test cases.

    def test_LdaCgsSeq_IO(self):

        from tempfile import NamedTemporaryFile
        import os
    
        c = random_corpus(1000, 50, 6, 100)
        tmp = NamedTemporaryFile(delete=False, suffix='.npz')
        try:
            m0 = LdaCgsSeq(c, 'document', K=10)
            m0.train(n_iterations=20)
            m0.save(tmp.name)
            m1 = LdaCgsSeq.load(tmp.name)
            self.assertTrue(m0.context_type == m1.context_type)
            self.assertTrue(m0.K == m1.K)
            self.assertTrue((m0.alpha == m1.alpha).all())
            self.assertTrue((m0.beta == m1.beta).all())
            self.assertTrue(m0.log_probs == m1.log_probs)
            for i in xrange(max(len(m0.corpus), len(m1.corpus))):
                self.assertTrue(m0.corpus[i].all() == m1.corpus[i].all())
            self.assertTrue(m0.V == m1.V)
            self.assertTrue(m0.iteration == m1.iteration)
            for i in xrange(max(len(m0.Z), len(m1.Z))):
                self.assertTrue(m0.Z[i].all() == m1.Z[i].all())
            self.assertTrue(m0.top_doc.all() == m1.top_doc.all())
            self.assertTrue(m0.word_top.all() == m1.word_top.all())
            self.assertTrue(m0.inv_top_sums.all() == m1.inv_top_sums.all())
            m0 = LdaCgsSeq(c, 'document', K=10)
            m0.train(n_iterations=20)
            m0.save(tmp.name)
            m1 = LdaCgsSeq.load(tmp.name)
            self.assertTrue(not hasattr(m1, 'log_prob'))
        finally:
            os.remove(tmp.name)


    def test_LdaCgsQuerySampler_init(self):

        old_corp = Corpus([])
        old_corp.corpus = np.array([ 0, 1, 1, 0, 0, 1 ], dtype='i')
        old_corp.context_data = [ np.array([(3, ), (3, )], dtype=[('idx', 'i')]) ]
        old_corp.context_types = [ 'document' ]
        old_corp.words = np.array([ '0', '1' ], dtype='i')
        old_corp.words_int = { '0': 0, '1': 1 }

        new_corp = Corpus([])
        new_corp.corpus = np.array([ 0, 0 ], dtype='i')
        new_corp.context_data = [ np.array([(2, )], dtype=[('idx', 'i')]) ]
        new_corp.context_types = [ 'document' ]
        new_corp.words = np.array([ '0', '1' ], dtype='i')
        new_corp.words_int = { '0': 0, '1': 1 }

        m = LdaCgsSeq(corpus=old_corp, context_type='document', K=2, V=2)
        m.Z[:] = np.array([0, 0, 0, 1, 1, 1], dtype='i')
        m.word_top[:] = np.array([[ 1.01, 2.01 ],
                                  [ 2.01, 1.01 ]], dtype='d')
        m.top_doc[:] = np.array([[ 3.01, 0.01 ], 
                                 [ 0.01, 3.01 ]], dtype='d')
        m.inv_top_sums[:] = 1. / m.word_top.sum(0)

        q = LdaCgsQuerySampler(m, new_corpus=new_corp, old_corpus=old_corp)
        self.assertTrue(q.V==2)
        self.assertTrue(q.K==2)
        self.assertTrue(len(q.corpus)==2)
        self.assertTrue((q.corpus==new_corp.corpus).all())
        self.assertTrue(len(q.indices)==1)
        self.assertTrue((q.indices==
                         new_corp.view_metadata('document')['idx']).all())
        self.assertTrue(q.word_top.shape==(2, 2))
        self.assertTrue((q.word_top==m.word_top).all())
        self.assertTrue(q.top_doc.shape==(2, 1))
        self.assertTrue((q.top_doc==[[ 0.01 ],
                                     [ 0.01 ]]).all())
        self.assertTrue(q.inv_top_sums.shape==(2, ))
        self.assertTrue((q.inv_top_sums==m.inv_top_sums).all())
        self.assertTrue(q.alpha.shape==(2, 1))
        self.assertTrue((q.alpha==m.alpha).all())
        self.assertTrue(q.beta.shape==(2, 1))
        self.assertTrue((q.beta==m.beta).all())

        



suite = unittest.TestLoader().loadTestsFromTestCase(TestLdaCgsSeq)
unittest.TextTestRunner(verbosity=2).run(suite)
