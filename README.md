# Stock Disposition Checker

This repository contains a simple tool to detect when a stock should be
classified as a **處置股** according to the guidelines from the Taiwan Stock
Exchange "公告或通知注意交易資訊暨處置作業要點".

The main script is `disposition_checker.py`. It reads a CSV file with daily
trading data and prints the dates that meet the criteria for disposition.

## Usage

Prepare a CSV file with the following columns:

```
date,open,high,low,close,volume,index_open,index_high,index_low,index_close,outstanding_shares
```

Run the script:

```bash
python disposition_checker.py stock_data.csv
```

The script outputs the dates where the stock becomes a `處置股`.
