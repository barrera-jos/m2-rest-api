# data_loaders.py
from pathlib import Path

import logging
import pandas as pd
import json
import yaml


# Do not call logging.basicConfig() here.
# Use the logging configuration from Part 1.
logger = logging.getLogger(__name__)


def load_csv(filepath):
    """Load a CSV file into a DataFrame.
    filepath is a Path object.
    """
    logger.debug(f"Loading CSV file: {filepath}")
    return pd.read_csv(filepath)


def load_json(filepath):
    """Load a JSON file into a Python object (dict or list).
    filepath is a Path object.
    """
    logger.debug(f"Loading JSON file: {filepath}")
    with filepath.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(filepath):
    """Load a YAML file into a Python object.
    filepath is a Path object.
    """
    logger.debug(f"Loading YAML file: {filepath}")
    with filepath.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(filepath):
    """Load a file based on its extension.
    filepath is a string, such as 'fixtures/sample.csv'
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return load_csv(path)
    elif suffix == ".json":
        return load_json(path)
    elif suffix in (".yaml", ".yml"):
        return load_yaml(path)
    else:
        raise ValueError(f"Unsupported file type '{suffix}' for {path}")