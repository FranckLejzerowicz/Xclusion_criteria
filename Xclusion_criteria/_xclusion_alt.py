# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import altair
import pandas as pd


def make_flowchart(flowcharts: dict):
    """Build the flowchart figure.

    Parameters
    ----------
    flowcharts : dict
        Steps of the workflow with samples counts (simple representation).

    Returns
    -------
    curve : altair figure
        Altair flowchart figure.

    """
    print(' - make filtering figure... ', end='')
    flowcharts_pds = []
    for step in ['init', 'add', 'filter']:
        if step in flowcharts:
            flowchart_pd = pd.DataFrame(flowcharts[step],
                                        columns=['filter', 'samples', 'variable',
                                                 'values', 'indicator'])
            flowchart_pd['step'] = step
            flowcharts_pds.append(flowchart_pd)
    flowcharts_pd = pd.concat(flowcharts_pds, axis=0, sort=False)
    filter_order = []
    for f in flowcharts_pd['filter'].tolist():
        if f not in filter_order:
            filter_order.append(f)

    # Selection progression figure (left panel)
    curve = altair.Chart(
        flowcharts_pd, width=200, height=200, title='Samples selection progression'
    ).mark_line(
        point=True
    ).encode(
        x=altair.X('filter', scale=altair.Scale(zero=False), sort=filter_order),
        y=altair.Y('samples', scale=altair.Scale(zero=False)),
        color='step',
        tooltip=['step', 'filter', 'samples',
                 'variable', 'values', 'indicator']
    )
    print('Done')
    return curve


def get_selectors(included_merged: pd.DataFrame):
    """Prepare the selector for the interactive panels.

    Parameters
    ----------
    included_merged : pd.DataFrame
        Merged numeric and categorical tables.

    Returns
    -------
    scatter : Altair chart
        Interactive scatter plot panel.

    """
    # Dropdown menu first numerical data menu
    numerical_variables_x = included_merged['numerical_variable_x'].unique().tolist()
    dropdown_variables_x = altair.binding_select(options=numerical_variables_x)
    dropdown_x = altair.selection_single(
        fields=['numerical_variable_x'],
        bind=dropdown_variables_x,
        init={'numerical_variable_x': numerical_variables_x[0]},
        name="numerical_variable_x",
        on="click[event.shiftKey&!event.shiftKey]",
        clear = False,
    )

    # Dropdown menu second numerical data menu
    numerical_variables_y = included_merged['numerical_variable_y'].unique().tolist()
    dropdown_variables_y = altair.binding_select(options=numerical_variables_y)
    dropdown_y = altair.selection_single(
        fields=['numerical_variable_y'],
        bind=dropdown_variables_y,
        init={'numerical_variable_y': numerical_variables_y[0]},
        name="numerical_variable_y",
        on="click[event.shiftKey&!event.shiftKey]",
        clear=False
    )

    # Samples selector brush
    brush = altair.selection(
        type='interval',
        resolve='global',
        clear=False
    )
    return dropdown_x, dropdown_y, brush


def make_scatter(included_merged: pd.DataFrame,
                 dropdown_x, dropdown_y, brush):
    """Make the interactive scatter plot panel (left panel).
    Parameters
    ----------
    included_merged : pd.DataFrame
        Merged numeric and categorical tables.
    dropdown_x : Altair feature
        Dropdown menu first numerical data menu
    dropdown_y : Altair feature
        Dropdown menu second numerical data menu
    brush : Altair feature
        Samples selector brush

    Returns
    -------
    scatter : Altair chart
        Interactive scatter plot panel.

    """
    print(' - make scatter figure... ', end='')
    scatter = altair.Chart(
        included_merged, width=400, height=400,
        title='Numeric variables values per sample'
    ).mark_point(
        filled=True
    ).encode(
        x=altair.X('numerical_value_x:Q',
                   scale=altair.Scale(zero=False,
                                      padding=15)),
        y=altair.Y('numerical_value_y:Q',
                   scale=altair.Scale(zero=False,
                                      padding=15)),
        color=altair.condition(brush, 'numerical_value_y:Q',
                               altair.ColorValue('gray')),
        tooltip="sample_name:N"
    ).transform_filter(
        dropdown_x
    ).transform_filter(
        dropdown_y
    ).add_selection(
        dropdown_x
    ).add_selection(
        dropdown_y
    ).add_selection(
        brush
    ).resolve_scale(
        color='independent'
    )
    print('Done')
    return scatter


def make_barplot(included_merged: pd.DataFrame,
                 dropdown_x, dropdown_y, brush):
    """Make the interactive batplot plot panel (right panel).

    Parameters
    ----------
    included_merged : pd.DataFrame
        Merged numeric and categorical tables.
    dropdown_x : Altair feature
        Dropdown menu first numerical data menu
    dropdown_y : Altair feature
        Dropdown menu second numerical data menu
    brush : Altair feature
        Samples selector brush

    Returns
    -------
    batplot : Altair chart
        Interactive scatter plot panel.

    """

    # the bars
    print(' - make barplots figure...', end='')
    sorted_factors = get_sorted_factors(included_merged)
    print(included_merged.loc[
          (included_merged.numerical_variable_x == 'num1') &
          (included_merged.numerical_variable_y == 'num3'),:])
    bars = altair.Chart(included_merged).mark_bar().encode(
        x=altair.X('categorical_value:N', sort=sorted_factors),
        y='count(categorical_value):Q',
        color='categorical_variable:N'
    ).properties(
        width=600, height=200,
        title='Number of samples per categorical variable'
    ).transform_filter(
        dropdown_x
    ).transform_filter(
        dropdown_y
    ).transform_filter(
        brush
    )
    # text on the bars
    text = bars.mark_text(
        align='center', baseline='middle', yOffset=-10
    ).encode(
        text='count(categorical_value):Q'
    )

    # merge bars and text
    barplot = (
        bars + text
    ).transform_filter(
        brush
    )
    print('Done')
    return barplot


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
    for var, var_pd in included_merged.sort_values(
            'categorical_variable').groupby('categorical_variable'):
        for val in sorted(var_pd.categorical_value):
            if str(val) != 'nan':
                sorted_factors.append(val)
    return sorted_factors
