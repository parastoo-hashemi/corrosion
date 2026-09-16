import pandas as pd
import matplotlib.pyplot as plt
import re

# بارگذاری و تمیزکاری اولیه (همان کد قبلی)
file_path = 'Images_Dataset_A-Z.xlsx'
try:
    df = pd.read_excel(file_path)
except:
    df = pd.read_csv(file_path)


# تابع استخراج هفته و نام
def parse_id(row_id):
    parts = str(row_id).split('-')
    if len(parts) >= 3:
        sample_name = parts[0]
        week_str = parts[-1]
        week_match = re.search(r'\d+', week_str)
        week = int(week_match.group()) if week_match else 0
        return sample_name, week
    return None, None


parsed = df.iloc[:, 0].apply(parse_id)
df['Sample'] = [x[0] for x in parsed]
df['Week'] = [x[1] for x in parsed]
df = df.dropna(subset=['Sample', 'Week']).sort_values(by=['Sample', 'Week'])
target_col = df.columns[1]  # Metodo A

# --- بخش جدید: رسم نمودارهای تفکیک شده ---

# لیست سری‌های اصلی که می‌خواهیم ببینیم
series_to_plot = ['D', 'S', 'F']

plt.figure(figsize=(15, 5))

for i, series_prefix in enumerate(series_to_plot):
    plt.subplot(1, 3, i + 1)  # ایجاد ۳ نمودار کنار هم

    # فیلتر کردن: فقط نمونه‌هایی که با این حرف شروع می‌شوند (مثلاً D01, D02...)
    subset = df[df['Sample'].str.startswith(series_prefix)]

    # رسم هر نمونه در این سری
    for sample in subset['Sample'].unique():
        sample_data = subset[subset['Sample'] == sample]
        plt.plot(sample_data['Week'], sample_data[target_col], marker='.', label=sample)

    plt.title(f'Series {series_prefix} Corrosion Trend')
    plt.xlabel('Week')
    plt.ylabel('Category (Method A)')
    plt.grid(True, alpha=0.5)
    # plt.legend() # لجند را برداشتم تا نمودار شلوغ نشود

plt.tight_layout()
plt.show()