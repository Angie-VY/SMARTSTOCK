import requests

base = 'http://127.0.0.1:8000'

# Login admin
r = requests.post(base + '/api/auth/login', json={'username':'admin','password':'admin123'})
print('LOGIN', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('Login failed')

token = r.json().get('token')
headers = {'Authorization': 'Bearer ' + token}

# Call seed
r2 = requests.post(base + '/api/seed/', headers=headers)
print('SEED', r2.status_code, r2.text)

# Check counts
r3 = requests.get(base + '/api/products/', headers=headers)
print('PRODUCTS COUNT', r3.status_code, len(r3.json()))
