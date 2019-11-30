import requests
import json
    
conversion_table = json.loads(
    requests.get('https://api.ratesapi.io/api/latest?base=EUR').text
)

def convert_currency_base_eur(value, currency, destination):
    if destination:
        result = conversion_table['rates'][currency] * value
    else:
        result = value / conversion_table['rates'][currency]

    return float("{0:.2f}".format(result))
    
