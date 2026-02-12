import pandas as pd
import matplotlib.pyplot as plt
import re

# --- تنظیمات فایل ---
# نام فایل اکسل خود را اینجا وارد کنید
file_path = 'Images_Dataset_A-Z.xlsx'

# بارگذاری داده‌ها
# اگر فایل شما فرمت CSV دارد از pd.read_csv استفاده کنید
try:
    df = pd.read_excel(file_path)
except:
    df = pd.read_csv(file_path)

# --- تابع برای استخراج اطلاعات از ستون ID ---
def parse_id(row_id):
    # فرض بر این است که فرمت به صورت SampleID-Date-Week است
    # مثال: D01-20240110-0W
    parts = str(row_id).split('-')
    if len(parts) >= 3:
        sample_name = parts[0]
        week_str = parts[-1]
        # استخراج عدد هفته از رشته (مثلاً '2W' -> 2)
        week_match = re.search(r'\d+', week_str)
        week = int(week_match.group()) if week_match else 0
        return sample_name, week
    return None, None

# اعمال تابع روی ستون ID
# فرض می‌کنیم ستون اول ID است. اگر نام ستون را می‌دانید جایگزین کنید: df['ID']
id_col = df.columns[0]
target_col = df.columns[1] # فرض بر اینکه ستون دوم کلاس خوردگی است (Metodo A)

parsed_data = df[id_col].apply(lambda x: parse_id(x))
df['Sample'] = [x[0] for x in parsed_data]
df['Week'] = [x[1] for x in parsed_data]

# حذف ردیف‌هایی که به درستی خوانده نشده‌اند
df_clean = df.dropna(subset=['Week', 'Sample'])
df_clean = df_clean.sort_values(by=['Sample', 'Week'])

# --- رسم نمودار ---
plt.figure(figsize=(14, 8))

# لیست نمونه‌های یکتا
unique_samples = df_clean['Sample'].unique()

# برای شلوغ نشدن نمودار، فقط 15 نمونه اول را رسم می‌کنیم (می‌توانید [:15] را حذف کنید تا همه را ببینید)
for sample in unique_samples[:15]:
    subset = df_clean[df_clean['Sample'] == sample]
    plt.plot(subset['Week'], subset[target_col], marker='o', label=sample)

plt.title('Corrosion Category Progression Over Time', fontsize=16)
plt.xlabel('Week', fontsize=14)
plt.ylabel('Corrosion Category (1-5)', fontsize=14)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Samples')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()