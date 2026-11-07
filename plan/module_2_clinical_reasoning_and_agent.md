# 【模組二實作計畫】臨床規則推理引擎與 LLM 代理人

- **負責組員**：組員 B（Clinical Domain Rules & LLM Agent Developer）
- **核心目標**：將醫學領域知識與台灣醫療法規轉換為確定性推理規則引擎（WHO 分級、骨科/神外圍術期螺釘鬆脫預警、健保第 5.6 節合規防核扣、接續用藥換藥演算法、牙科 MRONJ 護欄），並建構多服務相容之 LLM Clinical Copilot（支援 OpenAI、Gemini，以及無 API Key 也能順暢運作的離線 Mock 模式），產出臨床 SOAP 病歷草稿與白話病患衛教溝通圖卡。
- **產出檔案**：
  - `src/surgical_advisor.py`
  - `src/nhi_engine.py`
  - `src/sequential_therapy.py`
  - `src/patient_safety.py`
  - `src/agent.py`（含多 Provider 與 Mock 離線模式）
  - `src/knowledge_base/`（法規條文、ATC 藥物碼、臨床指引 JSON/規則庫）

---

## 一、詳細實作步驟清單

### Step 1: WHO / ISCD 骨質疏鬆診斷與最低部位原則 (WHO Criteria)
- 實作基準診斷規則：
  - 根據個案各解剖部位（股骨頸、全髖部、腰椎）DXA 數值，依「最低部位原則（Lowest Site Rule）」選定基準 $T\text{-score}$。
  - 分級準則：
    - 正常（Normal）：$T \ge -1.0$
    - 骨質減少（Osteopenia）：$-2.5 < T < -1.0$
    - 骨質疏鬆症（Osteoporosis）：$T \le -2.5$
    - 嚴重骨鬆（Severe Osteoporosis）：$T \le -2.5$ 且合併 $\ge 1$ 處脆弱性骨折。
- 嚴格維持架構邊界：**臨床 DXA 診斷與 ML 模型之自述告知史預測獨立分開呈現**，不混淆臨床診斷依據。

### Step 2: 骨科與神外圍術期螺釘鬆脫預警引擎 (`src/surgical_advisor.py`)
- 整合脊椎與關節置換生物力學指引：
  - 輸入：預計手術類型（如 `Spinal_Fusion`、`Vertebroplasty`、`Joint_Replacement`）、骨密分級與部位。
  - 觸發邏輯：
    - 若手術為脊椎融合術或椎體成形術，且 $T\text{-score} \le -2.5$：
      - 觸發 **「椎弓根螺釘鬆脫與內固定失敗高風險警訊（Pedicle Screw Loosening Alert）」**。
      - 術前對策建議：強烈建議術前 1–3 個月先行使用促骨生成劑（Anabolic Agent，如 Teriparatide / Romosozumab）強化骨小梁結構。
      - 術中對策建議：提示手術中採用骨水泥強化螺釘（Cement Augmentation）或皮質骨軌道螺釘（Cortical Bone Trajectory, CBT Screw），提高拔出力強度。
    - 若無高危手術需求，回傳常規術後骨密追蹤建議。

### Step 3: 台灣健保第 5.6 節用藥合規審核引擎 (`src/nhi_engine.py`)
- 將衛福部健保署《藥品給付規定》第 5.6 節結構化為規則引擎：
  - **5.6.1 第一線抗骨流失劑（Prolia 保骼麗、Aclasta 骨力強、雙磷酸鹽類等）**：
    - 條款 A（骨折條件）：$T \le -2.5$ 伴隨脊椎或髖部脆弱性骨折。
    - 條款 B（多處骨折）：骨質減少（$-2.5 < T < -1.0$）伴隨 $\ge 2$ 處骨折。
    - 條款 C（未骨折高危初級預防）：$T \le -2.5$ 合併三大高風險共病之一（類風濕性關節炎 RA、需胰島素治療之糖尿病、長期口服類固醇 $\ge 3$ 個月）。
  - **5.6.2 / 5.6.3 第二線促骨生成劑（Forteo 骨力強、Evenity 益穩挺）**：
    - 條件：$T \le -3.0$ 伴隨 $\ge 2$ 處骨折；或使用抗流失劑滿 12 個月仍發生新骨折。
    - **安全禁忌症檢核**：若欲選用 Evenity，自動檢查「過去 1 年內是否有心肌梗塞或腦中風」病史；若有則發出絕對禁忌紅燈警告。
  - **防核扣缺件檢查器（Missing Lab Checker）**：
    - 檢查是否具備 6 個月內之血鈣（Serum Calcium）與腎功能（肌酸酐 Creatinine / eGFR）檢驗報告。
    - 標註加簽審查必備之「DXA 報告影本與 X 光骨折影像附卡」缺件提示。

### Step 4: 接續治療換藥甘特圖時程演算法 (`src/sequential_therapy.py`)
- 輸入目前用藥名稱（`current_drug`）、起始施打日期與最近施打日期：
  - **單劑次週期推算**：
    - Prolia（皮下注射，每 6 個月一次）：計算下次預計施打日與剩餘天數。
    - 若逾期超過 30 天未回診施打（即自上次施打超過 7 個月），立即觸發 **「反彈性多發性脊椎骨折高風險紅色警報（Rebound Vertebral Fracture Warning）」**。
  - **藥物療程上限與換藥甘特排程**：
    - Evenity：療程嚴格上限為 12 個月（12 劑），期滿必須無縫轉換為抗流失劑（Prolia 或 Bisphosphonates）以鎖住骨密度。
    - Forteo：療程健保給付上限為 24 個月（2 年），期滿強制轉換後線抗流失用藥。
  - 輸出結構化換藥時間軸節點，供前端渲染時間軸甘特圖。

### Step 5: 病患安全護欄：牙科 MRONJ 與分級運動營養 (`src/patient_safety.py`)
- **牙科拔牙 MRONJ 護欄**：
  - 個案有近期（3 個月內）拔牙、植牙或牙周手術計畫時，提供抗骨鬆藥物之拔牙前評估時窗與術後傷口癒合追蹤指引。
  - 明確提供「醫病溝通指引」，避免病患因恐懼顎骨壞死而自行擅自斷藥。
- **分級運動與生活禁忌**：
  - 骨鬆或骨折個案：**嚴禁高衝擊跳躍與脊椎過度彎曲扭轉（如仰臥起坐、高爾夫全力揮桿）**，推薦防跌平衡與下肢肌力訓練。
- **基礎營養代謝**：
  - 推薦每日鈣質攝取目標 1,000–1,200 mg，維生素 D 補充 800–1,000 IU。

### Step 6: 多 Provider 與 Mock 支援之 LLM Copilot (`src/agent.py`)
- 實作支援多後端切換的 Clinical Copilot Agent：
  - 支援環境變數切換：`LLM_PROVIDER="openai"`、`"gemini"` 或 `"mock"`。
  - **Prompt 模板組裝**：整合病患特徵、SHAP 前三大成因、螺釘鬆脫警報、健保 5.6 節條款比對結果與換藥排程。
  - **雙重結構化輸出**：
    1. **SOAP 門診病歷摘要（Clinical Drafting Scribe）**：自動草擬主訴 (S)、客觀數據 (O)、臨床評估 (A)、治療與健保加簽處方計畫 (P)，供醫師過目簽章。
    2. **病患衛教溝通圖卡文案**：轉化為無醫學晦澀術語的白話繁體中文衛教文案，含拔牙衛教、飲食補充與運動紅綠燈。
  - **離線 Mock 模式（Fallback）**：無 API Key 時讀取內建高品質臨床模板快速回應，確保系統全功能離線仍可操作與演示。

---

## 二、進度追蹤檢查清單 (Checklist)

### 階段 1：WHO 準則與最低部位原則
- [ ] 1.1 建立 `src/who_rules.py`，實作最低部位原則演算法
- [ ] 1.2 測試正常、骨少、骨鬆與嚴重骨鬆 4 種分級邏輯，確保與脆弱性骨折判斷正確聯動

### 階段 2：圍術期螺釘鬆脫預警
- [ ] 2.1 建立 `src/surgical_advisor.py`，定義手術類型與骨密風險矩陣
- [ ] 2.2 實作脊椎融合術之螺釘鬆脫警報生成（含術前促進骨生成與術中骨水泥建議）
- [ ] 2.3 單元測試：非脊椎手術或骨質正常個案不觸發誤報

### 階段 3：健保第 5.6 節法規引擎
- [ ] 3.1 建立 `src/knowledge_base/nhi_rules.json`，將 5.6.1、5.6.2、5.6.3 條款轉換為結構化資料
- [ ] 3.2 建立 `src/nhi_engine.py`，實作一線與二線適應症核對演算法
- [ ] 3.3 實作 Evenity 一年內心血管事件禁忌症警示檢查
- [ ] 3.4 實作 6 個月內血鈣、肌酸酐抽血數據缺件警示

### 階段 4：接續用藥排程與牙科 MRONJ 護欄
- [ ] 4.1 建立 `src/sequential_therapy.py`，實作 Prolia 6 個月施打日推算與逾期 30 天反彈警報
- [ ] 4.2 實作 Evenity (12 個月) 與 Forteo (24 個月) 到期強制換藥排程演算法
- [ ] 4.3 建立 `src/patient_safety.py`，實作拔牙 MRONJ 處置指引與分級運動營養禁忌

### 階段 5：LLM Copilot 與離線 Mock 模式
- [ ] 5.1 建立 `src/agent.py`，封裝 OpenAI API 與 Google Gemini API 調用介面
- [ ] 5.2 撰寫臨床 Prompt 工程模板，注入 SHAP 歸因、手術風險與健保審查結論
- [ ] 5.3 實作離線 Mock 模式（在未填 API Key 時回傳標準結構化 SOAP 與衛教文案）
- [ ] 5.4 實作多輪問答介面函式 `ask_copilot(patient_case, user_question)`
- [ ] 5.5 單元測試全引擎模組串接，確認輸出符合 `CDSSResult` 規格

