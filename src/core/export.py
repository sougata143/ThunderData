from typing import Optional, Dict, Any, Union
import pandas as pd
import json
import sqlite3
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

class DataExporter:
    """Handles data export to various formats and destinations"""
    
    @staticmethod
    def to_csv(data: pd.DataFrame, filepath: str, **kwargs) -> None:
        """Export data to CSV file"""
        data.to_csv(filepath, **kwargs)
    
    @staticmethod
    def to_parquet(data: pd.DataFrame, filepath: str, compression: str = 'snappy') -> None:
        """Export data to Parquet file"""
        table = pa.Table.from_pandas(data)
        pq.write_table(table, filepath, compression=compression)
    
    @staticmethod
    def to_json(data: pd.DataFrame, filepath: str, orient: str = 'records') -> None:
        """Export data to JSON file"""
        data.to_json(filepath, orient=orient)
    
    @staticmethod
    def to_sqlite(data: pd.DataFrame, database: str, table_name: str, if_exists: str = 'replace') -> None:
        """Export data to SQLite database"""
        with sqlite3.connect(database) as conn:
            data.to_sql(table_name, conn, if_exists=if_exists, index=False)
    
    @staticmethod
    def to_excel(data: pd.DataFrame, filepath: str, sheet_name: str = 'Sheet1', **kwargs) -> None:
        """Export data to Excel file"""
        data.to_excel(filepath, sheet_name=sheet_name, **kwargs)
    
    @classmethod
    def export(cls, data: pd.DataFrame, format: str, destination: str, **kwargs) -> None:
        """
        Export data to specified format and destination
        
        Args:
            data: DataFrame to export
            format: Export format ('csv', 'parquet', 'json', 'sqlite', 'excel')
            destination: Export destination (filepath or database connection)
            **kwargs: Additional arguments for specific export functions
        """
        export_functions = {
            'csv': cls.to_csv,
            'parquet': cls.to_parquet,
            'json': cls.to_json,
            'sqlite': cls.to_sqlite,
            'excel': cls.to_excel
        }
        
        if format not in export_functions:
            raise ValueError(f"Unsupported export format: {format}")
        
        export_functions[format](data, destination, **kwargs)
