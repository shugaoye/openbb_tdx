"""TdxQuant Income Statement Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tdx.utils.helpers import get_financial_statement_data


class TdxQuantIncomeStatementQueryParams(IncomeStatementQueryParams):
    """TdxQuant Income Statement Query.

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


class TdxQuantIncomeStatementData(IncomeStatementData):
    """TdxQuant Income Statement Data."""

    __alias_dict__ = {
        "period_ending": "period_ending",
        "fiscal_period": "fiscal_period",
        "fiscal_year": "fiscal_year",
    }

    filing_date: Optional[str] = Field(
        default=None,
        description="The date the financial statement was filed.",
    )
    revenue: Optional[float] = Field(
        default=None,
        description="Total revenue.",
    )
    operating_income: Optional[float] = Field(
        default=None,
        description="Operating income.",
    )
    net_income: Optional[float] = Field(
        default=None,
        description="Net income.",
    )
    net_income_from_continuing_operations: Optional[float] = Field(
        default=None,
        description="Net income from continuing operations.",
    )
    net_income_attributable_to_common_shareholders: Optional[float] = Field(
        default=None,
        description="Net income attributable to common shareholders.",
    )
    consolidated_net_income: Optional[float] = Field(
        default=None,
        description="Consolidated net income.",
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Basic earnings per share.",
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Diluted earnings per share.",
    )
    depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    ebit: Optional[float] = Field(
        default=None,
        description="Earnings before interest and taxes.",
    )
    ebitda: Optional[float] = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation and amortization.",
    )
    weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Weighted average basic shares outstanding.",
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity.",
    )
    net_profit_margin: Optional[float] = Field(
        default=None,
        description="Net profit margin.",
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin.",
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Revenue growth.",
    )
    net_income_growth: Optional[float] = Field(
        default=None,
        description="Net income growth.",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="EBITDA margin.",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class TdxQuantIncomeStatementFetcher(
    Fetcher[
        TdxQuantIncomeStatementQueryParams,
        List[TdxQuantIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantIncomeStatementQueryParams:
        """Transform the query params."""
        return TdxQuantIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""
        limit = query.limit if query.limit is not None else 5

        data = get_financial_statement_data(
            symbol=query.symbol,
            statement_type="income_statement",
            period=query.period,
            use_cache=query.use_cache,
            limit=limit,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TdxQuantIncomeStatementQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantIncomeStatementData]:
        """Return the transformed data."""
        return [TdxQuantIncomeStatementData.model_validate(d) for d in data]
