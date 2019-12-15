import requests
import json

CURRENCIES = ('EUR', 'DKK')
conversion_table = {}
    
for currency in CURRENCIES:
    conversion_table[currency] = json.loads(
        requests.get('https://api.ratesapi.io/api/latest?base='+currency).text
    )['rates']

def convert(value, base, to):
    result = conversion_table[base][to] * value
    return float("{0:.2f}".format(result))
