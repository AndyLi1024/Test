# coding: utf-8
"""Tool to check if a stock becomes a '處置股' based on daily trading data.

The rules implemented are simplified from the Taiwan Stock Exchange
"公告或通知注意交易資訊暨處置作業要點" (Article 2 and 6). A stock is flagged
for unusual trading information when:
    1. The intraday amplitude exceeds 9%, the difference with the index
       amplitude exceeds 5%, and volume >= 3000 units.
    2. The intraday price change exceeds 6%, the difference with the index
       price change exceeds 4%, and volume >= 3000 units.
    3. The intraday turnover rate exceeds 10% and volume >= 3000 units.

A stock becomes a '處置股' when unusual trading information is announced for
three consecutive trading days, or when it occurs on six days within ten
consecutive trading days, or twelve days within thirty consecutive trading
days.

The script expects a CSV file with columns:
    date, open, high, low, close, volume, index_open, index_high,
    index_low, index_close, outstanding_shares

Example usage:
    python disposition_checker.py stock_data.csv
"""

import csv
import sys
from datetime import datetime, timedelta


def parse_row(row):
    return {
        'date': datetime.strptime(row['date'], '%Y-%m-%d'),
        'open': float(row['open']),
        'high': float(row['high']),
        'low': float(row['low']),
        'close': float(row['close']),
        'volume': float(row['volume']),
        'idx_open': float(row['index_open']),
        'idx_high': float(row['index_high']),
        'idx_low': float(row['index_low']),
        'idx_close': float(row['index_close']),
        'outstanding': float(row['outstanding_shares']),
    }


def compute_metrics(rows):
    prev_close = None
    prev_idx_close = None
    for row in rows:
        amplitude = (row['high'] - row['low']) / row['low'] * 100
        idx_amplitude = (row['idx_high'] - row['idx_low']) / row['idx_low'] * 100
        amplitude_diff = amplitude - idx_amplitude

        if prev_close is None:
            price_change = 0
            idx_price_change = 0
        else:
            price_change = (row['close'] - prev_close) / prev_close * 100
            idx_price_change = (row['idx_close'] - prev_idx_close) / prev_idx_close * 100
        price_diff = price_change - idx_price_change

        turnover = row['volume'] / row['outstanding'] * 100

        row.update({
            'amplitude': amplitude,
            'amplitude_diff': amplitude_diff,
            'price_change': price_change,
            'price_diff': price_diff,
            'turnover': turnover,
        })

        prev_close = row['close']
        prev_idx_close = row['idx_close']


def flag_unusual(rows):
    flags = []
    for row in rows:
        cond1 = row['amplitude'] > 9 and row['amplitude_diff'] > 5 and row['volume'] >= 3000
        cond2 = row['price_change'] > 6 and row['price_diff'] > 4 and row['volume'] >= 3000
        cond3 = row['turnover'] > 10 and row['volume'] >= 3000
        flagged = cond1 or cond2 or cond3
        flags.append(flagged)
    return flags


def check_disposition(dates, flags):
    n = len(dates)
    disposition_days = []
    for i in range(n):
        if i >= 2 and flags[i] and flags[i-1] and flags[i-2]:
            disposition_days.append(dates[i])
            continue
        # count last 10 days
        start10 = max(0, i-9)
        last10 = sum(flags[start10:i+1])
        if last10 >= 6:
            disposition_days.append(dates[i])
            continue
        # count last 30 days
        start30 = max(0, i-29)
        last30 = sum(flags[start30:i+1])
        if last30 >= 12:
            disposition_days.append(dates[i])
            continue
    return disposition_days


def main(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [parse_row(r) for r in reader]

    rows.sort(key=lambda r: r['date'])
    compute_metrics(rows)
    flags = flag_unusual(rows)
    dates = [row['date'] for row in rows]
    disposition_days = check_disposition(dates, flags)

    for d in disposition_days:
        print(f"{d.strftime('%Y-%m-%d')} becomes a 處置股")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python disposition_checker.py <stock_data.csv>')
        sys.exit(1)
    main(sys.argv[1])
