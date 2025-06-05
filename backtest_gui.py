import tkinter as tk
from tkinter import ttk
from backtest import fetch_binance_klines, STRATEGIES
import matplotlib.pyplot as plt
import pandas as pd


def run_backtest():
    symbol = symbol_var.get()
    interval = interval_var.get()
    capital = float(capital_var.get())
    df = fetch_binance_klines(symbol, interval)
    plt.figure()
    for name, var in strategy_vars.items():
        if var.get():
            curve = STRATEGIES[name](df)
            times = pd.to_datetime(df["close_time"].iloc[-len(curve):], unit="ms")
            capital_curve = capital + curve.values
            plt.plot(times, capital_curve, label=name)
            max_idx = capital_curve.argmax()
            min_idx = capital_curve.argmin()
            plt.scatter(times.iloc[max_idx], capital_curve[max_idx], color="green")
            plt.scatter(times.iloc[min_idx], capital_curve[min_idx], color="orange")
            if (capital_curve <= 0).any():
                b_idx = (capital_curve <= 0).argmax()
                plt.axvline(times.iloc[b_idx], color="red", linestyle="--")
    plt.title(f"Backtest on {symbol} ({interval})")
    plt.xlabel("Time")
    plt.ylabel("Capital")
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

# Capital
ttk.Label(frm, text="Capital:").grid(column=0, row=2, sticky=tk.W)
capital_var = tk.StringVar(value="1000")
entry_capital = ttk.Entry(frm, textvariable=capital_var)
entry_capital.grid(column=1, row=2, sticky=tk.W)

# Strategy checkboxes
ttk.Label(frm, text="Strategies:").grid(column=0, row=3, sticky=tk.W)
strategy_vars = {}
row = 4
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

