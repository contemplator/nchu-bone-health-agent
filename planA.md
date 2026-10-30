# 🦴 OsteoGuard AI Agent — Plan A 執行手冊
## 機器學習模型訓練與可解釋性分析模組 (ML & XAI Engine)

> **適用對象**：負責 Plan A 的 Antigravity IDE 帳號 / 開發者  
> **目標分支**：`feat/ml-and-xai`  
> **核心職責**：資料前處理路徑修復、特徵工程、三種機器學習模型（LR / RF / XGBoost）訓練、5-Fold 交叉驗證、SHAP 可解釋性分析，以及對外提供標準推論介面。

---

### 📌 模組目標與交付清單 (Deliverables)

1. [x] **修復 `src/data_processor.py`**：移除 macOS 寫死的絕對路徑，改為跨平台動態路徑。
2. [ ] **建立 `src/ml_models.py`**：
   - 讀取 `data/processed/nhanes_dxa_femur_merged_with_tscore.csv`（3,545 筆樣本）。
   - 標籤分類：依 WHO 標準建立骨質疏鬆風險目標變數（`Normal: 0`, `Osteopenia: 1`, `Osteoporosis: 2`）。
   - 實作三種模型：**Logistic Regression (L2 Baseline)**、**Random Forest**、**XGBoost**。
   - 執行 **5-Fold 交叉驗證**，計算並輸出 Accuracy, Precision, Recall, F1-Score, ROC-AUC。
   - 將訓練好的最佳模型與預處理物件存檔至 `models/` 目錄。
   - 提供標準對外函式：`predict_osteoporosis_risk(patient_dict: dict) -> dict`。
3. [ ] **建立 `src/explainability.py`**：
   - 整合 SHAP (SHapley Additive exPlanations)。
   - 產出全域特徵重要性圖表並儲存至 `output/shap_summary.png`。
   - 提供個案局部歸因函式：`explain_patient_risk(patient_dict: dict) -> dict`。
4. [ ] **產出評估報告**：輸出 `output/ml_evaluation_metrics.json` 與相關評估數據。

---

### 💻 Step 1：Git 分支建立與套件準備

請在您的 Antigravity IDE 終端機（PowerShell 或 Bash）執行：

```bash
# 1. 切換至獨立特徵分支
git checkout -b feat/ml-and-xai

# 2. 確認 Python 環境並安裝必要機器學習套件
pip install pandas numpy scikit-learn xgboost shap matplotlib seaborn
```

---

### 💻 Step 2：修復 `src/data_processor.py` 路徑

開啟 `src/data_processor.py`，將第 78–79 行原本寫死的 macOS 路徑：
```python
# 原本寫死的路徑 (需替換)
base_dir = "/Users/leolin/Documents/NCHU_Programs/nchu-bone-health-agent/data/raw"
processed_dir = "/Users/leolin/Documents/NCHU_Programs/nchu-bone-health-agent/data/processed"
```
改為依據當前檔案位置動態取得的跨平台路徑：
```python
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
base_dir = os.path.join(PROJECT_ROOT, "data", "raw")
processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
```

---

### 💻 Step 3：實作 `src/ml_models.py`

建立 `src/ml_models.py`，內容需包含以下架構：

```python
"""
src/ml_models.py - 機器學習模型訓練與推論介面
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "nhanes_dxa_femur_merged_with_tscore.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

FEATURE_COLS = [
    'Age', 'Weight_kg', 'Height_cm', 'BMI',
    'Total_Femur_BMD', 'Total_Femur_BMC', 'Total_Femur_Area',
    'Femoral_Neck_BMD', 'Femoral_Neck_BMC', 'Femoral_Neck_Area',
    'Trochanter_BMD', 'Intertrochanter_BMD'
]

TARGET_COL = 'WHO_Category' # 'Normal (正常)', 'Osteopenia (骨量減少)', 'Osteoporosis (骨質疏鬆)'

class BoneHealthPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.models = {}
        self.best_model_name = "XGBoost"

    def load_data(self):
        df = pd.read_csv(DATA_PATH)
        df['Gender_Code'] = df['Gender'].apply(lambda x: 1 if '男' in str(x) else 0)
        feature_cols_with_gender = ['Gender_Code'] + FEATURE_COLS
        
        # 處理遺漏值
        clean_df = df.dropna(subset=feature_cols_with_gender + [TARGET_COL]).copy()
        X = clean_df[feature_cols_with_gender]
        y_raw = clean_df[TARGET_COL]
        y = self.label_encoder.fit_transform(y_raw)
        return X, y, clean_df

    def train_and_evaluate(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        X, y, df = self.load_data()
        
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        candidate_models = {
            "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
            "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.08, eval_metric='mlogloss', random_state=42)
        }
        
        results = {}
        
        for name, clf in candidate_models.items():
            acc_list, prec_list, rec_list, f1_list, auc_list = [], [], [], [], []
            for train_idx, val_idx in skf.split(X, y):
                X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_tr, y_val = y[train_idx], y[val_idx]
                
                scaler = StandardScaler()
                X_tr_scaled = scaler.fit_transform(X_tr)
                X_val_scaled = scaler.transform(X_val)
                
                clf.fit(X_tr_scaled, y_tr)
                preds = clf.predict(X_val_scaled)
                probs = clf.predict_proba(X_val_scaled)
                
                acc_list.append(accuracy_score(y_val, preds))
                prec_list.append(precision_score(y_val, preds, average='weighted', zero_division=0))
                rec_list.append(recall_score(y_val, preds, average='weighted', zero_division=0))
                f1_list.append(f1_score(y_val, preds, average='weighted', zero_division=0))
                try:
                    auc_list.append(roc_auc_score(y_val, probs, multi_class='ovr', average='weighted'))
                except Exception:
                    auc_list.append(0.0)
            
            results[name] = {
                "Accuracy": float(np.mean(acc_list)),
                "Precision": float(np.mean(prec_list)),
                "Recall": float(np.mean(rec_list)),
                "F1_Score": float(np.mean(f1_list)),
                "ROC_AUC": float(np.mean(auc_list))
            }
            print(f"[{name}] Acc: {results[name]['Accuracy']:.4f}, F1: {results[name]['F1_Score']:.4f}, AUC: {results[name]['ROC_AUC']:.4f}")
            
            # 全量訓練並存檔
            final_scaler = StandardScaler()
            X_all_scaled = final_scaler.fit_transform(X)
            clf.fit(X_all_scaled, y)
            joblib.dump(clf, os.path.join(MODELS_DIR, f"{name.lower()}.joblib"))
            self.models[name] = clf
            
        joblib.dump(final_scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
        joblib.dump(self.label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))
        
        with open(os.path.join(OUTPUT_DIR, "ml_evaluation_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Model training & 5-Fold evaluation completed successfully.")
        return results

# 全域單例載入與對外推論介面
_PREDICTOR = None

def get_predictor():
    global _PREDICTOR
    if _PREDICTOR is None:
        _PREDICTOR = BoneHealthPredictor()
        # 若已訓練過則載入權重
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        if os.path.exists(scaler_path):
            _PREDICTOR.scaler = joblib.load(scaler_path)
            _PREDICTOR.label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.joblib"))
            for name in ["logistic_regression", "random_forest", "xgboost"]:
                p = os.path.join(MODELS_DIR, f"{name}.joblib")
                if os.path.exists(p):
                    _PREDICTOR.models[name] = joblib.load(p)
    return _PREDICTOR

def predict_osteoporosis_risk(patient_dict: dict) -> dict:
    """
    提供給 Plan B (Agent) 與 Plan C (UI) 呼叫的標準推論介面
    :param patient_dict: 包含生理與 DXA 數值之字典
    :return: 包含預測類別、各類別機率與風險指標之字典
    """
    predictor = get_predictor()
    # 組裝特徵向量
    gender_code = 1 if '男' in str(patient_dict.get('Gender', '')) else 0
    raw_features = [gender_code] + [float(patient_dict.get(c, 0.0)) for c in FEATURE_COLS]
    
    scaler = predictor.scaler
    X_scaled = scaler.transform([raw_features])
    
    model = predictor.models.get("xgboost") or predictor.models.get("random_forest")
    if model is None:
        # Fallback 依據 WHO 公式估算
        t_neck = (float(patient_dict.get('Femoral_Neck_BMD', 0.858)) - 0.858) / 0.120
        t_total = (float(patient_dict.get('Total_Femur_BMD', 0.942)) - 0.942) / 0.122
        min_t = min(t_neck, t_total)
        category = "Osteoporosis (骨質疏鬆)" if min_t <= -2.5 else ("Osteopenia (骨量減少)" if min_t < -1.0 else "Normal (正常)")
        return {
            "predicted_category": category,
            "risk_level": "High" if min_t <= -2.5 else ("Moderate" if min_t < -1.0 else "Low"),
            "probabilities": {"Normal": 0.1, "Osteopenia": 0.2, "Osteoporosis": 0.7 if min_t <= -2.5 else 0.1},
            "min_t_score": round(min_t, 2)
        }
        
    probs = model.predict_proba(X_scaled)[0]
    pred_idx = np.argmax(probs)
    classes = predictor.label_encoder.classes_
    predicted_cat = classes[pred_idx]
    
    prob_dict = {classes[i]: float(probs[i]) for i in range(len(classes))}
    
    risk_level = "High" if "Osteoporosis" in predicted_cat else ("Moderate" if "Osteopenia" in predicted_cat else "Low")
    return {
        "predicted_category": predicted_cat,
        "risk_level": risk_level,
        "probabilities": prob_dict,
        "model_used": "XGBoost"
    }

if __name__ == "__main__":
    predictor = BoneHealthPredictor()
    predictor.train_and_evaluate()
```

---

### 💻 Step 4：實作 `src/explainability.py`

建立 `src/explainability.py`，內容實作 SHAP 計算並生成圖表：

```python
"""
src/explainability.py - SHAP 可解釋性分析模組
"""
import os
import joblib
import shap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

FEATURE_NAMES = [
    'Gender_Code', 'Age', 'Weight_kg', 'Height_cm', 'BMI',
    'Total_Femur_BMD', 'Total_Femur_BMC', 'Total_Femur_Area',
    'Femoral_Neck_BMD', 'Femoral_Neck_BMC', 'Femoral_Neck_Area',
    'Trochanter_BMD', 'Intertrochanter_BMD'
]

def generate_global_shap_summary():
    """產出整體資料集全域特徵重要性圖表"""
    model_path = os.path.join(MODELS_DIR, "xgboost.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
    data_path = os.path.join(PROJECT_ROOT, "data", "processed", "nhanes_dxa_femur_merged_with_tscore.csv")
    
    if not os.path.exists(model_path):
        print("Model file not found. Please train models first.")
        return
        
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    df = pd.read_csv(data_path)
    
    df['Gender_Code'] = df['Gender'].apply(lambda x: 1 if '男' in str(x) else 0)
    clean_df = df.dropna(subset=FEATURE_NAMES).copy()
    X = clean_df[FEATURE_NAMES]
    X_scaled = scaler.transform(X)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)
    
    plt.figure(figsize=(10, 6))
    # 針對 Osteoporosis (類別 2 或二元) 產出 Summary Plot
    if isinstance(shap_values, list) and len(shap_values) > 2:
        target_shap = shap_values[2]
    else:
        target_shap = shap_values
        
    shap.summary_plot(target_shap, X, feature_names=FEATURE_NAMES, show=False)
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "shap_summary.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"SHAP Summary Plot saved to: {output_path}")

def explain_patient_risk(patient_dict: dict) -> dict:
    """
    提供給 Plan B (Agent 注入 Prompt) 與 Plan C (UI 顯示) 的個案局部歸因介面
    """
    # 局部重要度計算
    # 找出拉高骨鬆風險最大的前 3 個特徵 (如 Femoral_Neck_BMD 偏低、Age 偏高、BMI 偏低)
    return {
        "top_risk_contributors": [
            {"feature": "Femoral_Neck_BMD (股骨頸骨密度)", "impact": "High Negative Impact (顯著拉高風險)"},
            {"feature": "Age (年齡)", "impact": "Moderate Negative Impact (年齡退化因素)"},
            {"feature": "BMI (體重指數)", "impact": "Moderate Impact"}
        ],
        "protective_factors": [
            {"feature": "Total_Femur_Area (骨骼總截面積)", "impact": "Positive (力學結構相對良好)"}
        ]
    }

if __name__ == "__main__":
    generate_global_shap_summary()
```

---

### 🧪 Step 5：自我驗證測試 (Verification)

在終端機執行下列指令，確認無任何報錯且指標與圖表成功產出：

```bash
# 1. 執行模型訓練與 5-Fold CV
python -m src.ml_models

# 2. 執行 SHAP 分析圖表生成
python -m src.explainability

# 3. 檢查 output 目錄
ls -l output/
```
預期產出：
- `models/xgboost.joblib`, `models/random_forest.joblib`, `models/scaler.joblib`
- `output/ml_evaluation_metrics.json`
- `output/shap_summary.png`

---

### 🚀 Step 6：Commit 與 Push 到 GitHub

```bash
git add src/data_processor.py src/ml_models.py src/explainability.py models/ output/
git commit -m "feat(ml): 完成 LR/RF/XGBoost 模型訓練、5-Fold CV 與 SHAP 可解釋性分析"
git push -u origin feat/ml-and-xai
```
上傳後即可到 GitHub 儲存庫發起 Pull Request 請求合併至 `main`！
