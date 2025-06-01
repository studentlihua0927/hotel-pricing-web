import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = "model_grown_from_month_data.pkl"

# 模型加载
try:
    model = joblib.load(MODEL_PATH)
except:
    model = RandomForestRegressor(n_estimators=100, random_state=42)

# 成本基准（可通过网页传入自定义）
BASE_COSTS = {
    "大床房": 120,
    "双床房": 135,
    "湖景房": 160,
    "套房": 300
}
DEFAULT_OTA_CUT = 0.15

def predict_price(hotel, room_type, date, holiday=False, custom_cost=None, ota_cut=None):
    """
    主力函数：根据酒店、房型、时间等预测最优定价
    """
    base_rate = 0.9 if not holiday else 0.97
    sensitivity = 0.0015 if not holiday else 0.002

    cost = custom_cost if custom_cost is not None else BASE_COSTS.get(room_type, 140)
    cut = ota_cut if ota_cut is not None else DEFAULT_OTA_CUT

    best_profit = -1
    best_price = 300  # 初始参考起点
    price_range = range(180, 801, 5)  # 搜索价格空间

    for p in price_range:
        # 预测入住率 r
        feature = [[hotel, room_type, date.month, p]]
        try:
            r = model.predict(feature)[0]
        except:
            r = base_rate - sensitivity * (p - 200)
        profit = r * (p * (1 - cut) - cost)
        if profit > best_profit:
            best_profit = profit
            best_price = p

             return best_price

def retrain_model_from_excel(file_path, sheet_name=None):
    """
    用新数据更新模型
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.dropna(subset=['hotel', 'room_type', 'month', 'price', 'occupancy_rate'])

    X = df[['hotel', 'room_type', 'month', 'price']].values
    y = df['occupancy_rate'].values

    model_new = RandomForestRegressor(n_estimators=100, random_state=42)
    model_new.fit(X, y)
    joblib.dump(model_new, MODEL_PATH)
    return "模型已根据新数据更新。"



