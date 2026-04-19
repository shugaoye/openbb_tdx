# TdxQuant Financial Statements Integration - Implementation Plan

## [ ] Task 1: Create Balance Sheet Model
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - Create `openbb_tdx/models/balance_sheet.py`
  - Implement `TdxQuantBalanceSheetQueryParams` extending `BalanceSheetQueryParams`
  - Implement `TdxQuantBalanceSheetData` extending `BalanceSheetData`
  - Implement `TdxQuantBalanceSheetFetcher` with three static methods
  - Use `BalanceSheetMapper` for data transformation
- **Acceptance Criteria**: AC-1, AC-4, AC-5, AC-6
- **Test Requirements**: TR-1.1 to TR-1.4

## [ ] Task 2: Create Income Statement Model
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - Create `openbb_tdx/models/income_statement.py`
  - Implement `TdxQuantIncomeStatementQueryParams` extending `IncomeStatementQueryParams`
  - Implement `TdxQuantIncomeStatementData` extending `IncomeStatementData`
  - Implement `TdxQuantIncomeStatementFetcher` with three static methods
  - Use `IncomeStatementMapper` for data transformation
- **Acceptance Criteria**: AC-2, AC-4, AC-5, AC-6
- **Test Requirements**: TR-2.1 to TR-2.4

## [ ] Task 3: Create Cash Flow Statement Model
- **Priority**: P0
- **Depends On**: None
- **Description**:
  - Create `openbb_tdx/models/cash_flow.py`
  - Implement `TdxQuantCashFlowStatementQueryParams` extending `CashFlowStatementQueryParams`
  - Implement `TdxQuantCashFlowStatementData` extending `CashFlowStatementData`
  - Implement `TdxQuantCashFlowStatementFetcher` with three static methods
  - Use `CashFlowStatementMapper` for data transformation
- **Acceptance Criteria**: AC-3, AC-4, AC-5, AC-6
- **Test Requirements**: TR-3.1 to TR-3.4

## [ ] Task 4: Update Provider Registration
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - Add imports for all three new fetchers in `provider.py`
  - Add all three fetchers to the `fetcher_dict`
- **Acceptance Criteria**: AC-1, AC-2, AC-3
- **Test Requirements**: TR-4.1

## [ ] Task 5: Update Router
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - Add router commands for balance_sheet, income_statement, cash_flow
  - Follow the pattern of existing equity_historical endpoint
- **Acceptance Criteria**: AC-1, AC-2, AC-3
- **Test Requirements**: TR-5.1

## [ ] Task 6: Create Helper Functions for Financial Statements
- **Priority**: P1
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - Create `get_financial_statement_data()` function in `utils/helpers.py`
  - Implement caching logic similar to equity_historical
  - Handle period mapping (annual/quarterly to mmdd values)
- **Acceptance Criteria**: AC-5
- **Test Requirements**: TR-6.1 to TR-6.3

## [ ] Task 7: Write Unit Tests
- **Priority**: P0
- **Depends On**: Task 1, Task 2, Task 3, Task 6
- **Description**:
  - Create `tests/test_balance_sheet.py`
  - Create `tests/test_income_statement.py`
  - Create `tests/test_cash_flow.py`
  - Test transform_query, extract_data, transform_data methods
  - Use mock for tqcenter.tq
- **Acceptance Criteria**: AC-8
- **Test Requirements**: All TR-* tests

## [ ] Task 8: Integration Testing
- **Priority**: P1
- **Depends On**: Task 4, Task 5, Task 7
- **Description**:
  - Run pytest on all financial statement tests
  - Verify module integrates with OpenBB ecosystem
- **Acceptance Criteria**: AC-8
- **Test Requirements**: TR-8.1

## Test Requirements Detail

### TR-1.1: Balance Sheet Query Transform
- Verify symbol is normalized correctly
- Verify period choices are ["annual", "quarter"]
- Verify default limit is 5

### TR-1.2: Balance Sheet Data Extraction
- Verify TDX API is called with correct field list
- Verify data is returned in expected format
- Verify EmptyDataError is raised when no data

### TR-1.3: Balance Sheet Data Transformation
- Verify mapper transforms data correctly
- Verify required fields are present
- Verify fiscal_period and fiscal_year are derived correctly

### TR-1.4: Balance Sheet Caching
- Verify cache is used when enabled
- Verify cache key includes symbol and period

### TR-2.1 to TR-2.4: Income Statement (same pattern as TR-1.1 to TR-1.4)

### TR-3.1 to TR-3.4: Cash Flow Statement (same pattern as TR-1.1 to TR-1.4)

### TR-4.1: Provider Registration
- Verify all three fetchers are in fetcher_dict

### TR-5.1: Router Commands
- Verify all three endpoints are registered

### TR-6.1 to TR-6.3: Helper Functions
- Verify period mapping (annual -> 1231, quarter -> mmdd)
- Verify caching behavior
- Verify error handling

### TR-8.1: Integration Tests
- Verify pytest passes for all test files
