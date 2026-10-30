"""
src/ml_models.py - 機器學習模型訓練、評估與推論介面
實作 Logistic Regression, Random Forest, XGBoost 三大模型，
並透過 5-Fold Stratified Cross Validation 評估模型指標，存檔至 models/ 與 output/。
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

ALL_FEATURES = ['Gender_Code'] + FEATURE_COLS
TARGET_COL = 'WHO_Category'

class BoneHealthPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.models = {}
        self.best_model_name = "XGBoost"

    def load_data(self):
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Processed dataset not found at {DATA_PATH}. Please run data_processor.py first.")
            
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
        df['Gender_Code'] = df['Gender'].apply(lambda x: 1 if ('男' in str(x) or 'Male' in str(x)) else 0)
        
        # 移除關鍵特徵或標籤有缺漏的樣本
        clean_df = df.dropna(subset=ALL_FEATURES + [TARGET_COL]).copy()
        X = clean_df[ALL_FEATURES]
        y_raw = clean_df[TARGET_COL]
        y = self.label_encoder.fit_transform(y_raw)
        return X, y, clean_df

    def train_and_evaluate(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        X, y, df = self.load_data()
        print(f"Loaded {len(X)} complete samples for model training.")
        print(f"Target distribution: {dict(pd.Series(y).value_counts())}")
        print(f"Label classes: {list(self.label_encoder.classes_)}")
        
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        candidate_models = {
            "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
            "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.08, eval_metric='mlogloss', random_state=42)
        }
        
        cv_results = {}
        
        print("\n=== Running 5-Fold Stratified Cross Validation ===")
        for name, clf in candidate_models.items():
            acc_list, prec_list, rec_list, f1_list, auc_list = [], [], [], [], []
            
            for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
                X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_tr, y_val = y[train_idx], y[val_idx]
                
                fold_scaler = StandardScaler()
                X_tr_scaled = fold_scaler.fit_transform(X_tr)
                X_val_scaled = fold_scaler.transform(X_val)
                
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
            
            cv_results[name] = {
                "Accuracy": round(float(np.mean(acc_list)), 4),
                "Precision": round(float(np.mean(prec_list)), 4),
                "Recall": round(float(np.mean(rec_list)), 4),
                "F1_Score": round(float(np.mean(f1_list)), 4),
                "ROC_AUC": round(float(np.mean(auc_list)), 4)
            }
            print(f"  • {name:20s} => Accuracy: {cv_results[name]['Accuracy']:.4f}, Precision: {cv_results[name]['Precision']:.4f}, Recall: {cv_results[name]['Recall']:.4f}, F1: {cv_results[name]['F1_Score']:.4f}, ROC-AUC: {cv_results[name]['ROC_AUC']:.4f}")
            
            # 全量樣本訓練最終模型並序列化存檔
            full_scaler = StandardScaler()
            X_all_scaled = full_scaler.fit_transform(X)
            clf.fit(X_all_scaled, y)
            model_file = os.path.join(MODELS_DIR, f"{name.lower()}.joblib")
            joblib.dump(clf, model_file)
            self.models[name.lower()] = clf
            
        # 儲存 Scaler 與 LabelEncoder
        joblib.dump(full_scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
        joblib.dump(self.label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))
        self.scaler = full_scaler
        
        # 儲存評估結果為 JSON 與 CSV
        json_path = os.path.join(OUTPUT_DIR, "ml_evaluation_metrics.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(cv_results, f, ensure_ascii=False, indent=2)
            
        csv_path = os.path.join(OUTPUT_DIR, "ml_evaluation_metrics.csv")
        metrics_df = pd.DataFrame.from_dict(cv_results, orient='index')
        metrics_df.index.name = "Model"
        metrics_df.to_csv(csv_path, encoding='utf-8')
        
        print(f"\n[OK] Model files saved to: {MODELS_DIR}")
        print(f"[OK] Evaluation metrics saved to: {json_path}")
        return cv_results


# 全域單例載入與對外推論介面
_PREDICTOR = None

def get_predictor():
    global _PREDICTOR
    if _PREDICTOR is None:
        _PREDICTOR = BoneHealthPredictor()
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        encoder_path = os.path.join(MODELS_DIR, "label_encoder.joblib")
        
        if os.path.exists(scaler_path) and os.path.exists(encoder_path):
            _PREDICTOR.scaler = joblib.load(scaler_path)
            _PREDICTOR.label_encoder = joblib.load(encoder_path)
            for name in ["logistic_regression", "random_forest", "xgboost"]:
                p = os.path.join(MODELS_DIR, f"{name}.joblib")
                if os.path.exists(p):
                    _PREDICTOR.models[name] = joblib.load(p)
    return _PREDICTOR

def predict_osteoporosis_risk(patient_dict: dict) -> dict:
    """
    提供給 Plan B (Agent) 與 Plan C (UI) 呼叫的標準推論介面
    :param patient_dict: 包含受試者生理與 DXA 指標之字典
    :return: 包含預測類別、各類別機率與風險等級之字典
    """
    # 換算 WHO 最低 T-score 作為臨床基準
    fn_bmd = float(patient_dict.get('Femoral_Neck_BMD', 0.858))
    tf_bmd = float(patient_dict.get('Total_Femur_BMD', 0.942))
    t_neck = round((fn_bmd - 0.858) / 0.120, 2)
    t_total = round((tf_bmd - 0.942) / 0.122, 2)
    min_t = min(t_neck, t_total)
    
    predictor = get_predictor()
    model = predictor.models.get("xgboost") or predictor.models.get("random_forest")
    
    if model is None or not hasattr(predictor, 'scaler') or predictor.scaler is None:
        # Fallback 依 WHO 臨床公式精確判定
        cat = "Osteoporosis (骨質疏鬆)" if min_t <= -2.5 else ("Osteopenia (骨量減少)" if min_t < -1.0 else "Normal (正常)")
        risk_lvl = "High" if min_t <= -2.5 else ("Moderate" if min_t < -1.0 else "Low")
        return {
            "predicted_category": cat,
            "risk_level": risk_lvl,
            "probabilities": {
                "Normal (正常)": 0.05 if risk_lvl == "High" else (0.2 if risk_lvl == "Moderate" else 0.85),
                "Osteopenia (骨量減少)": 0.15 if risk_lvl == "High" else (0.65 if risk_lvl == "Moderate" else 0.12),
                "Osteoporosis (骨質疏鬆)": 0.80 if risk_lvl == "High" else (0.15 if risk_lvl == "Moderate" else 0.03)
            },
            "min_t_score": min_t,
            "t_score_femoral_neck": t_neck,
            "t_score_total_femur": t_total,
            "model_used": "WHO_Clinical_Formula (Fallback)"
        }
        
    # 組裝特徵向量 (對齊 ALL_FEATURES 順序)
    gender_code = 1 if ('男' in str(patient_dict.get('Gender', '')) or 'Male' in str(patient_dict.get('Gender', ''))) else 0
    raw_features = [gender_code] + [float(patient_dict.get(c, 0.0)) for c in FEATURE_COLS]
    
    X_df = pd.DataFrame([raw_features], columns=ALL_FEATURES)
    X_scaled = predictor.scaler.transform(X_df)
    probs = model.predict_proba(X_scaled)[0]
    pred_idx = np.argmax(probs)
    classes = predictor.label_encoder.classes_
    predicted_cat = str(classes[pred_idx])
    
    prob_dict = {str(classes[i]): round(float(probs[i]), 4) for i in range(len(classes))}
    
    # 風險分級判定
    if "Osteoporosis" in predicted_cat or min_t <= -2.5:
        risk_level = "High"
    elif "Osteopenia" in predicted_cat or min_t < -1.0:
        risk_level = "Moderate"
    else:
        risk_level = "Low"
        
    return {
        "predicted_category": predicted_cat,
        "risk_level": risk_level,
        "probabilities": prob_dict,
        "min_t_score": min_t,
        "t_score_femoral_neck": t_neck,
        "t_score_total_femur": t_total,
        "model_used": "XGBoost"
    }

if __name__ == "__main__":
    predictor = BoneHealthPredictor()
    predictor.train_and_evaluate()
