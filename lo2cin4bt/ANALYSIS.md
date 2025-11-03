# lo2cin4bt 專案結構與功能分析報告

## 1. 專案概觀

`lo2cin4bt` 是一個專為量化新手與非程式背景交易員設計的 Python 回測框架。其核心設計理念是「無需編寫程式碼」，透過豐富的命令列互動介面 (CLI) 和大量的中文提示，引導使用者完成從數據載入、統計分析、策略回測到結果可視化的完整量化研究流程。

### 核心架構

專案採用了高內聚、低耦合的模組化設計，將不同的功能拆分到獨立的目錄中，各模組職責清晰，易於維護與擴充。

- **主入口 (`main.py`)**: 整個框架的 CLI 介面，提供多種工作流程選項。
- **數據載入 (`dataloader`)**: 負責從多種來源（本地檔案、API）獲取數據並進行標準化。
- **回測引擎 (`backtester`)**: 框架的核心，負責協調回測流程、產生交易訊號、模擬交易並記錄結果。
- **統計分析 (`statanalyser`)**: 提供一系列工具，用於分析預測因子的有效性。
- **績效追蹤 (`metricstracker`)**: 讀取回測結果，計算詳細的績效指標。
- **可視化 (`plotter`)**: 使用 Dash 建立一個互動式的網頁儀表板，展示回測結果。
- **自動化 (`autorunner`)**: 支援透過 JSON 設定檔進行非互動式的批次自動回測。
- **數據記錄 (`records`)**: 存放輸入的數據、設定檔以及輸出的回測結果。

### `lo2cin4bt` 目錄結構樹狀圖

```
lo2cin4bt
├── LICENSE
├── README.md
├── __init__.py
├── assets
│   └── style.css
├── autorunner
│   ├── BacktestRunner_autorunner.py
│   ├── Base_autorunner.py
│   ├── ConfigLoader_autorunner.py
│   ├── ConfigSelector_autorunner.py
│   ├── ConfigValidator_autorunner.py
│   ├── DataLoader_autorunner.py
│   ├── MetricsRunner_autorunner.py
│   ├── README.md
│   └── SwitchDataSource_autorunner.py
├── backtester
│   ├── Base_backtester.py
│   ├── BollingerBand_Indicator_backtester.py
│   ├── DataImporter_backtester.py
│   ├── HL_Indicator_backtester.py
│   ├── IndicatorParams_backtester.py
│   ├── Indicators_backtester.py
│   ├── MovingAverage_Indicator_backtester.py
│   ├── Percentile_Indicator_backtester.py
│   ├── README.md
│   ├── SpecMonitor_backtester.py
│   ├── TradeRecordExporter_backtester.py
│   ├── TradeRecorder_backtester.py
│   ├── TradeSimulator_backtester.py
│   ├── VALUE_Indicator_backtester.py
│   ├── VectorBacktestEngine_backtester.py
│   └── __init__.py
├── dataloader
│   ├── README.md
│   ├── __init__.py
│   ├── base_loader.py
│   ├── binance_loader.py
│   ├── calculator_loader.py
│   ├── coinbase_loader.py
│   ├── data_exporter_loader.py
│   ├── file_loader.py
│   ├── predictor_loader.py
│   ├── validator_loader.py
│   └── yfinance_loader.py
├── images
│   ├── lo2cin4logo.png
│   └── template_1.jpg
├── main.py
├── metricstracker
│   ├── Base_metricstracker.py
│   ├── DataImporter_metricstracker.py
│   ├── MetricsCalculator_metricstracker.py
│   ├── MetricsExporter_metricstracker.py
│   ├── README.md
│   └── __init__.py
├── plotter
│   ├── Base_plotter.py
│   ├── CallbackHandler_plotter.py
│   ├── ChartComponents_plotter.py
│   ├── DashboardGenerator_plotter.py
│   ├── DataImporter_plotter.py
│   ├── MetricsDisplay_plotter.py
│   ├── ParameterPlateau_plotter.py
│   ├── README.md
│   ├── __init__.py
│   └── utils
│       ├── ParameterParser_utils_plotter.py
│       └── __init__.py
├── pytest.ini
├── records
│   ├── Read_parquet.py
│   ├── autorunner
│   │   ├── config_template.json
│   │   ├── config_template_5mdata.json
│   │   ├── config_template_defaultall.json
│   │   ├── config_template_single.json
│   │   └── config_template_single_timestamp.json
│   └── dataloader
│       └── import
│           └── predictor_example.xlsx
├── requirements.txt
├── setup.cfg
├── statanalyser
│   ├── AutocorrelationTest_statanalyser.py
│   ├── Base_statanalyser.py
│   ├── CorrelationTest_statanalyser.py
│   ├── DistributionTest_statanalyser.py
│   ├── README.md
│   ├── ReportGenerator_statanalyser.py
│   ├── SeasonalAnalysis_statanalyser.py
│   ├── StationarityTest_statanalyser.py
│   └── __init__.py
└── tests
    └── __init__.py
```

## 2. 五大核心功能 (由 `main.py` 提供)

當執行 `python main.py` 時，使用者可以從主選單中選擇以下五種工作流程：

1.  **全面回測 (選項 1)**
    *   **流程**: 載入數據 → 統計分析 → 回測交易 → 交易分析 → 可視化平台
    *   **用途**: 適用於最完整的研究流程，當你擁有一個新的預測因子時，可以先透過統計分析檢驗其有效性，再進行回測。

2.  **回測交易 (選項 2)**
    *   **流程**: 載入數據 → 回測交易 → 交易分析 → 可視化平台
    *   **用途**: 跳過統計分析，直接進行策略回測。適用於測試純技術指標策略，或者你對預測因子的有效性已有信心。

3.  **交易分析 (選項 3)**
    *   **流程**: 交易分析 → 可視化平台
    *   **用途**: 如果你已經執行過回測並產生了交易記錄檔案 (`.parquet` 格式)，這個選項可以讓你直接讀取這些記錄，重新計算績效指標並啟動可視化平台。

4.  **可視化平台 (選項 4)**
    *   **流程**: 僅啟動可視化平台
    *   **用途**: 直接讀取最近一次的交易分析結果，並啟動 Dash 網頁儀表板進行互動式分析。

5.  **自動化回測 (選項 5)**
    *   **流程**: 讀取設定檔 → 全自動執行回測
    *   **用途**: 適用於批次執行大量的回測任務。使用者可以預先在 `records/autorunner/` 目錄下準備好 `config.json` 設定檔，系統會自動完成所有回測流程，無需手動輸入參數。

## 3. 回測功能深度解析 (Step-by-Step 使用指南)

「回測交易」是整個框架最核心的功能。這個過程由 `backtester/Base_backtester.py` 模組透過一個互動式的問答流程來協調完成。以下是詳細的步驟拆解：

---

### **步驟 1: 選擇預測因子**

*   **目的**: 告訴回測引擎，要用哪個數據欄位來計算技術指標並產生交易訊號。
*   **選項**: 系統會列出數據中所有可用的欄位 (除了 `Time`, `High`, `Low`)。你可以選擇：
    *   **價格欄位**: `Open` 或 `Close` (適用於傳統技術分析)。
    *   **收益率欄位**: `open_return`, `close_return` 等 (通常用於統計套利策略)。
    *   **自訂因子欄位**: 如果你在數據載入階段合併了外部預測因子 (例如情緒指標、宏觀數據)，這裡就可以選擇它們。
    *   **差分後因子**: 如果你在數據載入階段對因子進行了差分處理，這裡會出現如 `factor_diff_sub` 的欄位。

---

### **步驟 2: 選擇開倉與平倉指標**

*   **目的**: 設定策略的進出場邏輯。
*   **操作**:
    1.  **輸入開倉條件**: 輸入一個或多個指標代碼，用逗號 `,` 分隔。如果輸入多個，代表需要**所有條件同時滿足**才會開倉 (AND 邏輯)。
    2.  **輸入平倉條件**: 輸入一個或多個指標代碼，規則同上。
*   **快速上手 (預設策略)**:
    *   如果你不確定如何選擇，可以在開倉和平倉條件**同時**輸入 `defaultlong` (預設多頭策略)、`defaultshort` (預設空頭策略) 或 `defaultall` (兩者皆有)。系統會自動為你建立一組經過驗證的策略組合。
*   **多策略回測**:
    *   設定完一組開/平倉條件後，系統會詢問是否繼續設定下一組。你可以重複這個步驟，一次執行多組不同的策略進行比較。

---

### **步驟 3: 輸入指標參數**

*   **目的**: 為上一步選擇的每一個指標設定具體的計算參數。
*   **格式**:
    *   **單一數值**: 直接輸入一個數字，例如 `20`。
    *   **參數範圍 (用於枚舉測試)**: 使用 `開始值:結束值:間隔` 的格式，例如 `10:200:20`，代表從 10 到 200，每隔 20 取一個值 (10, 30, 50, ..., 190)。
*   **系統會針對你設定的每一個策略，逐一詢問其中包含的所有指標的參數。**

---

### **步驟 4: 輸入回測環境參數**

*   **目的**: 模擬真實的交易環境，讓回測結果更貼近現實。
*   **參數**:
    *   **交易手續費 (`transaction_cost`)**: 小數形式，例如 `0.001` 代表 0.1%。
    *   **滑價 (`slippage`)**: 買賣價差造成的成本，格式同上。
    *   **交易延遲 (`trade_delay`)**: 訊號出現後，隔幾根 K 棒才執行交易。預設為 `1`，代表在下一根 K 棒的開盤價成交 (這是最常見且較合理的設定)。
    *   **交易價格 (`trade_price`)**: 選擇以 `open` (開盤價) 還是 `close` (收盤價) 來執行交易。

---

### **技術指標完整清單**

| 指標家族 | 代碼 | 描述 |
| :--- | :--- | :--- |
| **移動平均線 (MA)** | `MA1` | 價格升穿均線 (做多) |
| | `MA2` | 價格跌穿均線 (做多平倉) |
| | `MA3` | 價格升穿均線 (做空平倉) |
| | `MA4` | 價格跌穿均線 (做空) |
| | `MA5` | 短均線升穿長均線 (黃金交叉, 做多) |
| | `MA6` | 短均線跌穿長均線 (死亡交叉, 做多平倉) |
| | `MA7` | 短均線升穿長均線 (黃金交叉, 做空平倉) |
| | `MA8` | 短均線跌穿長均線 (死亡交叉, 做空) |
| | `MA9` | 連續 M 次價格高於 N 周期均線 (做多) |
| | `MA10`| 連續 M 次價格低於 N 周期均線 (做多平倉) |
| | `MA11`| 連續 M 次價格高於 N 周期均線 (做空平倉) |
| | `MA12`| 連續 M 次價格低於 N 周期均線 (做空) |
| **布林通道 (BOLL)** | `BOLL1` | 價格升穿上軌 (突破, 做多) |
| | `BOLL2` | 價格升穿中軌 (做多平倉/做空平倉) |
| | `BOLL3` | 價格跌穿中軌 (做多平倉/做空平倉) |
| | `BOLL4` | 價格跌穿下軌 (突破, 做空) |
| **高低點 (HL)** | `HL1` | 連續 N 次創 M 周期新高 (做多) |
| | `HL2` | 價格跌穿前 M 周期低點 (做多平倉) |
| | `HL3` | 價格升穿前 M 周期高點 (做空平倉) |
| | `HL4` | 連續 N 次創 M 周期新低 (做空) |
| **百分位 (PERC)** | `PERC1` | 價格高於過去 N 期的 M 百分位 (做多) |
| | `PERC2` | 價格高於過去 N 期的 M 百分位 (做空平倉) |
| | `PERC3` | 價格低於過去 N 期的 M 百分位 (做多平倉) |
| | `PERC4` | 價格低於過去 N 期的 M 百分位 (做空) |
| | `PERC5` | 價格介於 M1 和 M2 百分位之間 (區間, 做多) |
| | `PERC6` | 價格不介於 M1 和 M2 百分位之間 (區間, 做空) |
| **數值比較 (VALUE)** | `VALUE1` | 因子數值 > M (做多) |
| | `VALUE2` | 因子數值 < M (做多平倉) |
| | `VALUE3` | 因子數值 > M (做空平倉) |
| | `VALUE4` | 因子數值 < M (做空) |
| | `VALUE5` | 因子數值介於 M1 和 M2 之間 (區間, 做多) |
| | `VALUE6` | 因子數值不介於 M1 和 M2 之間 (區間, 做空) |
| **N日週期** | `NDAY1` | 開倉 N 日後平倉 (適用於多頭) |
| | `NDAY2` | 開倉 N 日後平倉 (適用於空頭) |

## 4. 數據與檔案流

專案透過 `records/` 目錄來管理所有非程式碼的資產。

*   **輸入 - 預測因子**:
    *   **位置**: `records/dataloader/import/`
    *   **格式**: `xlsx`, `csv`
    *   **說明**: 如果你需要使用外部數據作為預測因子，請將檔案放在此處。`dataloader` 模組會自動掃描這個目錄。

*   **輸出 - 回測結果**:
    *   **位置**: `records/backtester/`
    *   **格式**: `.parquet`
    *   **說明**: 每次回測都會產生一個以時間戳和唯一 ID 命名的 `.parquet` 檔案，包含了詳細的逐筆交易紀錄。

*   **輸出 - 績效分析結果**:
    *   **位置**: `records/metricstracker/`
    *   **格式**: `.parquet`
    *   **說明**: `metricstracker` 模組會讀取 `backtester` 的產出，計算更詳細的績效指標後，再儲存成新的 `.parquet` 檔，供可視化平台使用。

*   **輸出 - 統計分析報告**:
    *   **位置**: `records/statanalyser/`
    *   **格式**: `stats_report.txt`, `processed_data.csv`
    *   **說明**: 如果執行了完整的統計分析流程，相關的報告和處理後的數據會儲存在這裡。

## 5. 附录：Dash 仪表板前端开发与测试

本次任务旨在为 `lo2cin4bt` 框架新增一个简单的前端界面，允许使用者透过网页 UI 互动地设定回测参数，并触发 `autorunner` 执行回测。

### 5.1 测试驱动开发 (TDD) 过程

本次开发严格遵循 TDD "红-绿-重构" (Red-Green-Refactor) 的循环原则：

1.  **Red (红灯)**: 先为尚未实现的功能编写一个**失败的测试**。
2.  **Green (绿灯)**: 编写**最少量**的产品代码，刚好能让测试通过。
3.  **Refactor (重构)**: 在测试保护下，改善产品代码的设计和品质。

这个过程依序应用在以下功能的开发中：
*   **核心功能 `generate_config`**: 首先编写测试，断言该函数能根据输入的 ticker 和日期，正确地更新设定档范本。然后才实现该函数。
*   **UI 回调 `update_config_display`**: 编写测试，模拟 Dash 回调的输入 (如 `ticker="MSFT"`)，并断言其输出的 JSON 字串符合预期。然后实现回调函数。
*   **执行功能 `execute_backtest`**: 编写测试，使用 `@patch` 来模拟 (`mock`) `BaseAutorunner`，断言当 "执行" 按钮被点击时，`autorunner.run` 方法有被正确地以生成的 `config` 参数呼叫。

所有这些单元测试都被整合在 `lo2cin4bt/tests/test_app.py` 中，确保了核心逻辑和 UI 互动在程式码层面上的正确性。

### 5.2 最终测试结果

经过完整的开发与侦错，最终所有测试都成功通过，证明了前端功能的稳定与正确性。

```
$ pytest
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-7.4.0, pluggy-1.6.0
rootdir: /app
plugins: base-url-2.1.0, cov-7.0.0, playwright-0.7.1, timeout-2.4.0, dash-3.2.0
collected 6 items

lo2cin4bt/tests/test_app.py ......                                       [100%]

============================== 6 passed in 2.96s ===============================
```

### 5.3 技术决策：从 Selenium 迁移到 Playwright

在开发端对端 (End-to-End) 测试的过程中，最初选择了 `dash.testing` 框架搭配 `Selenium` 的技术栈。然而，这个组合在实际应用中暴露出严重的**脆弱性**和**高复杂性**，导致了大量的时间被耗费在解决工具链本身的问题上，而非测试应用逻辑。

遇到的主要问题包括：
1.  **相依性地狱 (Dependency Hell)**: `pytest-dash`、`dash[testing]`、`selenium`、`pytest` 等多个套件之间存在复杂的版本相依关系。任何一个套件的更新都可能破坏整个测试环境。
2.  **插件冲突**: `pytest-dash` 和 `dash` 套件内建的测试插件都试图定义 `--webdriver` 命令列参数，导致 `pytest` 无法启动。
3.  **环境管理困难**: 需要手动在测试环境中安装特定版本的 Chrome 浏览器，并处理 `webdriver` 的路径问题，非常繁琐。
4.  **竞态条件 (Race Condition)**: 测试启动时，`selenium` 经常在 Dash 伺服器完全就绪前就尝试连接，导致 `TimeoutException` 或 `ConnectionRefused` 错误。

鉴于以上问题，我们决定采纳社群的最佳实践，将 E2E 测试框架**迁移到 Playwright**。Playwright 的优势从根本上解决了上述所有痛点：

*   **高度整合**: Playwright 自我包含，会自动下载、管理并使用与函式库版本匹配的、经过修补的浏览器 (Chromium, Firefox, WebKit)，彻底消除了版本冲突和环境管理的问题。
*   **稳定性**: 其 `pytest-playwright` 插件设计优良，内建的 `page.goto()` 和 `expect()` 等 API 拥有强大的自动等待机制，极大地减少了因时序问题导致的测试不稳定 (flakiness)。
*   **开发效率**: API 更现代、更简洁，让我们能用更少的程式码编写更可靠的测试，专注于业务逻辑验证。

最终，我们透过编写一个手动的、在背景执行绪中启动 Dash 伺服器的 `pytest fixture`，将 Playwright 与 Dash 应用成功整合，实现了稳定、高效的端对端测试。

### 5.4 最终 E2E 测试代码范例

以下是最终使用 `Playwright` 实现的端对端测试，它清晰地展示了其简洁与强大的特性：

```python
# lo2cin4bt/tests/test_app.py (部分)
import pytest
from playwright.sync_api import Page, expect
from threading import Thread
import time
import requests

@pytest.fixture(scope="function")
def dash_server():
    """手動啟動 Dash 伺服器的 fixture。"""
    host = "127.0.0.1"
    port = 8051

    def run_server():
        from waitress import serve
        serve(app.server, host=host, port=port)

    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # 等待伺服器就緒
    url = f"http://{host}:{port}"
    start_time = time.time()
    while time.time() - start_time < 10:
        try:
            requests.get(url, timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.1)

    yield url

def test_full_app_flow(dash_server, page: Page):
    """
    使用 Playwright 和手動伺服器執行緒，測試完整的 UI 互動流程。
    """
    # 1. 導航到 App
    page.goto(dash_server)

    # 2. 找到 UI 元件
    ticker_input = page.locator("#ticker-input")
    config_display = page.locator("#config-display")
    h1_element = page.locator("h1")

    # 3. 驗證初始狀態
    expect(h1_element).to_have_text("lo2cin4bt 回測設定編輯器")
    expect(ticker_input).to_have_value("^GSPC")

    # 4. 模擬使用者輸入
    ticker_input.fill("GOOG")

    # 5. 驗證 UI 反應
    expect(config_display).to_contain_text('"symbol": "GOOG"')

    config_text = config_display.inner_text()
    config = json.loads(config_text)
    assert config["dataloader"]["yfinance_config"]["symbol"] == "GOOG"
```
