# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xclusion_criteria._xclusion import xclusion_criteria
from Xclusion_criteria import __version__


@click.command()
@click.option(
    "-m", "--m-metadata-file", required=True,
    help="Metadata file on which to apply included/exclusion criteria."
)
@click.option(
    "-c", "--i-criteria", required=False, default=None, show_default=True,
    help="Must be a yaml file (see README or 'examples/criteria.yml')."
)

@click.option(
    "-r", "--p-redbiom-context", required=False,
    default="Deblur-Illumina-16S-V4-150nt-780653", show_default=True,
    help="Redbiom context for fetching 16S data from Qiita."
)
@click.option(
    "-b", "--p-bloom-sequences", required=False, default=None, show_default=False,
    help="Fasta file containing the sequences known to bloom in fecal samples "
         "(defaults to 'newblooms.all.fasta' file from package's folder 'resources')."
)
@click.option(
    "-z", "--i-plot-groups", required=False, default=None, show_default=True,
    help="Must be a yaml file (see README or 'examples/criteria.yml')."
)
@click.option(
    "-ex", "--o-excluded", required=False,
    help="Output metadata for the excluded samples only."
)
@click.option(
    "-in", "--o-included", required=True,
    help="Output metadata for the included samples only."
)
@click.option(
    "-viz", "--o-visualization", required=True,
    help="Output metadata explorer for the included samples only."
)
@click.option(
    "--fetch/--no-fetch", default=False, show_default=True,
    help="Get the 16S data from RedBiom and apply microbiome filters."
)
@click.option(
    "--unique/--no-unique", default=True, show_default=True,
    help="Keep a unique sample per host (most read, or most features)."
)
@click.version_option(__version__, prog_name="Xclusion_criteria")


def standalone_xclusion(
        m_metadata_file,
        i_criteria,
        o_excluded,
        o_included,
        i_plot_groups,
        o_visualization,
        p_redbiom_context,
        p_bloom_sequences,
        unique,
        fetch
):

    xclusion_criteria(
        m_metadata_file,
        i_criteria,
        o_excluded,
        o_included,
        i_plot_groups,
        o_visualization,
        p_redbiom_context,
        p_bloom_sequences,
        unique,
        fetch
    )


if __name__ == "__main__":
    standalone_xclusion()