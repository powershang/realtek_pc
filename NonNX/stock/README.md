# Taiwan Value Strategy Backtest

台股估值策略回測系統，基於 PE × 下一財年 EPS + (金融股 P/B 交叉) 的選股邏輯。

## 安裝與設定

### 1. 安裝依賴套件

```bash
pip install yfinance==0.2.18 pandas==2.0.3 numpy==1.24.3 matplotlib==3.7.1 seaborn==0.12.2 pyyaml==6.0 twstock==1.3.1
```

### 2. 執行腳本

```bash
# 使用預設參數執行
python taiwan_value_strategy.py

# 自定義參數執行
python taiwan_value_strategy.py --start 2014-01-01 --end 2025-07-10 --cash 1000000

# 使用自定義配置檔
python taiwan_value_strategy.py --config my_config.yml
```

## 資料設定

### 更新 EPS CSV 檔案

腳本會自動生成範例 `eps_forecast.csv` 檔案，格式如下：

```csv
date,ticker,eps_next_fy,bvps_now
2014-06-30,2330,15.2,51.3
2014-06-30,2884,2.4,17.8
...
```

#### 真實使用時的資料更新步驟：

1. **從 TEJ API 取得資料**：
```python
# 範例：從 TEJ API 更新 EPS 預估
import tejapi
tejapi.ApiConfig.api_key = "your_api_key"
eps_data = tejapi.get('your_database', 
                     coid=['2330', '2884', ...], 
                     mdate={'gte': '2014-01-01'})
```

2. **從 Bloomberg API 取得資料**：
```python
# 範例：從 Bloomberg API 更新
from xbbg import blp
eps_data = blp.bdp(['2330 TT Equity', '2884 TT Equity'], 
                   ['BEST_EPS_GAAP', 'BOOK_VAL_PER_SH'])
```

3. **手動更新 CSV**：
   - 定期更新 `eps_forecast.csv` 中的 `eps_next_fy` (下一財年EPS預估)
   - 更新 `bvps_now` (當前每股淨值)
   - 確保日期格式為 `YYYY-MM-DD`

### 自定義 PE/PB 估值區間

#### 方法一：直接修改腳本中的估值帶

```python
# 修改 taiwan_value_strategy.py 中的估值區間
PE_BANDS = {
    "2330": (18, 25),      # 台積電 PE 區間調整為 18-25
    "3034": (12, 18),      # 聯詠 PE 區間調整為 12-18
    "2884": (13, 19),      # 玉山金 PE 區間調整為 13-19
    # ... 其他股票
}

PB_BANDS = {  # 僅對金融股生效
    "2884": (1.4, 2.0),    # 玉山金 PB 區間調整為 1.4-2.0
    "2886": (1.2, 1.8),    # 兆豐金 PB 區間調整為 1.2-1.8
    # ... 其他金融股
}
```

#### 方法二：使用 YAML 配置檔

創建或修改 `config.yml` 檔案：

```yaml
tickers: ['2330', '2884', '2886', '2891', '2892', '3034', '5871']
benchmark: '^TWII'
start_date: '2014-01-01'
end_date: '2025-07-10'
initial_cash: 1000000
rebalance_month: 7
rebalance_day: 1
buy_threshold: 0.9
sell_threshold: 1.1

pe_bands:
  '2330': [18, 25]
  '3034': [12, 18]
  '2884': [13, 19]
  '2886': [12, 18]
  '2891': [12, 18]
  '2892': [12, 18]
  '5871': [9, 15]

pb_bands:
  '2884': [1.4, 2.0]
  '2886': [1.2, 1.8]
  '2891': [1.2, 1.8]
  '2892': [1.2, 1.8]
```

## 策略邏輯

### 估值計算

1. **合理價下緣** = max(PE_lower × EPS_next_fy, PB_lower × BVPS_now)
2. **合理價上緣** = max(PE_upper × EPS_next_fy, PB_upper × BVPS_now)

### 交易訊號

- **買進**：當日收盤價 ≤ 合理價下緣 × 0.9
- **賣出**：當日收盤價 ≥ 合理價上緣 × 1.1
- **續抱**：價格在合理價區間內

### 重平衡機制

- **頻率**：每年 7 月第 1 個交易日
- **配置**：等權重分配符合買進條件的股票
- **持有期**：12 個月（至次年 6 月最後交易日）

## 輸出檔案

執行完成後會產生以下檔案：

1. **performance_chart.png** - 策略與基準指數績效比較圖
2. **allocation_chart.png** - 歷年資產配置圖
3. **trades.csv** - 詳細交易紀錄
4. **performance_summary.txt** - 績效指標摘要
5. **config.yml** - 配置檔案（若不存在會自動建立）
6. **eps_forecast.csv** - EPS 預估資料（若不存在會自動建立範例）

## 績效指標

- **年化報酬率 (CAGR)**：複合年均成長率
- **最大回撤 (Max Drawdown)**：最大虧損幅度
- **年化波動度 (Volatility)**：報酬率標準差年化
- **夏普比率 (Sharpe Ratio)**：風險調整後報酬
- **勝率 (Win Rate)**：正報酬交易日佔比

## 資料來源備註

- **股價資料**：主要使用 yfinance，台股代碼需加 .TW 後綴
- **基準指數**：台灣加權指數 (^TWII)
- **基本面資料**：需自行提供 eps_forecast.csv，建議從 TEJ/Bloomberg 取得

## 使用範例

```python
# 載入自定義配置並執行回測
from taiwan_value_strategy import TaiwanValueStrategy, load_config

# 載入配置
config = load_config('my_config.yml')

# 初始化策略
strategy = TaiwanValueStrategy(config)

# 執行回測
strategy.fetch_data()
strategy.load_fundamentals()
strategy.backtest()

# 分析績效
metrics = strategy.analyze_performance()
```

## 注意事項

1. **資料品質**：確保 EPS 預估資料的準確性和及時性
2. **估值區間**：建議根據產業特性和歷史估值調整 PE/PB 區間
3. **交易成本**：實際交易請考慮手續費和滑價成本
4. **流動性**：確保標的股票有足夠的流動性支援策略執行
5. **風險管理**：建議加入停損機制和最大權重限制

## 技術支援

如遇資料取得問題，可考慮以下替代方案：

1. **twstock 套件**：適用於台股歷史資料
2. **台灣證交所 API**：官方資料來源
3. **三竹資訊 API**：即時與歷史資料
4. **自建資料爬蟲**：定期更新股價和基本面資料 