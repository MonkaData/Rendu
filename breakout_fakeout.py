import pandas as pd


def breakout_fakeout_strategy(df):
    """Breakout fakeout (liquidity trap) strategy."""
    df = df.copy()
    equity_curve = []
    pnl = 0.0
    position = None
    entry_price = 0.0
    stop = 0.0
    target = 0.0

    for i in range(20, len(df)):
        high_range = df['high'].iloc[i-20:i].max()
        low_range = df['low'].iloc[i-20:i].min()
        close = df['close'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        if position is None:
            if high > high_range and close < high_range:
                position = 'short'
                entry_price = close
                stop = high
                target = (high_range + low_range) / 2
            elif low < low_range and close > low_range:
                position = 'long'
                entry_price = close
                stop = low
                target = (high_range + low_range) / 2
        elif position == 'long':
            if low <= stop:
                pnl += stop - entry_price
                position = None
            elif close >= target:
                pnl += target - entry_price
                position = None
        elif position == 'short':
            if high >= stop:
                pnl += entry_price - stop
                position = None
            elif close <= target:
                pnl += entry_price - target
                position = None
        equity_curve.append(pnl)
    return pd.Series(equity_curve)
