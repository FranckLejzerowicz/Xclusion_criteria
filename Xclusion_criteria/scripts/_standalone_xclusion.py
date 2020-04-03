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
    "-c", "--i-criteria", required=True,
    help="Must be a yaml file (see README or 'examples/criteria.yml')."
)
@click.option(
    "-p", "--i-plot-groups", required=False, default=None, show_default=True,
    help="Must be a yaml file (see README or 'examples/criteria.yml')."
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
    "-o", "--o-visualization", required=True,
    help="Output metadata explorer for the included samples only."
)
@click.option(
    "--random/--no-random", default=True, show_default=True,
    help="Reduce visualization to 100 random samples."
)
@click.version_option(__version__, prog_name="Xclusion_criteria")


def standalone_xclusion(
        m_metadata_file,
        i_criteria,
        i_plot_groups,
        o_included,
        o_excluded,
        o_visualization,
        random
):

    xclusion_criteria(
        m_metadata_file,
        i_criteria,
        i_plot_groups,
        o_included,
        o_excluded,
        o_visualization,
        random
    )


if __name__ == "__main__":
    standalone_xclusion()