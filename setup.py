import os
import sys
import json
import configparser

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Setup Wizard for OKX Leaderboard Tracker")

banner()

# Setup Telegram
config_file = 'config.ini'
telegram_info = configparser.RawConfigParser()
telegram_info.add_section('telegram')

xbot = input("[+] Enter Telegram Bot Token: ")
telegram_info.set('telegram', 'bottoken', xbot)

xchat = input("[+] Enter Telegram ChatID: ")
telegram_info.set('telegram', 'chatid', xchat)

with open(config_file, 'w') as setup:
    telegram_info.write(setup)

# Setup UIDs (Unique Names)
uids_file = 'uids.json'
uids = []

print("\n[+] Enter OKX Unique Names (contoh: 054F1B128E6181A7). Tekan Enter setelah setiap Unique Name, kosongkan untuk selesai):")
while True:
    uid = input("Unique Name: ").strip()
    if not uid:
        break
    uids.append(uid)

with open(uids_file, 'w') as f:
    json.dump(uids, f, indent=2)

print("\n[+] Setup completed successfully!")
