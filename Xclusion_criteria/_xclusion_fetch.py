# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import subprocess
from os.path import splitext


def fetch_redbiom(
    o_included: str,
    p_redbiom_context: str,
    p_bloom_sequences: str,
    p_reads_filter: int,
    unique: bool,
    update: bool,
    dim: bool,
    verbose: bool) -> None:
    """
    Parameters
    ----------
    o_included : str
        Path to output metadata for the included samples only.
    p_redbiom_context : str
        Redbiom context for fetching 16S data from Qiita.
    p_bloom_sequences : str
        Fasta file containing the sequences known to bloom in fecal samples.
    p_reads_filter : int
        Minimum number of reads per sample.
    unique : bool
        Whether to keep a unique sample per host or not.
    update : bool
        Update the sample names to remove Qiita-prep info.
    dim : bool
        Whether to add the number of samples in the final biom file name before extension or not.
    verbose : bool
        Whether to show missing, non-fetched samples and duplicates or not.
    """
    if not subprocess.getstatusoutput('Xrbftech --help'):
        o_included_fetched_meta = '%s_fetch.tsv' % splitext(o_included)[0]
        o_included_fetched_biom = '%s_fetch.biom' % splitext(o_included)[0]
        cmd = [
            'Xrbftech',
            '-m', o_included,
            '-o', o_included_fetched_meta,
            '-b', o_included_fetched_biom,
        ]
        if p_redbiom_context:
            cmd.extend(['-r', p_redbiom_context])
        if p_bloom_sequences:
            cmd.extend(['-s', p_bloom_sequences])
        if p_reads_filter:
            cmd.extend(['-f', str(p_reads_filter)])
        if unique:
            cmd.append('--unique')
        if update:
            cmd.append('--update')
        if dim:
            cmd.append('--dim')
        if verbose:
            cmd.append('--verbose')
        print('Fetching 16S:')
        subprocess.call(cmd)
    else:
        print('Install Xrbftech to automatise redbiom fetching: '
              'pip install git+https://github.com/FranckLejzerowicz/Xrbfetch.git'
              '(or see https://github.com/FranckLejzerowicz/Xrbfetch)')