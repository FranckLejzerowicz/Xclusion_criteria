# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import yaml
import pandas as pd
from os.path import isfile


def get_criteria(p_criterion: tuple, i_criteria: str,
                 metadata: pd.DataFrame, nulls: list) -> dict:
    """
    Collect the inclusion/exclusion criteria to
    apply based on the yaml file and superseded
    by those passed in command line.

    Parameters
    ----------
    p_criterion : tuple
        Inclusion/exclusion criteria passed
        from command line.
    i_criteria: str
        Path to yml config file for the different
        inclusion/exclusion criteria to apply.
    metadata : pd.DataFrame
        Metadata table.

        Factors to be interpreted as np.nan.

    Returns
    -------
    criteria : dict
        Inclusion/exclusion criteria to apply.
    """
    criteria = {}
    if i_criteria and isfile(i_criteria):
        with open(i_criteria) as handle:
            parsed_criteria = yaml.load(handle, Loader=yaml.FullLoader)
            for key, values in parsed_criteria.items():
                if key == 'no_nan':
                    for var in values:
                        if var not in metadata.columns:
                            print('no-nan variable %s not in metadata (skipped)' % var)
                        criteria[(var, '0')] = nulls
                    continue
                if ',' not in key or len(key.split(',')) != 2:
                    print('Must have a metadata variable and a numeric separated by a comma (",")\nExiting')
                    continue
                var, index = key.split(',')
                if var not in metadata.columns:
                    print('Variable %s not in metadata (skipped)' % var)
                    continue
                if index not in ['0', '1', '2']:
                    print('Numeric indicator not "0", "1" or "2" (%s) (%s skipped)' % (index, var))
                    continue
                if not isinstance(values, list):
                    print('Values to subset for must be in a list format (%s skipped)' % var)
                    continue
                if index == '2' and len(values) != 2:
                    print('For min-max subsetting, two-items list need: no min (or no max) should be "None"')
                    continue
                else:
                    values_set = set([x for x in values if x!='NULLS'])
                    md_factors = set(metadata[var])
                    if not len(values_set & md_factors):
                        print('Subset values for variable %s for not in table (skipped)' % var)
                        continue
                    elif len(values_set) > len(values_set & md_factors):
                        values_out = list(values_set ^ (values_set & md_factors))
                        print('[Warning] Subset values for variable %s for not in table\n'
                              ' - %s' % (var, '\n - '.join(values_out)))
                    criteria[(var, index)] = values

    if p_criterion:
        for criterion in p_criterion:
            var, index, values_ = criterion
            if var not in metadata.columns:
                print('Variable %s not in metadata (Skipped)' % var)
                continue
            if index not in ['0', '1', '2']:
                print('Numeric indicator not "0", "1" or "2" (%s) (Skipped)' % index)
                continue
            values = values_.split('/')
            if index == '2' and len(values) != 2:
                print('For min-max subsetting, two-items list need: no min (or no max) should be "None"')
                continue
            else:
                values_set = set(values)
                md_factors = set(metadata[var])
                if not len(values_set & md_factors):
                    print('Subset values for variable %s for not in table (skipped)' % var)
                    continue
                elif len(values_set) > len(values_set & md_factors):
                    values_out = list(values_set ^ (values_set & md_factors))
                    print('[Warning] Subset values for variable %s for not in table\n'
                          ' - %s' % (var, '\n - '.join(values_out)))
                criteria[(var, index)] = values

    return criteria


def apply_criteria(metadata: pd.DataFrame, criteria: dict,
                   numerical: list) -> tuple:
    """
    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata table.
    criteria : dict
        Inclusion/exclusion criteria to apply.
    numerical : list
        Metadata variables that are numeric.

    Returns
    -------
    flowchart : list
        Steps of the workflow with samples counts.
    flowchart2 : list
        Steps of the workflow with samples counts (simpler representation).
    included : pd.DataFrame
        Metadata for the included samples only.
    """

    flowchart = []
    flowchart2 = []
    included = metadata.copy()
    first_step = True
    prev_nam, prev_count, cur_name, cur_count = None, None, None, None
    for (var, index), values in criteria.items():

        # filter based on the criteria, and report the delta and the number of samples left
        if index == '0':
            cur_name = 'No_%s' % var
            included = included.loc[~included[var].fillna('nan').str.lower().isin([x.lower() for x in values])]
        elif index == '1':
            cur_name = var
            included = included.loc[included[var].isin(values)]
        elif index == '2':
            if var not in numerical:
                print('Metadata variable %s is not numerical (skipping)' % var)
                continue
            cur_name = 'Range_%s' % var
            crit_min = values[0]
            if crit_min:
                included = included.loc[(included[var].fillna((crit_min - 1)) > crit_min)]
            crit_max = values[1]
            if crit_max:
                included = included.loc[(included[var].fillna((crit_max + 1)) < crit_max)]

        cur_count = included.shape[0]
        if first_step:
            flowchart.append('Input_metadata_%s -> %s_%s' % (metadata.shape[0], cur_name, cur_count))
            flowchart2.extend([
                ['Input metadata', metadata.shape[0], None, None, None],
                [cur_name, cur_count, str(var), '\n'.join(map(str, values)), str(index)]
            ])
            first_step = False
        else:
            flowchart.append('%s_%s -> %s_%s' % (prev_nam, prev_count, cur_name, cur_count))
            flowchart2.append([cur_name, cur_count, str(var), '\n'.join(map(str, values)), str(index)])
        prev_nam, prev_count = cur_name, cur_count
    return flowchart, flowchart2, included
