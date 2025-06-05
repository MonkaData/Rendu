# Rendu

This repository provides a minimal MuZero implementation, a simplified Teamfight Tactics environment, and example cryptocurrency backtesting strategies.

- `tft_alias.py` implements a lightweight TFT-like environment with basic shop, board and synergy mechanics.
- `muzero_tft.py` contains a MuZero agent that interacts with this alias environment for demonstration.
- `backtest.py` fetches market data from Binance and runs simple BTC/ETC strategies.

Run a small MuZero training loop with:

```bash
python muzero_tft.py
```

Backtest a strategy (e.g. EMA breakout) with:

```bash
python backtest.py --strategy breakout_ema_volume --symbol BTCUSDT --interval 30m
```
