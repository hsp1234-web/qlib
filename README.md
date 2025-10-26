# 量化分析研究專案

[![在 Colab 中開啟](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hsp1234-web/qlib/blob/main/Master_Workflow.ipynb)

這是一個使用 Python 進行量化金融分析的專案範本。

## 快速開始

點擊上方的「在 Colab 中開啟」徽章，即可直接在 Google Colab 環境中啟動完整的分析工作流程。

### 工作流程筆記本 (`Master_Workflow.ipynb`)

筆記本 (`Master_Workflow.ipynb`) 提供了以下標準化的執行步驟：

1.  **(可選) 掛載 Google Drive**：您可以選擇性地掛載您的 Google Drive，以便將分析結果永久保存。如果跳過此步，所有資料將儲存在 Colab 的暫存空間中。
2.  **同步 GitHub 程式碼**：在此步驟中，您需要**手動輸入**想要執行的**分支名稱**。筆記本將會自動從 GitHub 下載或更新您指定分支的最新程式碼。
3.  **安裝 Python 環境**：自動安裝所有必要的 Python 函式庫。
4.  **執行核心分析**：執行資料下載與策略回測等核心任務。
5.  **啟動視覺化儀表板**：啟動一個 Streamlit 儀表板，讓您可以互動式地查看分析結果。
6.  **(可選) 同步成果**：如果您在未掛載雲端的情況下執行了分析，此步驟可以讓您將產出的成果同步回 Google Drive。

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
