"""TdxQuant Equity Dividends Model.

This module implements the TdxQuant Equity Dividends data provider for the OpenBB Platform.
It provides functionality to fetch historical dividend data from TdxQuant API.

Classes:
    TdxQuantEquityDividendsQueryParams: Query parameters for TdxQuant Equity Dividends
    TdxQuantEquityDividendsData: Data model for TdxQuant Equity Dividends
    TdxQuantEquityDividendsFetcher: Fetcher for TdxQuant Equity Dividends data
"""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
import logging
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_tdx import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)


class TdxQuantEquityDividendsQueryParams(HistoricalDividendsQueryParams):
    """TdxQuant Equity Dividends Query Parameters.

    Attributes:
        symbol (str): Symbol representing the entity requested in the data.
        start_date (Optional[dateType]): Start date for the dividend records.
        end_date (Optional[dateType]): End date for the dividend records.
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class TdxQuantEquityDividendsData(HistoricalDividendsData):
    """TdxQuant Equity Dividends Data Model.

    Attributes:
        symbol (str): Stock symbol code.
        name (str): Company name.
        ex_dividend_date (dateType): Ex-dividend date.
        declaration_date (dateType): Dividend announcement date.
        record_date (dateType): Record date for shareholders.
        payable_date (dateType): Payment date.
        amount (float): Dividend amount per share.
        dividend_type (str): Type of dividend (cash, stock, etc.).
        dividend_ratio (float): Dividend ratio per share.
        dividend_yield (float): Dividend yield percentage.
        bonus_share_ratio (float): Bonus share ratio.
        rights_issue_ratio (float): Rights issue ratio.
        tracking_number (str): Dividend tracking number.
    """

    symbol: Optional[str] = Field(
        default=None,
        description="Stock symbol code.",
    )
    name: Optional[str] = Field(
        default=None,
        description="Company name.",
    )
    ex_dividend_date: Optional[dateType] = Field(
        default=None,
        description="Ex-dividend date - the date on which the stock begins trading without rights to the dividend.",
    )
    declaration_date: Optional[dateType] = Field(
        default=None,
        description="Dividend announcement date.",
        validation_alias="announce_date",
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="Record date for shareholders.",
    )
    payable_date: Optional[dateType] = Field(
        default=None,
        description="Payment date.",
    )
    amount: Optional[float] = Field(
        default=None,
        description="The dividend amount per share.",
    )
    dividend_type: Optional[str] = Field(
        default=None,
        description="Type of dividend (cash/stock/combination).",
    )
    dividend_ratio: Optional[float] = Field(
        default=None,
        description="Dividend ratio per share.",
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield as a percentage.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    bonus_share_ratio: Optional[float] = Field(
        default=None,
        description="Bonus share ratio.",
    )
    rights_issue_ratio: Optional[float] = Field(
        default=None,
        description="Rights issue ratio.",
    )
    tracking_number: Optional[str] = Field(
        default=None,
        description="Dividend tracking number.",
        validation_alias="dividend_no",
    )

    @field_validator(
        "declaration_date",
        "record_date",
        "ex_dividend_date",
        "payable_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v: Any) -> Optional[dateType]:
        """Validate and parse date fields."""
        if v is None:
            return None
        if isinstance(v, dateType):
            return v
        if isinstance(v, str):
            if not v:
                return None
            try:
                return dateType.fromisoformat(v)
            except ValueError:
                return None
        return None

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Override model_validate to handle alias mapping manually."""
        if isinstance(obj, dict):
            data = obj.copy()
            if "dividend_ratio" in data and "amount" not in data:
                data["amount"] = data["dividend_ratio"]
        else:
            data = obj
        return super().model_validate(data, **kwargs)


class TdxQuantEquityDividendsFetcher(
    Fetcher[
        TdxQuantEquityDividendsQueryParams,
        List[TdxQuantEquityDividendsData],
    ]
):
    """TdxQuant Equity Dividends Fetcher.

    This class is responsible for fetching equity dividend data from TdxQuant API.
    It implements the three required methods for a Fetcher:
    - transform_query: Transforms the query parameters
    - extract_data: Extracts the raw data from TdxQuant API
    - transform_data: Transforms the raw data into the standard model
    """

    @staticmethod
    def transform_query(
        params: Dict[str, Any],
    ) -> TdxQuantEquityDividendsQueryParams:
        """Transform the query parameters.

        Args:
            params (Dict[str, Any]): The raw query parameters

        Returns:
            TdxQuantEquityDividendsQueryParams: The transformed query parameters
        """
        return TdxQuantEquityDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TdxQuantEquityDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from TdxQuant API.

        Args:
            query (TdxQuantEquityDividendsQueryParams): The query parameters
            credentials (Optional[Dict[str, str]]): The credentials for TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[Dict]: The raw data from TdxQuant API
        """
        # pylint: disable=import-outside-toplevel
        from tqcenter import tq

        symbols = query.symbol.split(",") if "," in query.symbol else [query.symbol]
        all_data: List[Dict] = []

        for symbol in symbols:
            try:
                symbol_b, symbol_f, market = normalize_symbol(symbol.strip())

                try:
                    tq.initialize(__file__)
                except Exception as e:
                    logger.warning(f"TdxQuant initialization warning: {e}")

                start_time = ""
                end_time = ""

                if query.start_date:
                    if hasattr(query.start_date, "strftime"):
                        start_time = query.start_date.strftime("%Y%m%d")
                    else:
                        start_time = str(query.start_date)

                if query.end_date:
                    if hasattr(query.end_date, "strftime"):
                        end_time = query.end_date.strftime("%Y%m%d")
                    else:
                        end_time = str(query.end_date)

                divid_factors = tq.get_divid_factors(
                    stock_code=symbol_f,
                    start_time=start_time,
                    end_time=end_time,
                )

                if divid_factors is None:
                    logger.info(f"No dividend data found for symbol {symbol}")
                    continue

                if isinstance(divid_factors, dict):
                    if "ErrorId" in divid_factors and divid_factors["ErrorId"] != "0":
                        logger.error(f"API error for symbol {symbol}: {divid_factors.get('ErrorId')}")
                        continue
                    logger.info(f"No dividend data found for symbol {symbol}")
                    continue

                if hasattr(divid_factors, 'empty') and divid_factors.empty:
                    logger.info(f"No dividend data found for symbol {symbol}")
                    continue

                if hasattr(divid_factors, 'iterrows'):
                    type_mapping = {
                        1: "除权除息",
                        11: "扩缩股",
                        15: "重新调整",
                    }
                    for idx, row in divid_factors.iterrows():
                        bonus_val = row.get("Bonus", 0)
                        share_bonus_val = row.get("ShareBonus", 0)
                        allotment_val = row.get("Allotment", 0)

                        item = {
                            "symbol": symbol_b,
                            "ex_dividend_date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                            "dividend_type": type_mapping.get(int(row.get("Type", 0)), "其他"),
                            "amount": float(bonus_val) / 10 if bonus_val is not None and bonus_val != 0 else None,
                            "bonus_share_ratio": float(share_bonus_val) / 10 if share_bonus_val is not None and share_bonus_val != 0 else None,
                            "rights_issue_ratio": float(allotment_val) / 10 if allotment_val is not None and allotment_val != 0 else None,
                        }
                        all_data.append(item)
                    logger.info(f"Retrieved {len(divid_factors)} dividend records for {symbol}")
                else:
                    logger.warning(f"Unexpected data format for symbol {symbol}: {type(divid_factors)}")

            except Exception as e:
                logger.error(f"Error fetching dividend data for symbol {symbol}: {e}")
                continue

        return all_data

    @staticmethod
    def transform_data(
        query: TdxQuantEquityDividendsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantEquityDividendsData]:
        """Transform the raw data into the standard model.

        Args:
            query (TdxQuantEquityDividendsQueryParams): The query parameters
            data (List[Dict]): The raw data from TdxQuant API
            **kwargs (Any): Additional keyword arguments

        Returns:
            List[TdxQuantEquityDividendsData]: The transformed data
        """
        result: List[TdxQuantEquityDividendsData] = []
        for item in data:
            try:
                item_copy = item.copy()
                if "dividend_ratio" in item_copy and "amount" not in item_copy:
                    item_copy["amount"] = item_copy["dividend_ratio"]
                result.append(TdxQuantEquityDividendsData(**item_copy))
            except Exception as e:
                logger.warning(f"Error transforming dividend record: {e}")
                continue

        logger.info(f"Transformed {len(result)} dividend records.")
        return result
