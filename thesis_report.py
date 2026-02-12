# نام فایل: 1_thesis_report.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import LabelEncoder

# 1. بارگذاری داده‌ها
print("⏳ در حال خواندن فایل اکسل...")
try:
    df = pd.read_excel('Final_Corrosion_Data.xlsx')
except:
    df = pd.read_csv('Final_Corrosion_Data.xlsx')  # اگر فرمت csv بود

df = df.sort_values(by=['Sample', 'Week'])


# 2. مهندسی ویژگی‌ها (Feature Engineering)
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
df['Series_Code'] = LabelEncoder().fit_transform(df['Series'])

# ساخت ستون‌های هدف (لگاریتمی برای دقت بالاتر)
df['Log_Rust'] = np.log1p(df['Rust_Percentage'])
df['Prev_Rust'] = df.groupby('Sample')['Rust_Percentage'].shift(1).fillna(0)
df['Rust_Change'] = df['Rust_Percentage'] - df['Prev_Rust']
df['Next_Rust_Pct'] = df.groupby('Sample')['Rust_Percentage'].shift(-1)

# حذف ردیف‌های آخر که آینده ندارند
df_model = df.dropna(subset=['Next_Rust_Pct'])
df_model['Log_Next_Rust'] = np.log1p(df_model['Next_Rust_Pct'])

# 3. تقسیم به Train و Test
features = ['Week', 'Rust_Percentage', 'Rust_Change', 'Has_Fiber', 'Mesh', 'Series_Code']
X = df_model[features]
y = df_model['Log_Next_Rust']
groups = df_model['Sample']

splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# 4. آموزش مدل
print("⚙️ در حال آموزش مدل روی داده‌های آموزشی...")
rf = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42)
rf.fit(X_train, y_train)

# 5. ارزیابی (تست)
y_pred_log = rf.predict(X_test)
y_pred_real = np.expm1(y_pred_log)  # تبدیل برگشتی از لگاریتم به عدد واقعی
y_test_real = np.expm1(y_test)

r2 = r2_score(y_test_real, y_pred_real)
rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))

print("\n" + "=" * 40)
print(f"📊 نتایج نهایی برای پایان‌نامه:")
print(f"✅ دقت مدل (R2 Score): {r2:.3f}")
print(f"✅ میانگین خطا (RMSE): {rmse:.3f}%")
print("=" * 40)

# 6. رسم نمودار و ذخیره
plt.figure(figsize=(8, 6))
plt.scatter(y_test_real, y_pred_real, alpha=0.6, color='purple')
plt.plot([0, max(y_test_real)], [0, max(y_test_real)], 'r--', lw=2)
plt.xlabel("Actual Corrosion (%)")
plt.ylabel("AI Predicted Corrosion (%)")
plt.title(f"AI Model Accuracy (R2 = {r2:.2f})")
plt.grid(True)
plt.savefig("Thesis_Accuracy_Plot.png")
print("🖼 نمودار 'Thesis_Accuracy_Plot.png' ذخیره شد.")