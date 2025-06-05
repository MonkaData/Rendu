import tkinter as tk
from tkinter import ttk
from backtest import fetch_binance_klines, STRATEGIES
import matplotlib.pyplot as plt


def run_backtest():
    symbol = symbol_var.get()
    interval = interval_var.get()
    df = fetch_binance_klines(symbol, interval)
    plt.figure()
    for name, var in strategy_vars.items():
        if var.get():
            curve = STRATEGIES[name](df)
            plt.plot(curve.index, curve.values, label=name)
    plt.title(f"Backtest on {symbol} ({interval})")
    plt.xlabel("Steps")
    plt.ylabel("PnL")
    plt.legend()
    plt.grid(True)
    plt.show()


root = tk.Tk()
root.title("Crypto Backtester")

frm = ttk.Frame(root, padding=10)
frm.grid()

# Symbol
ttk.Label(frm, text="Symbol:").grid(column=0, row=0, sticky=tk.W)
symbol_var = tk.StringVar(value="BTCUSDT")
entry_symbol = ttk.Entry(frm, textvariable=symbol_var)
entry_symbol.grid(column=1, row=0, sticky=tk.W)

# Interval
ttk.Label(frm, text="Interval:").grid(column=0, row=1, sticky=tk.W)
interval_var = tk.StringVar(value="15m")
entry_interval = ttk.Entry(frm, textvariable=interval_var)
entry_interval.grid(column=1, row=1, sticky=tk.W)

# Strategy checkboxes
ttk.Label(frm, text="Strategies:").grid(column=0, row=2, sticky=tk.W)
strategy_vars = {}
row = 3
for name in STRATEGIES.keys():
    var = tk.BooleanVar()
    chk = ttk.Checkbutton(frm, text=name, variable=var)
    chk.grid(column=0, row=row, columnspan=2, sticky=tk.W)
    strategy_vars[name] = var
    row += 1

# Run button
btn = ttk.Button(frm, text="Run Backtest", command=run_backtest)
btn.grid(column=0, row=row, columnspan=2, pady=5)

root.mainloop()

