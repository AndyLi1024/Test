import datetime
import json
from urllib import request, error


def fetch_limit_up(date: str | None = None):
    """Fetch today's limit-up stocks from Taiwan Stock Exchange.

    Parameters
    ----------
    date: str | None
        Date in YYYYMMDD format. Defaults to today.

    Returns
    -------
    list[dict]
        List of dictionaries with stock_no and stock_name.
    """
    if date is None:
        date = datetime.date.today().strftime("%Y%m%d")

    url = f"https://www.twse.com.tw/exchangeReport/TWT43U?response=json&date={date}"
    try:
        with request.urlopen(url) as resp:
            content = resp.read().decode("utf-8")
    except error.URLError as e:
        raise RuntimeError(f"Failed to fetch data: {e}")

    data = json.loads(content)
    if data.get("stat") != "OK":
        raise RuntimeError(f"API error: {data.get('stat')}")

    result = []
    for row in data.get("data", []):
        if len(row) >= 2:
            result.append({"stock_no": row[0], "stock_name": row[1]})
    return result


def main():
    stocks = fetch_limit_up()
    for s in stocks:
        print(f"{s['stock_no']} {s['stock_name']}")


if __name__ == "__main__":
    main()
