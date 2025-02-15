import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.dates as mdates

# 设置全局字体为 Microsoft YaHei（微软雅黑）
rcParams['font.sans-serif'] = ['Microsoft YaHei']
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 歷年資料夾
dirs = [d for d in os.listdir() if d[:4] == 'real']

dfs = []

for d in dirs:
    print(d)
    df = pd.read_csv(os.path.join(d,'a_lvr_land_a.csv'), index_col=False,low_memory=False)
    df['Q'] = d[-1]
    dfs.append(df.iloc[1:])
    
df = pd.concat(dfs, sort=True)
print(df.columns)

# 新增交易年份
df['year'] = df['交易年月日'].str[:-4].astype(int) + 1911

# 不同名稱同項目資料合併
# df['單價元平方公尺'].fillna(df['單價元/平方公尺'], inplace=True)
# df.drop(columns='單價元/平方公尺')

# 平方公尺換成坪
df['單價元平方公尺'] = df['單價元平方公尺'].astype(float)
df['單價元坪'] = df['單價元平方公尺'] * 3.30579

# 建物型態
df['建物型態2'] = df['建物型態'].str.split('(').str[0]

# 刪除有備註之交易（多為親友交易、價格不正常之交易）
df = df[df['備註'].isnull()]
try:
    df['year'] = df['交易年月日'].astype(str).str[:-4].astype(int) + 1911
except Exception as e:
    error_rows = df[~df['交易年月日'].astype(str).str[:-4].str.isnumeric()]
    print("無法轉換的資料行：")
    print(error_rows)
    raise e

# 1. 將日期轉為字串
df['交易年月日'] = df['交易年月日'].astype(str)

# 2. 過濾出純數字資料
df = df[df['交易年月日'].str.isnumeric()]

# 3. 忽略錯誤並處理缺失值
# df['year'] = pd.to_numeric(df['交易年月日'].str[:-4], errors='coerce').fillna(0).astype(int) + 1911


# 將index改成年月日
df.index =df['year']

prices = {}
for district in set(df['鄉鎮市區']):
    cond = (
        (df['主要用途'] == '住家用')
        & (df['鄉鎮市區'] == district)
        & (df['單價元坪'] < df["單價元坪"].quantile(0.95))
        & (df['單價元坪'] > df["單價元坪"].quantile(0.05))
        )
    
    groups = df[cond]['year']
    
    prices[district] = df[cond]['單價元坪'].astype(float).groupby(groups).mean().loc[2012:]
    
price_history = pd.DataFrame(prices)
price_history.plot()

plt.figure(figsize=(12, 6))  # 調整圖表大小
price_history.plot(linewidth=2.0, alpha=0.8)  # 加粗線條，並調整透明度
plt.title('台北市各區域歷年平均單價', fontsize=16)
plt.xlabel('年份', fontsize=12)
plt.ylabel('單價 (元/坪)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)  # 加入網格線
plt.legend(fontsize=8, loc='upper left', ncol=2)  # 調整圖例
plt.show()
