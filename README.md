# 量化分析研究專案

[![在 Colab 中開啟](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hsp1234-web/qlib/blob/main/Master_Workflow.ipynb)

這是一個使用 Python 進行量化金融分析的專案範本，其核心是提供一個在 Google Colab 環境中，可重複、標準化且易於使用的多儲存格工作流程。

## 快速開始

點擊上方的「在 Colab 中開啟」徽章，即可直接在 Google Colab 環境中啟動 `Master_Workflow.ipynb` 筆記本。請依照筆記本中的儲存格順序，逐一執行以完成完整的分析流程。

---

## 工作流程詳解 (`Master_Workflow.ipynb`)

筆記本內的每個儲存格都設計為一個獨立的步驟。以下是每個步驟的詳細說明：

### 儲存格 1: (可選) 掛載 Google Drive
*   **目的**: 建立 Colab 與您 Google Drive 的連接，以便**永久保存**您的分析成果。
*   **執行動作**:
    1. 觸發 Google 帳戶授權。
    2. 將您的 Google Drive 掛載至 Colab 的 `/content/drive/MyDrive` 路徑。
    3. 自動在您的雲端硬碟中，建立專案所需的資料夾結構 (`data/`, `results/` 等)。
*   **提示**: 如果您**跳過**此儲存格，整個工作流程將預設使用 Colab 的**本機暫存空間**。所有產出的資料和結果，將在您關閉 Colab 分頁後**自動刪除**。

### 儲存格 2: 從 GitHub 同步專案程式碼
*   **目的**: 從 GitHub 獲取最新版本的「執行邏輯」（Python 腳本）。
*   **執行動作**:
    1. **在 `GIT_BRANCH` 欄位中，手動填入您想要執行的開發分支名稱。** 這是整個流程中最關鍵的一步。
    2. 腳本會自動 `git clone` 或 `git checkout` 您指定的分支，並將其更新至最新版本。
*   **產出**: Colab 的 `/content/` 目錄下，會有一份與您指定的 GitHub 分-支完全同步的最新程式碼。

### 儲存格 3: 安裝專案所需的 Python 套件
*   **目的**: 確保 Colab 環境安裝了所有執行分析腳本所需要的 Python 套件。
*   **執行動作**: 讀取從 GitHub 下載的 `requirements.txt` 檔案，並使用 `pip` 自動安裝所有依賴項。

### 儲存格 4: 執行核心任務：下載數據與執行回測
*   **目的**: 執行主要的量化分析任務。
*   **執行動作**:
    1. 根據您在儲存格中設定的**股票代號**及**日期範圍**，執行 `src/data_loader.py` 從 `yfinance` 抓取歷史資料。
    2. 接著執行 `src/run_analysis.py`，讀取剛才下載的資料，並執行一個移動平均線交叉策略的回測。
*   **產出**:
    *   一份 `.csv` 格式的原始數據檔案，儲存在 `data/` 資料夾中。
    *   一份 `.json` 格式的回測結果檔案，儲存在 `results/` 資料夾中。

### 儲存格 5: 啟動 Streamlit 視覺化儀表板
*   **目的**: 將上一步產出的分析結果進行視覺化，以便互動式分析。
*   **執行動作**:
    1. 在背景啟動 `src/dashboard.py` Streamlit 服務。
    2. 使用 `ngrok` 建立一個安全的公開通道，將 Colab 內部的服務暴露出來。
*   **產出**: 一個公開的 `ngrok.io` 網址。點擊此網址，即可在新分頁中看到您的互動式量化分析儀表板。

### 儲存格 6: (可選) 同步本地成果至 Google Drive
*   **目的**: 如果您在未掛載雲端的情況下執行了分析，此步驟可以讓您事後將儲存在 Colab 本機的成果，完整同步回您的 Google Drive。
*   **執行動作**: 觸發 Google Drive 掛載（如果尚未掛載），並將本機的專案資料夾內容，完整複製到您在雲端硬碟上指定的專案目錄中。

---

## 專案結構

```
.
├── Master_Workflow.ipynb   # 主要的 Colab 工作流程筆記本
├── README.md               # 專案說明文件
├── requirements.txt        # Python 依賴套件列表
├── src/                    # 核心 Python 原始碼
│   ├── data_loader.py      # 資料下載模組
│   ├── run_analysis.py     # 回測分析模組
│   └── dashboard.py        # Streamlit 儀表板模組
└── history/                # 存放過往的參考設計
    └── colab_star          # 一個複雜的單體式 Colab 啟動器參考範例
```
