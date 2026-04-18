"""TdxQuant Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field

import logging
from openbb_tdx import project_name

# Import tq module for mocking purposes
try:
    from tqcenter import tq
except ImportError:
    tq = None

logger = logging.getLogger(__name__)


class TdxQuantEquitySearchQueryParams(EquitySearchQueryParams):
    """TdxQuant Equity Search Query.
    """

    query: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("query", ""),
    )
    market: str = Field(
        default="5",
        description="Market type. Default: '5' (all A-shares)",
    )
    list_type: int = Field(
        default=1,
        description="Return format. 0: only codes, 1: codes and names",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class TdxQuantEquitySearchData(EquitySearchData):
    """TdxQuant Equity Search Data."""


class TdxQuantEquitySearchFetcher(
    Fetcher[
        TdxQuantEquitySearchQueryParams,
        List[TdxQuantEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the TdxQuant endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TdxQuantEquitySearchQueryParams:
        """Transform the query."""
        return TdxQuantEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TdxQuantEquitySearchQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TdxQuant endpoint."""

        try:
            if tq is None:
                raise ImportError("tqcenter module not found")
            
            tq.initialize(__file__)
            
            list_type = 0
            if query.market != "102":
                list_type = query.list_type
            data = tq.get_stock_list(market=query.market, list_type=list_type)
            logger.info(f"Equity Search Raw data length from TdxQuant: {len(data)}")
            
            # Handle different return formats
            result = []
            if list_type == 0:
                # Return only codes
                for code in data:
                    result.append({"Code": code, "Name": ""})
            else:
                # Return codes and names
                return data
            
            # Apply limit if specified
            if query.limit is not None and query.limit > 0:
                result = result[:query.limit]
            
            return result
        except Exception as e:
            logger.error(f"Error extracting data from TdxQuant: {str(e)}")
            raise

    @staticmethod
    def transform_data(
        query: TdxQuantEquitySearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TdxQuantEquitySearchData]:
        """Transform the data to the standard format."""

        transformed_data = []
        
        for item in data:
            # Extract symbol and name
            symbol = item.get('Code', '')
            name = item.get('Name', '')
            
            # Extract exchange from symbol
            exchange = None
            if symbol.endswith('.SZ'):
                exchange = 'SZ'
            elif symbol.endswith('.SH'):
                exchange = 'SH'
            elif symbol.endswith('.HK'):
                exchange = 'HK'
            
            # Create data object
            equity_data = TdxQuantEquitySearchData(
                symbol=symbol,
                name=name,
                exchange=exchange
            )
            transformed_data.append(equity_data)
        
        # Filter results if query is provided
        if query.query:
            # Remove exchange suffixes if the query is a symbol
            search_query = query.query
            suffixes = [".SS", ".SH", ".HK", ".BJ", ".SZ"]
            for suffix in suffixes:
                if search_query.endswith(suffix):
                    search_query = search_query[:-len(suffix)]
                    break
            
            filtered = [
                d for d in transformed_data
                if search_query.lower() in d.symbol.lower() or search_query.lower() in d.name.lower()
            ]
            logger.info(f"Searching for {search_query} and found {len(filtered)} results.")
            return filtered

        return transformed_data