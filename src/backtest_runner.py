# src/backtest_runner.py

import argparse
import logging
import pandas as pd
from datetime import datetime
import sys
import os

# 確保 src 目錄在 Python 的搜尋路徑中
# 這樣我們才能正確地 import lo2cin4bt 模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 匯入 lo2cin4bt 的核心模組
from lo2cin4bt.dataloader.yfinance_loader import YahooFinanceLoader
from lo2cin4bt.backtester.Base_backtester import BaseBacktester
from lo2cin4bt.metricstracker.Base_metricstracker import BaseMetricTracker
from lo2cin4bt.dataloader.validator_loader import DataValidator
from lo2cin4bt.dataloader.calculator_loader import ReturnCalculator


# --- 日誌設定 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BacktestRunner")
# ---

def run_backtest(ticker: str, start_date: str, end_date: str, strategy: str = "defaultlong"):
    """
    執行一次完整的回測流程。

    Args:
        ticker (str): 要回測的股票/期貨代碼 (yfinance 格式)。
        start_date (str): 回測開始日期 (YYYY-MM-DD)。
        end_date (str): 回測結束日期 (YYYY-MM-DD)。
        strategy (str): 要使用的策略 ('defaultlong', 'defaultshort', 'defaultall')。
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
    backtester = BaseBacktester(data, frequency=frequency, logger=logger, symbol=ticker)

    # 產生預設策略設定
    config = backtester.generate_default_config(strategy=strategy, predictor="Close")

    # 以非互動方式執行回測
    backtester.run(config=config)

    logger.info("回測執行完畢。")

    # 3. 分析績效
    logger.info("--- 步驟 3: 正在計算績效指標 ---")
    # BaseMetricTracker 會自動讀取最新的回測結果檔案，所以不需要傳入參數
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

    args = parser.parse_args()

    # 處理台股期貨代碼
    # Yahoo Finance 期望的格式是 @TVC.TW F.1!，但直接在命令列傳入特殊字元會有問題
    # 我們讓使用者輸入 @TVC.TWF.1! 即可
    ticker_processed = args.ticker.replace('F.1!', ' F.1!')

    run_backtest(ticker_processed, args.start_date, args.end_date, args.strategy)
