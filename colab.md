# Colab 量化程式設計：多儲存格工作流

這份文件定義了在 Google Colab 中執行量化研究的標準作業流程。此設計的核心是將 Colab 視為一個純粹的「執行環境」，並將流程拆分為多個獨立的儲存格，以便於分段執行、控制和除錯。

## 使用說明

請依照以下順序，將每個儲存格的程式碼複製到您自己的 Google Colab 筆記本中，然後逐一執行。每個程式碼儲存格都包含了 `#@title` 和中文標題，方便您在 Colab 中將其摺疊收合，保持筆記本的整潔。

---

## 儲存格 1：掛載資料儲存庫 (Google Drive)

### 目的
建立 Colab 環境與您的 Google Drive 之間的連接，並設定好專案所需的資料夾結構。

### 執行動作
1.  **觸發授權**：執行後，會跳出一個 Google 授權視窗，請登入您的帳戶並授權 Colab 存取您的雲端硬碟。
2.  **掛載硬碟**：將您的 Google Drive 掛載到 Colab 的 `/content/drive/MyDrive` 路徑。
3.  **建立目錄**：腳本會自動檢查指定的專案根目錄 (`MyQuantProject`) 以及其中的 `data`, `models`, `results` 子目錄是否存在。如果不存在，將會自動建立。

### 產出
*   Colab 獲得對您 Google Drive 的完整讀寫權限。
*   一個標準化的專案資料夾結構，確保後續步驟可以正確地讀寫檔案。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 1. 掛載 Google Drive 並建立專案目錄
from google.colab import drive
import os

#@markdown ### **設定 Google Drive 專案目錄**
#@markdown 請輸入您希望在 Google Drive 中使用的專案根目錄名稱。
DRIVE_PROJECT_ROOT = "MyQuantProject" #@param {type:"string"}
# --- 設定區結束 ---

try:
    # 掛載 Google Drive
    print("正在嘗試掛載 Google Drive...")
    drive.mount('/content/drive', force_remount=True)
    gdrive_path = os.path.join('/content/drive/MyDrive', DRIVE_PROJECT_ROOT)

    # 將雲端路徑設定為環境變數
    os.environ['GDRIVE_PROJECT_PATH'] = gdrive_path
    # 同時也將它設定為預設的專案路徑
    os.environ['PROJECT_ROOT_PATH'] = gdrive_path

    print(f"✅ Google Drive 掛載成功！專案雲端路徑設定為：{gdrive_path}")

    # 檢查並在雲端硬碟上建立所需的核心資料夾
    for folder in ['data', 'models', 'results']:
        folder_path = os.path.join(gdrive_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"📁 已在雲端建立資料夾：{folder_path}")

except Exception as e:
    # 如果掛載失敗，清除雲端路徑的環境變數，並給予提示
    os.environ['GDRIVE_PROJECT_PATH'] = ""
    print(f"⚠️ 掛載 Google Drive 失敗或未授權。錯誤：{e}")
    print("後續儲存格將使用 Colab 本機儲存空間。")

```

---

## 儲存格 2：同步程式碼 (from GitHub)

### 目的
從 GitHub 獲取最新版本的「執行邏輯」（也就是我們的 Python 腳本）。

### 執行動作
1.  **檢查本地狀態**：檢查 Colab 目前的工作區 (`/content/`) 是否已經存在專案的程式碼資料夾。
2.  **下載或更新**：
    *   如果 **不存在**：執行 `git clone`，將 GitHub 上的整個專案完整下載下來。
    *   如果 **已存在**：執行 `git pull`，只下載自上次以來在 GitHub 上的更新，確保程式碼永遠是最新版本。

### 產出
*   Colab 的 `/content/` 目錄下，擁有了一份與您 GitHub 儲存庫完全同步的最新程式碼。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 2. 從 GitHub 同步專案程式碼
import os

#@markdown ### **1. 設定 GitHub 儲存庫**
#@markdown 請填寫您的 GitHub 儲存庫網址。
GITHUB_REPO_URL = "https://github.com/hsp1234-web/qlib.git" #@param {type:"string"}

#@markdown ---
#@markdown ### **2. 輸入分支名稱**
#@markdown 請輸入您想要使用的分支名稱（例如 `main` 或 `feature/new-strategy`）。
GIT_BRANCH = "main" #@param {type:"string"}
# --- 設定區結束 ---

# --- 將設定儲存為環境變數，供後續儲存格使用 ---
os.environ['GITHUB_REPO_URL'] = GITHUB_REPO_URL
os.environ['GIT_BRANCH'] = GIT_BRANCH
# ---

# 從網址中提取專案名稱
repo_name = GITHUB_REPO_URL.split('/')[-1].replace('.git', '')
local_repo_path = os.path.join('/content', repo_name)

print(f"目標 GitHub 儲存庫：{GITHUB_REPO_URL}")
print(f"預計本地路徑：{local_repo_path}")

# 檢查本地資料夾是否已存在
if os.path.exists(local_repo_path):
    print(f"專案資料夾已存在，正在切換至 '{GIT_BRANCH}' 分支並更新...")
    # 切換到該目錄
    os.chdir(local_repo_path)
    # 執行 git 指令來切換分支並拉取最新的程式碼
    get_ipython().system(f'git fetch origin')
    get_ipython().system(f'git checkout {GIT_BRANCH}')
    get_ipython().system(f'git pull origin {GIT_BRANCH}')
    # 切換回 content 根目錄
    os.chdir('/content')
else:
    print(f"專案資料夾不存在，正在從 '{GIT_BRANCH}' 分支下載整個專案...")
    # 使用 --branch 參數來 clone 指定的分支
    get_ipython().system(f'git clone --branch {GIT_BRANCH} {GITHUB_REPO_URL}')

print("\n✅ 程式碼同步完成！")
# 顯示目前資料夾結構，以確認程式碼已成功下載
print("\n--- 目前 /content/ 目錄結構 ---")
get_ipython().system('ls -F /content/')

```

---

## 儲存格 3：安裝/更新環境 (Requirements)

### 目的
確保 Colab 環境安裝了所有執行我們的量化分析腳本所需要的 Python 套件。

### 執行動作
1.  **讀取設定檔**：找到上一步從 GitHub 同步下來的 `requirements.txt` 檔案。
2.  **安裝套件**：使用 `pip install -r` 指令，自動安裝或更新清單中指定的所有 Python 函式庫。

### 產出
*   一個準備就緒、包含所有依賴項的 Python 執行環境。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 3. 安裝專案所需的 Python 套件
import os

# --- 從環境變數讀取設定 ---
# 這些設定是在儲存格 2 中定義的，確保了設定的統一性
GITHUB_REPO_URL = os.environ.get('GITHUB_REPO_URL')
GIT_BRANCH = os.environ.get('GIT_BRANCH')

if not GITHUB_REPO_URL or not GIT_BRANCH:
    raise ValueError("錯誤：找不到 GITHUB_REPO_URL 或 GIT_BRANCH 環境變數。請先執行儲存格 2。")
# ---

# 從網址中動態推斷專案名稱
repo_name = GITHUB_REPO_URL.split('/')[-1].replace('.git', '')
requirements_path = os.path.join('/content', repo_name, 'requirements.txt')

print(f"正在讀取設定檔：{requirements_path}")

if os.path.exists(requirements_path):
    print("找到 requirements.txt，開始安裝/更新環境...")
    # 使用 -q 參數來減少不必要的輸出訊息，讓介面更簡潔
    get_ipython().system(f'pip install -q -r {requirements_path}')
    print("\n✅ 環境安裝完成！")
else:
    print(f"⚠️ 警告：在 '{requirements_path}' 中找不到 requirements.txt 檔案。")
    print("請確認您的 GitHub 儲存庫中是否包含此檔案。")

```

---

## 儲存格 4：執行核心任務 (資料下載與回測)

### 目的
執行主要的、可能較為耗時的量化分析任務，例如下載歷史資料、訓練模型或執行策略回測。

### 執行動作
1.  **調用腳本**：依序執行我們在 GitHub 上的 `data_loader.py` 和 `run_analysis.py` 腳本。
2.  **動態路徑**：腳本會使用在「儲存格 1」中設定的環境變數 (`PROJECT_ROOT_PATH`) 來決定資料的讀取和寫入位置。這確保了無論您是使用 Google Drive 還是 Colab 本機空間，流程都能無縫接軌。
3.  **執行流程**：
    *   `data_loader.py` 會從 `yfinance` 抓取台積電 (`2330.TW`) 的歷史資料，並將其儲存到 `data` 資料夾中。
    *   `run_analysis.py` 會讀取剛剛下載的資料，執行一個簡單的移動平均線交叉策略回測，並將產出的統計結果儲存到 `results` 資料夾中。

### 產出
*   在 `data` 資料夾中的一份 `2330.TW.csv` 原始數據檔案。
*   在 `results` 資料夾中的一份 `backtest_results.json` 結果檔案。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 4. 執行核心任務：下載數據與執行回測
import os

# --- 從環境變數讀取設定 ---
GITHUB_REPO_URL = os.environ.get('GITHUB_REPO_URL')
GIT_BRANCH = os.environ.get('GIT_BRANCH')

if not GITHUB_REPO_URL or not GIT_BRANCH:
    raise ValueError("錯誤：找不到 GITHUB_REPO_URL 或 GIT_BRANCH 環境變數。請先執行儲存格 2。")
# ---

# --- 其他設定區 ---
# 執行的股票代號和日期範圍
STOCK_ID = "2330.TW"
START_DATE = "2020-01-01"
END_DATE = "2023-12-31"
# --- 設定區結束 ---

# --- 路徑設定與檢查 ---
# 檢查儲存格 1 是否已成功設定專案路徑
project_root = os.environ.get('PROJECT_ROOT_PATH')

if not project_root:
    # 如果儲存格 1 未執行或掛載失敗，則自動設定並使用 Colab 本機路徑
    print("⚠️ Google Drive 尚未掛載或設定失敗。")
    print("將自動在本機建立臨時專案目錄。執行結果將在 Colab 關閉後遺失。")

    # 從儲存格 1 的參數中讀取預設的專案名稱 (如果存在的話)
    # 這裡我們直接使用 'MyQuantProject' 作為後備名稱
    local_project_name = "MyQuantProject"
    project_root = os.path.join('/content', local_project_name)
    os.environ['PROJECT_ROOT_PATH'] = project_root

    print(f"📁 本機專案路徑已設定為：{project_root}")

# 無論是雲端還是本機，都確保 data 和 results 子資料夾存在
os.makedirs(os.path.join(project_root, 'data'), exist_ok=True)
os.makedirs(os.path.join(project_root, 'results'), exist_ok=True)
# --- 路徑設定結束 ---

# --- 定義檔案路徑 ---
# 從網址中動態推斷專案名稱
repo_name = GITHUB_REPO_URL.split('/')[-1].replace('.git', '')
# 腳本的存放路徑
scripts_path = f"/content/{repo_name}/src"
# 資料儲存路徑
data_output_path = os.path.join(project_root, 'data', f'{STOCK_ID}.csv')
# 結果儲存路徑
results_output_path = os.path.join(project_root, 'results', 'backtest_results.json')

print("--- 步驟 1: 執行 data_loader.py ---")
# 組合要執行的命令
data_loader_cmd = (
    f"python {scripts_path}/data_loader.py "
    f"--stock_id '{STOCK_ID}' "
    f"--start_date '{START_DATE}' "
    f"--end_date '{END_DATE}' "
    f"--output_path '{data_output_path}'"
)

print(f"執行命令: {data_loader_cmd}")
get_ipython().system(data_loader_cmd)

print("\n--- 步驟 2: 執行 run_analysis.py ---")
# 組合要執行的命令
run_analysis_cmd = (
    f"python {scripts_path}/run_analysis.py "
    f"--data_path '{data_output_path}' "
    f"--results_path '{results_output_path}'"
)

print(f"執行命令: {run_analysis_cmd}")
get_ipython().system(run_analysis_cmd)

print("\n✅ 核心任務執行完畢！")

```

---

## 儲存格 5：啟動前端儀表板 (Streamlit)

### 目的
將上一步驟產出的分析結果進行視覺化，以便我們進行互動式的分析與解讀。

### 執行動作
1.  **安裝通道工具**：`pyngrok` 是一個能將 Colab 內部的網路服務，安全地暴露到一個公開網址的工具。
2.  **啟動服務**：在背景執行 `streamlit run` 指令，來啟動我們的 `dashboard.py` 腳本。
3.  **建立通道**：`pyngrok` 會產生一個獨一無二的公開網址，並將它連接到我們剛剛啟動的 Streamlit 服務。
4.  **顯示網址**：最後，程式會將這個公開網址印出來。

### 產出
*   一個公開的 `ngrok.io` 網址。點擊此網址，即可在新的瀏覽器分頁中看到您的互動式量化分析儀表板。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 5. 啟動 Streamlit 視覺化儀表板
import os
import subprocess
import time

# --- 安裝 ngrok ---
# pyngrok 是 ngrok 的 Python wrapper，讓我們可以透過程式碼控制它
print("正在安裝 ngrok...")
get_ipython().system('pip install -q pyngrok')

from pyngrok import ngrok

# --- 從環境變數讀取設定 ---
GITHUB_REPO_URL = os.environ.get('GITHUB_REPO_URL')
GIT_BRANCH = os.environ.get('GIT_BRANCH')

if not GITHUB_REPO_URL or not GIT_BRANCH:
    raise ValueError("錯誤：找不到 GITHUB_REPO_URL 或 GIT_BRANCH 環境變數。請先執行儲存格 2。")
# ---

# 從網址中動態推斷專案名稱
repo_name = GITHUB_REPO_URL.split('/')[-1].replace('.git', '')

# --- 路徑設定與檢查 ---
project_root = os.environ.get('PROJECT_ROOT_PATH')

if not project_root:
    print("⚠️ Google Drive 尚未掛載或設定失敗。")
    print("將自動在本機建立臨時專案目錄。")
    local_project_name = "MyQuantProject"
    project_root = os.path.join('/content', local_project_name)
    os.environ['PROJECT_ROOT_PATH'] = project_root
    print(f"📁 本機專案路徑已設定為：{project_root}")

# 確保 results 子資料夾存在
os.makedirs(os.path.join(project_root, 'results'), exist_ok=True)
# --- 路徑設定結束 ---

# 定義儀表板腳本和結果檔案的路徑
dashboard_script_path = f"/content/{repo_name}/src/dashboard.py"
results_json_path = os.path.join(project_root, 'results', 'backtest_results.json')

# 檢查儀表板腳本是否存在
if not os.path.exists(dashboard_script_path):
    raise FileNotFoundError(f"錯誤：找不到儀表板腳本 '{dashboard_script_path}'。請確認儲存格 2 已成功執行。")

# 檢查結果檔案是否存在
if not os.path.exists(results_json_path):
    raise FileNotFoundError(f"錯誤：找不到結果檔案 '{results_json_path}'。請確認儲存格 4 已成功執行。")


# --- 啟動 Streamlit ---
# 我們將 Streamlit 服務在背景執行
command = (
    f"streamlit run {dashboard_script_path} -- "
    f"--results_path='{results_json_path}' "
    f"--server.port 8501 --server.headless true"  # headless 模式確保它不會試圖在 Colab 中打開瀏覽器
)

print("正在背景啟動 Streamlit 服務...")
# 使用 Popen 在背景啟動 streamlit
process = subprocess.Popen(command, shell=True)
time.sleep(5) # 等待幾秒鐘確保服務已啟動

# --- 建立公開通道 ---
# 關閉所有現有的 ngrok 通道，以防萬一
ngrok.kill()

# 設定 ngrok 連接到 Streamlit 預設的 8501 連接埠
public_url = ngrok.connect(8501)
print("✅ Streamlit 儀表板已啟動！")
print(f"👉 請點擊此公開網址查看：{public_url}")

```

---

## 儲存格 6：(可選) 同步本地成果至 Google Drive

### 目的
如果您在未掛載 Google Drive 的情況下執行了前面的步驟（例如儲存格 4），您的所有成果（下載的資料、回測的結果）都會被儲存在 Colab 的**本機**臨時空間中。這個儲存格提供了一個方便的功能，讓您可以**事後**將這些儲存在本機的成果，完整地同步回您的 Google Drive，以作永久保存。

### 執行動作
1.  **檢查雲端路徑**：檢查「儲存格 1」是否已經成功執行並設定了 Google Drive 的路徑。
2.  **觸發授權與掛載**：如果 Google Drive 尚未掛載，它會自動執行掛載流程，並要求您授權。
3.  **複製檔案**：使用 `distutils` 工具，遞迴地將 Colab 本機專案資料夾中的所有檔案和子資料夾，複製到您在 Google Drive 上指定的專案目錄中。

### 產出
*   您在本機執行的所有成果，都會被完整地備份一份到您的 Google Drive 中。

### 複製以下程式碼至 Colab 儲存格：
```python
#@title 6. (可選) 同步本地成果至 Google Drive
import os
from google.colab import drive
from distutils.dir_util import copy_tree

# --- 從環境變數讀取雲端路徑 ---
# 這個變數只有在儲存格 1 成功執行後才會被設定
gdrive_path = os.environ.get('GDRIVE_PROJECT_PATH')
# 獲取當前設定的（可能是本機的）專案根目錄
project_root = os.environ.get('PROJECT_ROOT_PATH')

# 檢查 project_root 是否存在
if not project_root or not os.path.exists(project_root):
    print("❌ 錯誤：找不到任何本地專案成果。請先執行儲存格 4。")
# 檢查本地路徑是否與雲端路徑相同
elif gdrive_path and project_root == gdrive_path:
    print("✅ 您的專案成果已經儲存在 Google Drive 中，無需同步。")
else:
    print("🔄 開始將本地成果同步至 Google Drive...")

    # 如果雲端路徑不存在 (儲存格 1 未執行或失敗)，則需要先掛載
    if not gdrive_path:
        try:
            print("正在嘗試掛載 Google Drive...")
            drive.mount('/content/drive', force_remount=True)

            # 從儲存格 1 的參數中讀取預設的專案名稱
            project_name = "MyQuantProject" # 確保這裡的名稱與儲存格 1 的預設值一致
            gdrive_path = os.path.join('/content/drive/MyDrive', project_name)
            os.environ['GDRIVE_PROJECT_PATH'] = gdrive_path
            print(f"✅ Google Drive 掛載成功！雲端路徑設定為：{gdrive_path}")
        except Exception as e:
            print(f"❌ 掛載 Google Drive 失敗。無法同步。錯誤：{e}")
            # 將 gdrive_path 設為 None 以跳過後續操作
            gdrive_path = None

    # 如果成功獲取到雲端路徑，則開始複製
    if gdrive_path:
        print(f"正在將 '{project_root}' 的內容複製到 '{gdrive_path}'...")

        # 確保雲端目標資料夾存在
        os.makedirs(gdrive_path, exist_ok=True)

        # 執行複製
        copy_tree(project_root, gdrive_path)

        print("✅ 同步完成！所有本地成果已成功複製到 Google Drive。")

```
