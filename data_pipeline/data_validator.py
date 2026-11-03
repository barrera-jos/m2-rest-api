# src/data_validator.py
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    # Every required column must exist
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        message = f"Missing required columns: {missing}"
        logger.error(message)
        raise ValueError(message)

    # Work on a copy so the caller's DataFrame is never changed
    df = df.copy()
    rows_before = len(df)

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning(
                        f"Column '{col}', row {i}: '{value}' is not a valid number, removing row"
                    )
                    invalid_rows.append(i)

        # Remove the invalid rows
        df = df.drop(index=invalid_rows)

        # Convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

    logger.debug(
        f"Validation kept {len(df)} valid row(s) and removed {rows_before - len(df)} row(s)"
    )
    return df