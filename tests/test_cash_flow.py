"""Tests for TdxQuant Cash Flow Statement Fetcher."""

from datetime import date
import pytest
from unittest.mock import patch, MagicMock
from openbb_tdx.models.cash_flow import (
    TdxQuantCashFlowStatementFetcher,
    TdxQuantCashFlowStatementQueryParams,
    TdxQuantCashFlowStatementData,
)


class TestTdxQuantCashFlowStatementFetcher:
    """Test cases for TdxQuant Cash Flow Statement Fetcher."""

    def test_transform_query(self):
        """Test transform_query returns correct params."""
        params = {
            "symbol": "600519.SH",
            "period": "annual",
            "limit": 5,
        }
        result = TdxQuantCashFlowStatementFetcher.transform_query(params)

        assert isinstance(result, TdxQuantCashFlowStatementQueryParams)
        assert result.symbol == "600519.SH"
        assert result.period == "annual"
        assert result.limit == 5

    def test_transform_query_default_values(self):
        """Test transform_query with default values."""
        params = {"symbol": "600519.SH"}
        result = TdxQuantCashFlowStatementFetcher.transform_query(params)

        assert result.period == "annual"
        assert result.limit == 5

    def test_transform_query_with_use_cache(self):
        """Test transform_query with use_cache parameter."""
        params = {
            "symbol": "600519.SH",
            "use_cache": False,
        }
        result = TdxQuantCashFlowStatementFetcher.transform_query(params)

        assert result.use_cache is False

    @patch("openbb_tdx.models.cash_flow.get_financial_statement_data")
    def test_extract_data_success(self, mock_get_data):
        """Test extract_data returns correct data."""
        mock_data = MagicMock()
        mock_data.empty = False
        mock_data.to_dict.return_value = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "net_cash_from_operating_activities": 500000000.0,
                "net_cash_from_investing_activities": -100000000.0,
                "net_cash_from_financing_activities": -200000000.0,
                "net_change_in_cash_and_equivalents": 200000000.0,
            }
        ]
        mock_get_data.return_value = mock_data

        query = TdxQuantCashFlowStatementQueryParams(
            symbol="600519.SH",
            period="annual",
            limit=5,
        )

        result = TdxQuantCashFlowStatementFetcher.extract_data(query, {})

        assert len(result) == 1
        assert result[0]["period_ending"] == "2023-12-31"
        mock_get_data.assert_called_once()

    @patch("openbb_tdx.models.cash_flow.get_financial_statement_data")
    def test_extract_data_empty(self, mock_get_data):
        """Test extract_data raises EmptyDataError when no data."""
        from openbb_core.provider.utils.errors import EmptyDataError

        mock_data = MagicMock()
        mock_data.empty = True
        mock_get_data.return_value = mock_data

        query = TdxQuantCashFlowStatementQueryParams(
            symbol="INVALID.SYMBOL",
            period="annual",
            limit=5,
        )

        with pytest.raises(EmptyDataError):
            TdxQuantCashFlowStatementFetcher.extract_data(query, {})

    def test_transform_data(self):
        """Test transform_data returns correct model."""
        data = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "net_cash_from_operating_activities": 500000000.0,
                "net_cash_from_investing_activities": -100000000.0,
                "net_cash_from_financing_activities": -200000000.0,
            }
        ]

        query = TdxQuantCashFlowStatementQueryParams(symbol="600519.SH")

        result = TdxQuantCashFlowStatementFetcher.transform_data(query, data)

        assert len(result) == 1
        assert isinstance(result[0], TdxQuantCashFlowStatementData)
        assert result[0].net_cash_from_operating_activities == 500000000.0

    def test_transform_data_multiple_records(self):
        """Test transform_data handles multiple records."""
        data = [
            {
                "period_ending": "2023-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2023,
                "net_cash_from_operating_activities": 500000000.0,
            },
            {
                "period_ending": "2022-12-31",
                "fiscal_period": "Q4",
                "fiscal_year": 2022,
                "net_cash_from_operating_activities": 450000000.0,
            },
        ]

        query = TdxQuantCashFlowStatementQueryParams(symbol="600519.SH")

        result = TdxQuantCashFlowStatementFetcher.transform_data(query, data)

        assert len(result) == 2
        assert result[0].fiscal_year == 2023
        assert result[1].fiscal_year == 2022

    def test_data_model_fields(self):
        """Test that TdxQuantCashFlowStatementData has expected fields."""
        data = TdxQuantCashFlowStatementData(
            period_ending=date(2023, 12, 31),
            fiscal_period="Q4",
            fiscal_year=2023,
            net_income=200000000.0,
            net_cash_from_operating_activities=500000000.0,
            net_cash_from_investing_activities=-100000000.0,
            net_cash_from_financing_activities=-200000000.0,
            capital_expenditure=-50000000.0,
            free_cash_flow=450000000.0,
        )

        assert data.period_ending == date(2023, 12, 31)
        assert data.fiscal_period == "Q4"
        assert data.fiscal_year == 2023
        assert data.net_cash_from_operating_activities == 500000000.0
        assert data.free_cash_flow == 450000000.0


class TestTdxQuantCashFlowStatementQueryParams:
    """Test cases for TdxQuant Cash Flow Statement Query Params."""

    def test_period_choices(self):
        """Test period field has correct choices."""
        assert TdxQuantCashFlowStatementQueryParams.__json_schema_extra__["period"]["choices"] == [
            "annual",
            "quarter",
        ]

    def test_default_values(self):
        """Test default values are set correctly."""
        params = TdxQuantCashFlowStatementQueryParams(symbol="600519.SH")

        assert params.period == "annual"
        assert params.limit == 5
        assert params.use_cache is True
