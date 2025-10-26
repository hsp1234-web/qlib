# src/data_loader.py
import yfinance as yf
import pandas as pd
import os
import argparse

def download_stock_data(stock_id, start_date, end_date, output_path):
    """
    從 Yahoo Finance 下載指定的股票數據，並儲存為 CSV 檔案。

    Args:
        stock_id (str): 股票代號，例如 '2330.TW'。
        start_date (str): 開始日期，格式 'YYYY-MM-DD'。
        end_date (str): 結束日期，格式 'YYYY-MM-DD'。
        output_path (str): 儲存資料的目標路徑 (包含檔名)。
    """
    try:
        # 確保目標資料夾存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"成功建立資料夾：{output_dir}")

        # 下載股票資料
        print(f"正在從 Yahoo Finance 下載股票 {stock_id} 的資料...")
        stock_data = yf.download(stock_id, start=start_date, end=end_date)

        if stock_data.empty:
            print(f"警告：找不到股票 {stock_id} 在指定日期範圍內的資料。")
            return

        # --- 資料清理與標準化 ---
        # 目的：確保輸出的 CSV 檔案格式永遠一致，不受 yfinance 版本變動影響

        # 1. 處理 yfinance 可能回傳的多層次欄位 (MultiIndex)
        if isinstance(stock_data.columns, pd.MultiIndex):
            # 只保留第一層的欄位名稱 (例如 'Open', 'Close')，並移除第二層 (通常是 Ticker)
            stock_data.columns = stock_data.columns.get_level_values(0)

        # 2. 將欄位名稱統一轉為標準格式 (首字大寫)，以處理 'open' vs 'Open' 的問題
        stock_data.columns = [str(col).capitalize() for col in stock_data.columns]

        # 3. 確保索引欄位有 'Date' 這個名稱
        stock_data.index.name = 'Date'

        # 4. 移除 yfinance 可能自動加入的非標準欄位 (例如 'Dividends', 'Stock splits')
        #    只保留回測所需的核心欄位
        standard_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        # 找出實際存在於 DataFrame 中的標準欄位
        cols_to_keep = [col for col in standard_cols if col in stock_data.columns]
        stock_data = stock_data[cols_to_keep]
        # --- 標準化結束 ---

        # 儲存為 CSV 檔案
        stock_data.to_csv(output_path)
        print(f"成功將資料儲存至：{output_path}")

    except Exception as e:
        print(f"下載過程中發生錯誤：{e}")

if __name__ == "__main__":
    # --- 主程式執行區 ---
    # 這個區塊允許我們直接從命令列執行此腳本

    # 建立一個命令列參數解析器
    parser = argparse.ArgumentParser(description="下載並儲存指定的股票歷史資料。")

    # 加入必要參數
    parser.add_argument('--stock_id', type=str, required=True, help='要下載的股票代號 (例如: 2330.TW)')
    parser.add_argument('--start_date', type=str, required=True, help='資料起始日期 (格式: YYYY-MM-DD)')
    parser.add_argument('--end_date', type=str, required=True, help='資料結束日期 (格式: YYYY-MM-DD)')
    parser.add_argument('--output_path', type=str, required=True, help='CSV 檔案的儲存路徑 (包含檔名)')

    # 解析傳入的參數
    args = parser.parse_args()

    # 呼叫主功能函數
    download_stock_data(
        stock_id=args.stock_id,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=args.output_path
    )
