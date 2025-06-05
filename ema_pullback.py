import pandas as pd


def ema_pullback_strategy(df):
    """EMA pullback trend trading strategy."""
    df = df.copy()
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema21'] = df['close'].ewm(span=21).mean()

    position = None
    entry_price = 0.0
    stop = 0.0
    target = 0.0
    equity_curve = []
    pnl = 0.0

    for i in range(21, len(df)):
        price = df['close'].iloc[i]
        trend_up = df['ema9'].iloc[i] > df['ema21'].iloc[i]
        pullback = df['low'].iloc[i] <= df['ema21'].iloc[i]
        bullish = df['close'].iloc[i] > df['open'].iloc[i]
        if position is None and trend_up and pullback and bullish:
            position = 'long'
            entry_price = price
            stop = df['ema21'].iloc[i]
            risk = entry_price - stop
            target = entry_price + 2 * risk
        elif position == 'long':
            if df['low'].iloc[i] <= stop:
                pnl += stop - entry_price
                position = None
            elif price >= target:
                pnl += target - entry_price
                position = None
        equity_curve.append(pnl)
    return pd.Series(equity_curve)
