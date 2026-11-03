
# data_processor.py
import logging
import pandas as pd
 
logger = logging.getLogger(__name__)
 
 
def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    result = df.drop_duplicates()
    logger.debug(f"remove_duplicates: removed {before - len(result)} duplicate row(s)")
    return result
 
 
def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis not in ("rows", "columns"):
        message = f"Unsupported axis '{axis}'. Use 'rows' or 'columns'."
        logger.error(message)
        raise ValueError(message)
 
    if axis == "rows":
        before = len(df)
        result = df.dropna(axis=0)
        logger.debug(f"handle_missing: removed {before - len(result)} row(s) with missing values")
    else:
        before = len(df.columns)
        result = df.dropna(axis=1)
        logger.debug(f"handle_missing: removed {before - len(result.columns)} column(s) with missing values")
 
    return result
 
 
def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        message = f"Unsupported outlier method '{method}'. Use 'iqr' or 'zscore'."
        logger.error(message)
        raise ValueError(message)
 
    result = df
    for col in columns:
        if col not in result.columns:
            logger.warning(f"remove_outliers: column '{col}' does not exist, skipping it")
            continue
        values = result[col]
        # True/False columns count as numeric in pandas, but outliers make no sense there
        if not pd.api.types.is_numeric_dtype(values) or pd.api.types.is_bool_dtype(values):
            logger.warning(f"remove_outliers: column '{col}' is not numeric, skipping it")
            continue
 
        if method == "iqr":
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            is_outlier = (values < lower) | (values > upper)
        else:  # method == "zscore"
            z_scores = (values - values.mean()) / values.std()
            is_outlier = z_scores.abs() > threshold
 
        before = len(result)
        result = result[~is_outlier]
        logger.debug(
            f"remove_outliers: column '{col}', method={method}, threshold={threshold}, "
            f"removed {before - len(result)} row(s)"
        )
 
    return result
 
def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    steps = config["processing"]

    if steps["remove_duplicates"]:
        df = remove_duplicates(df)

    missing = steps["missing"]
    if missing["enabled"]:
        df = handle_missing(df, axis=missing["axis"])

    outliers = steps["outliers"]
    if outliers["enabled"]:
        df = remove_outliers(
            df,
            columns=outliers["columns"],
            method=outliers["method"],
            threshold=outliers["threshold"],
        )

    return df
 
 
def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before, columns_before = df_before.shape
    rows_after, columns_after = df_after.shape
 
    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }
 
