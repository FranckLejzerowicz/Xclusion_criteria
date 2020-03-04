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
    curve = altair.Chart(
        curves_pd,
        width=200,
        height=200
    ).mark_line(
        point=True
    ).encode(
        x = altair.X('step', scale=altair.Scale(zero=False),
                     sort=curves_pd.step.tolist()),
        y = altair.Y('samples', scale=altair.Scale(zero=False)),
        tooltip = ['step', 'samples', 'variable', 'values', 'indicator']
    )

    included_num_us = included_num.unstack().reset_index().rename(columns={'level_0': 'num_var', 0: 'num_val'})
    included_num_us = included_num_us.loc[~included_num_us.isna().any(axis=1),:]
    included_num_us = pd.merge(included_num_us, included_num_us, on='sample_name')
    included_merged_num_cols = ['sample_name', 'num_var_x', 'num_var_y', 'num_val_x', 'num_val_y']
    included_num_us = included_num_us.loc[(included_num_us['num_var_x'] != included_num_us['num_var_y']), :]
    included_num_us = included_num_us[included_merged_num_cols]

    included_cat_us = included_cat.unstack().reset_index().rename(columns={'level_0': 'cat_var', 0: 'cat_val'})
    included_cat_us = included_cat_us.loc[~included_cat_us.isna().any(axis=1),:]
    included_merged = included_num_us.merge(included_cat_us, on='sample_name', how='left')
    included_merged = included_merged.loc[~included_merged.isna().any(axis=1),:]

    unique_per_cat_col_set = set()
    unique_per_cat_col = []
    for row in included_merged[['cat_var', 'cat_val']].values:
        tow = tuple(row)
        if tow not in unique_per_cat_col_set:
            unique_per_cat_col_set.add(tow)
            unique_per_cat_col.append('ID')
        else:
            unique_per_cat_col.append(np.nan)
    included_merged['is_unique_ID_for_altair_plot'] =  unique_per_cat_col

    has_slider = False
    slider_selection = None
    # if 'slider' in plot_groups:
    #     slider = plot_groups['slider']
    #     if slider not in included_merged['num_var_x'].unique():
    #         print('[Warning] Variable set for slider is not numeric:', slider)
    #     else:
    #         has_slider = True
    #         slider_values = included_merged.loc[included_merged['num_var_x']==slider, 'num_val_x'].unique()
    #         slider_altair = altair.binding_range(
    #             min=min(map(int, slider_values)),
    #             max=max(map(int, slider_values)),
    #             step=1
    #         )
    #         slider_selection = altair.selection_single(bind=slider_altair,
    #                                                    fields=['num_val_x'],
    #                                                    name="%s_" % slider)
    brush = altair.selection(type='interval', resolve='global')
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
    if has_slider:
        scatter_chart = altair.Chart(
            included_merged,
            width=400,
            height=400
        ).mark_point(
            point=True
        ).encode(
            x=altair.X('num_val_x:Q', scale=altair.Scale(zero=False)),
            y=altair.Y('num_val_y:Q', scale=altair.Scale(zero=False)),
            color=altair.condition(brush, 'num_val_y:Q', altair.ColorValue('gray')),
            tooltip="sample_name:N"
        ).add_selection(
            brush,
            cont_select_var_x,
            cont_select_var_y,
            slider_selection
        ).transform_filter(
            slider_selection
        ).transform_filter(
            cont_select_var_x
        ).transform_filter(
            cont_select_var_y
        )
    else:
        scatter_chart = altair.Chart(
            included_merged,
            width=400,
            height=400
        ).mark_point(
            filled=True
        ).encode(
            x=altair.X('num_val_x:Q', scale=altair.Scale(zero=False)),
            y=altair.Y('num_val_y:Q', scale=altair.Scale(zero=False)),
            color=altair.condition(brush, 'num_val_y:Q', altair.ColorValue('gray')),
            tooltip="sample_name:N"
        ).add_selection(
            brush,
            cont_select_var_x,
            cont_select_var_y,
        ).transform_filter(
            cont_select_var_x
        ).transform_filter(
            cont_select_var_y
        )
    scatter_chart = scatter_chart.resolve_scale(
        color='independent'
    )
    sorted_cat_vars = sorted(included_merged['cat_var'].unique().tolist())
    bars_sel = altair.Chart(included_merged).mark_bar().encode(
        x=altair.X(
            'cat_val:N',
            sort=[val for var in sorted_cat_vars
                  for val in sorted(included_merged.loc[
                                        included_merged['cat_var'] == var, 'cat_val'
                                    ].unique().tolist()) if str(val) != 'nan']),
        y='count(cat_val):Q',
        color='cat_var:N'
    ).properties(
        width=600,
        height=200
    ).transform_filter(
        {'not': altair.FieldEqualPredicate(field='is_unique_ID_for_altair_plot', equal='ID')}
    )

    text_sel = bars_sel.mark_text(
        align='center',
        baseline='middle',
        yOffset=-10
    ).encode(
        text='count(cat_val):Q'
    )
    meta_bars = (bars_sel + text_sel).transform_filter(
        brush
    )

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
    html_template = []
    html_template_fp = '%s/template.text.html' % RESOURCES
    with open(html_template_fp) as f:
        for ldx, line in enumerate(f):
            if len(line.strip()) < 400:
                html_template.append(line)
            else:
                html_template.append('      var spec = TO_REPLACE_HERE;\n')
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
