"""Test cases for TdxQuant Equity Search."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from openbb_tdx.models.equity_search import TdxQuantEquitySearchFetcher


@pytest.fixture
def mock_tq():
    """Mock tq module for testing"""
    with patch('openbb_tdx.models.equity_search.tq') as mock:
        mock.initialize.return_value = None
        yield mock


@pytest.mark.asyncio
async def test_basic_search(mock_tq):
    """Test basic search functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '600036.SH', 'Name': '招商银行'},
        {'Code': '601398.SH', 'Name': '工商银行'},
    ]
    
    # Test search
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': '银行', 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 3
    assert results[0].symbol == '000001.SZ'
    assert results[0].name == '平安银行'
    assert results[0].exchange == 'SZ'


@pytest.mark.asyncio
async def test_empty_search(mock_tq):
    """Test empty search functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '000002.SZ', 'Name': '万科A'},
    ]
    
    # Test search
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_limit_parameter(mock_tq):
    """Test limit parameter functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
        {'Code': '000002.SZ', 'Name': '万科A'},
        {'Code': '000004.SZ', 'Name': '*ST国华'},
    ]
    
    # Test with limit=2
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1, 'limit': 2}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_market_filtering(mock_tq):
    """Test market filtering functionality"""
    # Mock response for A-shares
    mock_tq.get_stock_list.side_effect = lambda market, list_type: [
        {'Code': '000001.SZ', 'Name': '平安银行'}
    ] if market == '5' else [
        {'Code': '00001.HK', 'Name': '长和'}
    ]
    
    # Test A-shares
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '000001.SZ'
    assert results[0].exchange == 'SZ'

    # Test Hong Kong
    params = {'query': None, 'market': '102', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 1
    assert results[0].symbol == '00001.HK'
    assert results[0].exchange == 'HK'


@pytest.mark.asyncio
async def test_error_handling(mock_tq):
    """Test error handling functionality"""
    # Mock exception
    mock_tq.get_stock_list.side_effect = Exception("API Error")
    
    # Test error handling
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    
    with pytest.raises(Exception, match="API Error"):
        await fetcher.aextract_data(query, None)


@pytest.mark.asyncio
async def test_symbol_formatting(mock_tq):
    """Test symbol formatting functionality"""
    # Mock response
    mock_tq.get_stock_list.return_value = [
        {'Code': '000001.SZ', 'Name': '平安银行'},
    ]
    
    # Test with suffix
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': '000001.SZ', 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results_with_suffix = fetcher.transform_data(query, data)
    
    # Test without suffix
    params = {'query': '000001', 'market': '5', 'list_type': 1}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results_without_suffix = fetcher.transform_data(query, data)
    
    assert len(results_with_suffix) == 1
    assert len(results_without_suffix) == 1
    assert results_with_suffix[0].symbol == results_without_suffix[0].symbol


@pytest.mark.asyncio
async def test_list_type_zero(mock_tq):
    """Test list_type=0 functionality"""
    # Mock response with just codes
    mock_tq.get_stock_list.return_value = ['000001.SZ', '000002.SZ']
    
    # Test with list_type=0
    fetcher = TdxQuantEquitySearchFetcher()
    params = {'query': None, 'market': '5', 'list_type': 0}
    query = fetcher.transform_query(params)
    data = await fetcher.aextract_data(query, None)
    results = fetcher.transform_data(query, data)
    
    assert len(results) == 2
    assert results[0].symbol == '000001.SZ'
    assert results[0].name == ''
    assert results[1].symbol == '000002.SZ'
    assert results[1].name == ''