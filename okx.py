import requests
import time

def get_position(headers, params, max_retries=5):
    """
    Mendapatkan posisi trading dari OKX Copy Trading menggunakan API.
    
    Parameters:
        headers (dict): Header yang diperlukan untuk request HTTP.
        params (dict): Parameter yang dikirim sebagai query string.
        max_retries (int): Jumlah maksimum percobaan ulang jika terjadi kesalahan koneksi.
    
    Returns:
        requests.Response: Respons dari API.
    """
    url = "https://www.okx.com/priapi/v5/ecotrade/public/positions-v2"
    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            else:
                print(f"API request failed with status code: {response.status_code}")
                raise requests.exceptions.RequestException(f"Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error occurred: {e}")
            if retry_count >= max_retries:
                print("Max retry count reached. Waiting for 10 minutes before next try...")
                time.sleep(600)
                retry_count = 0
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)
                retry_count += 1
    return None

def get_nickname(headers, params, max_retries=5):
    """
    Mendapatkan informasi dasar (seperti nickname) dari trader di OKX Copy Trading menggunakan API.
    
    Parameters:
        headers (dict): Header yang diperlukan untuk request HTTP.
        params (dict): Parameter yang dikirim sebagai query string.
        max_retries (int): Jumlah maksimum percobaan ulang jika terjadi kesalahan koneksi.
    
    Returns:
        requests.Response: Respons dari API.
    """
    url = "https://www.okx.com/priapi/v5/ecotrade/public/trade-records"
    retry_count = 0

    while retry_count <= max_retries:
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            else:
                print(f"API request failed with status code: {response.status_code}")
                raise requests.exceptions.RequestException(f"Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error occurred: {e}")
            if retry_count >= max_retries:
                print("Max retry count reached. Waiting for 10 minutes before next try...")
                time.sleep(600)
                retry_count = 0
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)
                retry_count += 1
    return None

def get_markprice(inst_id):
    """
    Mendapatkan harga mark (mark price) dari OKX API.
    
    Parameters:
        inst_id (str): ID instrumen (misalnya, BTC-USDT-SWAP).
    
    Returns:
        str: Harga mark atau pesan kesalahan jika gagal.
    """
    url = "https://www.okx.com/api/v5/public/mark-price"
    params = {
        'instType': 'SWAP',
        'instId': inst_id
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == "0":
                return data["data"][0]["markPx"]
        return "Market price retrieval error"
    except Exception as e:
        print(f"Error retrieving mark price: {e}")
        return "Market price retrieval error"
