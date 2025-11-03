# lo2cin4bt/tests/test_app.py
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import date

# 匯入新的 Gradio 後端函式
from lo2cin4bt.app import generate_config, update_preview, process_backtest_request

# --- 单元测试 ---

# 保留与核心逻辑 generate_config 相关的测试
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

# 新增对 Gradio 后端函式的单元测试
def test_update_preview():
    """测试 Gradio 的预览函式是否能正确生成設定檔。"""
    ticker = "MSFT"
    start_date = "2021-01-01"
    end_date = "2022-12-31"

    config = update_preview(ticker, start_date, end_date)

    assert config["dataloader"]["yfinance_config"]["symbol"] == "MSFT"
    assert config["dataloader"]["start_date"] == "2021-01-01"
    assert config["dataloader"]["end_date"] == "2022-12-31"

@patch('lo2cin4bt.app.BaseAutorunner')
def test_process_backtest_request(mock_autorunner_class):
    """测试 Gradio 的主处理函式是否能正确触发回测流程。"""
    mock_autorunner_instance = MagicMock()
    mock_autorunner_class.return_value = mock_autorunner_instance

    ticker = "TSLA"
    start_date = "2023-01-01"
    end_date = "2024-01-01"

    config, status_message = process_backtest_request(ticker, start_date, end_date)

    # 验证返回的 config 是否正确
    assert config["dataloader"]["yfinance_config"]["symbol"] == "TSLA"
    assert config["dataloader"]["start_date"] == "2023-01-01"

    # 验证返回的状态讯息
    assert "回測任務已成功啟動" in status_message

    # 验证 autorunner 是否被正确呼叫
    mock_autorunner_class.assert_called_once()
    mock_autorunner_instance.run.assert_called_once()

    # 验证传递给 autorunner 的 config 是否正确
    captured_config = mock_autorunner_instance.run.call_args[1]['config']
    assert captured_config["dataloader"]["yfinance_config"]["symbol"] == "TSLA"
