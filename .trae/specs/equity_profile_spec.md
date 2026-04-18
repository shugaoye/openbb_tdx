# TdxQuant Equity Profile Data Integration Module Specification

## 1. Executive Summary

This specification defines the implementation of an equity profile data integration module for TdxQuant (通达信量化平台), following OpenBB's data provider architecture and coding standards. The module will retrieve comprehensive equity profile information from TdxQuant's `get_stock_info` API and transform it into OpenBB's standardized format.

## 2. Objectives

### 2.1 Primary Objectives
- Implement a production-ready equity profile fetcher for TdxQuant
- Ensure seamless integration with OpenBB's existing architecture
- Provide comprehensive data validation and error handling
- Support multiple symbol queries with efficient batch processing
- Maintain consistency with OpenBB's standard models

### 2.2 Success Criteria
- ✅ Module successfully retrieves equity profile data from TdxQuant
- ✅ Data is properly validated and transformed to OpenBB standard format
- ✅ Error handling covers all edge cases (connection failures, invalid symbols, etc.)
- ✅ Unit tests achieve >90% code coverage
- ✅ Integration tests pass with live TdxQuant client
- ✅ Documentation is comprehensive and follows OpenBB standards

## 3. Architecture Design

### 3.1 Module Structure

```
openbb_tdx/
├── models/
│   ├── __init__.py
│   ├── equity_historical.py
│   ├── equity_quote.py
│   ├── equity_dividends.py
│   └── equity_profile.py          # NEW FILE
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_equity_historical.py
│   ├── test_equity_quote.py
│   ├── test_equity_dividends.py
│   └── test_equity_profile.py     # NEW FILE
├── __init__.py
├── openbb.py
├── provider.py                    # MODIFY
└── router.py                      # MODIFY
```

### 3.2 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenBB Platform                           │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Router Layer (FastAPI)                   │   │
│  │  - Endpoint routing                                   │   │
│  │  - Request validation                                 │   │
│  │  - Response formatting                                │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                       │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │           TdxQuantEquityProfileFetcher                │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  transform_query()                            │    │   │
│  │  │  - Validate input parameters                  │    │   │
│  │  │  - Create QueryParams object                  │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  aextract_data()                              │    │   │
│  │  │  - Initialize TdxQuant connection             │    │   │
│  │  │  - Call tq.get_stock_info()                   │    │   │
│  │  │  - Handle errors and edge cases               │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  transform_data()                             │    │   │
│  │  │  - Map TdxQuant fields to OpenBB fields       │    │   │
│  │  │  - Validate data types                        │    │   │
│  │  │  - Create Data objects                        │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                       │                                       │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │              TdxQuant API Layer                       │   │
│  │  - tqcenter.tq module                                 │   │
│  │  - TongDaXin client connection                        │   │
│  │  - get_stock_info() function                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 4. Implementation Details

### 4.1 Query Parameters Model

```python
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
```

### 4.2 Data Model

#### 4.2.1 Field Mapping Strategy

Map TdxQuant API fields to OpenBB standard fields:

| TdxQuant Field | OpenBB Field | Type | Description |
|----------------|--------------|------|-------------|
| `Name` | `name` | str | Company name |
| `J_start` | `listed_date` | date | Listing date |
| `rs_hyname` | `sector` | str | Industry sector |
| `tdx_dyname` | `hq_state` | str | Headquarters region |
| `J_zgb` | `employees` | float | Total shares (proxy for company size) |
| `J_ldzc` | `total_assets` | float | Total assets (万元) |
| `J_jzc` | `total_liabilities` | float | Net assets/shareholder equity (万元) |
| `J_yysy` | `revenue` | float | Operating revenue (万元) |
| `J_jly` | `net_income` | float | Net profit (万元) |
| `ActiveCapital` | `shares_outstanding` | float | Circulating shares (万股) |
| `J_mgsy` | `eps` | float | Earnings per share |
| `J_mgjzc` | `book_value_per_share` | float | Net assets per share |
| `J_jyl` | `roe` | float | Return on equity (%) |

#### 4.2.2 Data Model Implementation

```python
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
    
    __alias_dict__ = {
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
    
    # TdxQuant-specific fields (not in standard model)
    Name: Optional[str] = Field(
        default=None,
        description="Company name (Chinese)"
    )
    J_start: Optional[str] = Field(
        default=None,
        description="Listing date in YYYYMMDD format"
    )
    rs_hyname: Optional[str] = Field(
        default=None,
        description="Industry sector name"
    )
    tdx_dyname: Optional[str] = Field(
        default=None,
        description="Geographic region name"
    )
    J_zgb: Optional[float] = Field(
        default=None,
        description="Total shares (万股)"
    )
    J_ldzc: Optional[float] = Field(
        default=None,
        description="Current assets (万元)"
    )
    J_jzc: Optional[float] = Field(
        default=None,
        description="Net assets/Shareholder equity (万元)"
    )
    J_yysy: Optional[float] = Field(
        default=None,
        description="Operating revenue (万元)"
    )
    J_jly: Optional[float] = Field(
        default=None,
        description="Net profit (万元)"
    )
    ActiveCapital: Optional[float] = Field(
        default=None,
        description="Circulating shares (万股)"
    )
    J_mgsy: Optional[float] = Field(
        default=None,
        description="Earnings per share"
    )
    J_mgjzc: Optional[float] = Field(
        default=None,
        description="Net assets per share"
    )
    J_jyl: Optional[float] = Field(
        default=None,
        description="Return on equity (%)"
    )
```

### 4.3 Data Validators

```python
@field_validator("Name", mode="before", check_fields=False)
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

@field_validator("J_start", mode="before", check_fields=False)
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
    try:
        return datetime.strptime(str(v), "%Y%m%d").date()
    except (ValueError, TypeError):
        return None

@field_validator("J_zgb", "J_ldzc", "J_jzc", "J_yysy", "J_jly", mode="before", check_fields=False)
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
```

### 4.4 Fetcher Implementation

```python
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
        
        # Initialize TdxQuant connection
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
                # Call TdxQuant API
                data = tq.get_stock_info(stock_code=symbol, field_list=[])
                
                # Check for errors
                if not data:
                    messages.append(f"No data returned for symbol {symbol}")
                    return
                
                if data.get("ErrorId", "0") != "0":
                    messages.append(
                        f"API error for symbol {symbol}: {data.get('ErrorMsg', 'Unknown error')}"
                    )
                    return
                
                # Remove error fields from result
                data.pop("ErrorId", None)
                data.pop("ErrorMsg", None)
                
                results.append(data)
                
            except Exception as e:
                messages.append(
                    f"Error fetching data for {symbol}: {e.__class__.__name__}: {str(e)}"
                )
        
        # Process all symbols concurrently
        tasks = [get_one(symbol) for symbol in symbols]
        await asyncio.gather(*tasks)
        
        # Handle results
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
            Raw data from TdxQuant API
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
        >>> raw_data = [{"Name": "财富趋势", "J_start": "20200427"}]
        >>> transformed = TdxQuantEquityProfileFetcher.transform_data(query, raw_data)
        >>> transformed[0].name
        '财富趋势'
        """
        return [TdxQuantEquityProfileData.model_validate(d) for d in data]
```

## 5. Integration Steps

### 5.1 Update provider.py

```python
# Add import at the top of the file
from openbb_tdx.models.equity_profile import TdxQuantEquityProfileFetcher

# Update the fetcher_dict in the Provider initialization
provider = Provider(
    name="tdxquant",
    description="Data provider for TdxQuant.",
    website="https://tdxquant.com",
    fetcher_dict={
        "EquityHistorical": TdxQuantEquityHistoricalFetcher,
        "EquityQuote": TdxQuantEquityQuoteFetcher,
        "HistoricalDividends": TdxQuantEquityDividendsFetcher,
        "EquityProfile": TdxQuantEquityProfileFetcher,  # NEW LINE
    }
)
```

### 5.2 Update router.py (if needed)

```python
# Add endpoint route if not auto-generated
@router.command()
async def profile(
    symbol: str,
    use_cache: bool = True,
    credentials: Optional[Dict[str, str]] = None,
) -> List[TdxQuantEquityProfileData]:
    """Get equity profile data for one or more symbols.
    
    Parameters
    ----------
    symbol : str
        Stock symbol(s) to query
    use_cache : bool
        Whether to use cached data
    credentials : Optional[Dict[str, str]]
        API credentials
        
    Returns
    -------
    List[TdxQuantEquityProfileData]
        List of equity profile data objects
    """
    from openbb_tdx.models.equity_profile import TdxQuantEquityProfileFetcher
    
    params = {"symbol": symbol, "use_cache": use_cache}
    fetcher = TdxQuantEquityProfileFetcher()
    return await fetcher.fetch_data(params, credentials)
```

## 6. Testing Strategy

### 6.1 Unit Tests

Create comprehensive unit tests in `tests/test_equity_profile.py`:

```python
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
            "Name": "财富趋势",
            "J_start": "20200427",
            "rs_hyname": "软件服务",
            "tdx_dyname": "深圳板块",
            "J_zgb": "25611.94",
            "J_ldzc": "235598.84",
            "J_jzc": "370454.03",
            "J_yysy": "19827.85",
            "J_jly": "18421.34",
        }
        
        data = TdxQuantEquityProfileData.model_validate(test_data)
        
        assert data.name == "财富趋势"
        assert data.listed_date == date(2020, 4, 27)
        assert data.sector == "软件服务"
        assert data.hq_state == "深圳板块"
        assert data.employees == 25611.94
        assert data.total_assets == 235598.84
    
    def test_data_validation_with_empty_strings(self):
        """Test data model validation with empty strings."""
        test_data = {
            "Name": "",
            "J_start": "",
            "rs_hyname": "",
        }
        
        data = TdxQuantEquityProfileData.model_validate(test_data)
        
        assert data.name is None
        assert data.listed_date is None
        assert data.sector is None
    
    def test_data_validation_with_nan_values(self):
        """Test data model validation with NaN values."""
        test_data = {
            "Name": float('nan'),
            "J_zgb": float('nan'),
        }
        
        data = TdxQuantEquityProfileData.model_validate(test_data)
        
        assert data.name is None
        assert data.employees is None
    
    def test_data_validation_with_invalid_date(self):
        """Test data model validation with invalid date format."""
        test_data = {
            "J_start": "invalid_date",
        }
        
        data = TdxQuantEquityProfileData.model_validate(test_data)
        
        assert data.listed_date is None
    
    def test_field_alias_mapping(self):
        """Test that field aliases are correctly mapped."""
        test_data = {
            "Name": "测试公司",
        }
        
        data = TdxQuantEquityProfileData.model_validate(test_data)
        
        # Both Name and name should be accessible
        assert data.Name == "测试公司"
        assert data.name == "测试公司"


class TestTdxQuantEquityProfileFetcher:
    """Test suite for fetcher implementation."""
    
    @pytest.fixture
    def mock_tq(self):
        """Mock TdxQuant API."""
        with patch('openbb_tdx.models.equity_profile.tq') as mock:
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
        # Mock successful API response
        mock_tq.get_stock_info.return_value = {
            "Name": "财富趋势",
            "J_start": "20200427",
            "ErrorId": "0"
        }
        mock_tq.initialize.return_value = None
        
        query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        
        result = await TdxQuantEquityProfileFetcher.aextract_data(query, {})
        
        assert len(result) == 1
        assert result[0]["Name"] == "财富趋势"
        assert "ErrorId" not in result[0]
    
    @pytest.mark.asyncio
    async def test_extract_data_no_data(self, mock_tq):
        """Test data extraction when no data is returned."""
        mock_tq.get_stock_info.return_value = None
        mock_tq.initialize.return_value = None
        
        query = TdxQuantEquityProfileQueryParams(symbol="INVALID.SH")
        
        with pytest.raises(Exception):  # Should raise EmptyDataError or OpenBBError
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
        
        with pytest.raises(Exception):  # Should raise OpenBBError
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
        assert result[0]["Name"] == "财富趋势"
        assert result[1]["Name"] == "贵州茅台"
    
    def test_transform_data(self):
        """Test data transformation."""
        query = TdxQuantEquityProfileQueryParams(symbol="688318.SH")
        raw_data = [
            {
                "Name": "财富趋势",
                "J_start": "20200427",
                "rs_hyname": "软件服务",
            }
        ]
        
        result = TdxQuantEquityProfileFetcher.transform_data(query, raw_data)
        
        assert len(result) == 1
        assert isinstance(result[0], TdxQuantEquityProfileData)
        assert result[0].name == "财富趋势"
        assert result[0].listed_date == date(2020, 4, 27)
        assert result[0].sector == "软件服务"


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


def is_tdxquant_available() -> bool:
    """Check if TdxQuant client is available."""
    try:
        from tqcenter import tq
        tq.initialize(__file__)
        # Try a simple query
        test = tq.get_stock_info(stock_code='000001.SZ', field_list=['Name'])
        return test is not None and test.get('ErrorId', '1') == '0'
    except Exception:
        return False
```

### 6.2 Test Coverage Requirements

- **Query Parameters Model**: 100% coverage
- **Data Model Validators**: 100% coverage
- **Fetcher Methods**: >90% coverage
- **Error Handling Paths**: 100% coverage
- **Edge Cases**: All documented edge cases must have tests

### 6.3 Test Execution

```bash
# Run all tests
pytest tests/test_equity_profile.py -v

# Run with coverage
pytest tests/test_equity_profile.py --cov=openbb_tdx.models.equity_profile --cov-report=html

# Run only unit tests (skip integration tests)
pytest tests/test_equity_profile.py -v -m "not integration"

# Run only integration tests
pytest tests/test_equity_profile.py -v -m integration
```

## 7. Documentation Requirements

### 7.1 Module Documentation

The module must include comprehensive docstrings following Google/NumPy style:

```python
"""TdxQuant Equity Profile Model.

This module provides equity profile data integration for TdxQuant (通达信量化平台),
retrieving comprehensive company information from TdxQuant's get_stock_info API.

The module includes:
- TdxQuantEquityProfileQueryParams: Query parameters for equity profile requests
- TdxQuantEquityProfileData: Data model for equity profile information
- TdxQuantEquityProfileFetcher: Fetcher for retrieving and transforming data

Key Features:
- Support for single and multiple symbol queries
- Comprehensive data validation and error handling
- Concurrent processing for multiple symbols
- Field mapping from TdxQuant to OpenBB standard format

Requirements:
- TongDaXin (通达信) client must be installed and running
- Python packages: openbb-core, pydantic, pandas, tqcenter

Example Usage:
    >>> from openbb_tdx.models.equity_profile import TdxQuantEquityProfileFetcher
    >>> 
    >>> # Single symbol query
    >>> fetcher = TdxQuantEquityProfileFetcher()
    >>> params = {"symbol": "688318.SH"}
    >>> data = await fetcher.fetch_data(params, {})
    >>> print(data[0].name)
    '财富趋势'
    >>> 
    >>> # Multiple symbol query
    >>> params = {"symbol": "688318.SH,600519.SH"}
    >>> data = await fetcher.fetch_data(params, {})
    >>> print(len(data))
    2

See Also:
    - TdxQuant Documentation: https://help.tdx.com.cn/quant/
    - OpenBB Documentation: https://docs.openbb.co/

References:
    - TdxQuant get_stock_info API: references/tdxquant/get_stock_info.md
    - Example implementation: references/openbb_akshare/models/equity_profile.py
"""
```

### 7.2 API Reference Documentation

Create comprehensive API documentation:

```markdown
# TdxQuant Equity Profile API Reference

## Overview

The TdxQuant Equity Profile module provides access to comprehensive company information
for China A-share and Hong Kong stocks through TdxQuant's data platform.

## Endpoints

### GET /equity/profile

Retrieve equity profile data for one or more stock symbols.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | Yes | - | Stock symbol(s) to query. Multiple symbols separated by commas. Format: XXXXXX.SH or XXXXXX.SZ |
| use_cache | boolean | No | true | Whether to use cached data. Cache duration is 1 hour. |

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | Company name |
| listed_date | date | Listing date |
| sector | string | Industry sector |
| hq_state | string | Headquarters region |
| employees | float | Total shares outstanding (万股) |
| total_assets | float | Total assets (万元) |
| total_liabilities | float | Net assets/Shareholder equity (万元) |
| revenue | float | Annual revenue (万元) |
| net_income | float | Net profit (万元) |
| shares_outstanding | float | Circulating shares (万股) |
| eps | float | Earnings per share |
| book_value_per_share | float | Book value per share |
| roe | float | Return on equity (%) |

#### Example Request

```bash
curl -X GET "http://localhost:8000/equity/profile?symbol=688318.SH"
```

#### Example Response

```json
[
  {
    "name": "财富趋势",
    "listed_date": "2020-04-27",
    "sector": "软件服务",
    "hq_state": "深圳板块",
    "employees": 25611.94,
    "total_assets": 235598.84,
    "total_liabilities": 370454.03,
    "revenue": 19827.85,
    "net_income": 18421.34
  }
]
```

#### Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid symbol format |
| 404 | Symbol not found |
| 500 | TdxQuant connection error |
| 503 | TongDaXin client not running |

## Data Source

Data is sourced from TdxQuant's `get_stock_info` API, which provides comprehensive
company information including financial metrics, listing details, and sector classifications.

## Rate Limits

- No explicit rate limits from TdxQuant API
- Recommended to use caching to minimize API calls
- Cache duration: 1 hour for profile data

## Data Quality

- Data is sourced directly from TongDaXin's official data feeds
- Updated daily after market close
- Historical data available from listing date
```

### 7.3 User Guide

Create a user guide with practical examples:

```markdown
# TdxQuant Equity Profile User Guide

## Getting Started

### Prerequisites

1. Install TongDaXin (通达信) client
2. Start the client and log in
3. Install the OpenBB TdxQuant provider:
   ```bash
   pip install openbb-tdx
   ```

### Basic Usage

#### Single Symbol Query

```python
from openbb import obb

# Get equity profile for a single stock
profile = obb.equity.profile(symbol="688318.SH", provider="tdxquant")

# Access the data
print(profile.results[0].name)  # 财富趋势
print(profile.results[0].sector)  # 软件服务
print(profile.results[0].listed_date)  # 2020-04-27
```

#### Multiple Symbol Query

```python
# Get equity profiles for multiple stocks
profiles = obb.equity.profile(
    symbol="688318.SH,600519.SH,000001.SZ",
    provider="tdxquant"
)

# Iterate through results
for profile in profiles.results:
    print(f"{profile.name}: {profile.sector}")
```

#### Disable Caching

```python
# Force fresh data (not from cache)
profile = obb.equity.profile(
    symbol="688318.SH",
    provider="tdxquant",
    use_cache=False
)
```

### Advanced Usage

#### Convert to DataFrame

```python
import pandas as pd

profile = obb.equity.profile(symbol="688318.SH", provider="tdxquant")
df = profile.to_dataframe()

print(df[['name', 'sector', 'listed_date']])
```

#### Filter by Sector

```python
# Get profiles for multiple stocks
profiles = obb.equity.profile(
    symbol="688318.SH,600519.SH,000001.SZ",
    provider="tdxquant"
)

# Filter by sector
tech_stocks = [p for p in profiles.results if '软件' in (p.sector or '')]
```

### Troubleshooting

#### Connection Errors

**Problem**: "Failed to initialize TdxQuant connection"

**Solution**:
1. Ensure TongDaXin client is running
2. Check that you're logged in
3. Verify the client version is compatible

#### Invalid Symbol Format

**Problem**: "Invalid symbol format"

**Solution**:
- Use correct format: 6 digits + .SH or .SZ
- Example: "688318.SH" (not "688318" or "SH688318")

#### No Data Returned

**Problem**: "No data was returned for any symbol"

**Solution**:
1. Verify symbol exists in TdxQuant database
2. Check if market is open (some data only available during trading hours)
3. Try with use_cache=False to force fresh data

### Best Practices

1. **Use Caching**: Enable caching (default) to reduce API calls
2. **Batch Queries**: Query multiple symbols in a single call
3. **Error Handling**: Always wrap calls in try-except blocks
4. **Data Validation**: Check for None values before using data

```python
from openbb import obb
from openbb_core.provider.abstract.errors import OpenBBError

try:
    profile = obb.equity.profile(symbol="688318.SH", provider="tdxquant")
    
    if profile.results and profile.results[0].name:
        print(f"Company: {profile.results[0].name}")
    else:
        print("No profile data available")
        
except OpenBBError as e:
    print(f"Error fetching profile: {e}")
```
```

## 8. Performance Optimization

### 8.1 Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TdxQuantProfileCache:
    """Cache manager for TdxQuant profile data.
    
    Implements a time-based cache with 1-hour TTL for profile data.
    """
    
    _cache = {}
    _cache_ttl = timedelta(hours=1)
    
    @classmethod
    def get(cls, symbol: str):
        """Get cached data if still valid."""
        if symbol in cls._cache:
            data, timestamp = cls._cache[symbol]
            if datetime.now() - timestamp < cls._cache_ttl:
                return data
        return None
    
    @classmethod
    def set(cls, symbol: str, data):
        """Cache data with current timestamp."""
        cls._cache[symbol] = (data, datetime.now())
    
    @classmethod
    def clear(cls):
        """Clear all cached data."""
        cls._cache.clear()
```

### 8.2 Concurrent Processing

The fetcher already uses `asyncio.gather()` for concurrent processing of multiple symbols. This ensures optimal performance when querying multiple stocks.

### 8.3 Connection Pooling

TdxQuant maintains a persistent connection to the TongDaXin client, so no additional connection pooling is needed.

## 9. Error Handling

### 9.1 Error Types

```python
from openbb_core.provider.abstract.error import OpenBBError

class TdxQuantConnectionError(OpenBBError):
    """Raised when connection to TongDaXin client fails."""
    pass

class TdxQuantDataError(OpenBBError):
    """Raised when data retrieval or validation fails."""
    pass

class TdxQuantSymbolError(OpenBBError):
    """Raised when an invalid symbol is provided."""
    pass
```

### 9.2 Error Handling Strategy

1. **Connection Errors**: Provide clear instructions to start TongDaXin client
2. **Symbol Errors**: Validate format and provide examples
3. **Data Errors**: Log detailed error information and provide fallback options
4. **API Errors**: Parse TdxQuant error codes and provide user-friendly messages

## 10. Deployment Checklist

### 10.1 Pre-deployment

- [ ] All unit tests pass
- [ ] Integration tests pass with live TdxQuant client
- [ ] Code coverage >90%
- [ ] Documentation is complete and accurate
- [ ] Error handling covers all edge cases
- [ ] Performance benchmarks meet requirements

### 10.2 Deployment

- [ ] Update provider.py with new fetcher
- [ ] Update router.py if needed
- [ ] Run `openbb-build` to register the provider
- [ ] Verify provider appears in `obb.coverage.providers`
- [ ] Test with OpenBB CLI and Python API

### 10.3 Post-deployment

- [ ] Monitor error logs for unexpected issues
- [ ] Collect user feedback
- [ ] Update documentation based on user questions
- [ ] Plan for future enhancements

## 11. Future Enhancements

### 11.1 Phase 2 Features

- Real-time profile updates via TdxQuant subscription
- Historical profile data (changes over time)
- Additional financial metrics from TdxQuant
- Integration with other TdxQuant data endpoints

### 11.2 Performance Improvements

- Implement Redis caching for distributed deployments
- Add batch processing optimizations for large symbol lists
- Implement connection retry logic with exponential backoff

### 11.3 Data Quality

- Add data validation rules specific to Chinese markets
- Implement cross-validation with other data sources
- Add data freshness indicators

## 12. Appendix

### 12.1 TdxQuant API Reference

See [references/tdxquant/get_stock_info.md](references/tdxquant/get_stock_info.md) for complete API documentation.

### 12.2 Example Code

See [references/tdxdata_test.py](references/tdxdata_test.py) for working examples of TdxQuant API usage.

### 12.3 Related Implementations

See [references/openbb_akshare/models/equity_profile.py](references/openbb_akshare/models/equity_profile.py) for a similar implementation using AKShare.

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-18  
**Author**: OpenBB Development Team  
**Status**: Ready for Implementation
