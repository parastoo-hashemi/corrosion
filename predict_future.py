import pandas as pd
import numpy as np
import joblib

# 1. لود کردن مدل و داده‌ها
print("⏳ در حال بارگذاری سیستم...")
try:
    # لود کردن مدل‌ها
    model = joblib.load('corrosion_model.pkl')
    le_series = joblib.load('series_encoder.pkl')

    # لود کردن دیتابیس برای پیدا کردن اتوماتیک اطلاعات
    try:
        df_data = pd.read_excel('Final_Corrosion_Data.xlsx')
    except:
        df_data = pd.read_csv('Final_Corrosion_Data.xlsx')

    print("🤖 هوش مصنوعی آماده است!")
except Exception as e:
    print(f"❌ خطا: {e}")
    print("مطمئن شوید فایل‌های pkl و فایل اکسل در کنار برنامه هستند.")
    exit()

print("-" * 40)
print("🔮 سیستم پیش‌بینی هوشمند (فقط هفته آینده)")
print("-" * 40)

# 2. دریافت ورودی (فقط نام نمونه)
sample_name = input("نام نمونه را وارد کنید (مثلاً S4SAVF03): ").strip()

# 3. جستجو در اکسل
sample_data = df_data[df_data['Sample'] == sample_name].sort_values(by='Week')

if sample_data.empty:
    print(f"❌ خطا: نمونه '{sample_name}' در فایل اکسل پیدا نشد!")
    exit()

# استخراج آخرین وضعیت ثبت شده
last_record = sample_data.iloc[-1]
current_week = int(last_record['Week'])
current_rust = float(last_record['Rust_Percentage'])

# استخراج وضعیت هفته قبل (برای محاسبه تغییرات)
if len(sample_data) > 1:
    prev_record = sample_data.iloc[-2]
    prev_rust = float(prev_record['Rust_Percentage'])
else:
    prev_rust = 0.0

rust_change = current_rust - prev_rust

print(f"\n📊 آخرین وضعیت یافت شده در پایگاه داده:")
print(f"   - هفته جاری: {current_week}")
print(f"   - زنگ‌زدگی فعلی: {current_rust:.4f}%")
print(f"   - تغییر نسبت به قبل: {rust_change:.4f}%")

# 4. آماده‌سازی ویژگی‌ها برای هوش مصنوعی
has_fiber = 1 if 'VF' in sample_name else 0

mesh = 0
if 'MI' in sample_name:
    mesh = 1
elif 'SA' in sample_name:
    mesh = 2
elif 'PA' in sample_name:
    mesh = 3

series_str = sample_name[:2] if sample_name.startswith('S') else sample_name[0]
try:
    series_code = le_series.transform([series_str])[0]
except:
    series_code = 0

# ساخت پکیج داده (دقیقاً با ستون‌های زمان آموزش)
input_data = pd.DataFrame([[current_week, current_rust, rust_change, has_fiber, mesh, series_code]],
                          columns=['Week', 'Rust_Percentage', 'Rust_Change', 'Has_Fiber', 'Mesh', 'Series_Code'])

# 5. پیش‌بینی
predicted_log = model.predict(input_data)
predicted_real = np.expm1(predicted_log)[0]

# جلوگیری از پیش‌بینی منفی یا کاهش غیرمنطقی (اختیاری)
if predicted_real < current_rust:
    predicted_real = current_rust * 1.01  # حداقل یک درصد رشد

print("\n" + "*" * 40)
print(f"📅 پیش‌بینی برای هفته آینده (هفته {current_week + 1}):")
print(f"⚠️ میزان خوردگی به **{predicted_real:.4f}%** خواهد رسید.")
print("*" * 40)

input("\nبرای خروج اینتر بزنید...")