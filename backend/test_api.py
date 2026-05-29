import requests

base = 'http://127.0.0.1:8000'

# Login (admin auto-created if not exists)
r = requests.post(base + '/api/auth/login', json={'username':'admin','password':'admin123'})
print('LOGIN', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('Login failed')

token = r.json().get('token')
headers = {'Authorization': 'Bearer ' + token}

# Create product
prod = {'name':'TEST PROD API','category':'Testing','stock':5,'price':9.99,'min_stock':2,'supplier':'UnitTest'}
r2 = requests.post(base + '/api/products/', json=prod, headers=headers)
print('CREATE PRODUCT', r2.status_code, r2.text)

# List products
r3 = requests.get(base + '/api/products/', headers=headers)
print('LIST PRODUCTS', r3.status_code, len(r3.json()))
