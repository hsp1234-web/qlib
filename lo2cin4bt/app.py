# lo2cin4bt/app.py
import gradio as gr
import json
from typing import Optional, Tuple
from datetime import date
import logging
import time
import subprocess
import sys
import os

# --- 常數定義 ---
# 确保在任何执行环境下都能找到 backtest_runner.py
BACKTEST_RUNNER_PATH = "src/backtest_runner.py"
CONFIG_TEMPLATE_PATH = "lo2cin4bt/records/autorunner/config_template.json"
RESULTS_DIR = "lo2cin4bt/records/backtester"

# --- 後端核心邏輯 ---

# 初始化日誌記錄器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def generate_config(
    ticker: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: str = "yfinance"
) -> dict:
    """
    從一個範本檔案載入設定，並根據傳入的參數進行更新。
    """
    with open(CONFIG_TEMPLATE_PATH, "r") as f:
        config = json.load(f)

    if "dataloader_config" not in config:
        config["dataloader_config"] = {}

    config["dataloader_config"]["source"] = source
    if source == "yfinance":
        if "yfinance_config" not in config["dataloader_config"]:
            config["dataloader_config"]["yfinance_config"] = {}

        if ticker:
            config["dataloader_config"]["yfinance_config"]["symbol"] = ticker
        if start_date:
            config["dataloader_config"]["start_date"] = str(start_date)
        if end_date:
            config["dataloader_config"]["end_date"] = str(end_date)

    return config

def process_backtest_request(ticker: str, start_date: str, end_date: str) -> Tuple[dict, gr.update]:
    """
    Gradio 的主要處理函式。
    它接收 UI 輸入，啟動背景回測，並返回更新 UI 的指令。
    """
    config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date)
    status_message = ""

    try:
        logger.info(f"接收到回測請求: Ticker={ticker}, Start={start_date}, End={end_date}")

        command = [
            sys.executable,
            BACKTEST_RUNNER_PATH,
            "--ticker", ticker,
            "--start_date", start_date,
            "--end_date", end_date,
            "--strategy", "defaultlong"
        ]

        subprocess.Popen(command)
        logger.info(f"成功啟動背景回測腳本: {' '.join(command)}")

        current_time = time.strftime("%H:%M:%S", time.localtime())
        status_message = f"回測任務已在背景啟動！ Ticker: {ticker}, Time: {current_time}"

    except Exception as e:
        logger.error(f"啟動背景回測失敗: {e}", exc_info=True)
        status_message = f"錯誤：啟動回測失敗。詳情請查看日誌。"

    # 返回 config 和一個 Gradio 更新物件
    return config, gr.update(value=status_message)

def refresh_results():
    """扫描结果目录并返回 Parquet 文件列表。"""
    try:
        if not os.path.exists(RESULTS_DIR):
            return []

        files = [os.path.join(RESULTS_DIR, f) for f in os.listdir(RESULTS_DIR) if f.endswith(".parquet")]
        return files
    except Exception as e:
        logger.error(f"刷新结果列表失败: {e}", exc_info=True)
        return []

def update_preview(ticker: str, start_date: str, end_date: str) -> dict:
    """僅更新設定檔預覽，不執行回測。"""
    config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date)
    return config

# --- Gradio UI 介面定義 ---

with gr.Blocks() as demo:
    gr.Markdown("# lo2cin4bt 回測設定編輯器")

    with gr.Row():
        ticker_input = gr.Textbox(label="股票代碼 (Ticker)", value="^GSPC")
        start_date_input = gr.Textbox(label="開始日期 (YYYY-MM-DD)", value="2020-01-01")
        end_date_input = gr.Textbox(label="結束日期 (YYYY-MM-DD)", value="2023-01-01")

    with gr.Row():
        execute_button = gr.Button("執行回測", variant="primary")
        refresh_button = gr.Button("刷新結果列表")

    status_output = gr.Textbox(label="執行狀態", interactive=False)
    config_output = gr.JSON(label="即時設定檔預覽")
    results_output = gr.Files(label="回測結果檔案")

    # --- UI 事件綁定 ---

    inputs = [ticker_input, start_date_input, end_date_input]
    for input_component in inputs:
        input_component.change(fn=update_preview, inputs=inputs, outputs=config_output)

    # 點擊按鈕會觸發完整的回測流程
    execute_button.click(
        fn=process_backtest_request,
        inputs=inputs,
        outputs=[config_output, status_output]
    )

    # 點擊刷新按鈕會更新結果列表
    refresh_button.click(
        fn=refresh_results,
        inputs=None,
        outputs=results_output
    )

    # 初始載入時，觸發一次預覽和結果刷新
    demo.load(fn=update_preview, inputs=inputs, outputs=config_output)
    demo.load(fn=refresh_results, inputs=None, outputs=results_output)

# --- 主程式入口 ---
if __name__ == '__main__':
    print("--- 正在使用 Gradio 啟動伺服器 ---")
    demo.launch(share=True)
