# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pkg_resources
import pandas as pd

from os.path import abspath
from pandas.testing import assert_frame_equal

from Xclusion_criteria._xclusion_md import read_meta_pd
# from Xclusion_criteria._xclusion_dtypes import get_dtypes, split_variables_types

ROOT = pkg_resources.resource_filename('Xclusion_criteria', 'tests')


class TestMd(unittest.TestCase):

    def setUp(self):
        self.md_res = pd.DataFrame({
            'col1': ['A1', 'B1', 'C1'],
            'col2': ['A2', 'B2', 'C2'],
            'col3': ['A3', 'B3', 'C3']
        }, index = ['A', 'B', 'C'])
        self.md_res.index.name = 'sample_name'

    def test_read_meta_pd(self):
        md_comma_fp = '%s/metadata/test_md/md_commas.tsv' % ROOT
        md_comma = read_meta_pd(md_comma_fp)
        assert_frame_equal(md_comma, self.md_res)
        md_colons_fp = '%s/metadata/test_md/md_colons.tsv' % ROOT
        md_colons = read_meta_pd(md_colons_fp)
        assert_frame_equal(md_colons, self.md_res)
        md_tabs_fp = '%s/metadata/test_md/md_tabs.tsv' % ROOT
        md_tabs = read_meta_pd(md_tabs_fp)
        assert_frame_equal(md_tabs, self.md_res)
        md_upper_fp = '%s/metadata/test_md/md_upper.tsv' % ROOT
        md_upper = read_meta_pd(md_upper_fp)
        assert_frame_equal(md_upper, self.md_res)
        md_missing_fp = '%s/metadata/test_md/md_missing.tsv' % ROOT
        md_missing = read_meta_pd(md_missing_fp)
        assert_frame_equal(md_missing, self.md_res)


# class TestDtypes(unittest.TestCase):
#
#     def setUp(self):
#         self.md_res = pd.DataFrame({
#             'col1': [1, 2, np.nan],
#             'col2': [1.3, 1.5, 3.0],
#             'col3': ['x', 'y', 'z']
#         }, index = ['A', 'B', 'C'])
#         self.md_res.index.name = 'sample_name'
#
#     def test_read_meta_pd(self):
#         dtype_1_fp = '%s/metadata/test_dtypes/dtype_1_fp.tsv' % ROOT
#         dtype_1 = read_meta_pd(dtype_1_fp)
#         assert_frame_equal(dtype_1, self.md_res)


if __name__ == '__main__':
    unittest.main()
