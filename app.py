import streamlit as st
import pandas as pd
import numpy as np
import datetime
from xgboost import XGBRegressor
import joblib

# ---------------- 模拟模型加载（后期改为 joblib.load） ----------------
@st.cache_data

def load_model():
    model = XGBRegressor()
    model.load_model("hp_xgb_model.json")  # 后期导出模型用 joblib.dump(model, "hp_model.pkl")
    return model

# ---------------- 定义推荐定价函数 ----------------
def recommend_price(date_str, model, cost=0):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    day = dt.day
    is_weekend = 1 if dt.weekday() >= 5 else 0
    is_holiday = 1 if date_str in ["2025-05-01", "2025-06-01"] else 0

    price_range = np.arange(300, 801, 5)
    results = []

    for p in price_range:
        X = np.array([[p, day, is_weekend, is_holiday]])
        occ = model.predict(X)[0]
        occ = min(max(occ, 0), 1)
        revenue = occ * (p - cost)
        results.append((p, occ, revenue))

    df_result = pd.DataFrame(results, columns=["房价", "预测入住率", "预测利润"])
    best_row = df_result.loc[df_result["预测利润"].idxmax()]
    best_price = best_row["房价"]
    best_range = df_result[df_result["预测利润"] >= df_result["预测利润"].max() * 0.95]["房价"]

    return df_result, best_price, best_range.min(), best_range.max()

# ---------------- 网页界面 ----------------
st.title("智能酒店定价推荐系统")

# 用户输入区域
hotel = st.selectbox("请选择酒店", ["欢朋酒店", "菲伦酒店", "温德姆酒店"])
room = st.selectbox("请选择房型", ["舒适大床房", "高级大床房", "舒适双床房", "高级双床房", "豪华湖景双床房", "豪华湖景大床房", "欢朋套房"])
date = st.date_input("请选择入住日期", value=datetime.date(2025, 6, 2))
cost = st.number_input("请输入单间成本（可选）", value=0, step=10)

if st.button("生成推荐定价"):
    model = load_model()
    df, best_price, low, high = recommend_price(str(date), model, cost)

    st.success(f"推荐定价为：¥{best_price:.0f}，推荐区间：¥{low:.0f} ~ ¥{high:.0f}")

    st.line_chart(df.set_index("房价")["预测利润"], use_container_width=True)
    st.line_chart(df.set_index("房价")["预测入住率"], use_container_width=True)

    with st.expander("查看全部计算数据"):
        st.dataframe(df)

st.caption("© 酒店智能定价系统 V1")
