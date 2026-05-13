"""
淡水・八里 YouBike 整點抓取
由 GitHub Actions 每個整點自動執行，把結果寫到 data.json
"""
import requests
import json
from datetime import datetime, timezone, timedelta

TARGET_STATIONS = [
    "輕軌漁人碼頭",
    "橋管中心",
    "淡水轉運站",
    "八里文化公園",
]

API_URL = "https://data.ntpc.gov.tw/api/datasets/71CD1490-A2DF-4198-BEF1-318479775E8A/json/?size=10000"
TPE = timezone(timedelta(hours=8))


def fetch_youbike():
    r = requests.get(API_URL, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (github-actions youbike monitor)"
    })
    r.raise_for_status()
    all_data = r.json()

    picked = {}
    for target in TARGET_STATIONS:
        hit = None
        for d in all_data:
            sna = (d.get("sna") or "").replace("YouBike2.0_", "")
            if target in sna:
                hit = d
                break
        if hit:
            picked[target] = {
                "sna": hit.get("sna"),
                "sbi": int(hit.get("sbi", 0)),
                "bemp": int(hit.get("bemp", 0)),
                "tot": int(hit.get("tot", 0)),
                "mday": hit.get("mday") or hit.get("srcUpdateTime"),
                "sarea": hit.get("sarea"),
                "ar": hit.get("ar"),
            }
        else:
            picked[target] = None
    return picked


def main():
    now = datetime.now(TPE)
    stations = fetch_youbike()
    payload = {
        "updated_at": now.isoformat(timespec="seconds"),
        "updated_at_display": now.strftime("%Y-%m-%d %H:%M:%S"),
        "stations": stations,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[{now.strftime('%H:%M:%S')}] data.json 已更新")
    for name, info in stations.items():
        if info:
            print(f"   {name}: 車 {info['sbi']} / 空 {info['bemp']} (總 {info['tot']})")
        else:
            print(f"   {name}: 找不到此站 ⚠")


if __name__ == "__main__":
    main()
