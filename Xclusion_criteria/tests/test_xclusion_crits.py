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


from Xclusion_criteria.xclusion_crits import (
    check_in_md,
    check_factors,
    check_index,
    check_islist,
    check_key,
    check_numeric_indicator,
    check_var_in_md,
    get_criteria,
    do_filtering
)

ROOT = pkg_resources.resource_filename('Xclusion_criteria', 'tests')


class TestCrits(unittest.TestCase):

    def setUp(self):
        self.messages = []
        self.criteria = {}
        self.md = pd.DataFrame({
            'antibiotic_history': ['Yes', 'No', 'No'],
            'col2': [1., 2., 3.],
            'col3': [1.3, 1, 'missing']
        })
        self.nulls = ['missing', 'not applicable']

    def test_check_in_md(self):
        check_in_md(
            ['var_1', 'var_2', 'var_3'],
            ['var_1', 'var_2'],
            self.criteria,
            self.messages,
            ['missing', 'not applicable'],
            'init'
        )
        criteria = {'init': {
                ('var_1', '0'): ['missing', 'not applicable'],
                ('var_2', '0'): ['missing', 'not applicable']
            }
        }
        messages = ['Variable var_3 not in metadata (skipped)']
        self.assertEqual(self.criteria, criteria)
        self.assertEqual(self.messages, messages)

    def test_check_factors(self):
        test_message = []
        test_boolean, test_values = check_factors('col', '2', ['what', 'ever'], self.nulls, pd.DataFrame({'col': ['anything', 'else']}), test_message)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_values, ['what', 'ever'])
        self.assertEqual(test_message, [])
        test_message = []
        test_boolean, test_values = check_factors('col', '1', ['f4', 'f5'], self.nulls, pd.DataFrame({'col': ['f1', 'f2']}), test_message)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_values, [])
        self.assertEqual(test_message, ['Subset values for variable col not in table (skipped)'])
        test_message = []
        test_boolean, test_values = check_factors('col', '1', ['f1', 'f2', 'f3'], self.nulls, pd.DataFrame({'col': ['f1', 'f2']}), test_message)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_values, ['f1', 'f2'])
        self.assertEqual(test_message, ['[Warning] Subset values for variable col not in table\n - f3'])

    def test_check_index(self):
        test_boolean = check_index('0', ['f1', 'f2', 'f3'], [])
        self.assertEqual(test_boolean, False)
        test_boolean = check_index('1', ['f1', 'f2', 'f3'], [])
        self.assertEqual(test_boolean, False)
        test_message = []
        test_boolean = check_index('2', [None], test_message)
        self.assertEqual(test_boolean, True)
        test_message = []
        test_boolean = check_index('2', ['f1', 'f2', 'f3'], test_message)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_message,
                         ['For min-max subsetting, two-items list need: no min (or no max) should be "None"'])

    def check_is_list(self):
        test_messages = []
        test_boolean = check_islist('var', ['f1', 'f2', 'f3'], test_messages)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_messages, [])
        test_messages = []
        test_boolean = check_islist('var', 'f1', test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Values to subset for must be in a list format (var skipped)'])
        test_messages = []
        test_boolean = check_islist('var', False, test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Values to subset for must be in a list format (var skipped)'])
        test_messages = []
        test_boolean = check_islist('var', {'f1'}, test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Values to subset for must be in a list format (var skipped)'])

    def check_numeric_indicator(self):
        test_boolean = check_numeric_indicator('col', '0', [])
        self.assertEqual(test_boolean, False)
        test_boolean = check_numeric_indicator('col', '1', [])
        self.assertEqual(test_boolean, False)
        test_boolean = check_numeric_indicator('col', '2', [])
        self.assertEqual(test_boolean, False)
        test_messages = []
        test_boolean = check_numeric_indicator('col', 'x', test_messages)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_messages, ['Numeric indicator not "0", "1" or "2" (x) (col skipped)'])

    def check_var_in_md(self):
        test_messages = []
        test_boolean = check_var_in_md('col1', ['col1', 'col2'], test_messages)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_messages, [])
        test_boolean = check_var_in_md('col1', ['col2', 'col3'], test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Variable col1 not in metadata (skipped)'])

    def check_in_md(self):
        test_messages = []
        test_criteria = {}
        check_in_md(['col1', 'col2'], ['col1', 'col2', 'col3'],
                    test_criteria, test_messages, ['missing'], 'init')
        self.assertEqual(test_messages, [])
        self.assertEqual(test_criteria, {('col1', '0'): ['missing'], ('col2', '0'): ['missing']})
        test_messages = []
        test_criteria = {}
        check_in_md(['col1', 'col2'], ['col2', 'col3'],
                    test_criteria, test_messages, ['missing'], 'init')
        self.assertEqual(test_messages, ['Variable col1 not in metadata (skipped)'])
        self.assertEqual(test_criteria, {('col1', '0'): ['missing']})
        test_messages = []
        test_criteria = {}
        check_in_md(['col1', 'col2'], ['col3'],
                    test_criteria, test_messages, ['missing'], 'init')
        self.assertEqual(test_messages, ['Variable col1 not in metadata (skipped)',
                                         'Variable col2 not in metadata (skipped)'])
        self.assertEqual(test_criteria, {})

    def test_check_key(self):
        test_messages = []
        test_boolean = check_key('col,0', test_messages)
        self.assertEqual(test_boolean, False)
        self.assertEqual(test_messages, [])
        test_messages = []
        test_boolean = check_key('col+0', test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Must have a metadata variable and a numeric separated by a comma (",")'])
        test_messages = []
        test_boolean = check_key('col,0,', test_messages)
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Must have a metadata variable and a numeric separated by a comma (",")'])

    def test_get_criteria(self):

        no_comma = '%s/criteria/criteria_no_comma.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(no_comma, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(test_messages, ['Must have a metadata variable and a numeric separated by a comma (",")'])

        no_correct_index = '%s/criteria/criteria_no_correct_index.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(no_correct_index, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(test_messages, ['Numeric indicator not "0", "1" or "2" (9) (antibiotic_history skipped)'])

        no_index = '%s/criteria/criteria_no_index.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(no_index, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(test_messages, ['Must have a metadata variable and a numeric separated by a comma (",")'])

        var_not_in_md = '%s/criteria/criteria_var_not_in_md.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(var_not_in_md, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(test_messages, ['Variable not_in_md not in metadata (skipped)'])

        is_not_list = '%s/criteria/criteria_is_not_list.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(is_not_list, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(test_messages, ['Values to subset for must be in a list format (antibiotic_history skipped)'])

        wrong_minmax = '%s/criteria/criteria_wrong_minmax.yml' % ROOT
        test_messages = []
        test_criteria = get_criteria(wrong_minmax, self.md, self.nulls, test_messages)
        self.assertEqual(test_criteria, {})
        self.assertEqual(
            test_messages,
            ['For min-max subsetting, two-items list need: no min (or no max) should be "None"'])

    def test_do_filtering(self):

        md_abx_filt_y = pd.DataFrame({'antibiotic_history': ['Yes'], 'col2': [1.], 'col3': ['1.3']})
        test_name, test_boolean, test_md_abx_y = do_filtering(self.md, 'antibiotic_history', '1', ['Yes'], [], [])
        md_abx_filt_y.col3 = md_abx_filt_y.col3.astype('object')
        test_md_abx_y.col3 = md_abx_filt_y.col3.astype('object')
        self.assertEqual(test_name, 'antibiotic_history')
        self.assertEqual(test_boolean, False)
        assert_frame_equal(md_abx_filt_y, test_md_abx_y)

        md_abx_filt_n = pd.DataFrame({'antibiotic_history': ['No', 'No'], 'col2': [2., 3.], 'col3': [1, 'missing']})
        test_name, test_boolean, test_md_abx_x = do_filtering(self.md, 'antibiotic_history', '1', ['No'], [], [])
        md_abx_filt_n.index = range(md_abx_filt_n.shape[0])
        test_md_abx_x.index = range(test_md_abx_x.shape[0])
        self.assertEqual(test_name, 'antibiotic_history')
        self.assertEqual(test_boolean, False)
        assert_frame_equal(md_abx_filt_n, test_md_abx_x)

        md_abx_filt_n = pd.DataFrame({'antibiotic_history': ['No', 'No'], 'col2': [2., 3.], 'col3': [1, 'missing']})
        test_name, test_boolean, test_md_abx_x = do_filtering(self.md, 'antibiotic_history', '0', ['Yes'], [], [])
        md_abx_filt_n.index = range(md_abx_filt_n.shape[0])
        test_md_abx_x.index = range(test_md_abx_x.shape[0])
        self.assertEqual(test_name, 'No_antibiotic_history')
        self.assertEqual(test_boolean, False)
        assert_frame_equal(md_abx_filt_n, test_md_abx_x)

        md_abx_filt_mm = pd.DataFrame({'antibiotic_history': ['Yes', 'No'], 'col2': [1., 2.], 'col3': ['1.3', '1']})
        test_name, test_boolean, test_md_abx_mm = do_filtering(self.md, 'col2', '2', ['None', 3], ['col2'], [])
        # weirdly, if the two col3 contents are "object" and identical, the test fails, hence:
        md_abx_filt_mm.col3 = md_abx_filt_mm.col3.astype('float')
        test_md_abx_mm.col3 = test_md_abx_mm.col3.astype('float')
        md_abx_filt_mm.index = range(md_abx_filt_mm.shape[0])
        test_md_abx_mm.index = range(test_md_abx_mm.shape[0])
        self.assertEqual(test_name, 'Range_col2')
        self.assertEqual(test_boolean, False)
        assert_frame_equal(md_abx_filt_mm, test_md_abx_mm)

        md_abx_filt_mm = pd.DataFrame({'antibiotic_history': ['No'], 'col2': [2.], 'col3': ['1']})
        test_name, test_boolean, test_md_abx_mm = do_filtering(self.md, 'col2', '2', [1, 3], ['col2'], [])
        # weirdly, if the two col3 contents are "object" and identical, the test fails, hence:
        md_abx_filt_mm.col3 = md_abx_filt_mm.col3.astype('float')
        test_md_abx_mm.col3 = test_md_abx_mm.col3.astype('float')
        md_abx_filt_mm.index = range(md_abx_filt_mm.shape[0])
        test_md_abx_mm.index = range(test_md_abx_mm.shape[0])
        self.assertEqual(test_name, 'Range_col2')
        self.assertEqual(test_boolean, False)
        assert_frame_equal(md_abx_filt_mm, test_md_abx_mm)

        test_messages = []
        test_name, test_boolean, output_md = do_filtering(self.md, 'col2', '2', ['None', 3], ['col3'], test_messages)
        self.assertEqual(test_name, '')
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['Metadata variable col2 is not numerical (skipping)'])

        test_messages = []
        test_name, test_boolean, output_md = do_filtering(self.md, 'col2', '2', ['None', 'None'], ['col2'], test_messages)
        self.assertEqual(test_name, '')
        self.assertEqual(test_boolean, True)
        self.assertEqual(test_messages, ['[Warning] Both numerical bounds for col2 are "None" (skipping)'])


if __name__ == '__main__':
    unittest.main()
