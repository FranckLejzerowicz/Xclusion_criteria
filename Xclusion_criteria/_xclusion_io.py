# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import yaml
import pandas as pd
from os.path import isfile


def read_i_criteria(i_criteria: str) -> dict:
    """Read the yaml criteria file.

    Parameters
    ----------
    i_criteria: str
        Path to yml config file for the different
        inclusion/exclusion criteria to apply.
    Returns
    -------
    parsed_criteria : dict
        Key     = variable,indicator.
        Value   = list of factors to use for filtering.
    """
    parsed_criteria = {}
    if i_criteria and isfile(i_criteria):
        with open(i_criteria) as handle:
            parsed_criteria = yaml.load(handle, Loader=yaml.FullLoader)
    return parsed_criteria


def read_meta_pd(metadata_file: str) -> pd.DataFrame:
    """
    Read metadata with first column as index.

    Parameters
    ----------
    metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.

    Returns
    -------
    metadata : pd.DataFrame
        Metadata table.
    """
    with open(metadata_file) as f:
        for line in f:
            break
    header = line.strip()
    for sep in ['\t', ';', ',']:
        if len(header.split(sep))>1 and len(header.split(sep)) == (header.count(sep)+1):
            first_col = line.split(sep)[0]
            break
    else:
        print('no separator found among: "<tab>", ",", ";"\nExiting')
        sys.exit(1)
    meta_pd = pd.read_csv(metadata_file, header=0, sep=sep,
                          dtype={first_col: str}, low_memory=False)
    meta_pd.rename(columns={first_col: 'sample_name'}, inplace=True)
    meta_pd.set_index('sample_name', inplace=True)
    meta_pd.columns = [x.lower() for x in meta_pd.columns]
    # remove NaN only columns
    meta_pd = meta_pd.loc[:,~meta_pd.isna().all()]
    return meta_pd