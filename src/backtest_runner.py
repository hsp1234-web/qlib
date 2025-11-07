# src/backtest_runner.py

import argparse
import logging
import pandas as pd
from datetime import datetime
import sys
import os

# 將專案根目錄 (src 的上一層) 加入到 sys.path，以確保模組能被正確找到
# 使用 insert(0, ...) 確保專案路徑優先於其他路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 匯入 lo2cin4bt 的核心模組
from lo2cin4bt.dataloader.yfinance_loader import YahooFinanceLoader
from lo2cin4bt.backtester.Base_backtester import BaseBacktester, DEFAULT_LONG_STRATEGY_PAIRS, DEFAULT_SHORT_STRATEGY_PAIRS, DEFAULT_ALL_STRATEGY_PAIRS
from lo2cin4bt.backtester.VectorBacktestEngine_backtester import VectorBacktestEngine
from lo2cin4bt.backtester.Indicators_backtester import IndicatorsBacktester
from lo2cin4bt.metricstracker.Base_metricstracker import BaseMetricTracker
from lo2cin4bt.dataloader.validator_loader import DataValidator
from lo2cin4bt.dataloader.calculator_loader import ReturnCalculator


# --- 日誌設定 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BacktestRunner")
# ---

def run_backtest(ticker: str, start_date: str, end_date: str, strategy: str = "defaultlong", smoke_test: bool = False, limit_combinations: int = None):
    """
    執行一次完整的回測流程。

    Args:
        ticker (str): 要回測的股票/期貨代碼 (yfinance 格式)。
        start_date (str): 回測開始日期 (YYYY-MM-DD)。
        end_date (str): 回測結束日期 (YYYY-MM-DD)。
        strategy (str): 要使用的策略 ('defaultlong', 'defaultshort', 'defaultall')。
        smoke_test (bool): 如果為 True，則只執行一小部分回測用於快速測試。
        limit_combinations (int, optional): 限制執行的參數組合數量. Defaults to None.
    """
    logger.info(f"===== 開始執行回測任務 =====")
    logger.info(f"目標標的: {ticker}")
    logger.info(f"回測期間: {start_date} to {end_date}")
    logger.info(f"使用策略: {strategy}")

    # 1. 載入數據
    logger.info("--- 步驟 1: 正在從 Yahoo Finance 下載數據 ---")
    loader = YahooFinanceLoader()
    # 以非互動方式載入數據
    data, frequency = loader.load(ticker=ticker, start_date=start_date, end_date=end_date, frequency="1d")

    if data is None or data.empty:
        logger.error("數據下載或處理失敗，無法繼續回測。")
        return

    # 數據驗證與清洗
    validator = DataValidator(data)
    data = validator.validate_and_clean()
    if data is None:
        logger.error("數據清洗失敗，程式終止")
        return

    # 計算報酬率
    calculator = ReturnCalculator(data)
    data = calculator.calculate_returns()

    logger.info(f"數據載入與準備完成，共 {len(data)} 筆資料。")

    # 2. 執行回測
    logger.info("--- 步驟 2: 正在執行向量化回測 ---")

    # 手動建構非互動式回測設定
    logger.info(f"--- 正在為 '{strategy}' 策略建構非互動式設定檔 ---")

    strategy_map = {
        "defaultlong": DEFAULT_LONG_STRATEGY_PAIRS,
        "defaultshort": DEFAULT_SHORT_STRATEGY_PAIRS,
        "defaultall": DEFAULT_ALL_STRATEGY_PAIRS
    }

    selected_strategy_pairs = strategy_map.get(strategy)

    if selected_strategy_pairs is None:
        logger.error(f"錯誤：無效的策略名稱 '{strategy}'。請使用 'defaultlong', 'defaultshort', 或 'defaultall'。")
        return

    if smoke_test:
        logger.info("--- 煙霧測試模式已啟用：只執行前 2 個策略組合 ---")
        selected_strategy_pairs = selected_strategy_pairs[:2]

    condition_pairs = []
    for entry, exit_cond in selected_strategy_pairs:
        entry_list = entry if isinstance(entry, list) else [entry]
        exit_list = exit_cond if isinstance(exit_cond, list) else [exit_cond]
        condition_pairs.append({"entry": entry_list, "exit": exit_list})

    # --- 產生有效的指標參數 ---
    indicators_helper = IndicatorsBacktester(logger=logger)
    indicator_params = {}

    # 為不同指標類型定義預設參數
    default_params = {
        "MA": {"ma_type": "SMA", "ma_range": "10:200:20", "short_range": "10:50:20", "long_range": "60:90:30", "m_range": "1:20:5", "n_range": "10:200:40"},
        "BOLL": {"ma_range": "10:200:20", "sd_multi": "1,1.5,2"},
        "HL": {"n_range": "1:5:2", "m_range": "10:200:20"},
        "PERC": {"window_range": "10:200:20", "percentile_range": "90:100:10", "m1_range": "60:80:10", "m2_range": "80:100:10"},
        "VALUE": {"n_range": "1:5:2", "m_range": "10:50:10", "m1_range": "10:50:10", "m2_range": "60:90:10"},
        "NDAY": {"n_range": "1:10:3"}
    }

    for i, pair in enumerate(condition_pairs):
        all_indicators_in_pair = set(pair['entry']) | set(pair['exit'])
        for indicator_alias in all_indicators_in_pair:
            strategy_alias = f"{indicator_alias}_strategy_{i + 1}"

            # 確定指標主類型
            main_type = ""
            for key in default_params.keys():
                if indicator_alias.startswith(key):
                    main_type = key
                    break

            if main_type:
                params_config = default_params[main_type]
                params_list = indicators_helper.get_indicator_params(indicator_alias, params_config)
                indicator_params[strategy_alias] = params_list
            else:
                logger.warning(f"無法為指標 '{indicator_alias}' 找到預設參數，將傳入空字典。")
                indicator_params[strategy_alias] = indicators_helper.get_indicator_params(indicator_alias, {})


    config = {
        "condition_pairs": condition_pairs,
        "indicator_params": indicator_params,
        "predictors": ["Close"],
        "trading_params": {
            "transaction_cost": 0.001,
            "slippage": 0.0005,
            "trade_delay": 1,
            "trade_price": "open"
        },
        "initial_capital": 1000000,
    }

    logger.info("非互動式設定檔建構完成。")

    # 建立回測器實例並傳入數據
    backtester = BaseBacktester(data, frequency=frequency, logger=logger, symbol=ticker)

    # 以非互動方式執行回測
    logger.info("--- 開始執行回測引擎 ---")
    backtester.backtest_engine = VectorBacktestEngine(
        data, frequency or "1D", logger, getattr(backtester, 'symbol', 'X')
    )
    backtester.results = backtester.backtest_engine.run_backtests(config, limit_combinations=limit_combinations)

    # 手動觸發結果導出
    backtester._export_results(config)

    logger.info("回測執行完畢。")

    # 3. 分析績效
    logger.info("--- 步驟 3: 正在計算績效指標 ---")
    metric_tracker = BaseMetricTracker()
    metric_tracker.run_analysis()

    logger.info("績效分析完成。")

    logger.info("===== 回測任務執行完畢 =====")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="自動化回測執行器")
    parser.add_argument("--ticker", type=str, required=True, help="要回測的股票/期貨代碼")
    parser.add_argument("--start_date", type=str, required=True, help="回測開始日期 (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, required=True, help="回測結束日期 (YYYY-MM-DD)")
    parser.add_argument("--strategy", type=str, default="defaultlong", help="使用的策略 ('defaultlong', 'defaultshort', 'defaultall')")
    parser.add_argument("--smoke-test", action="store_true", help="啟用煙霧測試模式，只執行一小部分回測。")
    parser.add_argument("--limit-combinations", type=int, default=None, help="限制回測的參數組合數量")


    args = parser.parse_args()

    ticker_processed = args.ticker.replace('F.1!', ' F.1!')

    run_backtest(ticker_processed, args.start_date, args.end_date, args.strategy, smoke_test=args.smoke_test, limit_combinations=args.limit_combinations)
