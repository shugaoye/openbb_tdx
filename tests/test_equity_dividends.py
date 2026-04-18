"""Test TdxQuant equity dividends data module."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from openbb_tdx.models.equity_dividends import (
    TdxQuantEquityDividendsFetcher,
    TdxQuantEquityDividendsQueryParams,
    TdxQuantEquityDividendsData,
)


class TestTdxQuantEquityDividendsQueryParams:
    """Tests for TdxQuantEquityDividendsQueryParams class."""

    def test_init_with_symbol_only(self):
        """Test initialization with only symbol."""
        params = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
        assert params.symbol == "600000.SH"

    def test_init_with_date_range(self):
        """Test initialization with date range."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        params = TdxQuantEquityDividendsQueryParams(
            symbol="600000.SH",
            start_date=start_date,
            end_date=end_date,
        )
        assert params.symbol == "600000.SH"
        assert params.start_date == start_date
        assert params.end_date == end_date

    def test_multiple_symbols_string(self):
        """Test multiple symbols as comma-separated string."""
        params = TdxQuantEquityDividendsQueryParams(
            symbol="600000.SH,000001.SZ"
        )
        assert "," in params.symbol


class TestTdxQuantEquityDividendsFetcher:
    """Tests for TdxQuantEquityDividendsFetcher class."""

    def test_transform_query(self):
        """Test transform_query method."""
        params = {"symbol": "600000.SH"}
        result = TdxQuantEquityDividendsFetcher.transform_query(params)

        assert isinstance(result, TdxQuantEquityDividendsQueryParams)
        assert result.symbol == "600000.SH"

    def test_transform_query_with_dates(self):
        """Test transform_query with date parameters."""
        params = {
            "symbol": "600000.SH",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }
        result = TdxQuantEquityDividendsFetcher.transform_query(params)

        assert isinstance(result, TdxQuantEquityDividendsQueryParams)
        assert result.symbol == "600000.SH"

    def test_transform_data_empty_list(self):
        """Test transform_data with empty list."""
        query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
        result = TdxQuantEquityDividendsFetcher.transform_data(query, [])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_transform_data_single_record(self):
        """Test transform_data with single record."""
        query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
        sample_data = [
            {
                "symbol": "600000",
                "code": "600000",
                "name": "浦发银行",
                "ex_dividend_date": "2024-07-15",
                "announce_date": "2024-06-30",
                "record_date": "2024-07-16",
                "payable_date": "2024-07-17",
                "dividend_type": "现金",
                "dividend_ratio": 0.301,
                "dividend_yield": 5.2,
                "bonus_share_ratio": 0.0,
                "rights_issue_ratio": 0.0,
                "dividend_no": "2024001",
            }
        ]

        result = TdxQuantEquityDividendsFetcher.transform_data(query, sample_data)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TdxQuantEquityDividendsData)
        assert result[0].symbol == "600000"
        assert result[0].name == "浦发银行"

    def test_transform_data_multiple_records(self):
        """Test transform_data with multiple records."""
        query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
        sample_data = [
            {
                "symbol": "600000",
                "code": "600000",
                "name": "浦发银行",
                "ex_dividend_date": "2024-07-15",
                "announce_date": "2024-06-30",
                "record_date": "2024-07-16",
                "payable_date": "2024-07-17",
                "dividend_type": "现金",
                "dividend_ratio": 0.301,
                "dividend_yield": 5.2,
                "bonus_share_ratio": 0.0,
                "rights_issue_ratio": 0.0,
                "dividend_no": "2024001",
            },
            {
                "symbol": "600000",
                "code": "600000",
                "name": "浦发银行",
                "ex_dividend_date": "2023-07-14",
                "announce_date": "2023-06-30",
                "record_date": "2023-07-17",
                "payable_date": "2023-07-18",
                "dividend_type": "现金",
                "dividend_ratio": 0.295,
                "dividend_yield": 4.8,
                "bonus_share_ratio": 0.0,
                "rights_issue_ratio": 0.0,
                "dividend_no": "2023001",
            },
        ]

        result = TdxQuantEquityDividendsFetcher.transform_data(query, sample_data)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, TdxQuantEquityDividendsData) for item in result)

    @patch("openbb_tdx.models.equity_dividends.normalize_symbol")
    def test_extract_data_with_dataframe(self, mock_normalize):
        """Test extract_data with DataFrame from TdxQuant API."""
        mock_normalize.return_value = ("600000", "600000.SH", "SH")

        df = pd.DataFrame(
            {
                "Type": [1, 1],
                "Bonus": [6.0, 10.0],
                "AllotPrice": [0.0, 0.0],
                "ShareBonus": [0.0, 4.0],
                "Allotment": [0.0, 0.0],
            },
            index=pd.to_datetime(["2024-07-15", "2023-06-20"]),
        )

        with patch("tqcenter.tq") as mock_tq:
            mock_tq.get_divid_factors.return_value = df

            query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
            result = TdxQuantEquityDividendsFetcher.extract_data(query, None)

        assert isinstance(result, list)
        assert len(result) == 2

        assert result[0]["symbol"] == "600000"
        assert result[0]["ex_dividend_date"] == "2024-07-15"
        assert result[0]["dividend_type"] == "除权除息"
        assert result[0]["amount"] == 0.6
        assert result[0]["bonus_share_ratio"] is None
        assert result[0]["rights_issue_ratio"] is None

        assert result[1]["symbol"] == "600000"
        assert result[1]["ex_dividend_date"] == "2023-06-20"
        assert result[1]["dividend_type"] == "除权除息"
        assert result[1]["amount"] == 1.0
        assert result[1]["bonus_share_ratio"] == 0.4
        assert result[1]["rights_issue_ratio"] is None

    @patch("openbb_tdx.models.equity_dividends.normalize_symbol")
    def test_extract_data_empty_dataframe(self, mock_normalize):
        """Test extract_data with empty DataFrame."""
        mock_normalize.return_value = ("600000", "600000.SH", "SH")

        df = pd.DataFrame()

        with patch("tqcenter.tq") as mock_tq:
            mock_tq.get_divid_factors.return_value = df

            query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
            result = TdxQuantEquityDividendsFetcher.extract_data(query, None)

        assert isinstance(result, list)
        assert len(result) == 0

    @patch("openbb_tdx.models.equity_dividends.normalize_symbol")
    def test_extract_data_none_result(self, mock_normalize):
        """Test extract_data with None result."""
        mock_normalize.return_value = ("600000", "600000.SH", "SH")

        with patch("tqcenter.tq") as mock_tq:
            mock_tq.get_divid_factors.return_value = None

            query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
            result = TdxQuantEquityDividendsFetcher.extract_data(query, None)

        assert isinstance(result, list)
        assert len(result) == 0

    @patch("openbb_tdx.models.equity_dividends.normalize_symbol")
    def test_extract_data_type_11(self, mock_normalize):
        """Test extract_data with Type 11 (扩缩股)."""
        mock_normalize.return_value = ("600000", "600000.SH", "SH")

        df = pd.DataFrame(
            {
                "Type": [11],
                "Bonus": [0.0],
                "AllotPrice": [0.0],
                "ShareBonus": [2.0],
                "Allotment": [0.0],
            },
            index=pd.to_datetime(["2024-07-15"]),
        )

        with patch("tqcenter.tq") as mock_tq:
            mock_tq.get_divid_factors.return_value = df

            query = TdxQuantEquityDividendsQueryParams(symbol="600000.SH")
            result = TdxQuantEquityDividendsFetcher.extract_data(query, None)

        assert len(result) == 1
        assert result[0]["dividend_type"] == "扩缩股"


class TestTdxQuantEquityDividendsData:
    """Tests for TdxQuantEquityDividendsData class."""

    def test_date_validation_valid_string(self):
        """Test date validation with valid string."""
        data = TdxQuantEquityDividendsData(
            symbol="600000",
            ex_dividend_date="2024-07-15",
        )
        assert isinstance(data.ex_dividend_date, date)
        assert data.ex_dividend_date == date(2024, 7, 15)

    def test_date_validation_invalid_string(self):
        """Test date validation with invalid string returns None."""
        data = TdxQuantEquityDividendsData(
            symbol="600000",
            ex_dividend_date="invalid-date",
        )
        assert data.ex_dividend_date is None

    def test_date_validation_none(self):
        """Test date validation with None."""
        data = TdxQuantEquityDividendsData(
            symbol="600000",
            ex_dividend_date=None,
        )
        assert data.ex_dividend_date is None

    def test_date_validation_date_object(self):
        """Test date validation with date object."""
        test_date = date(2024, 7, 15)
        data = TdxQuantEquityDividendsData(
            symbol="600000",
            ex_dividend_date=test_date,
        )
        assert data.ex_dividend_date == test_date

    def test_optional_fields(self):
        """Test that all fields are optional."""
        data = TdxQuantEquityDividendsData(symbol="600000")
        assert data.symbol == "600000"
        assert data.name is None
        assert data.ex_dividend_date is None
        assert data.declaration_date is None
        assert data.record_date is None
        assert data.payable_date is None
        assert data.dividend_type is None
        assert data.dividend_ratio is None
        assert data.dividend_yield is None
        assert data.bonus_share_ratio is None
        assert data.rights_issue_ratio is None
        assert data.tracking_number is None

    def test_all_alias_mappings(self):
        """Test that all alias mappings work correctly."""
        sample_data = {
            "symbol": "600000",
            "code": "600000",
            "name": "测试股票",
            "ex_dividend_date": "2024-07-15",
            "announce_date": "2024-06-30",
            "record_date": "2024-07-16",
            "payable_date": "2024-07-17",
            "dividend_type": "现金",
            "dividend_ratio": 0.301,
            "dividend_yield": 5.2,
            "bonus_share_ratio": 0.1,
            "rights_issue_ratio": 0.2,
            "dividend_no": "2024001",
        }
        data = TdxQuantEquityDividendsData(**sample_data)

        assert data.symbol == "600000"
        assert data.name == "测试股票"
        assert data.ex_dividend_date == date(2024, 7, 15)
        assert data.declaration_date == date(2024, 6, 30)
        assert data.record_date == date(2024, 7, 16)
        assert data.payable_date == date(2024, 7, 17)
        assert data.dividend_type == "现金"
        assert data.dividend_ratio == 0.301
        assert data.dividend_yield == 5.2
        assert data.bonus_share_ratio == 0.1
        assert data.rights_issue_ratio == 0.2
        assert data.tracking_number == "2024001"
