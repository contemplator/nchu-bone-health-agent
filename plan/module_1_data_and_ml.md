# 【模組一實作計畫】數據清理、特徵工程、ML 模型與 SHAP 可解釋性

- **負責組員**：組員 A（Data & Machine Learning Engineer）
- **核心目標**：從 `data/raw/` 讀取 NHANES 2017–2020 XPT 原始檔，建立嚴謹的資料清理與特徵工程管線，完成 Logistic Regression、Random Forest 與 XGBoost 模型訓練、5-Fold 交叉驗證（以 PR-AUC 為主要指標）、模型持久化儲存，並實作 SHAP 可解釋性歸因引擎。
- **產出檔案**：
  - `data/processed/cohort_cleaned.csv`
  - `src/data_processor.py`
  - `src/ml_models.py`
  - `src/explainability.py`
  - `models/best_model.pkl`（或 `.joblib`）、`models/metrics.json`
  - `notebooks/01_eda_and_cleaning.ipynb`
  - `notebooks/02_model_training_shap.ipynb`

---

## 一、詳細實作步驟清單

### Step 1: 原始資料載入與樣本隊列篩選 (Cohort Definition)
- 讀取 `data/raw/` 目錄下的 4 份 XPT 檔案：
  - `P_DEMO.xpt`（人口統計：年齡 `RIDAGEYR`、性別 `RIAGENDR`）
  - `P_BMX.xpt`（身體測量：身高 `BMXHT`、體重 `BMXWT`、BMI `BMXBMI`）
  - `P_DXXFEM.xpt`（近端股骨 DXA：`DXAFMRST` 掃描狀態、各部位 BMD/BMC/Area）
  - `P_OSQ.xpt`（骨質疏鬆問卷：`OSQ060` 是否曾被告知骨鬆）
- 依 `SEQN` 進行 Inner Join 串聯。
- 嚴格落實篩選準則（對應 `DESIGN.md` 第 5.1 節）：
  - 年齡 $\ge 50$ 歲。
  - DXA 股骨掃描狀態有效（`DXAFMRST == 1`，排除假影、假體或未完成者）。
  - `OSQ060` 具備有效回答：`1`（是 $\rightarrow$ 標籤 1）、`2`（否 $\rightarrow$ 標籤 0）；排除 `7`（拒答）、`9`（不知道）與缺失值。
- 統計最終有效樣本數 $N$、陽性／陰性比例，確認類別不平衡程度。

### Step 2: 異常值檢核與特徵工程 (Feature Engineering)
- 執行生理合理性檢驗（如體重 $30 \sim 200 \text{ kg}$、身高 $120 \sim 220 \text{ cm}$、BMD $0.2 \sim 1.8 \text{ g/cm}^2$）。
- 建立特徵工程模組 `src/data_processor.py`：
  - **核心人口學特徵**：年齡、性別（One-Hot / Binary）、身高、體重、BMI。
  - **原始 DXA 解剖部位特徵**：
    - 全髖部（Total Femur）：BMD (`DXXOFBMD`)、BMC (`DXXOFBMC`)、Area (`DXXOFA`)
    - 股骨頸（Femoral Neck）：BMD (`DXXNKBMD`)、BMC (`DXXNKBMC`)、Area (`DXXNKA`)
    - 轉子區（Trochanter BMD `DXXTRBMD`、Intertrochanter BMD `DXXINBMD`）
  - **幾何結構衍生比值特徵**：
    - 股骨頸/全髖部 BMD 比值（`Neck_to_Total_BMD_Ratio = DXXNKBMD / DXXOFBMD`）
    - 全髖部單位面積骨礦含量比值（`Total_BMC_Area_Ratio = DXXOFBMC / DXXOFA`）
    - 股骨頸單位面積骨礦含量比值（`Neck_BMC_Area_Ratio = DXXNKBMC / DXXNKA`）
- 將清理後資料集儲存至 `data/processed/cohort_cleaned.csv`。

### Step 3: 多模型訓練與分層交叉驗證 (Model Training & Evaluation)
- 實作 `src/ml_models.py`：
  - 切分資料集：80% 訓練集（Train）、20% 保留測試集（Holdout Test），採 Stratified Split。
  - 在訓練集內執行 **5-Fold Stratified Cross Validation**。
  - 訓練三種模型：
    1. **Logistic Regression**（標準化 Scaler + L2 正則化，作為線性臨床 Baseline）
    2. **Random Forest**（隨機森林分類器，調整 `n_estimators`, `max_depth`, `min_samples_leaf`）
    3. **XGBoost**（極限梯度提升樹，調整 `learning_rate`, `max_depth`, `subsample`）
  - 同步設定基準對照：**僅人口學特徵（Demographics only）** vs **人口學 + DXA 幾何全特徵**，量化 DXA 的增益價值。
- 計算綜合評估指標：
  - **PR-AUC（Precision-Recall AUC，主要比較指標）**
  - **ROC-AUC**
  - **Precision、Recall、F1-Score（Macro & Positive）**
  - **Accuracy**
  - **Brier Score（校準度）**
- 評選最佳模型並將模型檔序列化儲存至 `models/best_model.pkl`，特徵欄位清單儲存至 `models/feature_columns.json`，各模型評估指標存為 `models/metrics.json`。

### Step 4: SHAP 可解釋性分析引擎 (Explainable AI)
- 實作 `src/explainability.py`：
  - 支援 `shap.TreeExplainer`（針對 RF / XGBoost）與 `shap.LinearExplainer`（針對 LR）。
  - **全域解釋（Global Attribution）**：產出測試集之 SHAP Summary Plot，產出特徵重要度排序圖檔 `output/shap_summary.png`。
  - **局部解釋（Local Attribution）**：提供 `explain_single_case(case_features)` 函式，接收單一個案向量，計算各特徵之 SHAP 貢獻值 $\phi_i$。
  - 產出前三大推升風險因子（Top 3 Risk Factors）與降低風險因子，以利注入後續 LLM Prompt 與前端視覺化。

### Step 5: 單元測試與推論 API 介面包裝
- 提供獨立命令列測試指令：`python -m src.ml_models`，能一鍵完成資料清洗、模型訓練與指標印出。
- 包裝高階推論介面函式 `predict_bone_risk(patient_dict)`：
  - 輸入：字典格式之個案生理與 DXA 數據。
  - 輸出：`{"risk_probability": float, "risk_tier": str, "top_shap_features": list}`。

---

## 二、進度追蹤檢查清單 (Checklist)

### 階段 1：資料清洗與前處理
- [ ] 1.1 驗證 `data/raw/` 目錄下的 4 份 XPT 檔案完整性
- [ ] 1.2 建立 Jupyter Notebook `notebooks/01_eda_and_cleaning.ipynb`，完成資料探索與欄位對應
- [ ] 1.3 實作 Inner Join 合併，並落實篩選規則（年齡 $\ge 50$、有效 DXA、有效 `OSQ060`）
- [ ] 1.4 計算衍生比值特徵（`Neck_to_Total_BMD_Ratio` 等），處理異常值
- [ ] 1.5 輸出清理完成資料集至 `data/processed/cohort_cleaned.csv`，確認有效樣本數 $N$ 與正負樣本比

### 階段 2：特徵工程與模組封裝
- [ ] 2.1 建立 `src/data_processor.py`，封裝可重複調用之 `DataProcessor` 類別
- [ ] 2.2 實作連續變數標準化（`StandardScaler`）與類別編碼，保存 scaler 權重至 `models/scaler.pkl`
- [ ] 2.3 確保線上推論時單筆病患輸入可自動通過相同的特徵轉換邏輯

### 階段 3：模型訓練與評估
- [ ] 3.1 建立 `src/ml_models.py`，撰寫 80/20 分層切分與 5-Fold Stratified CV
- [ ] 3.2 訓練 Logistic Regression（基準模型），計算 PR-AUC、ROC-AUC、F1
- [ ] 3.3 訓練 Random Forest 分類器，進行基本超參數調整
- [ ] 3.4 訓練 XGBoost 分類器，進行基本超參數調整
- [ ] 3.5 比較 Demographics-only 與 Demographics+DXA 之增益
- [ ] 3.6 產出模型評估比較表與混淆矩陣，儲存於 `models/metrics.json`
- [ ] 3.7 保存選定之最佳模型至 `models/best_model.pkl`

### 階段 4：SHAP 可解釋性分析
- [ ] 4.1 建立 `src/explainability.py`，初始化對應之 SHAP Explainer
- [ ] 4.2 繪製測試集全域 SHAP Summary Plot 並輸出儲存為 `output/shap_summary.png`
- [ ] 4.3 實作單筆推論解釋函式 `explain_single_case()`，輸出結構化特徵貢獻清單
- [ ] 4.4 提取 Top 3 風險影響特徵，格式符合模組間資料傳遞規範

### 階段 5：交付與單元測試
- [ ] 5.1 撰寫測試腳本，執行 `python -m src.ml_models` 確保訓練流程可無誤跑通
- [ ] 5.2 測試單筆輸入推論函式 `predict_bone_risk(sample_case)`，驗證輸出格式正確
- [ ] 5.3 將模型與推論函式交接給組員 C 進行 API 整合

