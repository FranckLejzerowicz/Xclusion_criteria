# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
from Xclusion_criteria._xclusion_io import read_i_criteria


def check_factors(var: str, values: list, metadata: pd.DataFrame, messages: list) -> tuple:
    """
    Parameters
    ----------
    var : str
        Metadata variable in criteria.
    values : list
        Metadata variables in criteria.
    metadata : pd.DataFrame
        Metadata table.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    common_vars : list
        Variable present in both the passed values and
        the metadata factors for the current variable.
    """
    boolean = False
    values_set = set([x for x in values if x != 'NULLS'])
    md_factors = set(metadata[var])
    common_vars = values_set & md_factors
    if not len(common_vars):
        messages.append('Subset values for variable %s for not in table (skipped)' % var)
        boolean = True
    elif len(values_set) > len(common_vars):
        values_out = list(values_set ^ common_vars)
        messages.append('[Warning] Subset values for variable %s for not in table\n'
                        ' - %s' % (var, '\n - '.join(values_out)))
    return boolean, sorted(common_vars)



def check_index(index: str, values: list, messages: list) -> bool:
    """
    Parameters
    ----------
    index : str
        Numeric indicator.
    values : list
        Metadata variables in criteria.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    """
    boolean = False
    if index == '2' and len(values) != 2:
        messages.append('For min-max subsetting, two-items list need: no min (or no max) should be "None"')
        boolean = True
    return boolean


def check_islist(var: str, values, messages: list) -> bool:
    """
    Parameters
    ----------
    var : str
        Metadata variable in criteria.
    values : list or else
        Should be a list of factors.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    """
    boolean = False
    if not isinstance(values, list):
        messages.append('Values to subset for must be in a list format (%s skipped)' % var)
        boolean = True
    return boolean


def check_numeric_indicator(var: str, index: str, messages: list) -> bool:
    """
    Parameters
    ----------
    var : str
        Metadata variable in criteria.
    index : str
        Numeric indicator.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    """
    boolean = False
    if index not in ['0', '1', '2']:
        messages.append('Numeric indicator not "0", "1" or "2" (%s) (%s skipped)' % (index, var))
        boolean = True
    return boolean


def check_var_in_md(var: str, columns: list, messages: list) -> bool:
    """
    Parameters
    ----------
    var : str
        Metadata variable in criteria.
    columns : list
        Metadata variables in table.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    """
    boolean = False
    if var not in columns:
        messages.append('Variable %s not in metadata (skipped)' % var)
        boolean = True
    return boolean


def check_in_md(values: list, columns: list, criteria: dict,
                messages: list, nulls: list) -> None:
    """
    Parameters
    ----------
    values : list
        Metadata variables in criteria.
    columns : list
        Metadata variables in table.
    criteria : dict
        Inclusion/exclusion criteria to apply.
    messages : list
        Message to print in case of error.
    nulls : list
        Factors to be interpreted as np.nan.
    """
    for var in values:
        if check_var_in_md(var, columns, messages):
            continue
        criteria[(var, '0')] = nulls


def check_key(key: str, messages: list) -> bool:
    """
    Parameters
    ----------
    key : str
        Current criterion.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    """
    boolean = False
    if ',' not in key or len(key.split(',')) != 2:
        messages.append('Must have a metadata variable and a numeric separated by a comma (",")')
        boolean = True
    return boolean


def get_criteria(p_criterion: tuple, i_criteria: str,
                 metadata: pd.DataFrame, nulls: list) -> tuple:
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
    nulls : list
        Factors to be interpreted as np.nan.

    Returns
    -------
    criteria : dict
        Inclusion/exclusion criteria to apply.
    message : str
        Message to print in case of error.
    """
    messages, criteria = [], {}
    for key, values in read_i_criteria(i_criteria).items():

        if key == 'no_nan':
            check_in_md(values, list(metadata.columns), criteria, messages, nulls)
            continue
        if check_key(key, messages):
            continue
        var, index = key.split(',')
        if check_var_in_md(var, list(metadata.columns), messages):
            continue
        if check_numeric_indicator(var, index, messages):
            continue
        if check_islist(var, values, messages):
            continue
        if check_index(index, values, messages):
            continue
        else:
            boolean, common_values = check_factors(var, values, metadata, messages)
            if boolean:
                continue
            criteria[(var, index)] = common_values

    if p_criterion:
        for criterion in p_criterion:
            var, index, values_ = criterion
            if check_var_in_md(var, list(metadata.columns), messages):
                continue
            if check_numeric_indicator(var, index, messages):
                continue
            values = values_.split('/')
            if check_index(index, values, messages):
                continue
            else:
                boolean, common_values = check_factors(var, values, metadata, messages)
                if boolean:
                    continue
                criteria[(var, index)] = common_values
    return criteria, messages


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
