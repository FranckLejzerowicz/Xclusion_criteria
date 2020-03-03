# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np
import pandas as pd


def get_dtypes_final(md: pd.DataFrame, nulls: list, dtypes_init: dict) -> dict:
    """
    Refine the inference of the current variables' dtypes

    Parameters
    ----------
    md : pd.DataFrame
        Current metadata table.
    nulls : list
        Factors to be interpreted as np.nan.
    dtypes_init : dict
        Inferred dtype(s) per variable.
        Key     = variable
        Value   = dtype(s) list
            dtype(s) list possibilities:
                ['int']              : factors are integers
                ['float']            : factors are floats
                ['object', 'object'] : factors are strings
                ['object', 'float']  : factors are float (or np.nan)
                ['object', 'check']  : factors are float + "polluting" string

    Returns
    -------
    dtypes_final : dict
        Key     = variable
        Value   = dtype
    """
    dtypes_final = {}
    for variable, dtypes in dtypes_init.items():
        if dtypes[-1] == 'check':
            factors = md[variable].copy()
            nan_tf = pd.Series(factors.astype(str).str.lower()).str.contains('|'.join(nulls))
            factors[nan_tf] = np.nan
            for val in factors.unique().tolist():
                if str(val) != 'nan':
                    try:
                        float(val)
                    except ValueError:
                        dtypes_final[variable] = 'object'
                        break
            else:
                dtypes_final[variable] = 'float'
                md[variable] = factors
                md[variable] = md[variable].astype('float64')
        else:
            dtypes_final[variable] = dtypes[-1]
    return dtypes_final


def get_dtypes_init(md: pd.DataFrame) -> dict:
    """
    Infer the variable's dtypes of each column.

    Parameters
    ----------
    md : pd.DataFrame
        Current metadata table.

    Returns
    -------
    dtypes_init : dict
        Inferred dtype(s) per variable.
        Key     = variable
        Value   = dtype(s) list
            dtype(s) list possibilities:
                ['int']              : factors are integers
                ['float']            : factors are floats
                ['object', 'object'] : factors are strings
                ['object', 'float']  : factors are float (or np.nan)
                ['object', 'check']  : factors are float + "polluting" string
    """
    dtypes_init = {}
    for variable in md.columns[1:]:
        # for the current metadata table's column
        native_type = str(md[variable].dtypes)   # get the current, pandas dtype
        if native_type.startswith('int'):
            dtypes_init[variable] = ['int']
        elif native_type.startswith('float'):
            dtypes_init[variable] = ['float']
        else:
            dtypes_init[variable] = check_dtype_object(md[variable])
    return dtypes_init


def check_dtype_object(factors: pd.Series) -> list:
    """
    Check variable's factors.

    Parameters
    ----------
    factors : pd.Series
        Factors of the current metadata variable.

    Returns
    -------
    d_type : str
        two-items list for the dtype status of the
        current metadata variable. Could be:
            ['object', 'object'] : factors are strings
            ['object', 'float']  : factors are float (or np.nan)
            ['object', 'check']  : factors are float + "polluting" string
            """
    d_type = ['object']
    has_nan = False
    has_float = False
    has_non_float = False
    has_tf = False
    # for the unique factors of the current variable
    for val in factors.unique().tolist():
        if str(val) == 'nan':
            has_nan = True # if np.nan in the factors
        elif str(val) in ['True', 'False']:
            has_tf = True  # if np.nan in the factors
        else:
            # check if the non-np.nan values are float
            try:
                float(val)
                has_float = True
            except ValueError:
                has_non_float = True
    # if factors contain at least one non-float
    if has_non_float:
        if has_float or has_nan:
            d_type.append('check')
        else:
            d_type.append('object')
    else:
        if has_tf:
            d_type.append('object')
        else:
            d_type.append('float')
    return d_type


def get_dtypes(metadata: pd.DataFrame, nulls: list) -> dict:
    """
    Get the dtypes of each column of the metadata table.

    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata table.
    nulls : list
        Factors to be interpreted as np.nan.

    Returns
    -------
    dtypes : dict
        Key     = Metadata variable
        Value   = Metadata variable's dtype
    """
    dtypes_init = get_dtypes_init(metadata)
    dtypes = get_dtypes_final(metadata, nulls, dtypes_init)
    return dtypes


def split_variables_types(dtypes: dict, criteria: dict) -> tuple:
    """
    Split variables of each metadata according to
    whether it is numeric or categorical.

    Parameters
    ----------
    dtypes : dict
        Key     = Metadata variable.
        Value   = Metadata variable's dtype.
    criteria : dict
        Inclusion/exclusion criteria to apply.

    Returns
    -------
    numerical : list
        Metadata variables that are numeric.
    categorical : list
        Metadata variables that are categorical.
    """
    numerical = []
    categorical = []
    for var, dtype in dtypes.items():
        if dtype == 'object':
            if var not in [x[0] for x in criteria]:
                continue
            categorical.append(var)
        elif dtype in ['int', 'float']:
            numerical.append(var)
    return numerical, categorical