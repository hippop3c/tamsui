"""
淡水・八里 YouBike 整點抓取
由 GitHub Actions 每個整點自動執行，把結果寫到 data.json
"""
import requests
import json
import time
import sys
from datetime import datetime, timezone, timedelta

TARGET_STATIONS = [
    "輕軌漁人碼頭",
    "橋管中心",
    "淡水轉運站",
    "八里文化公園",
]

# 多個資料來源依序嘗試
API_URLS = [
    # 新北市開放資料平台官方
    "https://data.ntpc.gov.tw/api/datasets/71CD1490-A2DF-4198-BEF1-318479775E8A/json/?size=10000",
    # 政府資料開放平台 data.gov.tw（同樣資料、不同主機，做為備援）
    "https://data.gov.tw/api/v2/rest/dataset/146969",
]

# 模擬真實瀏覽器
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://data.ntpc.gov.tw/",
}

TPE = timezone(timedelta(hours=8))


def try_fetch(url, attempt_label):
    """嘗試抓一個 URL，回傳 list 或 None"""
    print(f"\n→ 嘗試 {attempt_label}：{url[:80]}")
    try:
        r = requests.get(url, timeout=30, headers=HEADERS)
        print(f"   HTTP {r.status_code}, Content-Type: {r.headers.get('Content-Type', '?')}")
        print(f"   回傳大小：{len(r.content)} bytes")

        if r.status_code != 200:
            print(f"   前 300 字：{r.text[:300]}")
            return None

        try:
            data = r.json()
        except json.JSONDecodeError:
            print(f"   ⚠ 不是 JSON。前 500 字：{r.text[:500]}")
            return None

        if isinstance(data, list) and len(data) > 0:
            print(f"   ✓ 收到 {len(data)} 筆站點資料")
            return data
        if isinstance(data, dict):
            for key in ("result", "data", "records", "retVal"):
                if key in data and isinstance(data[key], list):
                    print(f"   ✓ 從 .{key} 收到 {len(data[key])} 筆")
                    return data[key]
        print(f"   ⚠ 資料格式不認得：{str(data)[:200]}")
        return None
    except Exception as e:
        print(f"   ⚠ 例外：{type(e).__name__}: {e}")
        return None


def fetch_youbike():
    """依序嘗試多個 URL 與多次重試"""
    for url in API_URLS:
        for attempt in range(1, 4):
            data = try_fetch(url, f"第 {attempt} 次")
            if data:
                return pick_stations(data)
            if attempt < 3:
                time.sleep(5)
    raise RuntimeError("所有資料來源都失敗")


def pick_stations(all_data):
    picked = {}
    for target in TARGET_STATIONS:
        hit = None
        for d in all_data:
            sna = (d.get("sna") or d.get("StationName") or "").replace("YouBike2.0_", "")
            if target in sna:
                hit = d
                break
        if hit:
            picked[target] = {
                "sna": hit.get("sna") or hit.get("StationName"),
                "sbi": int(hit.get("sbi") or hit.get("AvailableRentBikes") or 0),
                "bemp": int(hit.get("bemp") or hit.get("AvailableReturnBikes") or 0),
                "tot": int(hit.get("tot") or hit.get("TotalHoles") or 0),
                "mday": hit.get("mday") or hit.get("srcUpdateTime") or hit.get("UpdateTime"),
                "sarea": hit.get("sarea") or hit.get("AreaName"),
                "ar": hit.get("ar") or hit.get("Address"),
            }
        else:
            picked[target] = None
    return picked


def main():
    now = datetime.now(TPE)
    print(f"=== {now.strftime('%Y-%m-%d %H:%M:%S')} 開始抓取 ===")
    stations = fetch_youbike()
    payload = {
        "updated_at": now.isoformat(timespec="seconds"),
        "updated_at_display": now.strftime("%Y-%m-%d %H:%M:%S"),
        "stations": stations,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n[{now.strftime('%H:%M:%S')}] ✓ data.json 已寫入")
    for name, info in stations.items():
        if info:
            print(f"   {name}: 車 {info['sbi']} / 空 {info['bemp']} (總 {info['tot']})")
        else:
            print(f"   {name}: 找不到此站 ⚠")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 抓取失敗：{e}", file=sys.stderr)
        sys.exit(1)
