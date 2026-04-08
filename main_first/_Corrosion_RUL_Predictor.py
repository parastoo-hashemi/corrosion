import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# main_first. بارگذاری فایل اکسل نهایی
# اگر فایل شما فرمت csv دارد، خط زیر را به read_csv تغییر دهید
file_path = 'Final_Corrosion_Data.xlsx'
try:
    df = pd.read_excel(file_path)
except:
    df = pd.read_csv(file_path)

# اطمینان از مرتب بودن داده‌ها
df = df.sort_values(by=['Sample', 'Week'])


# ---------------------------------------------------------
# 2. مهندسی ویژگی‌ها (ساختن دوباره ستون‌های متریال از روی اسم)
# ---------------------------------------------------------
def extract_features_from_name(sample_name):
    features = {}
    sample_name = str(sample_name)

    # آیا الیاف دارد؟ (VF)
    features['Has_Fiber'] = 1 if 'VF' in sample_name else 0

    # نوع مش (MI, SA, PA)
    if 'MI' in sample_name:
        features['Mesh_Type'] = 'MI'
    elif 'SA' in sample_name:
        features['Mesh_Type'] = 'SA'
    elif 'PA' in sample_name:
        features['Mesh_Type'] = 'PA'
    else:
        features['Mesh_Type'] = 'None'

    # سری ساخت (D, E, F, S...)
    if sample_name.startswith('S'):
        features['Series'] = sample_name[:2]  # S1, S2...
    else:
        features['Series'] = sample_name[0]  # D, E...

    return pd.Series(features)


# الحاق ویژگی‌های جدید به دیتاست
feat_df = df['Sample'].apply(extract_features_from_name)
df = pd.concat([df, feat_df], axis=1)

# تبدیل متن به عدد (Encoding)
le = LabelEncoder()
df['Mesh_Code'] = le.fit_transform(df['Mesh_Type'])
df['Series_Code'] = le.fit_transform(df['Series'])

# ---------------------------------------------------------
# 3. آماده‌سازی برای پیش‌بینی (Predict Next Week's Rust %)
# ---------------------------------------------------------
# هدف: بر اساس هفته فعلی و درصد فعلی، درصد هفته آینده را حدس بزن
df['Next_Rust_Pct'] = df.groupby('Sample')['Rust_Percentage'].shift(-1)
df['Next_Week'] = df.groupby('Sample')['Week'].shift(-1)

# محاسبه فاصله زمانی (Gap) - شاید همیشه ۱ هفته نباشد
df['Weeks_Gap'] = df['Next_Week'] - df['Week']

# حذف ردیف‌های آخر هر نمونه (چون آینده‌ای ندارند)
df_model = df.dropna(subset=['Next_Rust_Pct'])

# انتخاب ویژگی‌های ورودی (X)
features = ['Week', 'Rust_Percentage', 'Has_Fiber', 'Mesh_Code', 'Series_Code', 'Weeks_Gap']
X = df_model[features]
y = df_model['Next_Rust_Pct']
groups = df_model['Sample']

# تقسیم داده‌ها به آموزش و تست (بر اساس نمونه، نه رندوم)
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# ---------------------------------------------------------
# 4. آموزش مدل (Random Forest Regressor)
# ---------------------------------------------------------
rf = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
rf.fit(X_train, y_train)

# پیش‌بینی
y_pred = rf.predict(X_test)

# ---------------------------------------------------------
# 5. ارزیابی و نمودار
# ---------------------------------------------------------
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"--- Model Performance ---")
print(f"R2 Score (دقت مدل): {r2:.2f} (هرچه به 1 نزدیکتر، بهتر)")
print(f"RMSE (میانگین خطا): {rmse:.2f}%")

# رسم نمودار برای 4 نمونه تصادفی از داده‌های تست
test_samples = df_model.iloc[test_idx]['Sample'].unique()
selected_samples = np.random.choice(test_samples, size=min(4, len(test_samples)), replace=False)

plt.figure(figsize=(12, 10))

for i, sample in enumerate(selected_samples):
    plt.subplot(2, 2, i + 1)

    # داده‌های واقعی این نمونه
    sample_data = df_model[(df_model['Sample'] == sample) & (df_model.index.isin(X_test.index))]

    # مرتب‌سازی برای رسم زیبا
    sample_data = sample_data.sort_values(by='Week')

    # مقادیر واقعی و پیش‌بینی شده
    weeks = sample_data['Week']
    actual = sample_data['Next_Rust_Pct']
    predicted = rf.predict(sample_data[features])

    plt.plot(weeks, actual, 'b-o', label='Actual Data', linewidth=2)
    plt.plot(weeks, predicted, 'r--x', label='AI Prediction', linewidth=2)

    plt.title(f"Sample: {sample}")
    plt.xlabel("Current Week")
    plt.ylabel("Next Week Rust %")
    plt.legend()
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Final_Prediction_Results.png')
plt.show()

# نمودار اهمیت ویژگی‌ها
plt.figure(figsize=(8, 4))
plt.barh(features, rf.feature_importances_, color='teal')
plt.title("What affects corrosion growth most?")
plt.xlabel("Importance")
plt.show()