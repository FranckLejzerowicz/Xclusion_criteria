# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import pkg_resources

from Xclusion_criteria.xclusion_io import read_meta_pd, parse_plot_groups, fetch_data
from Xclusion_criteria.xclusion_dtypes import get_dtypes, split_variables_types, check_num_cat_lists
from Xclusion_criteria.xclusion_crits import get_criteria, apply_criteria
from Xclusion_criteria.xclusion_plot import make_visualizations

RESOURCES = pkg_resources.resource_filename('Xclusion_criteria', 'resources')


def xclusion_criteria(
        m_metadata_file: str,
        i_criteria: str,
        i_plot_groups: str,
        o_included: str,
        o_excluded: str,
        o_visualization: str,
        p_random: int,
        fetch: bool,
        o_metadata_file: str,
        o_biom_file: str,
        p_redbiom_context: str,
        p_bloom_sequences: str,
        p_reads_filter: int,
        unique: bool,
        update: bool,
        dim: bool) -> None:
    """Main script for running the inclusion/exclusion
     criteria-based filtering on a metadata table.

    Parameters
    ----------
    m_metadata_file : str
        Path to metadata file on which to apply included/exclusion criteria.
    i_criteria: str
        Path to yml config file for the
        different inclusion/exclusion criteria to apply.
    i_plot_groups : str
        Path to yml config file for the different groups to visualize.
    o_included : str
        Path to output metadata for the included samples only.
    o_excluded : str
        Path to output metadata for the excluded samples only.
    o_visualization : str
        Path to output visualization for the included samples only.
    p_random : int
        Whether to reduce visualization to 100 random samples or not.
    fetch : bool
        Whether to fetch the samples on redbiom or not.
    o_metadata_file : str
        [if --fetch] Path to the output metadata table file.
    o_biom_file : str
        [if --fetch] Path to the output biom table file.
    p_redbiom_context : str
        [if --fetch] Redbiom context for fetching 16S data from Qiita.
    p_bloom_sequences : str
        [if --fetch] Fasta file containing the sequences known
        to bloom in fecal samples.
    p_reads_filter : int
        [if --fetch] Minimum number of reads per sample.
    unique : bool
        [if --fetch] Whether to keep a unique sample per host or not.
    update : bool
        [if --fetch] Update the sample names to remove Qiita-prep info.
    dim : bool
        [if --fetch] Whether to add the number of samples in the final
        biom file name before extension or not.
    """

    print('- read input metadata...', end=' ')
    nulls = [x.strip() for x in open('%s/nulls.txt' % RESOURCES).readlines()]
    metadata = read_meta_pd(m_metadata_file)
    messages = []
    print('Done.')

    # get yml content, i.e. all inclusion/exclusion criteria.
    print('- get yml content, i.e. all inclusion/exclusion criteria...')
    criteria = get_criteria(i_criteria, metadata, nulls, messages)
    if not criteria:
        print('No single criteria found: check input path / content\nExiting')
        sys.exit(1)
    # show yml criteria file formatting errors
    if messages:
        print('Problems encountered during criteria parsing:')
        for message in messages:
            print(message)
        messages = []

    # infer dtypes
    print('- infer dtypes...', end=' ')
    dtypes = get_dtypes(metadata, nulls)
    print('Done.')

    # get the numerical and categorical metadata variables
    numerical, categorical = [], []
    print('- get the numerical and categorical metadata variables...', end=' ')
    split_variables_types(dtypes, numerical, categorical)
    print('Done.')

    TF = {'False': 'No', 'false': 'No', False: 'No',
          'True': 'Yes', 'true': 'Yes', True: 'No'}
    metadata.replace(
        dict((x, TF) for x in metadata.columns if
             x in categorical and str(metadata[x].dtype)=='object'),
        inplace=True)

    # Apply filtering criteria to subset the metadata
    # -> get filtering flowchart and metadata for criteria-included samples
    print('- apply filtering criteria to subset the metadata...', end=' ')
    flowcharts, included = apply_criteria(
        metadata, criteria, numerical, messages)
    if messages:
        print('Problems encountered during application of criteria:')
        for message in messages:
            print(message)
    print('Done.')

    if included.shape[0]:
        # write the metadata for criteria-included samples
        print('- write the metadata for criteria-included samples...', end=' ')
        included.reset_index().to_csv(o_included, index=False, sep='\t')
        print('Done.')

    # write the metadata for criteria-excluded samples if requested
    if o_excluded and included.shape[0]:
        print('- write the metadata for criteria-excluded samples...', end=' ')
        excluded = metadata.loc[
            [x for x in metadata.index if x not in included.index],:
        ].copy()
        excluded.reset_index().to_csv(o_excluded, index=False, sep='\t')
        print('Done.')

    if fetch and included.shape[0]:
        included = fetch_data(
            o_included, flowcharts, o_metadata_file, o_biom_file,
            p_redbiom_context, p_bloom_sequences, p_reads_filter, unique,
            update, dim)

    # Check there's min 3 categorical and 2 numerical variables
    print('- check there are min 3 categorical and 2 numerical variables...')
    plot_groups = parse_plot_groups(i_plot_groups)

    if included.shape[0]:
        print()
        for num in sorted(numerical):
            print('  [numerical]', num, '(n=%s/%s)' % (
                sum(included[num].isnull() == False), included.shape[0]))
        print()
        for cat in sorted(categorical):
            if cat in included.columns:
                cats_dict = included[cat].value_counts().to_dict()
                print('  [categorical]', cat, '(n=%s:' % len(cats_dict),
                      end=' ')
                if len(cats_dict) > 10:
                    print('not showing)')
                else:
                    print('%s)' % ','.join([
                        '%s:%s' % (k,v) if len(str(k))<10 else
                        '%s:%s' % (k[:10],v) for k,v in cats_dict.items()]))

    no_fig = check_num_cat_lists(plot_groups, numerical, categorical)
    # show categorical/numerical variables concern
    if no_fig:
        # print(no_fig)
        print('   -> No figure...')

    if not no_fig:
        # Build the three-panel criteria-based filtering figure
        print('- build the three-panel criteria-based filtering figure...')
        make_visualizations(
            included, plot_groups, o_visualization,
            numerical, categorical, flowcharts, p_random, fetch)
