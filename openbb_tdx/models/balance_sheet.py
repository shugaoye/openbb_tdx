"""TdxQuant Balance Sheet Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_tdx.utils.helpers import get_financial_statement_data


class TdxQuantBalanceSheetQueryParams(BalanceSheetQueryParams):
    """TdxQuant Balance Sheet Query.

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


class TdxQuantBalanceSheetData(BalanceSheetData):
    """TdxQuant Balance Sheet Data."""

    __alias_dict__ = {
        "period_ending": "period_ending",
        "fiscal_period": "fiscal_period",
        "fiscal_year": "fiscal_year",
    }

    filing_date: Optional[str] = Field(
        default=None,
        description="The date the financial statement was filed.",
    )
    cash_and_cash_equivalents: Optional[float] = Field(
        default=None,
        description="Cash and cash equivalents.",
    )
    short_term_investments: Optional[float] = Field(
        default=None,
        description="Short term investments.",
    )
    cash_and_short_term_investments: Optional[float] = Field(
        default=None,
        description="Cash and short term investments.",
    )
    accounts_receivable: Optional[float] = Field(
        default=None,
        description="Accounts receivable.",
    )
    net_receivables: Optional[float] = Field(
        default=None,
        description="Net receivables.",
    )
    inventory: Optional[float] = Field(
        default=None,
        description="Inventory.",
    )
    total_current_assets: Optional[float] = Field(
        default=None,
        description="Total current assets.",
    )
    plant_property_equipment_net: Optional[float] = Field(
        default=None,
        description="Plant property and equipment, net.",
    )
    goodwill_and_intangible_assets: Optional[float] = Field(
        default=None,
        description="Goodwill and intangible assets.",
    )
    long_term_investments: Optional[float] = Field(
        default=None,
        description="Long term investments.",
    )
    non_current_assets: Optional[float] = Field(
        default=None,
        description="Non-current assets.",
    )
    total_assets: Optional[float] = Field(
        default=None,
        description="Total assets.",
    )
    accounts_payable: Optional[float] = Field(
        default=None,
        description="Accounts payable.",
    )
    short_term_debt: Optional[float] = Field(
        default=None,
        description="Short term debt.",
    )
    total_current_liabilities: Optional[float] = Field(
        default=None,
        description="Total current liabilities.",
    )
    long_term_debt: Optional[float] = Field(
        default=None,
        description="Long term debt.",
    )
    total_long_term_debt: Optional[float] = Field(
        default=None,
        description="Total long term debt.",
    )
    total_non_current_liabilities: Optional[float] = Field(
        default=None,
        description="Total non-current liabilities.",
    )
    total_liabilities: Optional[float] = Field(
        default=None,
        description="Total liabilities.",
    )
    common_stock: Optional[float] = Field(
        default=None,
        description="Common stock.",
    )
    retained_earnings: Optional[float] = Field(
        default=None,
        description="Retained earnings.",
    )
    total_common_equity: Optional[float] = Field(
        default=None,
        description="Total common equity.",
    )
    minority_interest: Optional[float] = Field(
        default=None,
        description="Minority interest.",
    )
    total_liabilities_and_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Total liabilities and shareholders' equity.",
    )
    total_equity: Optional[float] = Field(
        default=None,
        description="Total equity.",
    )
    net_debt: Optional[float] = Field(
        default=None,
        description="Net debt.",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class TdxQuantBalanceSheetFetcher(
    Fetcher[
        TdxQuantBalanceSheetQueryParams,
        List[TdxQuantBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantBalanceSheetQueryParams:
        """Transform the query params."""
        return TdxQuantBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""
        limit = query.limit if query.limit is not None else 5

        data = get_financial_statement_data(
            symbol=query.symbol,
            statement_type="balance_sheet",
            period=query.period,
            use_cache=query.use_cache,
            limit=limit,
        )

        if data.empty:
            raise EmptyDataError()

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TdxQuantBalanceSheetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantBalanceSheetData]:
        """Return the transformed data."""
        return [TdxQuantBalanceSheetData.model_validate(d) for d in data]
