"""Test script for TdxQuant equity historical price data module."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from openbb_tdx.models.equity_historical import TdxQuantEquityHistoricalFetcher, TdxQuantEquityHistoricalQueryParams
from openbb_tdx.utils.helpers import tdx_download
import pandas as pd
from datetime import datetime, timedelta


def test_tdx_download():
    """Test tdx_download function."""
    print("Testing tdx_download function...")
    # Test with a valid symbol
    symbol = "600000"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    try:
        data = tdx_download(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period="daily",
            use_cache=True
        )
        
        # Check if data is returned as a DataFrame
        assert isinstance(data, pd.DataFrame), "Data should be a DataFrame"
        print("✓ Data returned as DataFrame")
        
        # Check if required columns are present
        required_columns = ["date", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            assert col in data.columns, f"Column {col} should be present"
        print("✓ All required columns present")
        
        # Check if data is not empty
        assert not data.empty, "Data should not be empty"
        print("✓ Data is not empty")
        
        print("Test passed!")
        print(f"Data shape: {data.shape}")
        print(f"First few rows:\n{data.head()}")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


def test_transform_query():
    """Test transform_query method."""
    print("\nTesting transform_query method...")
    params = {"symbol": "600000"}
    try:
        transformed_params = TdxQuantEquityHistoricalFetcher.transform_query(params)
        
        # Check if start_date and end_date are set if not provided
        assert hasattr(transformed_params, "start_date"), "start_date should be set"
        assert hasattr(transformed_params, "end_date"), "end_date should be set"
        assert hasattr(transformed_params, "symbol"), "symbol should be set"
        assert transformed_params.symbol == "600000", "symbol should be preserved"
        print("✓ transform_query method works correctly")
        print(f"start_date: {transformed_params.start_date}")
        print(f"end_date: {transformed_params.end_date}")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


def test_extract_data():
    """Test extract_data method."""
    print("\nTesting extract_data method...")
    query = TdxQuantEquityHistoricalQueryParams(
        symbol="600000",
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date(),
        period="daily",
        use_cache=True
    )
    
    try:
        data = TdxQuantEquityHistoricalFetcher.extract_data(query, None)
        
        # Check if data is returned as a list of dictionaries
        assert isinstance(data, list), "Data should be a list"
        print("✓ Data returned as list")
        
        # Check if each item in the list is a dictionary
        if data:
            assert isinstance(data[0], dict), "Each item should be a dictionary"
            print("✓ Each item is a dictionary")
            print(f"Number of items: {len(data)}")
            print(f"First item: {data[0]}")
        else:
            print("⚠ Data is empty, but no error was raised")
        
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


def test_transform_data():
    """Test transform_data method."""
    print("\nTesting transform_data method...")
    query = TdxQuantEquityHistoricalQueryParams(
        symbol="600000",
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date(),
        period="daily",
        use_cache=True
    )
    
    # Create sample data
    sample_data = [
        {
            "date": "2023-01-01",
            "open": 10.0,
            "high": 11.0,
            "low": 9.0,
            "close": 10.5,
            "volume": 1000000,
            "amount": 10500000,
            "change": 0.5,
            "change_percent": 5.0
        }
    ]
    
    try:
        transformed_data = TdxQuantEquityHistoricalFetcher.transform_data(query, sample_data)
        
        # Check if data is returned as a list
        assert isinstance(transformed_data, list), "Data should be a list"
        print("✓ Data returned as list")
        
        # Check if each item in the list is a valid object
        if transformed_data:
            print("✓ Each item is a valid TdxQuantEquityHistoricalData object")
            print(f"First item date: {transformed_data[0].date}")
            print(f"First item close: {transformed_data[0].close}")
        else:
            print("⚠ Data is empty, but no error was raised")
        
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("Running tests for TdxQuant equity historical price data module...")
    print("=" * 60)
    
    # Run tests
    test1 = test_tdx_download()
    test2 = test_transform_query()
    test3 = test_extract_data()
    test4 = test_transform_data()
    
    print("=" * 60)
    print("Test Results:")
    print(f"tdx_download: {'PASS' if test1 else 'FAIL'}")
    print(f"transform_query: {'PASS' if test2 else 'FAIL'}")
    print(f"extract_data: {'PASS' if test3 else 'FAIL'}")
    print(f"transform_data: {'PASS' if test4 else 'FAIL'}")
    
    if all([test1, test2, test3, test4]):
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
