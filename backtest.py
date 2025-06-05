import argparse
import requests
import pandas as pd
import matplotlib.pyplot as plt

from breakout_ema_volume import ema_breakout_volume_strategy
from rsi_reversal import rsi_reversal_strategy
from vwap_mean_reversion import vwap_mean_reversion_strategy
from breakout_fakeout import breakout_fakeout_strategy
from ema_pullback import ema_pullback_strategy


STRATEGIES = {
    "breakout_ema_volume": ema_breakout_volume_strategy,
    "rsi_reversal": rsi_reversal_strategy,
    "vwap_mean_reversion": vwap_mean_reversion_strategy,
    "breakout_fakeout": breakout_fakeout_strategy,
    "ema_pullback": ema_pullback_strategy,
}


def fetch_binance_klines(symbol: str, interval: str, limit: int = 500):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "qav",
        "num_trades",
        "taker_base",
        "taker_quote",
        "ignore",
    ]
    df = pd.DataFrame(data, columns=cols)
    df = df.astype(
        {
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "float",
        }
    )
    return df


def main():
    parser = argparse.ArgumentParser(description="Backtest strategies on Binance data")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="15m")
    parser.add_argument("--strategy", choices=list(STRATEGIES.keys()), required=True)
    args = parser.parse_args()

    df = fetch_binance_klines(args.symbol, args.interval)
    strategy_fn = STRATEGIES[args.strategy]
    curve = strategy_fn(df)

    plt.plot(curve.index, curve.values)
    plt.title(f"{args.strategy} on {args.symbol}")
    plt.xlabel("Steps")
    plt.ylabel("PnL")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
