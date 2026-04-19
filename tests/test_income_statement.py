"""Tests for TdxQuant Income Statement Fetcher."""

from datetime import date
import pytest
from unittest.mock import patch, MagicMock
from openbb_tdx.models.income_statement import (
    TdxQuantIncomeStatementFetcher,
    TdxQuantIncomeStatementQueryParams,
    TdxQuantIncomeStatementData,
)


class TestTdxQuantIncomeStatementFetcher:
    """Test cases for TdxQuant Income Statement Fetcher."""

    def test_transform_query(self):
        """Test transform_query returns correct params."""
        params = {
            "symbol": "600519.SH",
            "period": "annual",
            "limit": 5,
        }
        result = TdxQuantIncomeStatementFetcher.transform_query(params)

        assert isinstance(result, TdxQuantIncomeStatementQueryParams)
        assert result.symbol == "600519.SH"
        assert result.period == "annual"
        assert result.limit == 5

    def test_transform_query_default_values(self):
        """Test transform_query with default values."""
        params = {"symbol": "600519.SH"}
        result = TdxQuantIncomeStatementFetcher.transform_query(params)

        assert result.period == "annual"
        assert result.limit == 5

    def test_transform_query_with_use_cache(self):
        """Test transform_query with use_cache parameter."""
        params = {
            "symbol": "600519.SH",
            "use_cache": False,
        }
        result = TdxQuantIncomeStatementFetcher.transform_query(params)

        assert result.use_cache is False

    @patch("openbb_tdx.models.income_statement.get_financial_statement_data")
    def test_extract_data_success(self, mock_get_data):
        """Test extract_data returns correct data."""
        mock_data = MagicMock()
        mock_data.empty = False
        mock_data.to_dict.return_value = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "revenue": 1000000000.0,
                "net_income": 200000000.0,
                "basic_earnings_per_share": 2.5,
            }
        ]
        mock_get_data.return_value = mock_data

        query = TdxQuantIncomeStatementQueryParams(
            symbol="600519.SH",
            period="annual",
            limit=5,
        )

        result = TdxQuantIncomeStatementFetcher.extract_data(query, {})

        assert len(result) == 1
        assert result[0]["period_ending"] == "2023-12-31"
        mock_get_data.assert_called_once()

    @patch("openbb_tdx.models.income_statement.get_financial_statement_data")
    def test_extract_data_empty(self, mock_get_data):
        """Test extract_data raises EmptyDataError when no data."""
        from openbb_core.provider.utils.errors import EmptyDataError

        mock_data = MagicMock()
        mock_data.empty = True
        mock_get_data.return_value = mock_data

        query = TdxQuantIncomeStatementQueryParams(
            symbol="INVALID.SYMBOL",
            period="annual",
            limit=5,
        )

        with pytest.raises(EmptyDataError):
            TdxQuantIncomeStatementFetcher.extract_data(query, {})

    def test_transform_data(self):
        """Test transform_data returns correct model."""
        data = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "revenue": 1000000000.0,
                "net_income": 200000000.0,
                "basic_earnings_per_share": 2.5,
            }
        ]

        query = TdxQuantIncomeStatementQueryParams(symbol="600519.SH")

        result = TdxQuantIncomeStatementFetcher.transform_data(query, data)

        assert len(result) == 1
        assert isinstance(result[0], TdxQuantIncomeStatementData)
        assert result[0].revenue == 1000000000.0

    def test_transform_data_multiple_records(self):
        """Test transform_data handles multiple records."""
        data = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "revenue": 1000000000.0,
            },
            {
                "period_ending": "2022-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2022,
                "revenue": 900000000.0,
            },
        ]

        query = TdxQuantIncomeStatementQueryParams(symbol="600519.SH")

        result = TdxQuantIncomeStatementFetcher.transform_data(query, data)

        assert len(result) == 2
        assert result[0].fiscal_year == 2023
        assert result[1].fiscal_year == 2022

    def test_data_model_fields(self):
        """Test that TdxQuantIncomeStatementData has expected fields."""
        data = TdxQuantIncomeStatementData(
            period_ending=date(2023, 12, 31),
            fiscal_period="Q4",
            fiscal_year=2023,
            revenue=1000000000.0,
            operating_income=250000000.0,
            net_income=200000000.0,
            basic_earnings_per_share=2.5,
            diluted_earnings_per_share=2.4,
        )

        assert data.period_ending == date(2023, 12, 31)
        assert data.fiscal_period == "Q4"
        assert data.fiscal_year == 2023
        assert data.revenue == 1000000000.0
        assert data.net_income == 200000000.0
        assert data.basic_earnings_per_share == 2.5


class TestTdxQuantIncomeStatementQueryParams:
    """Test cases for TdxQuant Income Statement Query Params."""

    def test_period_choices(self):
        """Test period field has correct choices."""
        assert TdxQuantIncomeStatementQueryParams.__json_schema_extra__["period"]["choices"] == [
            "annual",
            "quarter",
        ]

    def test_default_values(self):
        """Test default values are set correctly."""
        params = TdxQuantIncomeStatementQueryParams(symbol="600519.SH")

        assert params.period == "annual"
        assert params.limit == 5
        assert params.use_cache is True
