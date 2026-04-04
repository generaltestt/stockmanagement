import requests
#from models import db, Store, Colleague, Product, StoreStock


class ApiClient:
    def __init__(self, base_url='http://127.0.0.1:5000'):
        self.base_url = base_url
        self.token = None
        self.colleague_name = None
        self.store_id = None
        self.user = None

    def get_stores(self):
        try:
            r = requests.get(f'{self.base_url}/api/stores', timeout=5)
            if 'application/json' not in r.headers.get('Content-Type', ''):
                return []
            return r.json()
        except requests.exceptions.ConnectionError:
            return []

    def validate_store(self, store_text):
        try:
            r = requests.get(f'{self.base_url}/api/store/{store_text}', timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.store_id = data['id']
                return data
            return None
        except requests.exceptions.ConnectionError:
            return None

    def login(self, colleague_id, password, store_id):
        """Returns True on success, False for wrong credentials, None if server down."""
        try:
            r = requests.post(f'{self.base_url}/api/login', json={
                'colleague_id': colleague_id,
                'password': password,
                'store_id': store_id
            }, timeout=5)
            # only access token if status is 200 OK
            if r.status_code == 200:
                data = r.json()
                self.token = data['token']
                self.colleague_name = data['name']
                return True
                self.user = data
            # any non-200 response (e.g. 401) = wrong credentials
            return False
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            # distinguish server-down (None) from wrong password (False)
            return None

    def get_product(self, product_id: str):
        # Looks up a product by barcode. Returns dictionary or error
        params = {}

        # Includes store_id if store_id is provided (may not be if Head Office)
        if self.store_id:
            params['store_id'] = self.store_id  # e.g. '0725'

        try:
            # Sends GET request to the API
            r = requests.get(
                f'{self.base_url}/api/products/{product_id}',
                params=params,
                timeout=10       # 10s for slow stockroom WIFI
            )
            # Returns JSON response
            return r.json()
        except Exception:
            return {'error': 'Could not connect to server'} # if network error

    def waste(self, product_id: str, qty: int):
        # Sends API waste request which returns {'ok': True} or {'error': ...}
        payload = {
            'store_id':   self.store_id,
            'product_id': product_id,
            'qty':        int(qty),
        }
        try:
            # Sends POST request to API
            r  = requests.post(f'{self.base_url}/api/waste', json=payload, timeout=10)
            ct = (r.headers.get('Content-Type') or '').lower()

            # If non-JSON header then it means there is a server error
            if 'application/json' not in ct:
                return {'error': 'Server error'}
            return r.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return {'error': 'Could not connect to server'}

    def submit_stock_counts(self, items):
        payload = {'store_id': self.store_id, 'items': items}
        try:
            r  = requests.post(f'{self.base_url}/api/stockcount',  # fixed
                               json=payload, timeout=10)
            ct = (r.headers.get('Content-Type') or '').lower()
            if 'application/json' not in ct: return {'error': 'Server error'}
            return r.json()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            return {'error': 'Could not connect to server'}

