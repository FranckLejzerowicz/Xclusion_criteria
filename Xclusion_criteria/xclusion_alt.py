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
    print('   * make filtering figure... ', end='')
    flowcharts_pds = []
    for step in ['init', 'add', 'filter', 'data']:
        if step in flowcharts:
            flowchart_pd = pd.DataFrame(
                flowcharts[step],
                columns=['criterion', 'samples', 'variable',
                         'values', 'indicator'])
            flowchart_pd['criterion'] = [
                '%s (%s)' % (x, step) for x in flowchart_pd['criterion']]
            flowchart_pd['filter'] = '%s (%s steps)' % (
                step, len(flowchart_pd.criterion.unique()))
            flowcharts_pds.append(flowchart_pd)
    flowcharts_pd = pd.concat(flowcharts_pds, axis=0, sort=False)
    criterion_order = []
    for f in flowcharts_pd['criterion'].tolist():
        if f not in criterion_order:
            criterion_order.append(f)

    # width = 200
    # if len(criterion_order) >= 20:
    #     width = width + (width * ((len(criterion_order) - 30)/50))
    width = len(criterion_order) * 10
    # Selection progression figure (left panel)
    curve = altair.Chart(
        flowcharts_pd, width=width,
        height=200, title='Samples selection progression'
    ).mark_line(
        point=True
    ).encode(
        x=altair.X('criterion', scale=altair.Scale(zero=False),
                   sort=criterion_order),
        y=altair.Y('samples', scale=altair.Scale(zero=False)),
        color='filter',
        tooltip=['samples', 'variable', 'values', 'indicator']
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
    num_vals_y = {v: l['sample_name'].nunique() for v, l in
                  included_merged.groupby('numerical_variable_y')}
    numerical_variables_y = sorted(num_vals_y.items(), key=lambda x: x[1])[::-1]
    numerical_variables_y = [x[0] for x in numerical_variables_y]
    dropdown_variables_y = altair.binding_select(options=numerical_variables_y)
    dropdown_y = altair.selection_point(
        fields=['numerical_variable_y'],
        bind=dropdown_variables_y,
        value=numerical_variables_y[0],
        name="numerical_variable_y",
        on="click[event.shiftKey&!event.shiftKey]",
        clear=False
    )
    # Dropdown menu second numerical data menu
    num_vals_x = {v: l['sample_name'].nunique() for v, l in
                  included_merged.groupby('numerical_variable_x')}
    numerical_variables_x = sorted(num_vals_x.items(), key=lambda x: x[1])[::-1]
    numerical_variables_x = [x[0] for x in numerical_variables_x]
    dropdown_variables_x = altair.binding_select(options=numerical_variables_x)
    dropdown_x = altair.selection_point(
        fields=['numerical_variable_x'],
        bind=dropdown_variables_x,
        value=[x for x in numerical_variables_x
               if x != numerical_variables_y[0]][0],
        name="numerical_variable_x",
        on="click[event.shiftKey&!event.shiftKey]",
        clear=False,
    )
    # Samples selector brush
    brush = altair.selection_interval(
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
    print('   * make scatter figure... ', end='')
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
        dropdown_y
    ).transform_filter(
        dropdown_x
    ).add_params(
        dropdown_y
    ).add_params(
        dropdown_x
    ).add_params(
        brush
    ).resolve_scale(
        color='independent'
    )
    print('Done')
    return scatter


def make_table_text(included_merged: pd.DataFrame,
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
    table_text : Altair chart
        Interactive text plot panel.

    """

    table_text = altair.Chart(
        included_merged
    ).mark_text(
    ).encode(
        text='count(categorical_variable):Q'
    ).properties(
        title='# selected samples'
    ).transform_filter(
        brush
    ).transform_filter(
        dropdown_x
    ).transform_filter(
        dropdown_y
    ).transform_filter(
        altair.FieldEqualPredicate(
            field='categorical_variable',
            equal=included_merged.categorical_variable.unique().tolist()[0]
        )
    )
    return table_text


def make_barplot(included_merged: pd.DataFrame,
                 dropdown_x, dropdown_y, brush):
    """Make the interactive barplot plot panel (right panel).

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
    barplot : Altair chart
        Interactive barplot plot panel.

    """


    # the bars
    print('   * make barplots figure...', end='')
    sorted_factors = get_sorted_factors(included_merged)
    width = int(15 * len(list(sorted_factors)))
    bars = altair.Chart(included_merged).mark_bar().encode(
        x=altair.X('categorical_value:N', sort=sorted_factors,
                   axis=altair.Axis(labelLimit=500)),
        y='count(categorical_value):Q',
        color='categorical_variable:N'
    ).properties(
        width=width, height=200,
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
        for val in sorted(var_pd.categorical_value.unique()):
            if str(val) != 'nan':
                if val not in sorted_factors:
                    sorted_factors.append(val)
    return sorted_factors
