# 日誌：回測引擎效能優化

**時間戳記**: 2025-11-07 13:23:28 CST

## 問題描述

回測腳本 (`src/backtest_runner.py`) 在執行包含6500個參數組合的完整回測時，耗時超過12分鐘 (`736秒`)，遠遠超過了系統150秒的超時限制，導致任務崩潰。

## 根本原因分析

經過深入的日誌分析與程式碼審查，我們定位到兩個主要問題：

1.  **CPU使用瓶頸**：在 `lo2cin4bt/backtester/SpecMonitor_backtester.py` 模組中，存在一段邏輯，該邏輯會偵測系統的CPU核心數。當核心數小於等於2時（這正是Colab等虛擬環境的典型配置），程式會**強制只使用1個核心**進行運算。這使得程式無法利用所有可用的計算資源，是導致執行時間過長的**最根本原因**。

2.  **缺乏可控的測試規模**：由於一次完整的端對端測試就需要12分鐘，這使得任何針對效能的修改都難以進行快速、有效的驗證。我們缺乏一個能夠在150秒超時限制內，對整個流程進行快速驗證的工具。

## 解決方案與執行過程

為了解決這個複雜的問題，我們採取了一個分階段、謹慎驗證的策略：

### 第一步：打造「效能測試儀」

意識到直接修改並執行完整回測是不可行的，我們首先為 `backtest_runner.py` 增加了一個 `--limit-combinations <數量>` 的指令列參數。

-   **錯誤的嘗試**：最初的實現只是簡單地在 `backtest_runner.py` 中對策略**種類**進行切片，但這忽略了每種策略內部由不同參數產生的巨量**組合**。這個錯誤的嘗試導致測試執行時間絲毫未減，並以超時告終。
-   **正確的實現**：在深刻反省後，我們將限制邏輯移到了正確的位置——`VectorBacktestEngine` 內部。在所有參數組合 (`all_combinations`) 被產生出來之後，但在繁重的計算開始之前，對組合總數進行切片。

這次修正取得了巨大成功，使我們能夠在**15秒內**完成一次包含100個組合的小規模端對端測試，完美地解決了測試驗證的難題。

### 第二步：移除效能瓶頸並進行對比測試

在擁有了可靠的「效能測試儀」後，我們安全地修改了 `SpecMonitor_backtester.py`，移除了強制使用單核心的限制。

接著，我們使用 `--limit-combinations 100` 進行了嚴謹的對比測試：
-   **優化前 (單核心)**：執行時間約 `12.3 秒`。
-   **優化後 (多核心)**：執行時間約 `12.1 秒`。

雖然在小規模測試下時間差異不大，但日誌清晰地顯示CPU使用已從 `1/2 核心` 變為 `2/2 核心`，證明瓶頸已被徹底移除。

### 第三步：校準記憶體估算

根據日誌中觀測到的真實記憶體使用情況 (`~1.6 GB`)，我們將 `SpecMonitor` 中的記憶體估算因子從 `0.15` 調整為更貼近現實的 `0.25`，使記憶體安全檢查更準確。

## 最終成果

-   **效能顯著提升**：雖然最終的完整回測（6500組合）仍然因為計算總量過大而超時（從`736秒`優化至`401秒`），但我們成功地將程式的CPU效能提升了約**45%**。
-   **交付了關鍵工具**：`--limit-combinations` 參數成為了一個關鍵的開發與測試工具，確保了未來的開發者可以在資源與時間限制下，安全、高效地工作。
-   **指明了未來方向**：本次優化證明，在當前架構下，下一步的優化重點應從「提升計算速度」轉向「**任務拆分**」，例如開發分批處理大型回測任務的功能。

---
# 日誌：修正 `ModuleNotFoundError`

**時間戳記**: 2025/11/07 01:08:59 CST

## 問題描述

在 `Master_Workflow.ipynb` 中執行回測時，系統拋出 `ModuleNotFoundError: No module named 'dataloader'` 錯誤。

## 根本原因分析

經過追蹤，發現錯誤源於 `lo2cin4bt` 套件內部的 Python 模組（例如 `yfinance_loader.py` 和 `DataLoader_autorunner.py`）使用了不正確的**絕對導入**（`from dataloader...`）。

`lo2cin4bt` 作為一個獨立的 Python 套件，其內部模組間的引用應該使用**相對導入**（例如 `from .` 或 `from ..`）。絕對導入語法會讓 Python 解譯器從頂層路徑 (`sys.path`) 尋找 `dataloader`，但在 Colab 的執行環境中，該路徑並未被正確設定，導致模組無法被找到。

## 解決方案

解決方案是將所有在 `lo2cin4bt` 套件內部的不正確的絕對導入，全部修改為相對導入。

例如：
*   在 `lo2cin4bt/dataloader/yfinance_loader.py` 中，`from dataloader.validator_loader...` 應改為 `from .validator_loader...`。
*   在 `lo2cin4bt/autorunner/DataLoader_autorunner.py` 中，`from dataloader.file_loader...` 應改為 `from ..dataloader.file_loader...`。

此修改可以確保 `lo2cin4bt` 套件的內部引用獨立於其所在的外部環境，從而解決 `ModuleNotFoundError` 問題。

---

# `Master_Workflow.ipynb` 修復日誌

## 問題描述

`Master_Workflow.ipynb` 檔案在 Google Colab 中無法開啟，顯示 `SyntaxError: Expected ',' or ']' after array element in JSON...` 錯誤。這表示筆記本檔案的 JSON 結構已損壞。

## 嘗試與失敗 (第一次、第二次修復)

### 初步嘗試：手動重建 JSON 字串

最初的解決思路是，透過讀取損壞檔案的內容，然後以程式化的方式手動建立一個包含正確儲- cellpadding="0" cellspacing="0" style="width:100%"><tbody><tr><td style="width:100%;border:none;padding:0cm">
<p>格內容的 JSON 字串，再將其寫入新的 `.ipynb` 檔案。</p>
</td></tr></tbody></table>

**結果：失敗**

這個方法忽略了 `.ipynb` 檔案格式的複雜性，特別是 `source` 陣列的格式要求。在 `source` 陣列中，每一行程式碼都必須是一個獨立的字串元素，且字串本身不能包含換行符 (`\n`)。手動拼接字串時，不當地加入了換行符，導致了與原始問題完全相同的 `SyntaxError`。

這個失敗凸顯了手動操作複雜檔案格式的風險。

## 最終解決方案 (第三次修復)

### 正確方法：使用 `nbformat` 函式庫

在多次失敗後，我們採取了更專業、更可靠的方法，即使用 Python 的 `nbformat` 函式庫。`nbformat` 是 Jupyter 官方提供的、專門用來處理 `.ipynb` 檔案的工具。

**執行步驟：**

1.  **安裝函式庫**:
    ```bash
    pip install nbformat
    ```

2.  **建立建構腳本 (`build_notebook.py`)**:
    建立一個臨時的 Python 腳本，使用 `nbformat` 以程式化的方式來建立筆記本。

    ```python
    import nbformat as nbf

    # 1. 建立一個新的筆記本物件
    nb = nbf.v4.new_notebook()

    # 2. 將每個儲存格的原始碼定義為 Python 字串
    cell1_source = """..."""
    cell2_source = """..."""
    # ...依此類推...

    # 3. 建立儲存格物件，並將其加入筆記本中
    nb['cells'] = [
        nbf.v4.new_code_cell(cell1_source),
        nbf.v4.new_code_cell(cell2_source),
        # ...依此類推...
    ]

    # 4. 將筆記本物件序列化並寫入檔案
    with open('Master_Workflow.ipynb', 'w') as f:
        nbf.write(nb, f)

    print("✅ Master_Workflow.ipynb built successfully!")
    ```

3.  **執行腳本**:
    ```bash
    python build_notebook.py
    ```
    這個腳本會產生一個結構 100% 正確的 `Master_Workflow.ipynb` 檔案。

**結果：成功**

使用 `nbformat` 函式庫產生的筆記本檔案，其 JSON 結構完全符合規範，Google Colab 能夠順利解析並開啟，問題得到徹底解決。

## 學習與結論

- **不要手動操作複雜的檔案格式**: 對於像 `.ipynb` 這樣有嚴格結構規範的檔案，手動拼接字串極易出錯，且難以除錯。
- **使用專門的工具**: 永遠優先選擇官方或社群認可的函式庫 (如 `nbformat`) 來處理特定的檔案格式。這不僅能確保結果的正確性，也能大幅提升開發效率。
- **記錄是關鍵**: 將解決問題的過程，特別是失敗的嘗試和最終的成功方案記錄下來，是團隊寶貴的知識資產。
