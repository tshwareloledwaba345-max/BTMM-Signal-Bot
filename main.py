Okay sorry, here it is in plain text. Just copy all of this:

import time
import json
import websocket

SYMBOLS = ["frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxAUDUSD", "frxUSDCAD"]
candles_data = {}
last_signal_time = {}

def check_btmm(symbol):
    candles = candles_data.get(symbol, [])
    if len(candles) < 10:
        return "WAIT"
    sweep_candle = candles[-3]
    confirm_candle = candles[-2]
    current = candles[-1]
    last_low = min([c['low'] for c in candles[-10:-1]])
    last_high = max([c['high'] for c in candles[-10:-1]])
    entry = current['close']
    buy_sweep = sweep_candle['low'] < last_low
    buy_confirm = confirm_candle['close'] > sweep_candle['high']
    if buy_sweep and buy_confirm:
        sl = sweep_candle['low']
        tp = entry + (entry - sl) _ 2
        return f"BUY SIGNAL {symbol} | Entry {entry} SL {sl} TP {tp}"
    sell_sweep = sweep_candle['high'] > last_high
    sell_confirm = confirm_candle['close'] < sweep_candle['low']
    if sell_sweep and sell_confirm:
        sl = sweep_candle['high']
        tp = entry - (sl - entry) _ 2
        return f"SELL SIGNAL {symbol} | Entry {entry} SL {sl} TP {tp}"
    return "WAIT"

def on_message(ws, message):
    data = json.loads(message)
    if 'candles' in data:
        symbol = data.get('echo_req', {}).get('ticks_history', '')
        if symbol in SYMBOLS:
            candles_data[symbol] = [{'open': float(c['open']), 'high': float(c['high']), 'low': float(c['low']), 'close': float(c['close'])} for c in data['candles']]
            signal = check_btmm(symbol)
            now = time.time()
            if signal != "WAIT" and now - last_signal_time.get(symbol, 0) > 300:
                last_signal_time[symbol] = now
                print(signal, flush=True)
            else:
                print(f"{symbol} WAIT - No Signal", flush=True)

def on_open(ws):
    print("BTMM Level 3 Signal Bot Started", flush=True)
    for s in SYMBOLS:
        ws.send(json.dumps({"ticks_history": s, "adjust_start_time": 1, "count": 50, "end": "latest", "start": 1, "style": "candles", "granularity": 900}))

while True:
    try:
        ws = websocket.WebSocketApp("wss://ws.derivws.com/websockets/v3?app_id=1089", on_open=on_open, on_message=on_message)
        ws.run_forever()
    except Exception as e:
        print("Reconnect:", e, flush=True)
        time.sleep(5)

Now in GitHub:
1. Open main.py
2. Tap Edit
3. Delete everything
4. Paste this
5. Tap Commit changes
