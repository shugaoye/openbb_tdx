"""Test script for tdx_download function."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from openbb_tdx.utils.helpers import tdx_download
from mysharelib.tools import normalize_symbol, get_valid_date

import pandas as pd
from datetime import datetime, timedelta, date as dateType


def test_normalize_symbol():
    """Test normalize_symbol function."""
    print("Testing normalize_symbol function...")
    
    # Test various symbol formats
    test_cases = [
        ("600000", ("600000", "600000.SH", "SH")),
        ("000001", ("000001", "000001.SZ", "SZ")),
        ("830001", ("830001", "830001.BJ", "BJ")),
        ("600000.SH", ("600000", "600000.SH", "SH")),
        ("000001.SZ", ("000001", "000001.SZ", "SZ")),
        ("830001.BJ", ("830001", "830001.BJ", "BJ")),
    ]
    
    try:
        for symbol, expected in test_cases:
            result = normalize_symbol(symbol)
            assert result == expected, f"normalize_symbol({symbol}) should return {expected}, but got {result}"
            print(f"✓ normalize_symbol({symbol}) = {result}")
        
        print("All normalize_symbol tests passed!")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


def test_get_valid_date():
    """Test get_valid_date function."""
    print("\nTesting get_valid_date function...")
    
    try:
        # Test with date object
        test_date = datetime.now().date()
        result = get_valid_date(test_date)
        assert result == test_date, f"get_valid_date should return the same date object"
        print(f"✓ get_valid_date(date object) = {result}")
        
        # Test with string
        date_str = "2023-01-01"
        result = get_valid_date(date_str)
        assert result == datetime(2023, 1, 1).date(), f"get_valid_date should parse string correctly"
        print(f"✓ get_valid_date('{date_str}') = {result}")
        
        # Test with datetime object
        test_datetime = datetime.now()
        result = get_valid_date(test_datetime)
        assert isinstance(result, dateType), f"get_valid_date should return a date object"
        print(f"✓ get_valid_date(datetime object) = {result}")
        
        print("All get_valid_date tests passed!")
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False


def test_tdx_download():
    """Test tdx_download function."""
    print("\nTesting tdx_download function...")
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
            use_cache=False
        )
        
        # Check if data is returned as a DataFrame
        assert isinstance(data, pd.DataFrame), "Data should be a DataFrame"
        print("✓ Data returned as DataFrame")
        
        # Print columns for debugging
        print(f"Columns in DataFrame: {list(data.columns)}")
        
        # Check if required columns are present
        required_columns = ["date", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            if col in data.columns:
                print(f"✓ Column {col} is present")
            else:
                print(f"✗ Column {col} is missing")
        
        # Check if data is not empty
        if not data.empty:
            print("✓ Data is not empty")
            print(f"Data shape: {data.shape}")
            print(f"First few rows:\n{data.head()}")
        else:
            print("⚠ Data is empty, but no error was raised")
        
        return True
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Running tests for TdxQuant tdx_download function...")
    print("=" * 60)
    
    # Run tests
    test1 = test_normalize_symbol()
    test2 = test_get_valid_date()
    test3 = test_tdx_download()
    
    print("=" * 60)
    print("Test Results:")
    print(f"normalize_symbol: {'PASS' if test1 else 'FAIL'}")
    print(f"get_valid_date: {'PASS' if test2 else 'FAIL'}")
    print(f"tdx_download: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
