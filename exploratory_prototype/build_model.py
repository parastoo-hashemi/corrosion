# نام فایل: 2_build_model.py
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

print("🏗 در حال ساخت مدل نهایی روی تمام داده‌ها...")

# main_first. بارگذاری داده
try:
    df = pd.read_excel('Final_Corrosion_Data.xlsx')
except:
    df = pd.read_csv('Final_Corrosion_Data.xlsx')

df = df.sort_values(by=['Sample', 'Week'])


# 2. مهندسی ویژگی‌ها
def extract_features(row):
    name = str(row['Sample'])
    feats = {'Has_Fiber': 1 if 'VF' in name else 0}
    if 'MI' in name:
        feats['Mesh'] = 1
    elif 'SA' in name:
        feats['Mesh'] = 2
    elif 'PA' in name:
        feats['Mesh'] = 3
    else:
        feats['Mesh'] = 0
    feats['Series'] = name[:2] if name.startswith('S') else name[0]
    return pd.Series(feats)


feat_df = df.apply(extract_features, axis=1)
df = pd.concat([df, feat_df], axis=1)

# ذخیره اینکودر برای استفاده بعدی
le_series = LabelEncoder()
df['Series_Code'] = le_series.fit_transform(df['Series'])

# آماده‌سازی تارگت
df['Log_Rust'] = np.log1p(df['Rust_Percentage'])
df['Prev_Rust'] = df.groupby('Sample')['Rust_Percentage'].shift(1).fillna(0)
df['Rust_Change'] = df['Rust_Percentage'] - df['Prev_Rust']
df['Next_Rust_Pct'] = df.groupby('Sample')['Rust_Percentage'].shift(-1)
df_model = df.dropna(subset=['Next_Rust_Pct'])
df_model['Log_Next_Rust'] = np.log1p(df_model['Next_Rust_Pct'])

features = ['Week', 'Rust_Percentage', 'Rust_Change', 'Has_Fiber', 'Mesh', 'Series_Code']
X = df_model[features]
y = df_model['Log_Next_Rust']

# 3. آموزش مدل نهایی
rf_final = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42)
rf_final.fit(X, y)

# 4. ذخیره فایل‌ها
joblib.dump(rf_final, 'corrosion_model.pkl')
joblib.dump(le_series, 'series_encoder.pkl')

print("✅ مدل ساخته شد و در فایل 'corrosion_model.pkl' ذخیره گردید.")