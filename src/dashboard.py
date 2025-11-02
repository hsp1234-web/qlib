# src/dashboard.py
import streamlit as st
import json
import pandas as pd
import os
import argparse

def display_dashboard(results_path):
    """
    使用 Streamlit 讀取回測結果並顯示儀表板。

    Args:
        results_path (str): 儲存回測結果的 JSON 檔案路徑。
    """
    # --- 頁面設定 ---
    st.set_page_config(
        page_title="量化回測分析儀表板",
        page_icon="📊",
        layout="wide"
    )

    st.title("📈 量化回測分析儀表板")
    st.write("---")

    # --- 檢查檔案 ---
    if not os.path.exists(results_path):
        st.error(f"錯誤：找不到回測結果檔案！請確認路徑是否正確：`{results_path}`")
        st.warning("請先執行 `run_analysis.py` 來產生回測結果。")
        return

    # --- 讀取與顯示資料 ---
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        st.sidebar.header("回測設定")
        st.sidebar.info(
            "這是一個基於 **移動平均線交叉策略** 的回測結果。"
        )

        # --- 顯示關鍵指標 (KPIs) ---
        st.header("📊 績效總覽")
        col1, col2, col3, col4 = st.columns(4)

        # 使用 .get() 方法安全地讀取字典值，避免 KeyError
        col1.metric("最終權益 (Final Equity)", f"${stats.get('Equity Final [$]', 0):,.2f}")
        col2.metric("勝率 (Win Rate)", f"{stats.get('Win Rate [%]', 0):.2f}%")
        col3.metric("夏普比率 (Sharpe Ratio)", f"{stats.get('Sharpe Ratio', 0):.3f}")
        col4.metric("最大回撤 (Max Drawdown)", f"{stats.get('Max. Drawdown [%]', 0):.2f}%")

        st.write("---")

        # --- 繪製權益曲線圖 ---
        st.header("💹 權益曲線")

        # 檢查是否有權益曲線數據
        equity_curve_data = stats.get('Equity Curve (Date, Value)')
        if equity_curve_data:
            # 將權益曲線數據轉換為 Pandas DataFrame
            equity_df = pd.DataFrame(equity_curve_data, columns=['Date', 'Equity'])
            equity_df['Date'] = pd.to_datetime(equity_df['Date'])
            equity_df.set_index('Date', inplace=True)

            st.line_chart(equity_df['Equity'])
        else:
            st.warning("在結果檔案中找不到權益曲線資料。")

        # --- 顯示詳細統計數據 ---
        with st.expander("點擊查看詳細回測統計數據"):
            # 移除已經視覺化的部分，避免重複顯示
            stats.pop('Equity Curve (Date, Value)', None)
            st.json(stats)

    except json.JSONDecodeError:
        st.error(f"錯誤：無法解析 JSON 檔案。檔案可能已損毀或格式不正確：`{results_path}`")
    except Exception as e:
        st.error(f"載入儀表板時發生未知錯誤：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="啟動一個 Streamlit 儀表板來視覺化回測結果。")
    parser.add_argument('--results_path', type=str, required=True, help='包含回測結果的 JSON 檔案路徑。')

    args = parser.parse_args()

    # Streamlit 應用程式需要透過 `streamlit run` 指令來啟動，
    # 而不是直接執行。下面的程式碼確保您可以這樣做，
    # 但為了在 Colab 或命令列中更容易使用，我們通常會
    # 寫一個 shell 指令，例如：streamlit run dashboard.py -- --results_path "path/to/results.json"

    # 這裡我們直接呼叫函數，這樣 Streamlit 就可以正確地抓取它。
    display_dashboard(results_path=args.results_path)
