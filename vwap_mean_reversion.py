import pandas as pd


def vwap_mean_reversion_strategy(df):
    """VWAP mean reversion strategy."""
    df = df.copy()
    cumulative_vol = df['volume'].cumsum()
    cumulative_price_vol = (df['close'] * df['volume']).cumsum()
    df['vwap'] = cumulative_price_vol / cumulative_vol

    position = None
    entry_price = 0.0
    stop = 0.0
    equity_curve = []
    pnl = 0.0

    for i in range(1, len(df)):
        price = df['close'].iloc[i]
        vwap = df['vwap'].iloc[i]
        prev_vol = df['volume'].iloc[i-1]
        vol_drop = df['volume'].iloc[i] < prev_vol
        if position is None:
            if price > vwap * 1.02 and vol_drop:
                position = 'short'
                entry_price = price
                stop = price * 1.015
            elif price < vwap * 0.98:
                position = 'long'
                entry_price = price
                stop = price * 0.985
        elif position == 'long':
            if price >= vwap:
                pnl += price - entry_price
                position = None
            elif price <= stop:
                pnl += stop - entry_price
                position = None
        elif position == 'short':
            if price <= vwap:
                pnl += entry_price - price
                position = None
            elif price >= stop:
                pnl += entry_price - stop
                position = None
        equity_curve.append(pnl)
    return pd.Series(equity_curve)
