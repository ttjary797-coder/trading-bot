import os
import time
from binance.client import Client
import pandas as pd

# --- الإعدادات والاتصال ---
api_key = os.environ.get('BINANCE_API_KEY')
api_secret = os.environ.get('BINANCE_API_SECRET')
client = Client(api_key, api_secret, tld='com', testnet=True)
print("--- تم الاتصال بنجاح بـ Binance Testnet ---")

def get_market_data(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, lookback="1 day ago UTC"):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    return df

def calculate_indicators(df):
    # ADX
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    tr1 = pd.DataFrame(df['high'] - df['low'])
    tr2 = pd.DataFrame(abs(df['high'] - df['close'].shift(1)))
    tr3 = pd.DataFrame(abs(df['low'] - df['close'].shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1/14).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (14 - 1)) + dx) / 14
    df['adx'] = adx.rolling(14).mean().iloc[-1]
    return df

def run_bot():
    print("--- بدء دورة جديدة للبوت ---")
    df = get_market_data()
    df = calculate_indicators(df)
    adx_value = df['adx'].iloc[-1]
    print(f"قيمة ADX الحالية: {adx_value:.2f}")

    if adx_value > 25:
        print("تشخيص: السوق في حالة اتجاه. استدعاء مجلس خبراء السوق الصاعد.")
        # هنا يمكنك إضافة منطق التداول في السوق الصاعد
    else:
        print("تشخيص: السوق في حالة تذبذب. استدعاء مجلس خبراء السوق المتذبذب.")
        # هنا يمكنك إضافة منطق التداول في السوق المتذبذب

print("--- انتهاء الدورة، الانتظار لمدة 60 ثانية ---")
