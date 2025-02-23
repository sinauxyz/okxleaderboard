import pandas as pd
import time
import json
import requests
import datetime
import logging
import sys
from misc import get_header, get_json
from datetime import timedelta, timezone
from message import telegram_send_message
from okx import get_position, get_nickname, get_markprice

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Load UIDs dari file JSON
def load_uids():
    try:
        with open('uids.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File uids.json tidak ditemukan. Jalankan setup.py terlebih dahulu.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Format uids.json tidak valid.")
        sys.exit(1)

TARGETED_ACCOUNT_UIDs = load_uids()

ACCOUNT_INFO_URL_TEMPLATE = 'https://www.okx.com/copy-trading/account/{}?tab=trade'

# Modifying DataFrame, including calculating estimated entry size in USDT
def modify_data(data) -> pd.DataFrame:
    """
    Memproses data posisi trading dari API OKX.
    
    Parameters:
        data (dict): Data mentah dari API OKX.
    
    Returns:
        pd.DataFrame: DataFrame yang berisi posisi trading yang diproses.
    """
    if not data or 'code' not in data or data['code'] != "0":
        logging.warning("Invalid data structure received from API.")
        return pd.DataFrame()

    positions = data['data'][0]['posData']
    df = pd.DataFrame(positions)

    # Debugging: Cetak kolom yang tersedia
    logging.info(f"Available columns in DataFrame: {df.columns.tolist()}")

    # Pastikan kolom 'instId' ada di DataFrame
    if 'instId' not in df.columns:
        logging.error("Column 'instId' not found in DataFrame.")
        return pd.DataFrame()

    # Set 'instId' sebagai index
    df.set_index('instId', inplace=True)

    # Menghitung estimatedEntrySize
    df['estimatedEntrySize'] = df['pos']

    # Menentukan posisi (LONG/SHORT)
    df['estimatedPosition'] = df['posSide'].apply(lambda x: 'LONG' if x == 'long' else 'SHORT')

    # Memformat waktu update (UTC+7)
    df['updateTime'] = df['cTime'].apply(lambda x: datetime.datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc))
    df['updateTime'] = df['updateTime'] + timedelta(hours=7)  # Konversi ke UTC+7
    df['updateTime'] = df['updateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Memilih kolom yang diperlukan
    position_result = df[['estimatedPosition', 'lever', 'estimatedEntrySize', 
                          'avgPx', 'liqPx', 'uplRatio', 'updateTime']]
    return position_result

previous_symbols = {}
previous_position_results = {}
is_first_runs = {uid: True for uid in TARGETED_ACCOUNT_UIDs}

# Function to send new position message
def send_new_position_message(symbol, row, nickname):
    """
    Mengirim pesan Telegram ketika posisi baru dibuka.
    
    Parameters:
        symbol (str): Simbol trading (misalnya, BTC-USDT-SWAP).
        row (pd.Series): Baris DataFrame yang berisi detail posisi.
        nickname (str): Nickname dari trader.
    """
    estimated_position = row['estimatedPosition']
    leverage = row['lever']
    estimated_entry_size = row['estimatedEntrySize']
    entry_price = row['avgPx']
    liq_price = row['liqPx']
    pnl = float(row['uplRatio']) * 100
    updatetime = row['updateTime']
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"  # Emoji untuk PnL positif/negatif
    message = (
        f"⚠️ [<b>{nickname}</b>]\n"
        f"❇️ <b>New position opened</b>\n\n"
        f"<b>Position:</b> {symbol} {estimated_position} {leverage}X\n\n"
        f"💵 Base currency - USDT\n"
        f"------------------------------\n"
        f"🎯 <b>Entry Price:</b> {entry_price}\n"
        f"💰 <b>Est. Liq Price:</b> {liq_price}\n"
        f"{pnl_emoji} <b>PnL:</b> {pnl:.2f}%\n\n"
        f"🕒 <b>Last Update:</b>\n{updatetime} (UTC+7)\n"
        f"🔗 <a href='{ACCOUNT_INFO_URL}'><b>VIEW PROFILE ON OKX</b></a>"
    )
    telegram_send_message(message)

# Function to send closed position message
def send_closed_position_message(symbol, row, nickname):
    """
    Mengirim pesan Telegram ketika posisi ditutup.
    
    Parameters:
        symbol (str): Simbol trading.
        row (pd.Series): Baris DataFrame yang berisi detail posisi.
        nickname (str): Nickname dari trader.
    """
    estimated_position = row['estimatedPosition']
    leverage = row['lever']
    updatetime = row['updateTime']
    message = (
        f"⚠️ [<b>{nickname}</b>]\n"
        f"⛔️ <b>Position closed</b>\n\n"
        f"<b>Position:</b> {symbol} {estimated_position} {leverage}X\n"
        f"💵 <b>Current Price:</b> {get_markprice(symbol)} USDT\n\n"
        f"🕒 <b>Last Update:</b>\n{updatetime} (UTC+7)\n"
        f"🔗 <a href='{ACCOUNT_INFO_URL}'><b>VIEW PROFILE ON OKX</b></a>"
    )
    telegram_send_message(message)

# Function to send current positions
def send_current_positions(position_result, nickname):
    """
    Mengirim pesan Telegram dengan daftar posisi saat ini.
    
    Parameters:
        position_result (pd.DataFrame): DataFrame yang berisi posisi saat ini.
        nickname (str): Nickname dari trader.
    """
    if position_result.empty:
        telegram_send_message(f"⚠️ [<b>{nickname}</b>]\n💎 <b>No positions found</b>")
    else:
        telegram_send_message(f"⚠️ [<b>{nickname}</b>]\n💎 <b>Current positions:</b>")
        for symbol, row in position_result.iterrows():
            estimated_position = row['estimatedPosition']
            leverage = row['lever']
            estimated_entry_size = row['estimatedEntrySize']
            entry_price = row['avgPx']
            liq_price = row['liqPx']
            pnl = float(row['uplRatio']) * 100
            updatetime = row['updateTime']
            pnl_emoji = "🟢" if pnl >= 0 else "🔴"  # Emoji untuk PnL positif/negatif
            message = (
                f"🔄 <b>Position:</b> {symbol} {estimated_position} {leverage}X\n\n"
                f"💵 Base currency - USDT\n"
                f"------------------------------\n"
                f"🎯 <b>Entry Price:</b> {entry_price}\n"
                f"💰 <b>Est. Liq Price:</b> {liq_price}\n"
                f"{pnl_emoji} <b>PnL:</b> {pnl:.2f}%\n\n"
                f"🕒 <b>Last Update:</b>\n{updatetime} (UTC+7)\n"
                f"🔗 <a href='{ACCOUNT_INFO_URL}'><b>VIEW PROFILE ON OKX</b></a>"
            )
            telegram_send_message(message)

while True:
    try:
        start_time = time.time()  # Catat waktu mulai iterasi
        
        for TARGETED_ACCOUNT_UID in TARGETED_ACCOUNT_UIDs:
            ACCOUNT_INFO_URL = ACCOUNT_INFO_URL_TEMPLATE.format(TARGETED_ACCOUNT_UID)
            headers = get_header(ACCOUNT_INFO_URL)
            json_data = get_json(TARGETED_ACCOUNT_UID)

            response = requests.get(
                "https://www.okx.com/priapi/v5/ecotrade/public/positions-v2",
                headers=headers,
                params=json_data
            )
            if response.status_code == 200:
                data = response.json()
                if data["code"] == "0":
                    # Ambil nickname dari API trade-records
                    nickname_response = get_nickname(headers, json_data)
                    if nickname_response and nickname_response.status_code == 200:
                        nickname_data = nickname_response.json()
                        if nickname_data["code"] == "0" and len(nickname_data["data"]) > 0:
                            nickname = nickname_data["data"][0]["nickName"]
                        else:
                            nickname = "Unknown"
                    else:
                        nickname = "Unknown"

                    position_result = modify_data(data)

                    new_symbols = position_result.index.difference(previous_symbols.get(TARGETED_ACCOUNT_UID, pd.Index([])))
                    if not is_first_runs[TARGETED_ACCOUNT_UID] and not new_symbols.empty:
                        for symbol in new_symbols:
                            send_new_position_message(symbol, position_result.loc[symbol], nickname)

                    closed_symbols = previous_symbols.get(TARGETED_ACCOUNT_UID, pd.Index([])).difference(position_result.index)
                    if not is_first_runs[TARGETED_ACCOUNT_UID] and not closed_symbols.empty:
                        for symbol in closed_symbols:
                            if symbol in previous_position_results.get(TARGETED_ACCOUNT_UID, pd.DataFrame()).index:
                                send_closed_position_message(symbol, previous_position_results[TARGETED_ACCOUNT_UID].loc[symbol], nickname)

                    if is_first_runs[TARGETED_ACCOUNT_UID]:
                        send_current_positions(position_result, nickname)

                    previous_position_results[TARGETED_ACCOUNT_UID] = position_result.copy()
                    previous_symbols[TARGETED_ACCOUNT_UID] = position_result.index.copy()
                    is_first_runs[TARGETED_ACCOUNT_UID] = False

        # Hitung waktu eksekusi dan log
        ping_time = (time.time() - start_time) * 1000  # Konversi ke milidetik
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"✅ Bot is still running | Time: {current_time} | Ping: {ping_time:.2f}ms")
        
        time.sleep(150)
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        message = f"Error occurred for UID <b>{TARGETED_ACCOUNT_UID}</b>:\n{e}\n\n" \
                  f"Retrying after 60s"
        telegram_send_message(message)
        time.sleep(60)
