import time

def get_header(referer_url: str):
    """
    Membuat header HTTP yang diperlukan untuk request ke API OKX.
    
    Parameters:
        referer_url (str): URL referer untuk request.
    
    Returns:
        dict: Dictionary yang berisi header HTTP.
    """
    return {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        'Accept': "application/json",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'x-id-group': "2140401507149800008-c-9",
        'x-zkdex-env': "0",
        'sec-ch-ua-platform': "\"Linux\"",
        'sec-ch-ua': "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
        'x-cdn': "https://www.okx.com",
        'app-type': "web",
        'x-utc': "7",
        'sec-ch-ua-mobile': "?0",
        'devid': "2eaa91f9-36bc-47bf-8e0b-44eb3a5f3f81",
        'x-site-info': "==QfxojI5RXa05WZiwiIMFkQPx0Rfh1SPJiOiUGZvNmIsICRJJiOi42bpdWZyJye",
        'x-locale': "en_US",
        'sec-gpc': "1",
        'accept-language': "en-US,en;q=0.9",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': referer_url,
        'priority': "u=1, i",
        'Cookie': "ok_site_info===QfxojI5RXa05WZiwiIMFkQPx0Rfh1SPJiOiUGZvNmIsICRJJiOi42bpdWZyJye; ok_prefer_udColor=0; ok_prefer_udTimeZone=0; locale=en_US; devId=2eaa91f9-36bc-47bf-8e0b-44eb3a5f3f81; preferLocale=en_US; ok-exp-time=1740127222529; tmx_session_id=gaatq5rhbn7_1740127227914; fingerprint_id=450c66bd-8702-4c3b-8377-20d1cde5b775; ok_prefer_currency=%7B%22currencyId%22%3A0%2C%22isDefault%22%3A1%2C%22isPremium%22%3Afalse%2C%22isoCode%22%3A%22USD%22%2C%22precision%22%3A2%2C%22symbol%22%3A%22%24%22%2C%22usdToThisRate%22%3A1%2C%22usdToThisRatePremium%22%3A1%2C%22displayName%22%3A%22USD%22%7D; intercom-id-ny9cf50h=95beb527-685b-4969-8c51-605a4e53a387; intercom-session-ny9cf50h=; intercom-device-id-ny9cf50h=c3f103ef-ab61-44a0-bc14-8d41005dcc49; first_ref=https%3A%2F%2Fsearch.brave.com%2F; okg.currentMedia=md; traceId=2140401507149800008; ok_prefer_exp=1; ok-ses-id=QqZKA97WFWOw8asBj4lhu0CanQKBqbajb2+VX4KRxB9m4ip1sxc4PAL6qUftnT4Adce7ORn1XCXTbuzOa8UrQ69NZ3ez8EuE12AmSydeYmoN4QzD7kc1/uEUs9IgLD/7; __cf_bm=ymVlkL1ZfHsO9sFtQrbqMhvpCrhjTzrjIqzCplxxNA0-1740150717-1.0.1.1-_RNHotjCWC8BWhMd.ji1Q1JWa1kn9XibSCxxA1ty78_pGSJRl5fzidtMaIFSD0qvcMkAzayTeK0wTBpfbkmJqQ; _monitor_extras={\"deviceId\":\"mVSi8RJIYLpbGLtTDY0ZLy\",\"eventId\":48,\"sequenceNumber\":48}"
    }

def get_json(unique_name: str):
    """
    Membuat payload JSON yang diperlukan untuk request ke API OKX.
    
    Parameters:
        unique_name (str): Unique Name dari akun OKX yang ingin dilacak.
    
    Returns:
        dict: Dictionary yang berisi payload JSON.
    """
    return {
        'limit': "10",
        'uniqueName': unique_name,
        't': str(int(time.time() * 1000))  # Timestamp dalam milidetik
    }
