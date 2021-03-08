# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import numpy as np
import pandas as pd

from Xclusion_criteria.xclusion_dtypes import (
    get_dtypes,
    get_dtypes_init,
    get_dtypes_final,
    check_dtype_object,
    split_variables_types,
    check_num_cat_lists
)


class TestDtypes(unittest.TestCase):

    def setUp(self):

        self.dtypes = {
            'num': 'int',
            'float': 'float',
            'num_nan': 'int',
            'num_str_ok': 'int',
            'num_str_notok': 'int',
            'cat_1': 'object',
            'cat_nan': 'object',
            'cat_str_ok': 'object'
        }
        self.criteria = {
            ('cat_1', '0'): ['f1', 'f2', 'f3'], ('cat_nan', '1'): ['f1', 'f2']}

        self.nulls = ['missing', 'not applicable']
        self.dtype_pd1 = pd.DataFrame({
            'sample_name': ['sam_1', 'sam_2', 'sam_3'],
            'col1': [1, 2, np.nan],
            'col2': [1.3, 1.5, 3.0],
            'col3': ['x', 'y', 'z'],
            'col4': [0, 1, 2],
            'col5': [1.2, 1.5, 'missing']
        })
        self.test_dtype_pd1 = {
            'col1': 'float',
            'col2': 'float',
            'col3': 'object',
            'col4': 'int',
            'col5': 'float'
        }
        self.dtype_pd2 = pd.DataFrame({
            'sample_name': ['sam_1', 'sam_2', 'sam_3'],
            'cat_1': ['a', 'b', 'c'],
            'cat_2': ['a', 'b', False],
            'cat_3': [1, 1.3, True],
            'cat_4': ['a', 'b', 2.4],
            'cat_5': ['a', 'b', np.nan],
            'float': [1.2, 1.4, 1],
            'int': [1, 2, 3],
            'check': [1, 1.3, 'not applicable']})
        self.test_dtype_pd2 = {
            'cat_1': 'object',
            'cat_2': 'object',
            'cat_3': 'object',
            'cat_4': 'object',
            'cat_5': 'object',
            'check': 'float',
            'float': 'float',
            'int': 'int'
        }

    def test_split_variables_types(self):
        num, cat = [], []
        split_variables_types(self.dtypes, num, cat)
        self.assertEqual(sorted(num), sorted(['num','float','num_nan', 'num_str_ok','num_str_notok']))
        self.assertEqual(sorted(cat), sorted(['cat_1','cat_nan', 'cat_str_ok']))

    def test_get_dtypes_init(self):
        test_dtypes_init = {
            'col1': ['float'],
            'col2': ['float'],
            'col3': ['object', 'object'],
            'col4': ['int'],
            'col5': ['object', 'check']
        }
        self.assertEqual(get_dtypes_init(self.dtype_pd1), test_dtypes_init)
        cur_dict = {
            'cat_1': ['object', 'object'],
            'cat_2': ['object', 'object'],
            'cat_3': ['object', 'object'],
            'cat_4': ['object', 'check'],
            'cat_5': ['object', 'check'],
            'check': ['object', 'check'],
            'float': ['float'],
            'int': ['int']
        }
        self.assertEqual(get_dtypes_init(self.dtype_pd2), cur_dict)

    def test_get_dtypes_final(self):

        self.assertEqual(
            get_dtypes_final(self.dtype_pd1, self.nulls,
                             get_dtypes_init(self.dtype_pd1)),
            self.test_dtype_pd1
        )
        self.assertEqual(
            get_dtypes_final(self.dtype_pd2, self.nulls,
                             get_dtypes_init(self.dtype_pd2)),
            self.test_dtype_pd2
        )

    def test_check_dtype_object(self):
        dtype = check_dtype_object(pd.Series(['a', 'b', 'c']))
        self.assertEqual(dtype, ['object', 'object'])
        dtype = check_dtype_object(pd.Series(['a', 'b', False]))
        self.assertEqual(dtype, ['object', 'object'])
        dtype = check_dtype_object(pd.Series([1, 1.3, True]))
        self.assertEqual(dtype, ['object', 'object'])
        dtype = check_dtype_object(pd.Series([1.2, 1.4, 1]))
        self.assertEqual(dtype, ['object', 'float'])
        dtype = check_dtype_object(pd.Series([1, 2, 3]))
        self.assertEqual(dtype, ['object', 'float'])
        dtype = check_dtype_object(pd.Series(['a', 'b', 2.4]))
        self.assertEqual(dtype, ['object', 'check'])
        dtype = check_dtype_object(pd.Series(['a', 'b', np.nan]))
        self.assertEqual(dtype, ['object', 'check'])
        dtype = check_dtype_object(pd.Series([1, 1.3, 'not applicable']))
        self.assertEqual(dtype, ['object', 'check'])

    def test_get_dtypes(self):
        test_dtypes1 = get_dtypes(self.dtype_pd1, self.nulls)
        self.assertEqual(self.test_dtype_pd1, test_dtypes1)
        test_dtypes2 = get_dtypes(self.dtype_pd2, self.nulls)
        self.assertEqual(self.test_dtype_pd2, test_dtypes2)

    def test_check_num_cat_lists(self):

        boolean, test_message = check_num_cat_lists([], ['1'])
        self.assertEqual(boolean, True)
        self.assertEqual(test_message, 'Not enough numerical variables in the metadata (0)')

        boolean, test_message = check_num_cat_lists(['1'], ['1'])
        self.assertEqual(boolean, True)
        self.assertEqual(test_message, 'Not enough numerical variables in the metadata (1)')

        boolean, test_message = check_num_cat_lists(['1', '2'], [])
        self.assertEqual(boolean, True)
        self.assertEqual(test_message, 'Not enough categorical variables in the metadata (0)')

        boolean, test_message = check_num_cat_lists(['1', '2'], ['1'])
        self.assertEqual(boolean, False)
        self.assertEqual(test_message, '')


if __name__ == '__main__':
    unittest.main()
