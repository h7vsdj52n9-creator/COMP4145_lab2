import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from trading_strategy import (
    get_stock_data,
    calculate_moving_averages,
    identify_golden_cross,
    implement_strategy,
)

st.set_page_config(page_title="MSFT Trading Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    trades = implement_strategy(data)
    trades = trades.dropna(subset=["SellPrice", "ProfitPct"]).copy()

    if not trades.empty:
        trades["BuyDate"] = pd.to_datetime(trades["BuyDate"])
        trades["SellDate"] = pd.to_datetime(trades["SellDate"])

    total_trades = len(trades)
    winning_trades = int((trades["ProfitPct"] > 0).sum()) if total_trades else 0
    losing_trades = total_trades - winning_trades
    win_rate = (winning_trades / total_trades * 100) if total_trades else 0
    average_profit = float(trades["ProfitPct"].mean()) if total_trades else 0
    average_holding = float(trades["HoldingDays"].mean()) if total_trades else 0

    summary = {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
        "average_profit": round(average_profit, 2),
        "average_holding_days": round(average_holding, 2),
    }

    return data, trades, summary


page = st.sidebar.radio("Select Page", ["Price Chart", "Trade Statistics", "Detailed Trades"])

data, trades, summary = load_data()

if page == "Price Chart":
    st.title("MSFT Price Chart with Moving Averages and Trades")

    chart_df = data.reset_index().rename(columns={"index": "Date"})
    chart_df["Date"] = pd.to_datetime(chart_df["Date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(chart_df["Date"], chart_df["Close"], label="Close Price", color="blue", linewidth=2)
    ax.plot(chart_df["Date"], chart_df["MA50"], label="MA50", color="green", linewidth=1.5)
    ax.plot(chart_df["Date"], chart_df["MA200"], label="MA200", color="orange", linewidth=1.5)

    if not trades.empty:
        buy_df = trades[["BuyDate", "BuyPrice"]].rename(columns={"BuyDate": "Date", "BuyPrice": "Price"})
        sell_df = trades[["SellDate", "SellPrice"]].rename(columns={"SellDate": "Date", "SellPrice": "Price"})

        ax.scatter(buy_df["Date"], buy_df["Price"], color="green", s=30, label="Buy")
        ax.scatter(sell_df["Date"], sell_df["Price"], color="red", s=30, label="Sell")

    ax.set_title("MSFT Price Chart")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

elif page == "Trade Statistics":
    st.title("Trade Statistics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Trades", summary["total_trades"])
    col2.metric("Winning Trades", summary["winning_trades"])
    col3.metric("Losing Trades", summary["losing_trades"])
    col4.metric("Win Rate", f"{summary['win_rate']}%")
    col5.metric("Average Profit", f"{summary['average_profit']}%")
    col6.metric("Average Holding Days", f"{summary['average_holding_days']}")

else:
    st.title("Detailed Trades")
    if trades.empty:
        st.info("No completed trades to display.")
    else:
        display = trades[["BuyDate", "BuyPrice", "SellDate", "SellPrice", "HoldingDays", "ProfitPct", "SellReason"]].copy()
        display["BuyDate"] = display["BuyDate"].dt.strftime("%Y-%m-%d")
        display["SellDate"] = display["SellDate"].dt.strftime("%Y-%m-%d")
        display["BuyPrice"] = display["BuyPrice"].round(2)
        display["SellPrice"] = display["SellPrice"].round(2)
        display["ProfitPct"] = display["ProfitPct"].round(2)
        st.dataframe(display, use_container_width=True)
