# lo2cin4bt/app.py
import dash
from dash import dcc, html, Input, Output, State
import json
from typing import Optional
from datetime import date
import logging

# 匯入 autorunner
from .autorunner.Base_autorunner import BaseAutorunner

# --- 常數定義 ---
CONFIG_TEMPLATE_PATH = "lo2cin4bt/records/autorunner/config_template.json"

# --- 核心邏輯 (非 Dash 相關) ---
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
            config["dataloader"]["start_date"] = start_date
        if end_date:
            config["dataloader"]["end_date"] = end_date

    return config

# --- Dash App 初始化 ---
app = dash.Dash(__name__)
# 設定日誌
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)


# --- App 佈局 ---
app.layout = html.Div([
    html.H1("lo2cin4bt 回測設定編輯器"),

    html.Label("股票代碼 (Ticker):"),
    dcc.Input(id='ticker-input', value='^GSPC', type='text'),

    html.Br(),

    html.Label("開始日期:"),
    dcc.DatePickerSingle(id='start-date-picker', date=date(2020, 1, 1)),

    html.Label("結束日期:"),
    dcc.DatePickerSingle(id='end-date-picker', date=date(2023, 1, 1)),

    html.Hr(),

    html.Button('執行回測', id='execute-button', n_clicks=0),
    html.Div(id='execute-status'), # 用於顯示執行狀態

    html.Hr(),

    html.H3("即時設定檔預覽:"),
    html.Pre(id='config-display')
])

# --- 回呼函式 (Callbacks) ---
@app.callback(
    Output('config-display', 'children'),
    Input('ticker-input', 'value'),
    Input('start-date-picker', 'date'),
    Input('end-date-picker', 'date')
)
def update_config_display(ticker: Optional[str], start_date: Optional[str], end_date: Optional[str]) -> str:
    """當 UI 輸入改變時，更新設定檔的 JSON 預覽。"""
    config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date)
    return json.dumps(config, indent=2, ensure_ascii=False)

@app.callback(
    Output('execute-status', 'children'),
    Input('execute-button', 'n_clicks'),
    State('ticker-input', 'value'),
    State('start-date-picker', 'date'),
    State('end-date-picker', 'date'),
    prevent_initial_call=True
)
def execute_backtest(n_clicks: int, ticker: str, start_date: str, end_date: str) -> str:
    """當點擊執行按鈕時，啟動 autorunner 進行回測。"""
    if n_clicks == 0:
        return "尚未執行回測。"

    try:
        app.logger.info(f"接收到回測請求: Ticker={ticker}, Start={start_date}, End={end_date}")

        # 1. 產生設定檔
        config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date)

        # 2. 實例化並執行 autorunner
        autorunner = BaseAutorunner(logger=app.logger)
        autorunner.run(config=config)

        app.logger.info("Autorunner 執行成功。")
        return f"回測任務已成功啟動！ Ticker: {ticker}"

    except Exception as e:
        app.logger.error(f"回測執行失敗: {e}", exc_info=True)
        return f"回測執行失敗: {e}"

# --- 主程式入口 ---
if __name__ == '__main__':
    from waitress import serve
    print("--- 正在使用 waitress 啟動伺服器 ---")
    serve(app.server, host="0.0.0.0", port=8050)
