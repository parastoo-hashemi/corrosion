import os
import cv2
import pandas as pd
import numpy as np
import re

# ================= تنظیمات =================
# آدرس پوشه‌ای که ۷۹۲ عکس شما در آن است را اینجا بنویسید
# مثال ویندوز: r"C:\Users\Name\Desktop\Corrosion_Photos"
FOLDER_PATH = r"C:\Users\parastoo\PycharmProjects\PythonProject\Images_dataset\Images_dataset"


# ================= بدنه اصلی کد =================
def process_batch_images(folder_path):
    results = []

    # تنظیمات رنگ زنگ‌زدگی (بر اساس پروژه شما)
    lower_rust = np.array([50, 0, 0])
    upper_rust = np.array([255, 100, 80])

    # لیست کردن تمام عکس‌ها
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tif'}
    try:
        files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in valid_extensions]
    except FileNotFoundError:
        print(f"خطا: پوشه {folder_path} پیدا نشد!")
        return pd.DataFrame()

    print(f"شروع پردازش {len(files)} تصویر...")

    for i, filename in enumerate(files):
        # نمایش پیشرفت کار هر 50 عکس
        if i % 50 == 0:
            print(f"Processing image {i}/{len(files)}...")

        file_path = os.path.join(folder_path, filename)

        # main_first. خواندن و تبدیل رنگ
        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            continue
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # 2. محاسبه درصد زنگ‌زدگی
        rust_mask = cv2.inRange(img_rgb, lower_rust, upper_rust)
        total_pixels = img_rgb.shape[0] * img_rgb.shape[1]
        rust_pixels = cv2.countNonZero(rust_mask)
        rust_pct = (rust_pixels / total_pixels) * 100

        # 3. استخراج اطلاعات از نام فایل
        # فرمت: S4SAVF03-20220603-2W.png
        name_body = os.path.splitext(filename)[0]
        parts = name_body.split('-')

        sample_name = "Unknown"
        week = 0

        if len(parts) >= 3:
            sample_name = parts[0]
            # پیدا کردن عدد هفته (Week)
            week_str = parts[-1]
            week_match = re.search(r'\d+', week_str)
            if week_match:
                week = int(week_match.group())
        else:
            sample_name = name_body  # اگر نام فایل استاندارد نبود

        # 4. ذخیره نتیجه
        results.append({
            'Filename': filename,
            'Sample': sample_name,
            'Week': week,
            'Rust_Percentage': rust_pct
        })

    # تبدیل به اکسل
    df_results = pd.DataFrame(results)
    return df_results


# اجرای تابع
if __name__ == "__main__":
    df = process_batch_images(FOLDER_PATH)

    if not df.empty:
        output_file = "Final_Corrosion_Data.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\nتمام شد! فایل '{output_file}' ساخته شد.")
        print(df.head())
    else:
        print("هیچ عکسی پردازش نشد.")