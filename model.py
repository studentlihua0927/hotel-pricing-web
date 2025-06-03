import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 1. 加载数据（请将路径替换为你本地的 Excel 文件）
df = pd.read_excel("梅溪半岛三家酒店日营业状况对照表（25.5）.xlsx")

# 2. 仅选择欢朋酒店数据 + "舒适大床房" 为例
hp_room = df[(df["酒店名称"] == "欢朋酒店") & (df["房型"] == "舒适大床房")].copy()

# 3. 添加节假日、是否周末、日期等基本特征
holiday_dates = ["2025-05-01", "2025-06-01"]
hp_room["日期"] = pd.to_datetime(hp_room["日期"])
hp_room["day"] = hp_room["日期"].dt.day
hp_room["is_weekend"] = hp_room["日期"].dt.weekday >= 5
hp_room["is_weekend"] = hp_room["is_weekend"].astype(int)
hp_room["is_holiday"] = hp_room["日期"].astype(str).isin(holiday_dates).astype(int)

# 4. 构造模拟入住率（根据房型热度 + 噪声）
heat_coefs = {
    "舒适大床房": 1.10,
    "高级大床房": 1.08,
    "舒适双床房": 1.05,
    "高级双床房": 1.00,
    "豪华湖景双床房": 0.90,
    "豪华湖景大床房": 0.85,
    "欢朋套房": 0.80
}
np.random.seed(42)
base_occ = hp_room["入住率"]
noise = np.random.normal(loc=1.0, scale=0.05, size=len(base_occ))
coef = heat_coefs["舒适大床房"]
hp_room["模拟入住率"] = np.clip(base_occ * coef * noise, 0, 1)

# 5. 准备模型训练数据
X = hp_room[["模拟房价", "day", "is_weekend", "is_holiday"]]
y = hp_room["模拟入住率"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. 模型训练
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# 7. 保存模型
model.save_model("hp_xgb_model.json")

print("模型训练完成并已保存为 hp_xgb_model.json")
