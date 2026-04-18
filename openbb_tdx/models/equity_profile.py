"""TdxQuant Equity Profile Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from datetime import date as dateType, datetime

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, field_validator
import pandas as pd

import logging
from mysharelib.tools import setup_logger, normalize_symbol
from openbb_tdx import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)

class TdxQuantEquityProfileQueryParams(EquityInfoQueryParams):
    """TdxQuant Equity Profile Query Parameters.

    This model extends the standard EquityInfoQueryParams to add
    TdxQuant-specific parameters.

    Attributes
    ----------
    symbol : str
        Stock symbol(s) to query. Multiple symbols can be separated by commas.
        Format: XXXXXX.SH or XXXXXX.SZ (e.g., "688318.SH" or "688318.SH,600519.SH")
    use_cache : bool
        Whether to use cached data. Default is True.
        Cache duration is 1 hour for profile data.

    Examples
    --------
    >>> params = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
    >>> params = TdxQuantEquityProfileQueryParams(symbol="688318.SH,600519.SH", use_cache=False)
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The data is cached for one hour.",
    )


class TdxQuantEquityProfileData(EquityInfoData):
    """TdxQuant Equity Profile Data Model.

    This model represents the equity profile data retrieved from TdxQuant
    and transformed to OpenBB's standard format.

    Attributes
    ----------
    name : str
        Company name
    listed_date : date
        Date when the stock was listed
    sector : str
        Industry sector classification
    hq_state : str
        Headquarters state or region
    employees : float
        Total shares outstanding (used as proxy for company size)
    total_assets : float
        Total assets in 万元 (ten thousand yuan)
    total_liabilities : float
        Total liabilities in 万元
    revenue : float
        Annual revenue in 万元
    net_income : float
        Net income in 万元
    shares_outstanding : float
        Number of outstanding shares in 万股
    eps : float
        Earnings per share
    book_value_per_share : float
        Book value per share
    roe : float
        Return on equity (percentage)

    Examples
    --------
    >>> data = TdxQuantEquityProfileData(
    ...     name="财富趋势",
    ...     listed_date=date(2020, 4, 27),
    ...     sector="软件服务",
    ...     hq_state="深圳板块"
    ... )
    """

    listed_date: Optional[dateType] = Field(
        default=None,
        description="Listing date"
    )
    total_assets: Optional[float] = Field(
        default=None,
        description="Total assets (万元)"
    )
    total_liabilities: Optional[float] = Field(
        default=None,
        description="Total liabilities (万元)"
    )
    revenue: Optional[float] = Field(
        default=None,
        description="Operating revenue (万元)"
    )
    net_income: Optional[float] = Field(
        default=None,
        description="Net profit (万元)"
    )
    shares_outstanding: Optional[float] = Field(
        default=None,
        description="Circulating shares (万股)"
    )
    eps: Optional[float] = Field(
        default=None,
        description="Earnings per share"
    )
    book_value_per_share: Optional[float] = Field(
        default=None,
        description="Net assets per share"
    )
    roe: Optional[float] = Field(
        default=None,
        description="Return on equity (%)"
    )

    @field_validator("name", mode="before", check_fields=False)
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate company name.

        Parameters
        ----------
        v : Optional[str]
            Input value to validate

        Returns
        -------
        Optional[str]
            Validated name or None if invalid

        Examples
        --------
        >>> validate_name("财富趋势")
        '财富趋势'
        >>> validate_name("")
        None
        >>> validate_name(float('nan'))
        None
        """
        if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
            return None
        return str(v)

    @field_validator("listed_date", mode="before", check_fields=False)
    @classmethod
    def validate_listed_date(cls, v):
        """Validate and transform listing date.

        Parameters
        ----------
        v : str or None
            Date string in YYYYMMDD format

        Returns
        -------
        date or None
            Parsed date object or None if invalid

        Examples
        --------
        >>> validate_listed_date("20200427")
        datetime.date(2020, 4, 27)
        >>> validate_listed_date("")
        None
        >>> validate_listed_date("invalid")
        None
        """
        if not v or pd.isna(v):
            return None
        if isinstance(v, dateType):
            return v
        try:
            return datetime.strptime(str(v), "%Y%m%d").date()
        except (ValueError, TypeError):
            return None

    @field_validator("sector", "hq_state", mode="before", check_fields=False)
    @classmethod
    def validate_string_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate string fields.

        Parameters
        ----------
        v : Optional[str]
            Input value to validate

        Returns
        -------
        Optional[str]
            Validated string or None if invalid
        """
        if v is None or v == "" or (isinstance(v, float) and pd.isna(v)):
            return None
        return str(v)

    @field_validator("employees", mode="before", check_fields=False)
    @classmethod
    def validate_employees(cls, v):
        """Validate and convert employees field to integer.

        TdxQuant returns employees as a float (e.g., 1940591.88),
        but the base class expects an integer.

        Parameters
        ----------
        v : str, float, int, or None
            Input value to validate

        Returns
        -------
        int or None
            Validated integer value or None if invalid
        """
        if v is None or v == "" or pd.isna(v):
            return None
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return None

    @field_validator(
        "total_assets", "total_liabilities", "revenue", "net_income",
        "shares_outstanding", "eps", "book_value_per_share", "roe",
        mode="before", check_fields=False
    )
    @classmethod
    def validate_numeric_fields(cls, v):
        """Validate numeric financial fields.

        Parameters
        ----------
        v : str, float, or None
            Input value to validate

        Returns
        -------
        float or None
            Validated numeric value or None if invalid

        Examples
        --------
        >>> validate_numeric_fields("25611.94")
        25611.94
        >>> validate_numeric_fields("")
        None
        """
        if v is None or v == "" or pd.isna(v):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None


class TdxQuantEquityProfileFetcher(
    Fetcher[TdxQuantEquityProfileQueryParams, List[TdxQuantEquityProfileData]]
):
    """TdxQuant Equity Profile Fetcher.

    This fetcher retrieves equity profile data from TdxQuant's get_stock_info API
    and transforms it into OpenBB's standardized format.

    The fetcher handles:
    - Multiple symbol queries with concurrent processing
    - Connection management with TongDaXin client
    - Error handling for various failure scenarios
    - Data validation and transformation

    Examples
    --------
    >>> fetcher = TdxQuantEquityProfileFetcher()
    >>> params = {"symbol": "688318.SH"}
    >>> data = await fetcher.fetch_data(params, {})
    >>> print(data[0].name)
    '财富趋势'

    See Also
    --------
    EquityInfoQueryParams : Base query parameters model
    EquityInfoData : Base data model
    """

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantEquityProfileQueryParams:
        """Transform and validate query parameters.

        Parameters
        ----------
        params : Dict[str, Any]
            Raw input parameters

        Returns
        -------
        TdxQuantEquityProfileQueryParams
            Validated query parameters object

        Raises
        ------
        ValidationError
            If parameters fail validation

        Examples
        --------
        >>> params = {"symbol": "688318.SH", "use_cache": True}
        >>> query = TdxQuantEquityProfileFetcher.transform_query(params)
        >>> query.symbol
        '688318.SH'
        """
        return TdxQuantEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TdxQuantEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract raw data from TdxQuant API.

        This method:
        1. Initializes connection to TongDaXin client
        2. Processes symbols concurrently for better performance
        3. Calls tq.get_stock_info() for each symbol
        4. Handles errors and aggregates results

        Parameters
        ----------
        query : TdxQuantEquityProfileQueryParams
            Validated query parameters
        credentials : Optional[Dict[str, str]]
            API credentials (not used for TdxQuant)
        **kwargs : Any
            Additional keyword arguments

        Returns
        -------
        List[Dict]
            List of raw data dictionaries from TdxQuant

        Raises
        ------
        OpenBBError
            If all symbols fail to retrieve data
        EmptyDataError
            If no data is returned for any symbol

        Notes
        -----
        Requires TongDaXin client to be running and logged in.
        The method uses asyncio.gather() for concurrent processing.

        Examples
        --------
        >>> query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        >>> data = await TdxQuantEquityProfileFetcher.aextract_data(query, {})
        >>> len(data)
        1
        >>> data[0]['Name']
        '财富趋势'
        """
        import asyncio
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from warnings import warn
        from tqcenter import tq

        try:
            tq.initialize(__file__)
        except Exception as e:
            raise OpenBBError(
                f"Failed to initialize TdxQuant connection. "
                f"Ensure TongDaXin client is running and logged in. Error: {str(e)}"
            )

        symbols = query.symbol.split(",")
        results = []
        messages: list = []

        async def get_one(symbol: str) -> None:
            """Fetch profile data for a single symbol.

            Parameters
            ----------
            symbol : str
                Stock symbol in XXXXXX.SH or XXXXXX.SZ format

            Notes
            -----
            This function updates the results and messages lists in-place.
            Errors are caught and added to messages rather than raised,
            allowing other symbols to continue processing.
            """
            try:
                symbol_b, symbol_f, market = normalize_symbol(symbol.strip())
                data = tq.get_stock_info(stock_code=symbol_f, field_list=[])

                if not data:
                    messages.append(f"No data returned for symbol {symbol}")
                    return

                if data.get("ErrorId", "0") != "0":
                    messages.append(
                        f"API error for symbol {symbol}: {data.get('ErrorMsg', 'Unknown error')}"
                    )
                    return

                # Remove error fields
                data.pop("ErrorId", None)
                data.pop("ErrorMsg", None)
                
                # Map TdxQuant field names to OpenBB field names
                field_mapping = {
                    "Name": "name",
                    "J_start": "listed_date",
                    "rs_hyname": "sector",
                    "tdx_dyname": "hq_state",
                    "J_zgb": "employees",
                    "J_ldzc": "total_assets",
                    "J_jzc": "total_liabilities",
                    "J_yysy": "revenue",
                    "J_jly": "net_income",
                    "ActiveCapital": "shares_outstanding",
                    "J_mgsy": "eps",
                    "J_mgjzc": "book_value_per_share",
                    "J_jyl": "roe",
                }
                
                # Create a new dict with mapped fields
                mapped_data = {"symbol": symbol}  # Add symbol field
                for key, value in data.items():
                    # If the key is in our mapping, use the mapped name
                    if key in field_mapping:
                        mapped_key = field_mapping[key]
                        mapped_data[mapped_key] = value
                    else:
                        # Keep other fields as-is (they'll be stored as extra fields)
                        mapped_data[key] = value

                results.append(mapped_data)

            except Exception as e:
                messages.append(
                    f"Error fetching data for {symbol}: {e.__class__.__name__}: {str(e)}"
                )

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for any symbol")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: TdxQuantEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TdxQuantEquityProfileData]:
        """Transform raw data to OpenBB standard format.

        This method validates and transforms each dictionary in the data list
        into a TdxQuantEquityProfileData object.

        Parameters
        ----------
        query : TdxQuantEquityProfileQueryParams
            Original query parameters
        data : List[Dict]
            Raw data from TdxQuant API (already mapped to OpenBB field names)
        **kwargs : Any
            Additional keyword arguments

        Returns
        -------
        List[TdxQuantEquityProfileData]
            List of validated data objects

        Raises
        ------
        ValidationError
            If data fails validation

        Examples
        --------
        >>> query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        >>> raw_data = [{"symbol": "688318.SH", "name": "财富趋势", "listed_date": "20200427"}]
        >>> transformed = TdxQuantEquityProfileFetcher.transform_data(query, raw_data)
        >>> transformed[0].name
        '财富趋势'
        """
        return [TdxQuantEquityProfileData.model_validate(d) for d in data]
