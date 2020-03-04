# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pandas as pd
import pkg_resources

from pandas.testing import assert_frame_equal

from Xclusion_criteria._xclusion_plot import get_parsed_plot_groups

ROOT = pkg_resources.resource_filename('Xclusion_criteria', 'tests')

class MyPlot(unittest.TestCase):

    def test_get_parsed_plot_groups(self):

        not_exists = '%s/plot/non_existent_file.yml' % ROOT
        plot_groups = get_parsed_plot_groups(not_exists)
        self.assertEqual(plot_groups, {})

        plot_ok = '%s/plot/plot_ok.yml' % ROOT
        plot_groups = get_parsed_plot_groups(plot_ok)
        self.assertEqual(plot_groups, {'categories': ['age_cat']})

if __name__ == '__main__':
    unittest.main()
