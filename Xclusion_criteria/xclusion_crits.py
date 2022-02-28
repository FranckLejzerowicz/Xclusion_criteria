# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
from Xclusion_criteria.xclusion_io import read_i_criteria


def check_factors(var: str, index: str, values: list, nulls: list,
                  metadata: pd.DataFrame, messages: list) -> tuple:
    """Checks that subset values for the
    current variable are in metadata.

    Parameters
    ----------
    var : str
        Metadata variable in criteria.
    index : str
        Numeric indicator.
    values : list
        Metadata variables in criteria.
    nulls : list
        Factors to be interpreted as np.nan.
    metadata : pd.DataFrame
        Metadata table.
    messages : list
        Message to print in case of error.

    Returns
    -------
    boolean : bool
        Whether to keep the key/value or not.
    common_vars_list : list
        Variable present in both the passed values and
        the metadata factors for the current variable.

    """
    boolean = False
    if index == '2':
        return boolean, values
    else:
        values_set = set([x for x in values if x!='NULLS'])
        md_factors = set(metadata[var])
        common_vars = values_set & md_factors
        if not len(common_vars):
            messages.append('Subset values for variable %s not in table (skipped)' % var)
            boolean = True
        elif len(values_set) > len(common_vars):
            values_out = list(values_set ^ common_vars)
            messages.append('[Warning] Subset values for variable %s not in table\n'
                            ' - %s' % (var, '\n - '.join(values_out)))
        common_vars_list = sorted(common_vars)
        if 'NULLS' in values:
            common_vars_list.extend(nulls)
        return boolean, common_vars_list


def check_index(index: str, values: list, messages: list) -> bool:
    """Checks that min-max values are a two-items list.

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
    """Checks that subsetting values are in a list.

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
    """Checks that variable's numeric
    indicator is "0", "1" or "2".

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
    """Checks that variable is in the metadata.

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
    if var not in columns:
        messages.append('Variable %s not in metadata (skipped)' % var)
        return True
    return False


def check_in_md(values: list, columns: list, criteria: dict,
                messages: list, nulls: list, step: str) -> None:
    """Check that variables are present in the metadata.

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
    step : str
        The type of criterion to apply (init, filter, add).

    """
    for var in values:
        # Checks that variable is in the metadata.
        if check_var_in_md(var, columns, messages):
            continue
        if step in criteria:
            criteria[step][(var, '0')] = nulls
        else:
            criteria[step] = {(var, '0'): nulls}


def check_key(key: str, messages: list) -> bool:
    """Checks that criterion has a metadata variable
    and a numeric separated by a comma (",").

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


def check_filtering_criteria(init_filter: dict, metadata: pd.DataFrame,
                             messages: list, criteria: dict,
                             nulls: list, step: str) -> None:
    """Check the passed criteria and
    collect those that are properly formatted.

    Parameters
    ----------
    init_filter : dict
        Inclusion/exclusion criteria to apply.
    metadata : pd.DataFrame
        Metadata table.
    messages : list
        Message to print in case of error.
    criteria : dict
        Fill the yml content, including all inclusion/exclusion criteria.
    nulls : list
        Factors to be interpreted as np.nan.
    step : str
        The type of criterion to apply (init, filter, add)

    """
    for variable_index, values in init_filter.items():
        # Checks that criterion has a metadata variable
        # and a numeric separated by a comma (",").
        if check_key(variable_index, messages):
            continue
        variable, index = variable_index.split(',')
        # Checks that variable is in the metadata.
        if check_var_in_md(variable, list(metadata.columns), messages):
            continue
        # Checks that variable's numeric indicator is "0", "1" or "2"
        if check_numeric_indicator(variable, index, messages):
            continue
        # Checks that subsetting values are in a list
        if check_islist(variable, values, messages):
            continue
        # Checks that min-max values are a two-items list
        if check_index(index, values, messages):
            continue
        else:
            # Checks that subset values for the
            # current variable are in metadata
            boolean, common_values = check_factors(
                variable, index, values, nulls, metadata, messages
            )
            # this is true if the variable is not in the metadata
            if boolean:
                continue
            # fill the correctly formatted criteria
            if step in criteria:
                criteria[step][variable, index] = common_values
            else:
                criteria[step] = {(variable, index): common_values}


def get_criteria(i_criteria: str, metadata: pd.DataFrame, nulls: list,
                 messages: list) -> dict:
    """
    Collect the inclusion/exclusion criteria to
    apply based on the yaml file and superseded
    by those passed in command line.

    Parameters
    ----------
    i_criteria: str
        Path to yml config file for the different
        inclusion/exclusion criteria to apply.
    metadata : pd.DataFrame
        Metadata table.
    nulls : list
        Factors to be interpreted as np.nan.
    messages : list
        Message to print in case of error.

    Returns
    -------
    criteria : dict
        Full yml content, including all inclusion/exclusion criteria.

    """
    criteria = {}
    # Read the yaml criteria file
    criteria_dict = read_i_criteria(i_criteria)
    # for each criteria application level and its criteria to apply
    for level, values in criteria_dict.items():
        # for the filtering / grafting criteria
        if level in ['init', 'filter', 'add']:
            # Check the passed criteria and collect
            # those that are properly formatted
            check_filtering_criteria(
                values,
                metadata,
                messages,
                criteria,
                nulls,
                level
            )
        # for the must-be non-nan variables
        elif level == 'no_nan':
            # check that they are present in the metadata
            check_in_md(
                values,
                list(metadata.columns),
                criteria,
                messages,
                nulls,
                level
            )
            continue
        # else:
        #     raise(!)
    return criteria


def do_filtering(input_pd: pd.DataFrame, var: str, index: str,
                 values: list, numerical: list, messages: list) -> tuple:
    """

    Parameters
    ----------
    input_pd : pd.DataFrame
        Metadata with all current to filter.
    var : str
        Metadata variable in criteria.
    index : str
        Numeric indicator.
    values : list
        Metadata variables in criteria.
    numerical : list
        Metadata variables that are numeric.
    messages : list
        Message to print in case of error.

    Returns
    -------
    cur_name : str
        Name of the current selection step.
    boolean : bool
        Whether to keep the key/value or not.
    included : pd.DataFrame
        Metadata for the included samples only.
    """
    cur_name = ''
    boolean = False
    included = input_pd.copy()
    # filter based on the criteria, and report the
    # delta and the number of samples left
    if index == '0':
        cur_name = 'No_%s' % var
        included = included.loc[~included[var].fillna('nan').isin(values)]
    elif index == '1':
        cur_name = var
        included = included.loc[included[var].isin(values)]
    elif index == '2':
        if var not in numerical:
            messages.append(
                'Metadata variable %s is not numerical (skipping)' % var)
            return cur_name, True, included
        crit_min, crit_max = values
        if crit_min == 'None' and crit_max == 'None':
            messages.append(
                '[Warning] Both numerical bounds for %s'
                ' are "None" (skipping)' % var)
            return cur_name, True, included
        cur_name = 'Range_%s' % var
        if crit_min != 'None':
            included = included.loc[(included[var].fillna(
                (float(crit_min) - 0.0001)) > float(crit_min))]
        if crit_max != 'None':
            included = included.loc[(included[var].fillna(
                    (float(crit_max) + 0.0001)) < float(crit_max))
            ]
    return cur_name, boolean, included


def apply_step_criteria(metadata: pd.DataFrame, criteria: dict,
                        numerical: list, messages: list,
                        flowcharts: dict, step: str) -> pd.DataFrame:
    """Apply the filtering criteria for the current step.
    There are three possible steps for now:
        - init      initial filtering on the raw metadata.
        - filter    selection based on the initially included samples.
        - add       another filtering on the initially included samples.

    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata table.
    criteria : dict
        Inclusion/exclusion criteria to apply.
    numerical : list
        Metadata variables that are numeric.
    messages : list
        Message to print in case of error.
    flowcharts : dict
        Steps of the workflow with samples counts (simpler representation).
    step : str
        The type of criterion to apply (init, filter, add)

    Returns
    -------
    included : pd.DataFrame
        Metadata for the included samples only.
    """

    flowchart = []
    included = metadata.copy()
    first_step = True
    for (var, index), values in criteria[step].items():

        cur_name, boolean, included = do_filtering(
            included, var, index, values, numerical, messages)
        if boolean:
            continue

        cur_count = included.shape[0]
        if first_step:
            flowchart.extend([
                ['%s metadata' % step, metadata.shape[0], None, None, None],
                [cur_name, cur_count, str(var),
                 '\n'.join(map(str, values)), str(index)]
            ])
            first_step = False
        else:
            flowchart.append([cur_name, cur_count, str(var),
                              '\n'.join(map(str, values)), str(index)])
    flowcharts[step] = flowchart
    return included


def apply_criteria(metadata: pd.DataFrame, criteria: dict,
                   numerical: list, messages: list) -> tuple:
    """Apply filtering criteria to subset the metadata.

    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata table.
    criteria : dict
        Inclusion/exclusion criteria to apply.
    numerical : list
        Metadata variables that are numeric.
    messages : list
        Message to print in case of error.

    Returns
    -------
    flowcharts : dict
        Steps of the workflow with samples counts (simpler representation).
    included : pd.DataFrame
        Metadata for the included samples only.

    """

    flowcharts = {}
    # Perform initial filtering on the raw metadata
    # -> init_included = initially included samples
    if 'init' in criteria:
        init_included = apply_step_criteria(
            metadata, criteria, numerical, messages, flowcharts, 'init')
        print('init', metadata.shape)
    else:
        init_included = metadata.copy()

    # Perform a selection based on the initially included samples
    # -> add_included = keep samples to be re-added later
    if 'add' in criteria:
        add_included = apply_step_criteria(
            init_included, criteria, numerical, messages, flowcharts, 'add')
    else:
        add_included = pd.DataFrame()

    if 'no_nan' in criteria:
        nan_included = apply_step_criteria(
            init_included, criteria, numerical, messages, flowcharts, 'no_nan')
    else:
        nan_included = init_included.copy()

    # Perform another filtering on the initially included samples
    # -> filter_included = finally included samples
    if 'filter' in criteria:
        filter_included = apply_step_criteria(
            nan_included, criteria, numerical, messages, flowcharts, 'filter')
    else:
        filter_included = nan_included.copy()

    # if there were samples to be re-added later
    if add_included.shape[0]:
        # only get the samples not already in finally included samples
        common_sams = set(filter_included.index) & set(add_included.index)
        added_sams = set(add_included.index) ^ common_sams
        if common_sams:
            messages.append(
                '%s samples not removed by criteria of "init"/"filter" steps re-added by '
                'criteria of "add" step (not to worry: duplicates are dropped).' % len(common_sams)
            )
        # add the samples add_included samples to the filter_included samples
        included = pd.concat([filter_included, add_included], axis=0, sort=False)

        # in
        flowcharts['filter'].append([
            '"add" samples',
            included.shape[0],
            'adding %s samples' % len(added_sams),
            '(see "add" criteria)',
            None
        ])
    else:
        included = filter_included.copy()
    return flowcharts, included
