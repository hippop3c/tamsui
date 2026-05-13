# 淡水・八里 YouBike 整點監測

每個整點自動抓取以下四個 YouBike 站點的車輛數與空位數：

- 輕軌漁人碼頭
- 橋管中心
- 淡水轉運站
- 八里文化公園

## 架構

- **`fetch.py`**：Python 程式，抓新北市開放資料 API，把結果寫進 `data.json`
- **`.github/workflows/hourly.yml`**：GitHub Actions 排程，每個整點自動執行 `fetch.py` 並把更新的 `data.json` commit 回 repo
- **`index.html`**：靜態網頁，從 `data.json` 讀資料並顯示

## 啟用步驟

1. **啟用 GitHub Pages**：Settings → Pages → Source 選 `main` / `(root)` → Save
2. **啟用 GitHub Actions**：Settings → Actions → General → 確認允許 Actions 執行
3. 等第一個整點到了，Actions 會自動跑；想立刻測試可到 Actions 頁手動觸發 `Hourly YouBike fetch`
4. 同事打開：`https://你的帳號.github.io/這個repo名稱/`

## 資料來源

[新北市公共自行車租賃系統 (YouBike2.0)](https://data.ntpc.gov.tw/datasets/71cd1490-a2df-4198-bef1-318479775e8a)
