# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re, ast
from setuptools import find_packages, setup

classes = """
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: 3 :: Only
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""

classifiers = [s.strip() for s in classes.split('\n') if s]

description = (
    "Generate interactive, user-defined visualisations to help"
    "defining inclusion/exclusion criteria on a metadata table."
)

with open("README.md") as f:
    long_description = f.read()

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("Xclusion_criteria/__init__.py", "rb") as f:
    hit = _version_re.search(f.read().decode("utf-8")).group(1)
    version = str(ast.literal_eval(hit))

standalone = ['Xclusion_criteria=Xclusion_criteria.scripts._standalone_xclusion:standalone_xclusion']

setup(
    name="Xclusion_criteria",
    version=version,
    license="BSD",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Franck Lejzerowicz",
    author_email="franck.lejzerowicz@gmail.com",
    maintainer="Franck Lejzerowicz",
    maintainer_email="franck.lejzerowicz@gmail.com",
    url="https://github.com/FranckLejzerowicz/Xclusion_criteria",
    packages=find_packages(),
    install_requires=[
        "click >= 6.7",
        'numpy >= 1.18.1',
        'pandas >= 1.0.1',
        'altair >= 3.2.0',
        'cython >= 0.29.15',
        'biom-format >= 2.1.5',
        'redbiom >= 0.3.5',
        'matplotlib',
        'pyyaml'
    ],
    classifiers=classifiers,
    package_data={'Xclusion_criteria': ['resources/nulls.txt',
                                        'resources/template.chart.json',
                                        'resources/template.text.html']},
    entry_points={'console_scripts': standalone},
    python_requires='>=3.6',
)
