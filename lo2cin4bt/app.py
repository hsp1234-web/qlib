# lo2cin4bt/app.py
import gradio as gr
import json
from typing import Optional
from datetime import date
import logging
import time

# 匯入 autorunner
from .autorunner.Base_autorunner import BaseAutorunner

# --- 常數定義 ---
CONFIG_TEMPLATE_PATH = "lo2cin4bt/records/autorunner/config_template.json"

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

    config["dataloader"]["source"] = source

    if source == "yfinance":
        if ticker:
            config["dataloader"]["yfinance_config"]["symbol"] = ticker
        if start_date:
            config["dataloader"]["start_date"] = str(start_date) # 確保日期是字串
        if end_date:
            config["dataloader"]["end_date"] = str(end_date) # 確保日期是字串

    return config

def process_backtest_request(ticker: str, start_date: str, end_date: str) -> (dict, str):
    """
    Gradio 的主要處理函式。
    它接收 UI 輸入，產生設定檔，執行回測，並返回結果。
    """
    # 1. 產生設定檔 (用於 UI 預覽)
    config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date)

    try:
        logger.info(f"接收到回測請求: Ticker={ticker}, Start={start_date}, End={end_date}")

        # 2. 實例化並執行 autorunner
        autorunner = BaseAutorunner(logger=logger)
        autorunner.run(config=config)

        logger.info("Autorunner 執行成功。")
        status_message = f"回測任務已成功啟動！ Ticker: {ticker}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

    except Exception as e:
        logger.error(f"回測執行失敗: {e}", exc_info=True)
        status_message = f"回測執行失敗: {e}"

    return config, status_message

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
        status_output = gr.Textbox(label="執行狀態", interactive=False)

    config_output = gr.JSON(label="即時設定檔預覽")

    # --- UI 事件綁定 ---

    # 任何輸入的變動都會觸發預覽更新
    inputs = [ticker_input, start_date_input, end_date_input]
    for input_component in inputs:
        input_component.change(fn=update_preview, inputs=inputs, outputs=config_output)

    # 點擊按鈕會觸發完整的回測流程
    execute_button.click(
        fn=process_backtest_request,
        inputs=inputs,
        outputs=[config_output, status_output]
    )

    # 初始載入時，先觸發一次預覽
    demo.load(fn=update_preview, inputs=inputs, outputs=config_output)


# --- 主程式入口 ---
if __name__ == '__main__':
    import time
    print("--- 正在使用 Gradio 啟動伺服器 ---")
    demo.launch(share=True)
