import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "tests", "data")

# The validation scripts are plain modules in scripts/, not a package
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))


@pytest.fixture
def samples_path():
    """Three valid rows copied verbatim from common_samples.tsv."""
    return os.path.join(DATA_DIR, "samples.tsv")


@pytest.fixture
def libraries_path():
    """The libraries of the three samples in samples.tsv, copied verbatim from common_libraries.tsv."""
    return os.path.join(DATA_DIR, "libraries.tsv")


@pytest.fixture
def schemas_samples():
    return os.path.join(REPO_ROOT, "schemas_samples")


@pytest.fixture
def schemas_libraries():
    return os.path.join(REPO_ROOT, "schemas_libraries")
