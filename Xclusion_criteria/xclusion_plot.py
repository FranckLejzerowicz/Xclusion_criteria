# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import random
import pandas as pd
import pkg_resources
import itertools
from os.path import dirname, isdir, splitext

from Xclusion_criteria.xclusion_alt import (
    make_flowchart,
    get_selectors,
    make_scatter,
    make_barplot,
    make_table_text
)

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def make_visualizations(included: pd.DataFrame, plot_groups: dict,
                        o_visualization: str, numerical: list,
                        categorical: list, flowcharts: dict,
                        p_random: int, fetch: bool) -> None:
    """Build the three-panel criteria-based filtering figure.

    Parameters
    ----------
    included : pd.DataFrame
        Metadata for the included samples only.
    plot_groups : dict
        Path to yml config file for the different groups to visualize.
    o_visualization : str
        Path to output visualization for the included samples only.
    numerical : list
        Metadata variables that are numeric.
    categorical : list
        Metadata variables that are categorical.
    flowcharts : dict
        Steps of the workflow with samples counts (simple representation).
    p_random : int
        Whether to reduce visualization to 100 random samples or not.
    fetch : bool
        Whether to fetch the samples on redbiom or not.
    """

    numerical = [x for x in numerical if x in included.columns]
    categorical = [x for x in categorical if x in included.columns]
    included.columns = [x for x in included.columns]

    # Subset the metadata to the plotting numeric variables
    included_num = get_included_num(
        'numerical', numerical, included, plot_groups)
    # Subset the metadata to the plotting categorical variables
    included_cat = get_included_num(
        'categorical', categorical, included, plot_groups)

    # get output visualization file name
    if '/' in o_visualization:
        o_visualization_dir = dirname(o_visualization)
        if not isdir(o_visualization_dir):
            os.makedirs(o_visualization_dir)
    if not o_visualization.endswith('.html'):
        o_visualization = '%s.html' % o_visualization

    print('Start making the chart (html) figure')
    make_user_chart(included_num, included_cat, flowcharts,
                    o_visualization, p_random)


def get_included_num(nc: str, num_cat: list, included: pd.DataFrame,
                     plot_groups: dict) -> pd.DataFrame:
    """Subset the metadata to the numeric or (categorical)
    variables passed for plotting (from the plotting .yml file).

    Parameters
    ----------
    nc : str
        "numerical" or "categorical"
    num_cat : list
        Metadata variables that are numerical (or categorical).
    included : pd.DataFrame
        Metadata for the included samples only.
    plot_groups : dict
        Groups (values) for barplots and scatters (keys).

    Returns
    -------
    included_nc : pd.DataFrame
        Metadata for the included samples and the
        passed numerical (or categorical) variables.

    """

    included_nc = included[num_cat].copy()
    if nc not in plot_groups or not plot_groups[nc]:
        # for the numerical data, no passed variable will use all
        # variables in the dropdown menu (i.e. non subsetted "included_nc")
        if nc == 'categorical':
            included_nc['number_of_samples'] = 'number_of_samples'
            included_nc = included_nc[['number_of_samples']]
    else:
        # get plotting variables
        plot_groups_cats = set(plot_groups[nc])
        # get plotting variables in the metadata
        cat_to_plot = plot_groups_cats & set(num_cat)
        # get plotting variables NOT in the metadata
        cat_not_to_plot = plot_groups_cats ^ cat_to_plot
        # if there is no plotting variables in the metadata
        if not cat_to_plot:
            # show warning and create a number of samples variable
            print(' --> all passed "%s" variables are not %s' % (nc, nc))
            if nc == 'categorical':
                included_nc['number_of_samples'] = 'count'
                cat_to_plot = ['number_of_samples']
        # show plotting variables NOT in the metadata
        if cat_not_to_plot:
            print(' --> %s passed "%s" variables that are '
                  'not %s:' % (len(cat_not_to_plot), nc, nc))
            print('\t* %s' % '\n\t* '.join(cat_not_to_plot))
        # in any case subset to the plotting variables in the metadata
        included_nc = included_nc[sorted(cat_to_plot)]
        if nc == 'categorical':
            included_nc = included_nc.fillna('Unspecified')
        if nc == 'numerical':
            included_nc = included_nc.fillna(0.0)
    return included_nc


def get_included_us(
        num_cat: str, included_num_cat: pd.DataFrame) -> pd.DataFrame:
    """Melt the table to get pairwise combinations
    of numeric (or categorial) variables' values.

    Parameters
    ----------
    num_cat : str
        Whether the input table is numerical (or categorical)
    included_num_cat : pd.DataFrame
        Metadata for the included samples only
        and for numerical (or categorical) variables only.
            e.g. input (for numerical):
                            variable1   variable2   variable3
                sample_name
                sample.ID.1 100000001   200000001   nan
                sample.ID.2 100000002   200000002   300000002

    Returns
    -------
    included_num_us : pd.DataFrame
        Metadata for the included samples only and for numerical
        (or categorical) variables only but now unstacked to have
        the numeric values as one column, merged with itself.
            e.g. output for the above input (for numerical):
                sample_name num_var_x   num_var_y   num_val_x   num_val_y
                sample.ID.1 variable1   variable2   100000001   200000001
                sample.ID.2 variable1   variable2   100000002   200000002
                sample.ID.2 variable1   variable3   100000002   300000002
                sample.ID.1 variable2   variable1   200000001   100000001
                sample.ID.2 variable2   variable1   200000002   100000002
                sample.ID.2 variable2   variable3   200000002   300000002
                sample.ID.2 variable3   variable1   300000002   100000002
                sample.ID.2 variable3   variable2   300000002   200000002
        Note that the nan value is removed
        and that the 2-columns format is symmetric.
    """

    variables_pairs = list(itertools.combinations(
        included_num_cat.columns.tolist(), 2))
    included_num_cat_us = included_num_cat.unstack().reset_index().rename(
        columns={'level_0': '%s_variable' % num_cat, 0: '%s_value' % num_cat})
    # included_num_cat_us = included_num_cat_us.loc[
    #     ~included_num_cat_us.isna().any(axis=1), :]
    # included_num_cat_us = included_num_cat_us.loc[
    #     ~included_num_cat_us.isna().any(axis=1), :]

    if num_cat == 'numerical':
        included_num_cat_us = pd.merge(
            included_num_cat_us, included_num_cat_us, on='sample_name'
        )
        included_num_cat_us = included_num_cat_us.set_index(
            ['numerical_variable_x', 'numerical_variable_y']
        ).loc[variables_pairs,:].reset_index()

        included_merged_num_cols = [
            'sample_name',
            'numerical_variable_x',
            'numerical_variable_y',
            'numerical_value_x',
            'numerical_value_y'
        ]
        included_num_cat_us = included_num_cat_us.loc[
            (included_num_cat_us['numerical_variable_x']!=
             included_num_cat_us['numerical_variable_y']),:]
        included_num_cat_us = included_num_cat_us[included_merged_num_cols]
    return included_num_cat_us


def add_unique_categorical(included_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    included_merged : pd.DataFrame
        Table to which a column is to be added
    """
    ids = set()
    for val, var_tab in included_merged[
        ['categorical_variable',
         'categorical_value']
    ].drop_duplicates().groupby('categorical_value'):
        if var_tab.shape[0] > 1:
            ids.update(set(included_merged.loc[
                (included_merged.categorical_variable.isin(
                    var_tab.categorical_variable.tolist())) &
                (included_merged.categorical_value == val), :].index.tolist()))
    if ids:
        rep = included_merged.loc[ids, 'categorical_value'] + \
              ' (' + included_merged.loc[ids, 'categorical_variable'] + ')'
        included_merged.loc[ids, 'categorical_value'] = rep
    return included_merged


def make_user_chart(included_num: pd.DataFrame,
                    included_cat: pd.DataFrame,
                    flowcharts: dict,
                    o_visualization: str,
                    p_random: int) -> None:
    """Build the figure.

    Parameters
    ----------
    included_num : pd.DataFrame
        Metadata for the included samples only
        and for numerical variables only.
    included_cat : pd.DataFrame
        Metadata for the included samples only
        and for categorical variables only.
    flowcharts : dict
        Steps of the workflow with samples counts (simple representation).
    o_visualization : str
        Path to output visualization for the included samples only.
    p_random : int
        Whether to reduce visualization to a number random samples or not.

    """

    flowchart = make_flowchart(flowcharts)

    if included_num.shape[0]:
        # melt the table to get pairwise combinations
        # of numeric variables' values
        print(' - get numeric melted table... ')
        included_num_us = get_included_us('numerical', included_num)
        print(' - get categorical melted table... ')
        included_cat_us = get_included_us('categorical', included_cat)

        # get either the full sample set for figure representation or,
        # because the table can be huge, a random sample.
        all_samples = included_cat_us.sample_name.unique()

        R = 2
        if p_random and all_samples.size > p_random:
            print('More than %s samples -> %s times %s samples will be used:'
                  % (p_random, R, p_random))
            cur_samples = [
                random.sample(all_samples.tolist(), p_random) for r in range(R)]
            suffixes = ['_rand%s_%s' % (p_random, r) for r in range(R)]
        else:
            cur_samples = [all_samples.tolist()]
            suffixes = ['']

        # For each set of randomly-picked 100 samples
        for sdx, suffix in enumerate(suffixes):

            # subset categorical and numerical melted
            # tables to the random samples
            cur_included_num_us = included_num_us.loc[
                included_num_us.sample_name.isin(cur_samples[sdx])]
            cur_included_cat_us = included_cat_us.loc[
                included_cat_us.sample_name.isin(cur_samples[sdx])]

            print(' - merge numeric and categorical tables... ')
            included_merged = cur_included_num_us.merge(
                cur_included_cat_us, on='sample_name', how='right')
            # remove the samples that have NaN in any of the row
            included_merged = included_merged.loc[
                ~included_merged.isna().any(axis=1), :]

            # make redundant factor unique
            included_merged = add_unique_categorical(included_merged)
            included_merged.to_csv('/Users/franck/projects/test.tsv')

            dropdown_x, dropdown_y, brush = get_selectors(included_merged)
            scatter = make_scatter(
                included_merged, dropdown_x, dropdown_y,  brush)
            table_text = make_table_text(
                included_merged, dropdown_x, dropdown_y, brush)
            barplot = make_barplot(
                included_merged, dropdown_x, dropdown_y, brush)

            print(' - Write figure... ', end='')
            # concatenate the three panels
            chart = (flowchart | scatter | (table_text & barplot))
            chart = chart.resolve_scale(
                color='independent'
            )

            o_visualization_fp = '%s%s%s' % (
                splitext(o_visualization)[0],
                suffix,
                splitext(o_visualization)[1]
            )
            chart.save(o_visualization_fp)
            print('Done: %s' % o_visualization_fp)
    else:
        print(' - Write figure... ', end='')
        # concatenate the three panels
        chart = flowchart
        chart = chart.resolve_scale(
            color='independent'
        )

        o_visualization_fp = '%s_emptySelection%s' % (
            splitext(o_visualization)[0],
            splitext(o_visualization)[1]
        )
        chart.save(o_visualization_fp)
        print('Done: %s' % o_visualization_fp)
