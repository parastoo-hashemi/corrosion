import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# 1. Load Data
file_path = 'Images_Dataset_A-Z.xlsx - Foglio1.csv'
try:
    df = pd.read_csv(file_path)
except:
    # Fallback if needed, though CSV read worked before
    df = pd.read_excel('Images_Dataset_A-Z.xlsx')


# 2. Basic Parsing (ID -> Sample, Week)
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
df = df.dropna(subset=['Sample', 'Week'])

# Rename Target
target_col = df.columns[1]  # Assuming 2nd column is Method A
df.rename(columns={target_col: 'Category'}, inplace=True)


# ---------------------------------------------------------
# 3. ADVANCED FEATURE ENGINEERING (The New Part)
# ---------------------------------------------------------

def extract_material_features(sample_name):
    features = {}

    # Feature 1: Has Fiber? (VF indicates Vetro Fibra / Steel Fiber)
    features['Has_Fiber'] = 1 if 'VF' in sample_name else 0

    # Feature 2: Mesh Type (MI=Mesh Iron, SA=Square, PA=Polygonal)
    if 'MI' in sample_name:
        features['Mesh_Type'] = 'MI'
    elif 'SA' in sample_name:
        features['Mesh_Type'] = 'SA'
    elif 'PA' in sample_name:
        features['Mesh_Type'] = 'PA'
    else:
        features['Mesh_Type'] = 'None'  # For D, E, F, G series or pure fiber

    # Feature 3: Campaign (S series vs others)
    features['Campaign'] = 'Campaign_1' if sample_name.startswith('S') else 'Campaign_2'

    # Feature 4: Base Material Series (D, E, F, G, S1, S2...)
    # We take the first letter for Campaign 2, or first 2 chars for Campaign 1
    if sample_name.startswith('S'):
        features['Base_Series'] = sample_name[:2]  # S1, S2, S3...
    else:
        features['Base_Series'] = sample_name[0]  # D, E, F...

    return pd.Series(features)


# Apply the feature extraction
df_features = df['Sample'].apply(extract_material_features)
df = pd.concat([df, df_features], axis=1)

# Encode Categorical Features to Numbers
le_mesh = LabelEncoder()
df['Mesh_Type_Code'] = le_mesh.fit_transform(df['Mesh_Type'])

le_campaign = LabelEncoder()
df['Campaign_Code'] = le_campaign.fit_transform(df['Campaign'])

le_base = LabelEncoder()
df['Base_Series_Code'] = le_base.fit_transform(df['Base_Series'])

# ---------------------------------------------------------

# Prepare for Modeling (Next Week Prediction)
df = df.sort_values(by=['Sample', 'Week'])
df['Next_Category'] = df.groupby('Sample')['Category'].shift(-1)
df_model = df.dropna(subset=['Next_Category'])

# Select Features (X) - Now including our engineered features
features_list = ['Week', 'Category', 'Has_Fiber', 'Mesh_Type_Code', 'Campaign_Code', 'Base_Series_Code']
X = df_model[features_list]
y = df_model['Next_Category']
groups = df_model['Sample']

# Train/Test Split
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))
X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# Train Model
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Evaluate
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Improved Model Accuracy: {acc:.2f}")

# ---------------------------------------------------------
# 4. Feature Importance Plot (To show WHAT matters)
# ---------------------------------------------------------
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]
feature_names = X.columns

plt.figure(figsize=(10, 6))
plt.title("What Drives Corrosion? (Feature Importance)")
plt.bar(range(X.shape[1]), importances[indices], align="center", color='teal')
plt.xticks(range(X.shape[1]), [feature_names[i] for i in indices], rotation=45)
plt.ylabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.show()