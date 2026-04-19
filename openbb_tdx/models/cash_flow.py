"""TdxQuant Cash Flow Statement Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tdx.utils.helpers import get_financial_statement_data


class TdxQuantCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """TdxQuant Cash Flow Statement Query.

    Source: https://tdxquant.com/api
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class TdxQuantCashFlowStatementData(CashFlowStatementData):
    """TdxQuant Cash Flow Statement Data."""

    __alias_dict__ = {
        "period_ending": "period_ending",
        "fiscal_period": "fiscal_period",
        "fiscal_year": "fiscal_year",
    }

    filing_date: Optional[str] = Field(
        default=None,
        description="The date the financial statement was filed.",
    )
    net_income: Optional[float] = Field(
        default=None,
        description="Net income.",
    )
    depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    net_cash_from_operating_activities: Optional[float] = Field(
        default=None,
        description="Net cash from operating activities.",
    )
    operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Operating cash flow.",
    )
    net_cash_from_investing_activities: Optional[float] = Field(
        default=None,
        description="Net cash from investing activities.",
    )
    net_cash_from_financing_activities: Optional[float] = Field(
        default=None,
        description="Net cash from financing activities.",
    )
    net_change_in_cash_and_equivalents: Optional[float] = Field(
        default=None,
        description="Net change in cash and equivalents.",
    )
    cash_at_beginning_of_period: Optional[float] = Field(
        default=None,
        description="Cash at beginning of period.",
    )
    cash_at_end_of_period: Optional[float] = Field(
        default=None,
        description="Cash at end of period.",
    )
    capital_expenditure: Optional[float] = Field(
        default=None,
        description="Capital expenditure.",
    )
    free_cash_flow: Optional[float] = Field(
        default=None,
        description="Free cash flow.",
    )
    cash_flow_per_share: Optional[float] = Field(
        default=None,
        description="Cash flow per share.",
    )
    net_cash_flow_per_share: Optional[float] = Field(
        default=None,
        description="Net cash flow per share.",
    )
    ratio_of_operating_cash_to_net_income: Optional[float] = Field(
        default=None,
        description="Ratio of operating cash to net income.",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class TdxQuantCashFlowStatementFetcher(
    Fetcher[
        TdxQuantCashFlowStatementQueryParams,
        List[TdxQuantCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantCashFlowStatementQueryParams:
        """Transform the query params."""
        return TdxQuantCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""
        limit = query.limit if query.limit is not None else 5

        data = get_financial_statement_data(
            symbol=query.symbol,
            statement_type="cash_flow",
            period=query.period,
            use_cache=query.use_cache,
            limit=limit,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TdxQuantCashFlowStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantCashFlowStatementData]:
        """Return the transformed data."""
        return [TdxQuantCashFlowStatementData.model_validate(d) for d in data]
