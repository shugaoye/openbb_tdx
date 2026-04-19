# TdxQuant Financial Statements Integration - Product Requirement Document

## Overview
- **Summary**: A Python module for retrieving financial statement data (Balance Sheet, Income Statement, Cash Flow Statement) using TdxQuant API, following OpenBB's data provider structure and implementation patterns demonstrated in the reference AKShare module.
- **Purpose**: To integrate TdxQuant's financial statement data retrieval capabilities into the OpenBB ecosystem, providing users with access to comprehensive financial data for China A-share and Hong Kong markets.
- **Target Users**: OpenBB users who need financial statement data for equities, particularly focusing on China A-share and Hong Kong markets supported by TdxQuant.

## Goals
- Implement TdxQuant financial statement fetchers (Balance Sheet, Income Statement, Cash Flow) following OpenBB's provider structure
- Replicate the functionality described in OpenBB's financial statement documentation
- Ensure proper data validation, error handling, and adherence to TdxQuant's API specifications
- Create production-ready modules with comprehensive documentation and unit tests
- Verify data accuracy and functionality through pytest test cases

## Non-Goals (Out of Scope)
- Support for real-time financial data retrieval (statements are periodic)
- Integration with other data types beyond financial statements
- Implementation of non-standard parameters not specified in OpenBB's documentation
- Modifications to the core OpenBB provider structure

## Background & Context
- The implementation should follow the structure and patterns demonstrated in the reference AKShare module at:
  - `openbb_akshare/models/balance_sheet.py`
  - `openbb_akshare/models/income_statement.py`
  - `openbb_akshare/models/cash_flow.py`
- TdxQuant (TongDaXin) provides financial data through `get_financial_data_by_date` API
- Mappers are already available in `openbb_tdx/utils/financial_statement_mapping.py`:
  - `BalanceSheetMapper`
  - `IncomeStatementMapper`
  - `CashFlowStatementMapper`
- OpenBB's standard models for financial statements are used as base classes

## OpenBB Documentation References
- Balance Sheet: `https://docs.openbb.co/odp/python/reference/equity/fundamental/balance`
- Income Statement: `https://docs.openbb.co/odp/python/reference/equity/fundamental/income`
- Cash Flow: `https://docs.openbb.co/odp/python/reference/equity/fundamental/cash`

## Functional Requirements

### FR-1: Balance Sheet Fetcher
- **FR-1.1**: Implement `TdxQuantBalanceSheetQueryParams` with symbol, period (annual/quarter), and limit parameters
- **FR-1.2**: Implement `TdxQuantBalanceSheetData` model mapping to OpenBB's `BalanceSheetData`
- **FR-1.3**: Implement `TdxQuantBalanceSheetFetcher` with transform_query, extract_data, and transform_data methods
- **FR-1.4**: Use `BalanceSheetMapper` from `financial_statement_mapping.py` for data transformation
- **FR-1.5**: Support annual and quarterly reporting periods

### FR-2: Income Statement Fetcher
- **FR-2.1**: Implement `TdxQuantIncomeStatementQueryParams` with symbol, period (annual/quarter), and limit parameters
- **FR-2.2**: Implement `TdxQuantIncomeStatementData` model mapping to OpenBB's `IncomeStatementData`
- **FR-2.3**: Implement `TdxQuantIncomeStatementFetcher` with transform_query, extract_data, and transform_data methods
- **FR-2.4**: Use `IncomeStatementMapper` from `financial_statement_mapping.py` for data transformation
- **FR-2.5**: Support annual and quarterly reporting periods

### FR-3: Cash Flow Statement Fetcher
- **FR-3.1**: Implement `TdxQuantCashFlowStatementQueryParams` with symbol, period (annual/quarter), and limit parameters
- **FR-3.2**: Implement `TdxQuantCashFlowStatementData` model mapping to OpenBB's `CashFlowStatementData`
- **FR-3.3**: Implement `TdxQuantCashFlowStatementFetcher` with transform_query, extract_data, and transform_data methods
- **FR-3.4**: Use `CashFlowStatementMapper` from `financial_statement_mapping.py` for data transformation
- **FR-3.5**: Support annual and quarterly reporting periods

### FR-4: Integration Requirements
- **FR-4.1**: Register all three fetchers in `provider.py` fetcher_dict
- **FR-4.2**: Add router commands in `router.py` for all three endpoints
- **FR-4.3**: Use `TableCache` for caching financial statement data
- **FR-4.4**: Follow existing TdxQuant patterns for initialization and cleanup

## Non-Functional Requirements
- **NFR-1**: The module should follow OpenBB's coding standards and best practices
- **NFR-2**: The module should be well-documented with clear docstrings
- **NFR-3**: The module should have comprehensive unit tests to verify functionality
- **NFR-4**: The module should handle edge cases gracefully, such as invalid symbols or empty data

## Constraints
- **Technical**: Python 3.8+, OpenBB Core Provider framework, TdxQuant API
- **Dependencies**: OpenBB Core Provider, TdxQuant Python SDK (`tqcenter`)
- **Windows Only**: TdxQuant SDK only available on Windows

## Data Flow Architecture
```
Router → Fetcher.transform_query → Fetcher.extract_data → Fetcher.transform_data → Response
              ↓                        ↓                          ↓
       QueryParams Validation    TDX API Call            Mapper.transform_to_openbb
                                      ↓
                              BalanceSheetMapper
                              IncomeStatementMapper
                              CashFlowStatementMapper
```

## TdxQuant API Usage
- Financial statements are retrieved using `tq.get_financial_data_by_date()`
- Parameters: `stock_list`, `field_list`, `year`, `mmdd`
- Year parameter: 0 = latest, positive = years back
- MMDD parameter: 331 (Q1), 630 (Q2), 930 (Q3), 1231 (Q4)

## Acceptance Criteria

### AC-1: Balance Sheet
- **Given**: A user queries balance sheet data for a symbol
- **When**: Valid parameters are provided
- **Then**: Return balance sheet data including total_assets, total_liabilities, total_equity
- **Verification**: `programmatic`

### AC-2: Income Statement
- **Given**: A user queries income statement data for a symbol
- **When**: Valid parameters are provided
- **Then**: Return income statement data including revenue, net_income, eps
- **Verification**: `programmatic`

### AC-3: Cash Flow Statement
- **Given**: A user queries cash flow statement data for a symbol
- **When**: Valid parameters are provided
- **Then**: Return cash flow data including operating_cash_flow, investing_cash_flow, financing_cash_flow
- **Verification**: `programmatic`

### AC-4: Error Handling
- **Given**: Invalid symbol or empty data
- **When**: The API returns empty data
- **Then**: Raise appropriate EmptyDataError
- **Verification**: `programmatic`

### AC-5: Caching
- **Given**: Repeated queries for the same data
- **When**: Cache is enabled and valid
- **Then**: Return cached data
- **Verification**: `programmatic`

### AC-6: Period Support
- **Given**: User specifies annual or quarterly period
- **When**: Data is retrieved
- **Then**: Return data for the specified reporting period
- **Verification**: `programmatic`

## Open Questions
- [x] How to use TdxQuant's financial data API? - Use `get_financial_data_by_date` with field lists from mappers
- [x] How to map TDX fields to OpenBB format? - Use existing `BalanceSheetMapper`, `IncomeStatementMapper`, `CashFlowStatementMapper`
- [x] How to handle caching? - Use `TableCache` similar to equity_historical
- [x] How to integrate with existing ecosystem? - Add to provider.py and router.py
