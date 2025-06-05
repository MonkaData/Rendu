import pandas as pd


def rsi_reversal_strategy(df):
    """RSI reversal strategy using RSI14."""
    df = df.copy()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['rsi'] = 100 - 100 / (1 + rs)

    position = None
    entry_price = 0.0
    stop = 0.0
    target = 0.0
    equity_curve = []
    pnl = 0.0

    for i in range(15, len(df)):
        price = df['close'].iloc[i]
        rsi = df['rsi'].iloc[i]
        candle_bull = df['close'].iloc[i] > df['open'].iloc[i]
        candle_bear = df['close'].iloc[i] < df['open'].iloc[i]
        recent_low = df['low'].iloc[i-5:i+1].min()
        if position is None and rsi < 25 and candle_bull:
            position = 'long'
            entry_price = price
            stop = recent_low
            risk = entry_price - stop
            target = entry_price + 2 * risk
        elif position == 'long':
            if price <= stop:
                pnl += stop - entry_price
                position = None
            elif rsi > 75 and candle_bear:
                pnl += price - entry_price
                position = None
            elif price >= target:
                pnl += target - entry_price
                position = None
        equity_curve.append(pnl)
    return pd.Series(equity_curve)
