import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0
        
    def save_data(self, df, filename):
        self._counter += 1
        dataset_id = self._counter

        self._store[dataset_id] = {"filename": filename, "data": df.copy()} 
        logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
        return dataset_id
    

    def get_data(self, dataset_id):
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Dataset not found: id={dataset_id}")
            return None
        logger.debug(f"Retrieved dataset: id={dataset_id}")
        return item["data"].copy()

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Dataset metadata not found: id={dataset_id}")
            return None
        
        df = item["data"]
        metadata = {
            "dataset_id": dataset_id,
            "filename": item["filename"],
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist()
            }
        logger.debug(f"Retrieved metadata: id={dataset_id}")
        return metadata

    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if missing."""
        item = self._store.get(dataset_id)
        if item is None:
            logger.debug(f"Dataset not found: id={dataset_id}")
            return False
        
        item['data'] = df.copy()
        logger.debug(f'Updated dataset: id{dataset_id}')
        return item["data"].copy()

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
        logger.debug("Cleared all datasets")