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
    "-c", "--p-criterion", nargs=3, required=False, multiple=True, default=None,
    show_default=True, help="Criterion to use for metadata filtering. "
                            "Use 3 space-separated terms for filtering: (i) the variable, "
                            "(ii) a numeric indicator (0, 1 or 2) and (iii) the '/'-separated "
                            "variable factors, e.g.: '-p sample_type 1 Stool' (to include only "
                            "stool sample types), or '-p sample_type 0 Stool/Skin' (to exclude "
                            "all stool and skin sample types). The '2' indicator indicates a "
                            "numeric data subsetting. In this case, the '/'-separated variable "
                            "factors must start with either '>',  '>=', '<' or '<='."
)
@click.option(
    "-y", "--i-criteria", required=False, default=None, show_default=True,
    help="Must be a yaml file (see README or 'examples/criteria.yml')."
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
@click.version_option(__version__, prog_name="Xclusion_criteria")


def standalone_xclusion(
        m_metadata_file,
        p_criterion,
        i_criteria,
        o_excluded,
        o_included,
        i_plot_groups,
        o_visualization
):

    xclusion_criteria(
        m_metadata_file,
        p_criterion,
        i_criteria,
        o_excluded,
        o_included,
        i_plot_groups,
        o_visualization
    )


if __name__ == "__main__":
    standalone_xclusion()