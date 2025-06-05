import pandas as pd


def ema_breakout_volume_strategy(df):
    """Breakout strategy using EMA20/50 and volume spike."""
    df = df.copy()
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()
    df['vol_avg20'] = df['volume'].rolling(20).mean()

    position = None
    entry_price = 0.0
    stop = 0.0
    target = 0.0
    equity_curve = []
    pnl = 0.0

    for i in range(50, len(df)):
        price = df['close'].iloc[i]
        high_range = df['high'].iloc[i-20:i].max()
        low_range = df['low'].iloc[i-20:i].min()
        volume = df['volume'].iloc[i]
        cond_breakout = (
            price > high_range and
            price > df['ema20'].iloc[i] and
            price > df['ema50'].iloc[i] and
            volume > df['vol_avg20'].iloc[i]
        )
        if position is None and cond_breakout:
            position = 'long'
            entry_price = price
            stop = low_range
            risk = entry_price - stop
            target = entry_price + 1.5 * risk
        elif position == 'long':
            if df['low'].iloc[i] <= stop:
                pnl += stop - entry_price
                position = None
            elif price >= target:
                pnl += target - entry_price
                position = None
        equity_curve.append(pnl)
    return pd.Series(equity_curve)
