"""Test TdxQuant equity historical price data module."""

import pytest
from openbb_tdx.models.equity_historical import TdxQuantEquityHistoricalFetcher
from openbb_tdx.utils.helpers import tdx_download
import pandas as pd
from datetime import datetime, timedelta


def test_tdx_download():
    """Test tdx_download function."""
    # Test with a valid symbol
    symbol = "600000"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    data = tdx_download(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period="daily",
        use_cache=True
    )
    
    # Check if data is returned as a DataFrame
    assert isinstance(data, pd.DataFrame)
    
    # Check if required columns are present
    required_columns = ["date", "open", "high", "low", "close", "volume"]
    for col in required_columns:
        assert col in data.columns
    
    # Check if data is not empty
    assert not data.empty


def test_tdx_download_invalid_symbol():
    """Test tdx_download with invalid symbol."""
    symbol = "INVALID"
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    data = tdx_download(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period="daily",
        use_cache=True
    )
    
    # Check if empty DataFrame is returned for invalid symbol
    assert isinstance(data, pd.DataFrame)
    assert data.empty


def test_transform_query():
    """Test transform_query method."""
    params = {"symbol": "600000"}
    transformed_params = TdxQuantEquityHistoricalFetcher.transform_query(params)
    
    # Check if start_date and end_date are set if not provided
    assert hasattr(transformed_params, "start_date")
    assert hasattr(transformed_params, "end_date")
    assert hasattr(transformed_params, "symbol")
    assert transformed_params.symbol == "600000"


def test_extract_data():
    """Test extract_data method."""
    from openbb_tdx.models.equity_historical import TdxQuantEquityHistoricalQueryParams
    
    query = TdxQuantEquityHistoricalQueryParams(
        symbol="600000",
        start_date=datetime.now().date() - timedelta(days=30),
        end_date=datetime.now().date(),
        period="daily",
        use_cache=True
    )
    
    data = TdxQuantEquityHistoricalFetcher.extract_data(query, None)
    
    # Check if data is returned as a list of dictionaries
    assert isinstance(data, list)
    
    # Check if each item in the list is a dictionary
    if data:
        assert isinstance(data[0], dict)


def test_transform_data():
    """Test transform_data method."""
    from openbb_tdx.models.equity_historical import TdxQuantEquityHistoricalQueryParams, TdxQuantEquityHistoricalData
    
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
    
    transformed_data = TdxQuantEquityHistoricalFetcher.transform_data(query, sample_data)
    
    # Check if data is returned as a list of TdxQuantEquityHistoricalData objects
    assert isinstance(transformed_data, list)
    
    # Check if each item in the list is a TdxQuantEquityHistoricalData object
    if transformed_data:
        assert isinstance(transformed_data[0], TdxQuantEquityHistoricalData)
        assert transformed_data[0].date == "2023-01-01"
        assert transformed_data[0].open == 10.0
        assert transformed_data[0].high == 11.0
        assert transformed_data[0].low == 9.0
        assert transformed_data[0].close == 10.5
        assert transformed_data[0].volume == 1000000
