# Colab 量化分析工作流專案

[![在 Colab 中開啟](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hsp1234-web/qlib/blob/8.1/Master_Workflow.ipynb)

這是一個標準化的量化分析工作流程，專為在 Google Colab 中執行而設計。點擊上方的「在 Colab 中開啟」按鈕，即可一鍵啟動完整的分析筆記本。

## 核心設計

本專案遵循「關注點分離」的原則，將不同職責的元件清晰地劃分開來：

- **GitHub (程式碼儲存庫)**：儲存所有專案的「程式碼」檔案，包含 Python 腳本和 Colab 筆記本。
- **Colab (執行環境)**：作為一個無狀態的計算工廠，負責依照順序執行任務。

## 工作流程 (`Master_Workflow.ipynb`)

Colab 筆記本將整個分析流程拆分為多個獨立的儲存格，以便於分段執行、控制和除錯：

1.  **同步 GitHub 程式碼**：從指定的 GitHub 分支下載最新的執行邏輯。
2.  **安裝環境**：根據 `requirements.txt` 智慧安裝所有必要的 Python 函式庫。
3.  **執行回測 (指令列模式)**：透過填寫表單，以傳統的指令列方式執行 `backtest_runner.py` 腳本。
4.  **(新功能) 啟動互動式儀表板 (Gradio)**：啟動一個網頁圖形化介面 (GUI)，讓您可以更直觀地設定參數並執行回測。

## 使用方法

1.  點擊本文件最上方的「在 Colab 中開啟」按鈕，即可在 Google Colab 環境中開啟主工作流程筆記本。
2.  在打開的 Colab 筆記本 (`Master_Workflow.ipynb`) 中，依照儲存格的順序（由 1 至 4），逐一執行：

    -   **儲存格 1 - 同步 GitHub 專案程式碼**:
        -   **作用**: 將最新的程式碼從 GitHub 下載到 Colab 環境中。
        -   **操作**: 您可以修改預設的 GitHub 儲存庫 URL 和分支名稱，然後執行此儲存格。

    -   **儲存格 2 - 智慧安裝 Python 套件**:
        -   **作用**: 檢查 `requirements.txt` 檔案，並自動安裝所有必要的 Python 函式庫。此過程使用 `uv` 以提升安裝速度。
        -   **操作**: 直接執行此儲存格即可。

    -   **儲存格 3 - 執行回測 (指令列模式)**:
        -   **作用**: 提供一個簡單的表單，讓您能以傳統的指令列方式執行一次快速的回測。
        -   **操作**: 在表單中填寫您想回測的股票代碼、起訖日期和策略，然後執行儲存格。

    -   **儲存格 4 - 啟動互動式回測設定儀表板**:
        -   **作用**: 啟動一個基於 Gradio 的網頁圖形化介面 (GUI)，提供更豐富、更直觀的回測設定與操作體驗。
        -   **操作**: 執行此儲存格後，會在輸出區看到一個公開的 `.gradio.live` 網址。點擊該網址，即可在新分頁中開啟互動式儀表板。

## 檔案架構

```
.
├── Master_Workflow.ipynb       # 主要的 Google Colab 工作流程筆記本，為專案的進入點。
├── README.md                   # 專案說明文件 (您正在閱讀的檔案)。
├── requirements.txt            # 定義了專案所需的 Python 相依套件。
├── log.md                      # 記錄專案開發過程中的重要決策與問題解決方案。
│
├── lo2cin4bt/                  # 核心的回測引擎函式庫。
│   ├── __init__.py
│   ├── app.py                  # Gradio 互動式儀表板的應用程式碼。
│   ├── autorunner/             # 自動化回測模組，用於批次執行。
│   ├── backtester/             # 核心回測引擎模組。
│   ├── dataloader/             # 數據載入與前處理模組。
│   ├── metricstracker/         # 績效指標計算與追蹤模組。
│   ├── plotter/                # 可視化模組，用於繪製圖表。
│   └── statanalyser/           # 統計分析模組。
│
└── src/                        # 存放非核心函式庫的原始碼。
    └── backtest_runner.py      # 指令列模式的回測執行腳本。
```
