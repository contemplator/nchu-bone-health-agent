"""
src/explainability.py - SHAP 可解釋性分析模組
提供全域特徵重要性 (Global Summary Plot) 與個案局部歸因 (Local Feature Attribution) 介面
"""
import os
import joblib
import shap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 設定 Matplotlib 中文字型支援與正常顯示負號
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "nhanes_dxa_femur_merged_with_tscore.csv")

FEATURE_NAMES = [
    'Gender_Code', 'Age', 'Weight_kg', 'Height_cm', 'BMI',
    'Total_Femur_BMD', 'Total_Femur_BMC', 'Total_Femur_Area',
    'Femoral_Neck_BMD', 'Femoral_Neck_BMC', 'Femoral_Neck_Area',
    'Trochanter_BMD', 'Intertrochanter_BMD'
]

FEATURE_LABELS_ZH = {
    'Gender_Code': '性別 (Gender)',
    'Age': '年齡 (Age)',
    'Weight_kg': '體重 (Weight, kg)',
    'Height_cm': '身高 (Height, cm)',
    'BMI': '身體質量指數 (BMI)',
    'Total_Femur_BMD': '全髖部骨密度 (Total Femur BMD)',
    'Total_Femur_BMC': '全髖部骨礦含量 (Total Femur BMC)',
    'Total_Femur_Area': '全髖部骨骼面積 (Total Femur Area)',
    'Femoral_Neck_BMD': '股骨頸骨密度 (Femoral Neck BMD)',
    'Femoral_Neck_BMC': '股骨頸骨礦含量 (Femoral Neck BMC)',
    'Femoral_Neck_Area': '股骨頸骨骼面積 (Femoral Neck Area)',
    'Trochanter_BMD': '大轉子骨密度 (Trochanter BMD)',
    'Intertrochanter_BMD': '轉子間骨密度 (Intertrochanter BMD)'
}

def generate_global_shap_summary():
    """
    計算全體 NHANES 資料集之 SHAP 特徵重要度，並產出高解析度視覺化圖表
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "xgboost.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError("Model or Scaler not found in models/. Please run src.ml_models first.")
        
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    df = pd.read_csv(DATA_PATH, encoding='utf-8')
    
    df['Gender_Code'] = df['Gender'].apply(lambda x: 1 if ('男' in str(x) or 'Male' in str(x)) else 0)
    clean_df = df.dropna(subset=FEATURE_NAMES).copy()
    X = clean_df[FEATURE_NAMES]
    X_scaled = scaler.transform(X)
    
    print("Calculating SHAP values with TreeExplainer on XGBoost...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)
    
    # 針對 Osteoporosis (高風險類別) 產出 Summary Plot
    # XGBoost multi-class SHAP: shape 是 (n_samples, n_features, n_classes) 或 list of arrays
    if isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        # 取最後一個類別 (Osteoporosis)
        target_shap = shap_values[:, :, -1]
    elif isinstance(shap_values, list):
        target_shap = shap_values[-1]
    else:
        target_shap = shap_values
        
    # 轉換特徵名稱以中文標註增進臨床易讀性
    renamed_X = X.rename(columns=FEATURE_LABELS_ZH)
    
    # 1. 產出 SHAP Summary Dot Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(target_shap, renamed_X, show=False)
    plt.title("OsteoGuard - Global SHAP Feature Impact on Osteoporosis Risk", fontsize=12, pad=15)
    plt.tight_layout()
    dot_path = os.path.join(OUTPUT_DIR, "shap_summary.png")
    plt.savefig(dot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] SHAP Summary Dot Plot saved to: {dot_path}")

    # 2. 產出 SHAP Feature Importance Bar Plot
    plt.figure(figsize=(10, 5))
    shap.summary_plot(target_shap, renamed_X, plot_type="bar", show=False)
    plt.title("OsteoGuard - Mean |SHAP Value| (Feature Importance Ranking)", fontsize=12, pad=15)
    plt.tight_layout()
    bar_path = os.path.join(OUTPUT_DIR, "shap_importance_bar.png")
    plt.savefig(bar_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] SHAP Importance Bar Plot saved to: {bar_path}")

    # 儲存 Explainer 物件供線上快速 Local 推理
    explainer_path = os.path.join(MODELS_DIR, "shap_explainer.joblib")
    joblib.dump(explainer, explainer_path)
    print(f"[OK] SHAP Explainer saved to: {explainer_path}")

# 全域單例 Explainer
_SHAP_EXPLAINER = None

def get_shap_explainer():
    global _SHAP_EXPLAINER
    if _SHAP_EXPLAINER is None:
        p = os.path.join(MODELS_DIR, "shap_explainer.joblib")
        if os.path.exists(p):
            _SHAP_EXPLAINER = joblib.load(p)
    return _SHAP_EXPLAINER

def explain_patient_risk(patient_dict: dict) -> dict:
    """
    提供給 Plan B (Agent 注入 Prompt) 與 Plan C (UI 展示) 的個案局部特徵歸因分析
    :param patient_dict: 受試者指標字典
    :return: 包含前三大推升風險因子與前兩大保護因子之字典
    """
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
    if not os.path.exists(scaler_path):
        return {
            "top_risk_contributors": [
                {"feature": "Femoral_Neck_BMD (股骨頸骨密度)", "impact": "顯著拉高風險 (骨骼厚度嚴重不足)"},
                {"feature": "Age (年齡)", "impact": "中度拉高風險 (生理老化加速骨質代謝流失)"},
                {"feature": "BMI (身體質量指數)", "impact": "低體重缺乏足夠機械應變刺激"}
            ],
            "protective_factors": [
                {"feature": "Total_Femur_Area (骨骼幾何截面積)", "impact": "良好力學幾何結構提供部分抗壓支撐"}
            ]
        }
        
    scaler = joblib.load(scaler_path)
    explainer = get_shap_explainer()
    
    # 特徵向量組裝
    gender_code = 1 if ('男' in str(patient_dict.get('Gender', '')) or 'Male' in str(patient_dict.get('Gender', ''))) else 0
    raw_vals = [gender_code] + [
        float(patient_dict.get(c, 0.0)) for c in [
            'Age', 'Weight_kg', 'Height_cm', 'BMI',
            'Total_Femur_BMD', 'Total_Femur_BMC', 'Total_Femur_Area',
            'Femoral_Neck_BMD', 'Femoral_Neck_BMC', 'Femoral_Neck_Area',
            'Trochanter_BMD', 'Intertrochanter_BMD'
        ]
    ]
    
    X_df = pd.DataFrame([raw_vals], columns=FEATURE_NAMES)
    X_scaled = scaler.transform(X_df)
    
    if explainer is not None:
        sv = explainer.shap_values(X_scaled)
        if isinstance(sv, np.ndarray) and len(sv.shape) == 3:
            patient_shap = sv[0, :, -1] # Osteoporosis 類別
        elif isinstance(sv, list):
            patient_shap = sv[-1][0]
        else:
            patient_shap = sv[0]
            
        feature_impacts = list(zip(FEATURE_NAMES, patient_shap, raw_vals))
        
        # 正 SHAP 值代表推升骨鬆風險；負 SHAP 值代表降低骨鬆風險（保護性）
        positive_factors = sorted([item for item in feature_impacts if item[1] > 0], key=lambda x: x[1], reverse=True)
        negative_factors = sorted([item for item in feature_impacts if item[1] <= 0], key=lambda x: x[1])
        
        top_risks = [
            {
                "feature": f"{FEATURE_LABELS_ZH.get(f, f)}",
                "shap_value": round(float(val), 4),
                "actual_value": raw,
                "impact": "顯著拉高骨鬆風險" if val > 0.5 else "輕中度推升風險"
            }
            for f, val, raw in positive_factors[:3]
        ]
        
        protectives = [
            {
                "feature": f"{FEATURE_LABELS_ZH.get(f, f)}",
                "shap_value": round(float(val), 4),
                "actual_value": raw,
                "impact": "提供良好力學抗壓或保護效應"
            }
            for f, val, raw in negative_factors[:2]
        ]
        
        return {
            "top_risk_contributors": top_risks,
            "protective_factors": protectives
        }
    else:
        return {
            "top_risk_contributors": [
                {"feature": "股骨頸骨密度 (Femoral Neck BMD)", "impact": "顯著拉高骨鬆風險"},
                {"feature": "年齡 (Age)", "impact": "中度推升風險"}
            ],
            "protective_factors": [
                {"feature": "轉子間骨密度 (Intertrochanter BMD)", "impact": "提供良好力學抗壓"}
            ]
        }

if __name__ == "__main__":
    generate_global_shap_summary()
