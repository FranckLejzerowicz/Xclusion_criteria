# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xclusion_criteria.xclusion import xclusion_criteria
from Xclusion_criteria import __version__


@click.command()
@click.option(
    "-m", "--m-metadata-file", required=True,
    help="Metadata file on which to apply included/exclusion criteria."
)
@click.option(
    "-c", "--i-criteria", required=True,
    help="Must be a yaml file (see README or 'examples/criteria_nonempty_output.yml')."
)
@click.option(
    "-p", "--i-plot-groups", required=False, default=None, show_default=True,
    help="Must be a yaml file (see README or 'examples/plot.yml')."
)
@click.option(
    "-in", "--o-included", required=True,
    help="Output metadata for the included samples only."
)
@click.option(
    "-ex", "--o-excluded", required=False, default=None, show_default=True,
    help="Output metadata for the excluded samples only."
)
@click.option(
    "-v", "--o-visualization", required=False,
    help="Output metadata explorer for the included samples only."
)
@click.option(
    "-r", "--p-random", default=1000, show_default=True,
    help="Reduce visualization to the passed number of (random) samples."
)
@click.option(
    "--fetch/--no-fetch", default=False, show_default=True,
    help="Run Xrbfetch (third-party) to get features data."
)
@click.option(
    "-o", "--o-metadata-file", default=None,
    help="[if --fetch] Path to the output metadata table file. "
         "(Default = add _fetched_#s.tsv)."
)
@click.option(
    "-b", "--o-biom-file", default=None,
    help="[if --fetch] Path to the output biom table file. "
         "(Default = add _fetched_#s.biom)."
)
@click.option(
    "-x", "--p-redbiom-context", required=False,
    default="Deblur-Illumina-16S-V4-150nt-780653", show_default=True,
    help="[if --fetch] Redbiom context for fetching 16S data from Qiita."
)
@click.option(
    "-s", "--p-bloom-sequences", required=False, default=None, show_default=False,
    help="[if --fetch] Fasta file containing the sequences known to bloom in fecal samples "
         "(defaults to 'newblooms.all.fasta' file from Xrbfetch package's folder 'resources')."
)
@click.option(
    "-f", "--p-reads-filter", default=1000, show_default=True, type=int,
    help="[if --fetch] Minimum number of reads per sample."
)
@click.option(
    "--unique/--no-unique", default=True, show_default=True,
    help="[if --fetch] Keep a unique sample per host (most read, or most features)."
)
@click.option(
    "--update/--no-update", default=True, show_default=True,
    help="[if --fetch] Update the sample names to remove Qiita-prep info."
)
@click.option(
    "--dim/--no-dim", default=True, show_default=True,
    help="[if --fetch] Add the number of samples in the final biom file name before "
         "extension (e.g. for '-b out.biom' it becomes 'out_1000s.biom')."
)
@click.version_option(__version__, prog_name="Xclusion_criteria")


def standalone_xclusion(
        m_metadata_file,
        i_criteria,
        i_plot_groups,
        o_included,
        o_excluded,
        o_visualization,
        p_random,
        fetch,
        o_metadata_file,
        o_biom_file,
        p_redbiom_context,
        p_bloom_sequences,
        p_reads_filter,
        unique,
        update,
        dim
):

    xclusion_criteria(
        m_metadata_file,
        i_criteria,
        i_plot_groups,
        o_included,
        o_excluded,
        o_visualization,
        p_random,
        fetch,
        o_metadata_file,
        o_biom_file,
        p_redbiom_context,
        p_bloom_sequences,
        p_reads_filter,
        unique,
        update,
        dim
    )


if __name__ == "__main__":
    standalone_xclusion()