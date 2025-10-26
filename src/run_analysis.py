# src/run_analysis.py
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import os
import argparse
import json

class CustomEncoder(json.JSONEncoder):
    """
    自訂的 JSON 編碼器，用來處理 Pandas 和 Numpy 中特殊的資料型別。
    """
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Timedelta):
            return obj.total_seconds()
        if pd.isna(obj): # 處理 pd.NaT
            return None
        if isinstance(obj, (np.floating, float)) and np.isnan(obj): # 處理 np.nan
            return None
        return super().default(obj)

class SmaCross(Strategy):
    """
    一個簡單的移動平均線 (SMA) 交叉策略。
    當短期均線由下往上穿越長期均線時，買入。
    當短期均線由上往下穿越長期均線時，賣出。
    """
    # 定義策略參數
    n1 = 10  # 短期均線天數
    n2 = 20  # 長期均線天數

    def init(self):
        # 在策略初始化時，計算移動平均線
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)

    def next(self):
        # 在每個時間點，檢查均線是否交叉
        if crossover(self.sma1, self.sma2):
            self.buy()  # 買入信號
        elif crossover(self.sma2, self.sma1):
            self.sell() # 賣出信號

def run_backtest(data_path, results_path):
    """
    執行回測分析並儲存結果。

    Args:
        data_path (str): 包含股票數據的 CSV 檔案路徑。
        results_path (str): 儲存回測結果的 JSON 檔案路徑。
    """
    try:
        # 檢查資料檔案是否存在
        if not os.path.exists(data_path):
            print(f"錯誤：找不到資料檔案 {data_path}。請先執行 data_loader.py。")
            return

        # 讀取數據
        print(f"正在從 {data_path} 讀取資料...")
        data = pd.read_csv(data_path, index_col='Date', parse_dates=True)

        # 由於 data_loader.py 已確保 CSV 格式標準化 (欄位名稱為 'Open', 'High', etc.)
        # 此處不再需要額外的欄位名稱清理

        # 初始化回測
        # 我們設定 100萬 的初始資金和 0.1% 的交易手續費
        bt = Backtest(data, SmaCross, cash=1_000_000, commission=.001)

        # 執行回測
        print("正在執行回測分析...")
        stats = bt.run()

        # 確保目標資料夾存在
        results_dir = os.path.dirname(results_path)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"成功建立資料夾：{results_dir}")

        # 將回測統計數據轉換為字典並儲存
        # --- 結果序列化 ---
        # 將回測統計數據轉換為字典
        stats_dict = dict(stats)

        # 移除 '_strategy' 物件
        stats_dict.pop('_strategy', None)

        # 將 '_equity_curve' DataFrame 轉換為可序列化的格式，並改名
        if '_equity_curve' in stats_dict:
            equity = stats_dict.pop('_equity_curve')
            stats_dict['Equity Curve'] = equity.reset_index().to_dict('records')

        # 將 '_trades' DataFrame 轉換為可序列化的格式，並改名
        if '_trades' in stats_dict:
            trades = stats_dict.pop('_trades')
            stats_dict['Trades'] = trades.reset_index().to_dict('records')
        # --- 序列化結束 ---

        with open(results_path, 'w', encoding='utf-8') as f:
            # 使用我們自訂的編碼器來處理特殊資料型別
            json.dump(stats_dict, f, ensure_ascii=False, indent=4, cls=CustomEncoder)

        print(f"回測完成！結果已儲存至：{results_path}")
        print("\n--- 回測結果摘要 ---")
        print(stats)
        print("--------------------")

    except Exception as e:
        print(f"執行回測時發生錯誤：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="對指定的股票數據執行一個簡單的移動平均線交叉策略回測。")
    parser.add_argument('--data_path', type=str, required=True, help='輸入的 CSV 數據檔案路徑。')
    parser.add_argument('--results_path', type=str, required=True, help='用來儲存回測結果的 JSON 檔案路徑。')

    args = parser.parse_args()

    run_backtest(data_path=args.data_path, results_path=args.results_path)
