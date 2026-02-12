import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

# --- Settings ---
FAILURE_THRESHOLD = 10.0  # Failure limit (%)

print("⏳ Loading model and data...")
try:
    # Load models
    model = joblib.load('corrosion_model.pkl')

    le_series = joblib.load('series_encoder.pkl')

    # Load Excel file to automatically extract records
    try:
        df_data = pd.read_excel('Final_Corrosion_Data.xlsx')
    except:
        df_data = pd.read_csv('Final_Corrosion_Data.xlsx')

    print("✅ System is ready.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please make sure the .pkl files and the data file are present in the folder.")
    exit()

print("-" * 50)
print("🔮 Time Machine: Remaining Useful Life (RUL) Simulation")
print("-" * 50)

# 1. Get sample name from user
sample_name = input("Enter sample name (e.g., S4SAVF03): ").strip()

# 2. Automatic lookup in database
sample_data = df_data[df_data['Sample'] == sample_name].sort_values(by='Week')

if sample_data.empty:
    print("❌ Sample not found in the dataset!")
    exit()

# Last recorded state
last_record = sample_data.iloc[-1]
current_week = int(last_record['Week'])
current_rust = float(last_record['Rust_Percentage'])

# Previous week (for growth rate)
if len(sample_data) > 1:
    prev_record = sample_data.iloc[-2]
    prev_rust = float(prev_record['Rust_Percentage'])
else:
    prev_rust = 0.0

print(f"\n📊 Retrieved data for {sample_name}:")
print(f"   - Last recorded week: {current_week}")
print(f"   - Current corrosion level: {current_rust:.3f}%")
print(f"   - Previous corrosion level: {prev_rust:.3f}%")
print("   (Simulation automatically starts from this point...)")

# Extract static sample features
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

# 3. Simulation Loop
future_weeks = [current_week]
future_rust = [current_rust]
rust_change = current_rust - prev_rust

temp_rust = current_rust
temp_week = current_week

# Run until failure threshold or 150 weeks
while temp_rust < FAILURE_THRESHOLD and temp_week < 150:

    input_data = pd.DataFrame(
        [[temp_week, temp_rust, rust_change, has_fiber, mesh, series_code]],
        columns=['Week', 'Rust_Percentage', 'Rust_Change', 'Has_Fiber', 'Mesh', 'Series_Code']
    )

    # Predict next week
    pred_log = model.predict(input_data)
    next_rust = np.expm1(pred_log)[0]

    # Update growth rate
    new_change = next_rust - temp_rust

    # Corrective logic: add inertia to corrosion growth
    rust_change = (rust_change * 0.7) + (new_change * 0.3)

    # Prevent corrosion decrease
    if next_rust < temp_rust:
        next_rust = temp_rust + 0.001

    temp_rust = next_rust
    temp_week += 1

    future_weeks.append(temp_week)
    future_rust.append(temp_rust)

# 4. Results
rul = temp_week - current_week
print(f"\n🏁 Prediction Result:")
print(f"💀 Estimated failure time (10%): Week {temp_week}")
print(f"⏳ Remaining Useful Life (RUL): {rul} weeks")

# 5. Plot
plt.figure(figsize=(10, 6))

# Safe zone
plt.axhspan(0, FAILURE_THRESHOLD, color='green', alpha=0.1, label='Safe Zone')

# Failure threshold
plt.axhline(
    FAILURE_THRESHOLD,
    color='red',
    linestyle='--',
    linewidth=2,
    label=f'Failure Threshold ({FAILURE_THRESHOLD}%)'
)

# Historical data
plt.plot(
    sample_data['Week'],
    sample_data['Rust_Percentage'],
    'gray',
    marker='.',
    linestyle=':',
    label='Historical Data'
)

# Prediction path
plt.plot(
    future_weeks,
    future_rust,
    color='blue',
    linewidth=3,
    label='AI Prediction Path'
)

# Start point
plt.scatter(
    [current_week],
    [current_rust],
    color='black',
    s=100,
    zorder=5,
    label='Start of Prediction'
)

plt.title(
    f"RUL Prediction for {sample_name}\nEstimated Remaining Life: {rul} Weeks",
    fontsize=14
)
plt.xlabel("Time (Weeks)")
plt.ylabel("Corrosion Percentage (%)")
plt.legend()
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.savefig(f"RUL_Prediction_{sample_name}.png")
plt.show()

print(f"🖼 Chart saved as: RUL_Prediction_{sample_name}.png")
