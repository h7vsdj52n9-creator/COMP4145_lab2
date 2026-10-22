import pandas as pd
import yfinance as yf

# Download 5 years of MSFT data
def get_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Calculate moving averages
def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

# Identify golden cross (buy signals)
def identify_golden_cross(data):
    data['Signal'] = 0
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    return data

# Implement trading strategy
def implement_strategy(data):
    positions = []
    data = data.iloc[200:].copy()

    buy_dates = data[data['GoldenCross'] == True].index.tolist()

    for buy_date in buy_dates:
        buy_price = data.loc[buy_date, 'Close']
        target_price = buy_price * 1.15
        max_sell_date = buy_date + pd.Timedelta(days=60)
        sell_period = data.loc[buy_date:max_sell_date].copy()
        target_reached = sell_period[sell_period['Close'] >= target_price]

        if not target_reached.empty:
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            sell_reason = "Target reached"
        else:
            sell_date_candidates = sell_period.index.tolist()
            if sell_date_candidates:
                sell_date = sell_date_candidates[-1]
                sell_price = data.loc[sell_date, 'Close']
                sell_reason = "Max holding period"
            else:
                continue

        holding_days = (sell_date - buy_date).days
        profit_pct = (sell_price / buy_price - 1) * 100

        positions.append({
            'BuyDate': buy_date,
            'BuyPrice': buy_price,
            'SellDate': sell_date,
            'SellPrice': sell_price,
            'HoldingDays': holding_days,
            'ProfitPct': profit_pct,
            'SellReason': sell_reason
        })

    return pd.DataFrame(positions)


def analyze_results(positions):
    if positions.empty:
        return "No trading signals detected"

    total_trades = len(positions)
    win_trades = len(positions[positions['ProfitPct'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
    avg_profit = positions['ProfitPct'].mean()
    avg_holding = positions['HoldingDays'].mean()

    print("\n===== Trading Strategy Results (Golden Cross)=====")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {win_trades} ({win_rate:.2f}%)")
    print(f"Losing Trades: {loss_trades}")
    print(f"Average Profit: {avg_profit:.2f}%")
    print(f"Average Holding Days: {avg_holding:.2f}")

    return positions


def main():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    analyze_results(positions)
    return positions


if __name__ == "__main__":
    positions = main()
    print("\nDetailed Trades:")
    print(positions.to_string())
