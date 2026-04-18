from openbb import obb

if 'info' in obb.reference:
    obj = obb.reference["info"]["extensions"]["openbb_provider_extension"]
    print([item for item in obj if "tdx" in item])

symbols = "601919,600519,000001,00300"
symbols_a = "601919,600519,000001,600325,600028,600036,430047"
symbol_a = "000001"
symbol_hk = "01658"
provider = "tdxquant"
start_date="2025-09-08"
end_date="2025-12-31"

print(obb.equity.search(query="", market="102", provider=provider).to_dataframe())