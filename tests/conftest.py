import pytest
import os
from pathlib import Path

@pytest.fixture(scope='session', autouse=True)
def data_dir() -> Path:
    '''
    Returns path to directory with data samples
    '''
    path = Path(os.path.abspath(__file__)).parent / 'data_samples'
    return path