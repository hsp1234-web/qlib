# lo2cin4bt/tests/test_app.py
import pytest
import json
from unittest.mock import patch, MagicMock
import re
import requests
import time
from threading import Thread

# 匯入 Playwright 相关的断言
from playwright.sync_api import Page, expect

from lo2cin4bt.app import app, generate_config, update_config_display, execute_backtest

# --- Unit Tests ---

def test_generate_config_updates_yfinance_parameters_correctly():
    ticker = "AAPL"
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    config = generate_config(ticker=ticker, start_date=start_date, end_date=end_date, source="yfinance")
    assert config["dataloader"]["source"] == "yfinance"
    assert config["dataloader"]["yfinance_config"]["symbol"] == "AAPL"
    assert config["dataloader"]["start_date"] == "2022-01-01"
    assert config["dataloader"]["end_date"] == "2023-01-01"

def test_generate_config_uses_default_values_when_no_parameters_given():
    config = generate_config()
    with open("lo2cin4bt/records/autorunner/config_template.json", "r") as f:
        template_config = json.load(f)
    template_config["dataloader"]["source"] = "yfinance"
    assert config == template_config

def test_update_config_display_callback_for_ticker():
    output_json_string = update_config_display(ticker="MSFT", start_date=None, end_date=None)
    config = json.loads(output_json_string)
    assert config["dataloader"]["yfinance_config"]["symbol"] == "MSFT"

def test_update_config_display_callback_for_dates():
    output_json_string = update_config_display(ticker=None, start_date="2021-01-01", end_date="2022-12-31")
    config = json.loads(output_json_string)
    assert config["dataloader"]["start_date"] == "2021-01-01"
    assert config["dataloader"]["end_date"] == "2022-12-31"

@patch('lo2cin4bt.app.BaseAutorunner')
def test_execute_backtest_callback(mock_autorunner_class):
    mock_autorunner_instance = MagicMock()
    mock_autorunner_class.return_value = mock_autorunner_instance
    ticker = "TSLA"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    n_clicks = 1
    assert execute_backtest(0, ticker, start_date, end_date) == "尚未執行回測。"
    result_message = execute_backtest(n_clicks, ticker, start_date, end_date)
    assert "回測任務已成功啟動" in result_message
    mock_autorunner_class.assert_called_once()
    mock_autorunner_instance.run.assert_called_once()
    captured_config = mock_autorunner_instance.run.call_args[1]['config']
    assert captured_config["dataloader"]["yfinance_config"]["symbol"] == "TSLA"
    assert captured_config["dataloader"]["start_date"] == "2023-01-01"

# --- End-to-End Test (with Playwright and manual server thread) ---

@pytest.fixture(scope="function")
def dash_server():
    """手動啟動 Dash 伺服器的 fixture。"""
    host = "127.0.0.1"
    port = 8051

    def run_server():
        # 使用 waitress 作為生產級伺服器，以避免 Flask 開發伺服器的問題
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
            break # 伺服器已回應
        except requests.ConnectionError:
            time.sleep(0.1)

    yield url
    # 測試結束後，不需要手動停止，因為 daemon thread 會隨主程序退出

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

    # 6. 產生螢幕截圖以供驗證
    page.screenshot(path="verification/verification.png")
