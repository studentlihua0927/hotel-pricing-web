# hotel_pricing_app_with_new_hotel.py
import streamlit as st
import datetime

from model import predict_price

# 设置页面
st.set_page_config(page_title="酒店收益最大化定价系统", layout="wide")

# 页面头部 Logo 与介绍
st.image("https://yourdomain.com/logo.png", width=100)
st.title("🏨 酒店收益最大化定价系统")
st.markdown("""
欢迎使用酒店智能定价助手！该系统可基于历史数据、节假日与市场策略，预测最优房价，实现收益最大化。
""")

# 假设已有的酒店与房型信息
hotels = {
    "希尔顿欢朋": ["大床房", "双床房", "套房"],
    "麦客达": ["大床房", "景观房"],
    "菲伦": ["标准间", "湖景大床房"]
}

# 功能：新建酒店
with st.sidebar.expander("➕ 新建酒店"):
    if st.checkbox("启用自定义酒店"):
        custom_hotel = st.text_input("请输入新酒店名称")
        custom_room_type = st.text_input("请输入新房型（如双床房）")
        if custom_hotel and custom_room_type:
            hotels[custom_hotel] = [custom_room_type]
            st.success(f"已添加酒店：{custom_hotel}，房型：{custom_room_type}")

# 用户输入模块
hotel = st.sidebar.selectbox("选择酒店", list(hotels.keys()))
room_type = st.sidebar.selectbox("房型", hotels[hotel])
date = st.sidebar.date_input("入住日期", datetime.date.today())
holiday = st.sidebar.checkbox("是否为节假日")

# 成本设置
st.sidebar.markdown("---")
st.sidebar.markdown("**可选：自定义成本设置**")
cost = st.sidebar.number_input("单间房服务成本（元）", value=80)
ota_cut = st.sidebar.slider("OTA 抽成比率", 0.05, 0.3, value=0.15)

# 预测按钮
if st.button("🎯 生成建议定价"):
    price = predict_price(hotel, room_type, date, holiday, cost, ota_cut)
    st.success(f"📊 建议定价：￥{price:.2f}")
