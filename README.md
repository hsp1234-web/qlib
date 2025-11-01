# Colab 量化分析工作流專案

[![在 Colab 中開啟](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hsp1234-web/qlib/blob/main/Master_Workflow.ipynb)

這是一個標準化的量化分析工作流程，專為在 Google Colab 中執行而設計。點擊上方的「在 Colab 中開啟」按鈕，即可一鍵啟動完整的分析筆記本。

## 核心設計

本專案遵循「關注點分離」的原則，將不同職責的元件清晰地劃分開來：

- **GitHub (程式碼儲存庫)**：儲存所有專案的「程式碼」檔案，包含 Python 腳本和 Colab 筆記本。
- **Google Drive (資料儲存庫)**：儲存所有「非程式碼」的資料檔案，例如原始數據、訓練好的模型和執行結果。
- **Colab (執行環境)**：作為一個無狀態的計算工廠，負責依照順序執行任務。

## 工作流程

Colab 筆記本 (`Master_Workflow.ipynb`) 將整個分析流程拆分為多個獨立的儲存格，以便於分段執行、控制和除錯：

1.  **掛載 Google Drive**：建立 Colab 與 Google Drive 之間的連接（可選）。
2.  **同步 GitHub 程式碼**：從指定的 GitHub 分支下載最新的執行邏輯。
3.  **安裝環境**：根據 `requirements.txt` 安裝所有必要的 Python 函式庫。
4.  **執行核心任務**：執行數據下載、回測分析等核心任務。
5.  **啟動儀表板**：使用 Streamlit 將分析結果視覺化。
6.  **同步成果 (可選)**：如果一開始未掛載 Google Drive，可以事後將儲存在本機的成果同步回雲端。

## 使用方法

1.  點擊本文件最上方的「在 Colab 中開啟」按鈕。
2.  在打開的 Colab 筆記本中，依照儲存格的順序，逐一執行即可。
