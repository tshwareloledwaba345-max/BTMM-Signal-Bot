import time
import json
import websocket

SYMBOLS = ["frxEURUSD", "frxGBPUSD", "frxUSDJPY", "R_75", "R_100", "R_50", "frxXAUUSD", "frxUSOIL", "frxUKOIL"]
candles_data = {}
last_signal_time = {}

def check_btmm(symbol):
    candles = candles_data.get(symbol, [])
    if len(candles) < 10:
        return "WAIT"
    prev = candles[-6:-2]
    sweep_candle = candles[-3]
    confirm_candle = candles[-2]
    current = candles[-1]
    last_low = min([c['low'] for c in prev])
    last_high = max([c['high'] for c in prev])
    entry = current['close']
    buy_sweep = sweep_candle['low'] < last_low and sweep_candle['close'] > last_low
    buy_confirm = confirm_candle['close'] > confirm_candle['open'] and confirm_candle['close'] > sweep_candle['close']
    if buy_sweep and buy_confirm:
        sl = sweep_candle['low']
        tp = entry + (entry - sl) _ 2
        return f"BUY SIGNAL {symbol} | Entry {entry} | SL {sl} | TP {tp} | BTMM LEVEL 3 MATCHED"
    sell_sweep = sweep_candle['high'] > last_high and sweep_candle['close'] < last_high
    sell_confirm = confirm_candle['close'] < confirm_candle['open'] and confirm_candle['close'] < sweep_candle['close']
    if sell_sweep and sell_confirm:
        sl = sweep_candle['high']
        tp = entry - (sl - entry) _ 2
        return f"SELL SIGNAL {symbol} | Entry {entry} | SL {sl} | TP {tp} | BTMM LEVEL 3 MATCHED"
    return "WAIT"

def on_message(ws, message):
    data = json.loads(message)
    if 'candles' in data:
        symbol = data.get('echo_req', {}).get('ticks_history', '')
        if symbol in SYMBOLS:
            candles_data[symbol] = [{'open': float(c['open']), 'low': float(c['low']), 'high': float(c['high']), 'close': float(c['close'])} for c in data['candles']]
            signal = check_btmm(symbol)
            now = time.time()
            if signal != "WAIT" and now - last_signal_time.get(symbol, 0) > 300:
                last_signal_time[symbol] = now
                print(signal, flush=True)
            else:
                print(f"{symbol} WAIT - No Level 3 Match", flush=True)

def on_open(ws):
    print("BTMM Level 3 Signal Bot Started - 9 Markets", flush=True)
    for s in SYMBOLS:
        ws.send(json.dumps({"ticks_history": s, "count": 100, "end": "latest", "granularity": 60, "style": "candles", "subscribe": 1}))

while True:
    try:
        ws = websocket.WebSocketApp("wss://ws.derivws.com/websockets/v3?app_id=1089", on_open=on_open, on_message=on_message)
        ws.run_forever()
    except Exception as e:
        print("Reconnect:", e, flush=True)
        time.sleep(5)


