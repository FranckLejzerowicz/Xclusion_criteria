# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import sys
import yaml
import json
import altair
import numpy as np
import pandas as pd
import pkg_resources
from os.path import dirname, isdir, isfile, splitext

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def make_visualizations(included: pd.DataFrame, i_plot_groups: str,
                        o_visualization: str, numerical: list,
                        categorical: list, flowchart: list) -> None:
    """
    Parameters
    ----------
    included : pd.DataFrame
        Metadata for the included samples only.
    i_plot_groups : str
        Path to yml config file for the different groups to visualize.
    o_visualization : str
        Path to output visualization for the included samples only.
    numerical : list
        Metadata variables that are numeric.
    categorical : list
        Metadata variables that are categorical.
    flowchart : list
        Steps of the workflow with samples counts (simple representation).
    """
    included_num = included[numerical].copy()
    included_cat = included[categorical].copy()

    plot_groups = get_parsed_plot_groups(i_plot_groups)

    o_visualization_dir = dirname(o_visualization)
    if not isdir(o_visualization_dir):
        os.makedirs(o_visualization_dir)
    if not o_visualization.endswith('.html'):
        o_visualization = '%s.html' % o_visualization
    make_user_chart(included_num, included_cat, plot_groups, flowchart, o_visualization)

    # o_explorer = '%s_metadataExplorer.html' % splitext(o_visualization)[0]
    # make_explorer_chart(included.reset_index(), o_explorer, numerical, categorical)


def add_unique_per_cat_col(included_merged: pd.DataFrame) -> list:
    """
    Parameters
    ----------
    included_merged : pd.DataFrame
        Table to which a column is to be added

    Returns
    -------
    unique_per_cat_col : list
        Column to add that tells whether the sample is the first encountered for each
        - sample_name
        - categorical variable
        - categorical variable's factor
    """
    unique_per_cat_col_set = set()
    unique_per_cat_col = []
    for row in included_merged[['cat_var', 'cat_val']].values:
        tow = tuple(row)
        if tow not in unique_per_cat_col_set:
            unique_per_cat_col_set.add(tow)
            unique_per_cat_col.append('ID')
        else:
            unique_per_cat_col.append(np.nan)
    return unique_per_cat_col


def get_sorted_factors(included_merged: pd.DataFrame) -> list:
    """
    Parameters
    ----------
    included_merged : pd.DataFrame
        Merged the numeric and categorical tables.
    Returns
    -------
    sorted_factors : list
        All the factors, sorted per variable.
    """
    sorted_factors = []
    for var, var_pd in included_merged.sort_values('cat_var').groupby('cat_var'):
        for val in sorted(var_pd.cat_val):
            if str(val) != 'nan':
                sorted_factors.append(val)
    return sorted_factors


def make_user_chart(included_num: pd.DataFrame,
                    included_cat: pd.DataFrame,
                    plot_groups: dict,
                    flowchart: list,
                    o_visualization: str) -> None:
    """
    Parameters
    ----------
    included_num : pd.DataFrame
        Metadata for the included samples only
        and for numerical variables only.
    included_cat : pd.DataFrame
        Metadata for the included samples only
        and for categorical variables only.
    plot_groups : dict
        Groups (values) for barplots and scatters (keys).
    flowchart : list
        Steps of the workflow with samples counts (simple representation).
    o_visualization : str
        Path to output visualization for the included samples only.
    """

    curves_pd = pd.DataFrame(flowchart, columns = ['step', 'samples', 'variable', 'values', 'indicator'])
    curves_pd['order'] = curves_pd.index.tolist()

    # Selection progression figure (left panel)
    curve = altair.Chart(
        curves_pd, width=200, height=200, title='Samples selection progression'
    ).mark_line(
        point=True
    ).encode(
        x=altair.X('step', scale=altair.Scale(zero=False), sort=curves_pd.step.tolist()),
        y=altair.Y('samples', scale=altair.Scale(zero=False)),
        tooltip=['step', 'samples', 'variable', 'values', 'indicator']
    )

    included_num_us = get_included_us(included_num, 'num')
    included_cat_us = get_included_us(included_cat, 'cat')
    # merge the numeric and categorical tables
    included_merged = included_num_us.merge(included_cat_us, on='sample_name', how='left')
    included_merged = included_merged.loc[~included_merged.isna().any(axis=1), :]
    # add variable to indicate unique sample/variable/factor instances
    included_merged['is_unique_ID_for_altair_plot'] =  add_unique_per_cat_col(included_merged)

    num_var_x = included_merged['num_var_x'].unique().tolist()
    num_var_y = included_merged['num_var_y'].unique().tolist()
    cont_dropdown_var_x = altair.binding_select(options=num_var_x)
    cont_dropdown_var_y = altair.binding_select(options=num_var_y)
    cont_select_var_x = altair.selection_single(fields=['num_var_x'],
                                                bind=cont_dropdown_var_x,
                                                init={'num_var_x': num_var_x[0]},
                                                name="num_var_x", clear=False)
    cont_select_var_y = altair.selection_single(fields=['num_var_y'],
                                                bind=cont_dropdown_var_y,
                                                init={'num_var_y': num_var_y[0]},
                                                name="num_var_y", clear=False)
    brush = altair.selection(type='interval', resolve='global')

    # Scatter figure (left panel)
    scatter_chart = altair.Chart(
        included_merged, width=400, height=400, title='Numeric variables values per sample'
    ).mark_point(
        filled=True
    ).encode(
        x=altair.X('num_val_x:Q', scale=altair.Scale(zero=False)),
        y=altair.Y('num_val_y:Q', scale=altair.Scale(zero=False)),
        color=altair.condition(brush, 'num_val_y:Q', altair.ColorValue('gray')),
        tooltip="sample_name:N"
    ).add_selection(
        brush, cont_select_var_x, cont_select_var_y,
    ).transform_filter(
        cont_select_var_x
    ).transform_filter(
        cont_select_var_y
    ).resolve_scale(
        color='independent'
    )

    # Make barplot, including:
    # - the bars
    sorted_factors = get_sorted_factors(included_merged)
    bars_sel = altair.Chart(included_merged).mark_bar().encode(
        x=altair.X('cat_val:N', sort=sorted_factors),
        y='count(cat_val):Q',
        color='cat_var:N'
    ).properties(
        width=600, height=200, title='Number of samples per categorical variable'
    ).transform_filter(
        {'not': altair.FieldEqualPredicate(field='is_unique_ID_for_altair_plot', equal='ID')}
    )
    # - the text on the bars
    text_sel = bars_sel.mark_text(
        align='center', baseline='middle', yOffset=-10
    ).encode(
        text='count(cat_val):Q'
    )
    # merge bars and text
    meta_bars = (bars_sel + text_sel).transform_filter(
        brush
    )

    # concatenate the three panels
    chart = (curve | scatter_chart | meta_bars)
    chart = chart.resolve_scale(
        color='independent'
    )
    chart.save(o_visualization)


def read_template_chart() -> dict:
    """Read the template figure from resources."""
    html_json_fp = '%s/template.chart.json' % RESOURCES
    with open(html_json_fp) as f:
        html_json = json.load(f)
    return html_json


def read_html_template() -> list:
    """Read the template java code for resources."""
    html_template_fp = '%s/template.text.html' % RESOURCES
    html_template = open(html_template_fp).readlines()
    return html_template


def make_explorer_chart(metadata: pd.DataFrame, o_explorer: str,
                        numerical: list, categorical: list) -> None:
    """
    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata table.
    o_explorer : str
        Path to output visualization for the included samples only.
    numerical : list
        Metadata variables that are numeric.
    categorical : list
        Metadata variables that are categorical.
    """
    html_json = read_template_chart()
    html_template = read_html_template()

    n_rows = metadata.shape[0]
    cols = [col for col in metadata.columns if col.lower() != 'description']
    allCols = [col for col in cols if sum(metadata[col].isna()) < (n_rows*0.9)]
    cat_also_cont = [col for col in cols if metadata[col].unique().size < 20]

    all_data_from_table_testSet = ['sample_name'] + numerical + categorical
    all_data_from_table = []
    for r, row in metadata.iterrows():
        cur_d = {}
        for col, value in row.to_dict().items():
            if col not in all_data_from_table_testSet:
                continue
            if str(value) == 'nan':
                cur_d[col] = None
            elif col in numerical:
                cur_d[col] = float(value)
            else:
                cur_d[col] = value
        all_data_from_table.append(cur_d)

    toEdit = [idx for idx, x in enumerate(html_json['data']) if x['name'].startswith('data-')][0]
    html_json['data'][toEdit]['values'] = all_data_from_table

    longest_cat = [0, '']
    longest_cont = [0, '']
    for allCol in allCols:
        if allCol not in all_data_from_table_testSet:
            continue
        if allCol in numerical:
            maxlen = max([len(x) for x in metadata[allCol].astype('str').tolist()])
            if maxlen >= longest_cont[0]:
                longest_cont[0] = maxlen
                longest_cont[1] = allCol
        elif allCol in categorical:
            if 'country' in allCol.lower() or metadata[allCol].unique().size <= 30:
                maxlen = metadata[allCol].unique().size
                if maxlen >= longest_cat[0]:
                    longest_cat[0] = maxlen
                    longest_cat[1] = allCol

    roReplaceSignals = {}
    for idx, signal_dict in enumerate(html_json['signals']):
        if signal_dict['name'] == 'Continuous_y':
            cur_cols = [x for x in numerical if x in all_data_from_table_testSet]
        elif signal_dict['name'] == 'Continuous_x':
            cur_cols = [x for x in numerical if x in all_data_from_table_testSet]
        elif signal_dict['name'] == 'Categorical_x':
            cur_cols =  [
                x for x in categorical if metadata[x].unique().size <= 30 or
                    x in cat_also_cont or 'country' in x.lower()
            ]
        elif signal_dict['name'] == 'Legend':
            cur_cols = [
                x for x in categorical if metadata[x].unique().size <= 30 and
                    x in all_data_from_table_testSet or
                    x in cat_also_cont or 'country' in x.lower()
            ]
        else:
            continue
        roReplaceSignals[(idx, signal_dict['name'])] = cur_cols

    for idx_name, var_list in roReplaceSignals.items():
        idx, name = idx_name
        cur_L = [x for x in var_list if x in all_data_from_table_testSet]
        if name == 'Continuous_y':
            html_json['signals'][idx]['value'] = longest_cont[1]
            html_json['signals'][idx]['bind']['options'] = cur_L
        elif name == 'Continuous_x':
            html_json['signals'][idx]['value'] = longest_cont[1]
            html_json['signals'][idx]['bind']['options'] = cur_L
        elif name == 'Categorical_x':
            html_json['signals'][idx]['value'] = [x for x in cur_L if metadata[x].unique().size == max(
                [metadata[x].unique().size for x in cur_L])][0]
            html_json['signals'][idx]['bind']['options'] = cur_L
        elif name == 'Legend':
            html_json['signals'][idx]['value'] = longest_cat[1]
            html_json['signals'][idx]['bind']['options'] = cur_L

    html_json['height'] = 300
    html_json['width'] = 600
    html_json['padding'] = 10
    html_json['legends'][0]['columns'] = 3
    html_json["config"] = {"axis": {"labelLimit": 3000}}

    with open(o_explorer, 'w') as o:
        for line in html_template:
            if 'TO_REPLACE_HERE' in line:
                o.write(line.replace(
                    'TO_REPLACE_HERE',
                    json.dumps(html_json, sort_keys=True, indent=4, separators=(',', ': ')))
                )
            else:
                o.write(line)


def get_parsed_plot_groups(i_plot_groups: str) -> dict:
    """
    Get the groups to plots for each barplots and scatters.

    Parameters
    ----------
    i_plot_groups : str
        Path to yml config file for the
        different groups to visualize.

    Returns
    -------
    plot_groups : dict
        Groups (values) for barplots and scatters (keys).
    """
    plot_groups = {}
    if i_plot_groups and isfile(i_plot_groups):
        with open(i_plot_groups) as handle:
            plot_groups.update(yaml.load(handle, Loader=yaml.FullLoader))
    return plot_groups


def get_included_us(included_num_cat: pd.DataFrame, num_cat: str) -> pd.DataFrame:
    """
    Parameters
    ----------
    included_num_cat : pd.DataFrame
        Metadata for the included samples only
        and for numerical (or categorical) variables only.
            e.g. input (for numerical):
                            variable1   variable2   variable3
                sample_name
                sample.ID.1 100000001   200000001   nan
                sample.ID.2 100000002   200000002   300000002
    num_cat : str
        Whether the input table is numerical (or categorical)

    Returns
    -------
    included_num_us : pd.DataFrame
        Metadata for the included samples only and for numerical (or categorical) variables
        only but now unstacked to have the numeric values as one column, merged with itself.
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
        Note that the nan value is removed and that the 2-columns format is symmetric.
    """
    included_num_cat_us = included_num_cat.unstack().reset_index().rename(
        columns={'level_0': '%s_var' % num_cat, 0: '%s_val' % num_cat})
    included_num_cat_us = included_num_cat_us.loc[~included_num_cat_us.isna().any(axis=1), :]

    if num_cat == 'num':
        included_num_cat_us = pd.merge(included_num_cat_us, included_num_cat_us, on='sample_name')
        included_merged_num_cols = ['sample_name', 'num_var_x', 'num_var_y', 'num_val_x', 'num_val_y']
        included_num_cat_us = included_num_cat_us.loc[
                          (included_num_cat_us['num_var_x'] !=
                           included_num_cat_us['num_var_y']), :]
        included_num_cat_us = included_num_cat_us[included_merged_num_cols]

    return included_num_cat_us
