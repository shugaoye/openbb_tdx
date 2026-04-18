"""Unit tests for TdxQuant Equity Profile module."""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd

from openbb_tdx.models.equity_profile import (
    TdxQuantEquityProfileQueryParams,
    TdxQuantEquityProfileData,
    TdxQuantEquityProfileFetcher,
)
from openbb_core.provider.standard_models.equity_info import EquityInfoData


class TestTdxQuantEquityProfileQueryParams:
    """Test suite for query parameters model."""

    def test_single_symbol(self):
        """Test query params with single symbol."""
        params = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        assert params.symbol == "688318.SH"
        assert params.use_cache == True

    def test_multiple_symbols(self):
        """Test query params with multiple symbols."""
        params = TdxQuantEquityProfileQueryParams(
            symbol="688318.SH,600519.SH",
            use_cache=False
        )
        assert params.symbol == "688318.SH,600519.SH"
        assert params.use_cache == False

    def test_default_use_cache(self):
        """Test default use_cache value."""
        params = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        assert params.use_cache == True


class TestTdxQuantEquityProfileData:
    """Test suite for data model."""

    def test_data_validation_with_valid_data(self):
        """Test data model validation with valid input."""
        test_data = {
            "symbol": "688318.SH",
            "name": "财富趋势",
            "listed_date": "20200427",
            "sector": "软件服务",
            "hq_state": "深圳板块",
            "employees": 25611,
            "total_assets": 235598.84,
            "total_liabilities": 370454.03,
            "revenue": 19827.85,
            "net_income": 18421.34,
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.name == "财富趋势"
        assert data.listed_date == date(2020, 4, 27)
        assert data.sector == "软件服务"
        assert data.hq_state == "深圳板块"
        assert data.employees == 25611
        assert data.total_assets == 235598.84

    def test_data_validation_with_empty_strings(self):
        """Test data model validation with empty strings."""
        test_data = {
            "symbol": "688318.SH",
            "Name": "",
            "J_start": "",
            "rs_hyname": "",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.name is None
        assert data.listed_date is None
        assert data.sector is None

    def test_data_validation_with_nan_values(self):
        """Test data model validation with NaN values."""
        test_data = {
            "symbol": "688318.SH",
            "Name": float('nan'),
            "J_zgb": float('nan'),
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.name is None
        assert data.employees is None

    def test_data_validation_with_invalid_date(self):
        """Test data model validation with invalid date format."""
        test_data = {
            "symbol": "688318.SH",
            "J_start": "invalid_date",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.listed_date is None

    def test_field_alias_mapping(self):
        """Test that field aliases are correctly mapped."""
        test_data = {
            "symbol": "688318.SH",
            "name": "测试公司",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.name == "测试公司"

    def test_numeric_field_validation(self):
        """Test numeric field validation with various inputs."""
        test_data = {
            "symbol": "688318.SH",
            "employees": "25611",
            "total_assets": 235598.84,
            "total_liabilities": "",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.employees == 25611
        assert data.total_assets == 235598.84
        assert data.total_liabilities is None

    def test_data_validation_with_empty_strings(self):
        """Test that empty strings are converted to None."""
        test_data = {
            "symbol": "688318.SH",
            "name": "",
            "listed_date": "",
            "sector": "",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.name is None
        assert data.listed_date is None
        assert data.sector is None

    def test_data_validation_with_invalid_date(self):
        """Test that invalid dates are handled gracefully."""
        test_data = {
            "symbol": "688318.SH",
            "listed_date": "invalid_date",
        }

        data = TdxQuantEquityProfileData.model_validate(test_data)

        assert data.symbol == "688318.SH"
        assert data.listed_date is None


class TestTdxQuantEquityProfileFetcher:
    """Test suite for fetcher implementation."""

    @pytest.fixture
    def mock_tq(self):
        """Mock TdxQuant API."""
        with patch('tqcenter.tq') as mock:
            yield mock

    def test_transform_query(self):
        """Test query transformation."""
        params = {
            "symbol": "688318.SH",
            "use_cache": True
        }

        result = TdxQuantEquityProfileFetcher.transform_query(params)

        assert isinstance(result, TdxQuantEquityProfileQueryParams)
        assert result.symbol == "688318.SH"
        assert result.use_cache == True

    @pytest.mark.asyncio
    async def test_extract_data_success(self, mock_tq):
        """Test successful data extraction."""
        mock_tq.get_stock_info.return_value = {
            "Name": "财富趋势",
            "J_start": "20200427",
            "ErrorId": "0"
        }
        mock_tq.initialize.return_value = None

        query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")

        result = await TdxQuantEquityProfileFetcher.aextract_data(query, {})

        assert len(result) == 1
        assert result[0]["symbol"] == "688318.SH"
        assert result[0]["name"] == "财富趋势"  # Mapped from "Name"
        assert result[0]["listed_date"] == "20200427"  # Mapped from "J_start"

    @pytest.mark.asyncio
    async def test_extract_data_no_data(self, mock_tq):
        """Test data extraction when no data is returned."""
        mock_tq.get_stock_info.return_value = None
        mock_tq.initialize.return_value = None

        query = TdxQuantEquityProfileQueryParams(symbol="INVALID.SH")

        with pytest.raises(Exception):
            await TdxQuantEquityProfileFetcher.aextract_data(query, {})

    @pytest.mark.asyncio
    async def test_extract_data_api_error(self, mock_tq):
        """Test data extraction when API returns error."""
        mock_tq.get_stock_info.return_value = {
            "ErrorId": "1",
            "ErrorMsg": "Invalid symbol"
        }
        mock_tq.initialize.return_value = None

        query = TdxQuantEquityProfileQueryParams(symbol="INVALID.SH")

        with pytest.raises(Exception):
            await TdxQuantEquityProfileFetcher.aextract_data(query, {})

    @pytest.mark.asyncio
    async def test_extract_data_multiple_symbols(self, mock_tq):
        """Test data extraction for multiple symbols."""
        def mock_get_stock_info(stock_code, field_list):
            if stock_code == "688318.SH":
                return {"Name": "财富趋势", "ErrorId": "0"}
            elif stock_code == "600519.SH":
                return {"Name": "贵州茅台", "ErrorId": "0"}
            return None

        mock_tq.get_stock_info.side_effect = mock_get_stock_info
        mock_tq.initialize.return_value = None

        query = TdxQuantEquityProfileQueryParams(symbol="688318.SH,600519.SH")

        result = await TdxQuantEquityProfileFetcher.aextract_data(query, {})

        assert len(result) == 2
        assert result[0]["symbol"] == "688318.SH"
        assert result[0]["name"] == "财富趋势"
        assert result[1]["symbol"] == "600519.SH"
        assert result[1]["name"] == "贵州茅台"

    def test_transform_data(self):
        """Test data transformation."""
        query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        # Data from aextract_data has mapped field names (OpenBB field names)
        raw_data = [
            {
                "symbol": "688318.SH",
                "name": "财富趋势",
                "listed_date": "20200427",
                "sector": "软件服务",
            }
        ]

        result = TdxQuantEquityProfileFetcher.transform_data(query, raw_data)

        assert len(result) == 1
        assert isinstance(result[0], TdxQuantEquityProfileData)
        assert result[0].symbol == "688318.SH"
        assert result[0].name == "财富趋势"
        assert result[0].listed_date == date(2020, 4, 27)
        assert result[0].sector == "软件服务"


def is_tdxquant_available() -> bool:
    """Check if TdxQuant client is available."""
    try:
        from tqcenter import tq
        import os
        tq.initialize(os.path.abspath(__file__))
        test = tq.get_stock_info(stock_code='000001.SZ', field_list=['Name'])
        return test is not None and test.get('ErrorId', '1') == '0'
    except Exception:
        return False


class TestIntegration:
    """Integration tests for the complete fetcher workflow."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not is_tdxquant_available(),
        reason="TdxQuant client not available"
    )
    async def test_full_workflow(self):
        """Test complete fetcher workflow with real TdxQuant client."""
        fetcher = TdxQuantEquityProfileFetcher()
        params = {"symbol": "688318.SH"}

        result = await fetcher.fetch_data(params, {})

        assert len(result) > 0
        assert isinstance(result[0], EquityInfoData)
        assert hasattr(result[0], "name")
        assert result[0].name is not None
