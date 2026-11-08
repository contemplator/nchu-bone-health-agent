# 【模組三實作計畫】現代醫療儀表板、API 串接與 VPS 部署

- **負責組員**：組員 C（Full-Stack UI, API Integration & Deployment Engineer）
- **核心目標**：基於 FastAPI 打造高效後端服務，結合現代化 Tailwind CSS、Alpine.js 與 ApexCharts/Chart.js，建構兼具專業美感與高效流暢度的臨床 CDSS 醫療儀表板；整合組員 A 的 ML/SHAP 模組與組員 B 的規則引擎/LLM Copilot；內建 4 組典型臨床示範案例快捷鈕，並提供可在現有 VPS 上無痛運行的部署腳本。
- **產出檔案**：
  - `app.py`（FastAPI 主應用程式）
  - `templates/index.html`（Tailwind + Alpine.js 醫療儀表板頁面）
  - `templates/components/`（拆分之表單、四大面板與對話框組件）
  - `static/js/presets.js`（4 組示範案例資料）
  - `static/css/custom.css`（現代醫療介面微調樣式）
  - `ecosystem.config.js` 或 `deploy/osteoguard.service`（VPS 常駐程序設定）
  - `deploy/nginx.conf.example`（VPS 反向代理設定範本）

---

## 一、詳細實作步驟清單

### Step 1: FastAPI 服務骨架與 REST API 路由規劃
- 搭建 FastAPI 服務主程式 `app.py`：
  - 掛載 Jinja2 模板目錄 `templates/` 與靜態資源目錄 `static/`。
  - 定義 Pydantic 驗證資料模型：
    - `PatientCaseRequest`（輸入個案）
    - `CopilotChatRequest`（醫師對話）
  - 規劃核心 API 端點：
    - `GET /`：渲染 CDSS 互動儀表板首頁。
    - `POST /api/analyze`：接收病患個案數據，同時觸發模組一（ML 預測與 SHAP 歸因）與模組二（WHO 分級、手術螺釘預警、健保 5.6 審核、換藥甘特圖與 Copilot 摘要），彙整為 `CDSSResult` 回傳前端。
    - `POST /api/copilot/chat`：支援醫師針對該個案在網頁右下角進行追問與互動。
    - `GET /api/presets/{preset_id}`：提供 4 組典型臨床案例的預設參數。

### Step 2: 現代醫療儀表板 UI 設計 (Tailwind CSS + Alpine.js)
- 採用高質感醫療科技風格調色（深藍灰、青藍 Primary、警示琥珀與危險朱紅）：
  - **頂部導航欄（Header）**：系統名稱「OsteoGuard AI Agent」、專案標章、連線狀態與 4 組快速載入示範個案按鈕（One-Click Preset Buttons）。
  - **左側個案資料錄入欄（Case Input Form）**：
    - 快速填入數值滑桿或輸入框（年齡、性別、BMI、DXA 股骨頸/全髖部 BMD/BMC/Area）。
    - 手術選單（脊椎融合術、椎體成形術、人工關節置換等）。
    - 骨折史與共病勾選清單（脊椎骨折、髖部骨折、RA、糖尿病、類固醇）。
    - 用藥歷程（Prolia / Evenity / Forteo / Aclasta、起始日期、最近施打日期）。
    - 拔牙/植牙與心血管病史開關。
    - 「啟動臨床綜合評估 (Analyze Case)」主要觸發按鈕。
  - **右側四大臨床決策支援面板（Four CDSS Result Panels）**：
    1. **面板一：骨鬆風險分級 + SHAP 歸因圖 + 圍術期螺釘鬆脫預警**
       - 骨密分級與 AI 風險機率儀表盤（ApexCharts Radial/Gauge）。
       - 局部 SHAP 特徵貢獻水平長條圖（標示前三大推升與降低因子）。
       - 醒目的「椎弓根螺釘鬆脫高風險」警示卡（紅框警報與術前/術中對策）。
    2. **面板二：健保第 5.6 節給付審查卡（防核扣）**
       - 條文適應症核准狀態徽章（第 5.6.1 條一線通過 / 5.6.2 條二線通過 / 不符資格）。
       - 核准法規條款依據與理由說明。
       - 防核扣提醒清單（如抽血報告缺件、心血管禁忌症紅燈）。
    3. **面板三：接續用藥時間軸與換藥甘特圖**
       - 目前用藥狀態、下次預計施打日倒數計時卡。
       - 逾期斷藥反彈性骨折紅色危急警訊。
       - 換藥時間軸甘特圖（標示 Evenity 滿 12 個月 / Forteo 滿 24 個月接續換藥節點）。
    4. **面板四：醫病溝通白話圖卡與 SOAP 病歷摘要**
       - 牙科 MRONJ 拔牙前安全護欄卡。
       - 分級運動紅綠燈指南與鈣/維生素 D 營養建議。
       - 結構化門診 SOAP 病歷草稿與「一鍵複製（Copy to Clipboard）」功能。
       - 側邊/底部的 AI Copilot 對話抽屜（Drawer/Chatbox）。

### Step 3: 內建 4 組典型臨床示範案例 (One-Click Quick Load Presets)
- 在前端實作 `static/js/presets.js`，包含 4 組具臨床代表性的預設情境，點擊按鈕即可自動填入表單並觸發分析：
  - **案例一（嚴重骨鬆合併脊椎融合手術）**：
    - 72 歲女性，股骨頸 $T=-3.4$，預計接受脊椎融合內固定術（Spinal Fusion），有 L2 壓迫性骨折。
    - 預期展示：觸發高危螺釘鬆脫警訊、建議骨水泥強化螺釘或術前施打促骨生成劑、健保審查第二線符合。
  - **案例二（健保第 5.6 節第二線促骨生成換藥個案）**：
    - 68 歲男性，使用 Evenity 滿 11 個月，$T=-3.1$。
    - 預期展示：甘特圖顯示 Evenity 剩餘 1 個月即達 12 個月上限、警示必須強制無縫轉換為 Prolia 等抗流失劑。
  - **案例三（拔牙前 Prolia 恐慌停藥個案）**：
    - 65 歲女性，使用 Prolia 治療，最近一次施打已超過 7 個月（逾期 35 天），且預計下週拔牙。
    - 預期展示：觸發 Prolia 逾期斷藥反彈性多發骨折紅色警報、啟動牙科 MRONJ 處置安全溝通指引，消除病患恐慌。
  - **案例四（輕度骨少合併高危初級預防個案）**：
    - 58 歲女性，股骨頸 $T=-2.6$，無骨折史，但患有類風濕性關節炎（RA）且長期服用類固醇。
    - 預期展示：健保 5.6.1 條款 C（未骨折高危初級預防）核准判定，提示醫師可申報第一線抗流失劑。

### Step 4: 跨模組整合與本地聯調
- 在 `app.py` 中引入組員 A 的模型推論介面 `src.ml_models.predict_bone_risk` 與 `src.explainability.explain_single_case`。
- 引入組員 B 的規則引擎 `src.nhi_engine.evaluate_nhi_5_6`、`src.surgical_advisor.evaluate_screw_risk`、`src.sequential_therapy.calculate_switch_schedule` 與 `src.agent.generate_copilot_draft`。
- 設定保護機制（Graceful Degradation）：若組員 A 尚未產出模型或組員 B 尚未完成 LLM API 串接，自動載入 Mock 假資料回傳，確保介面開發隨時可進行可視化除錯。

### Step 5: VPS 雲端部署配置 (Deployment Configuration)
- 撰寫部署設定檔與自動啟動腳本：
  - 建立 `requirements.txt`（包含 `fastapi`, `uvicorn`, `jinja2`, `pandas`, `scikit-learn`, `xgboost`, `shap` 等）。
  - 提供兩種 VPS 常駐運行方案：
    1. **PM2 管理方案**（適合已有 Node 環境的 VPS）：`pm2 start "uvicorn app:app --host 0.0.0.0 --port 8000" --name osteoguard`
    2. **Linux Systemd 服務檔**（`deploy/osteoguard.service`）
  - 撰寫 Nginx 反向代理設定範例（支援網域名稱與 HTTPS 反代）。

---

## 二、進度追蹤檢查清單 (Checklist)

### 階段 1：FastAPI 骨架與路由
- [x] 1.1 建立 `app.py`，配置靜態目錄 `static/` 與模板目錄 `templates/`
- [x] 1.2 定義 Pydantic 資料結構：`PatientCaseRequest` 與 `CDSSResponse`
- [x] 1.3 實作 `/api/analyze` 路由並串聯測試用 Dummy 回傳
- [x] 1.4 實作 `/api/copilot/chat` 路由

### 階段 2：現代 Tailwind + Alpine.js 介面開發
- [x] 2.1 引入 Tailwind CSS CDN 與 Alpine.js，建構響應式 Header 與佈局
- [x] 2.2 刻劃左側個案輸入表單（年齡、DXA 各部位、手術類型、共病、用藥日期）
- [x] 2.3 刻劃面板一：骨密風險等級、SHAP 長條圖（ApexCharts）與螺釘鬆脫警報卡
- [x] 2.4 刻劃面板二：健保 5.6 節給付審查卡（核准狀態、條款理由、缺件核扣提醒）
- [x] 2.5 刻劃面板三：用藥時間軸與換藥甘特圖（倒數計時、逾期斷藥反彈紅燈）
- [x] 2.6 刻劃面板四：牙科 MRONJ 衛教圖卡、運動營養紅綠燈與一鍵複製 SOAP 病歷
- [x] 2.7 刻劃右下角浮動 AI Copilot 對話抽屜

### 階段 3：4 組臨床示範案例快選 (Presets)
- [x] 3.1 建立 `static/js/presets.js`，定義 4 組經典個案參數
- [x] 3.2 於導航欄加入案例 1～案例 4 按鈕，點擊後透過 Alpine.js 自動填入表單並觸發計算
- [x] 3.3 驗證 4 組案例呈現之結果面板均符合預期臨床邏輯

### 階段 4：跨模組對接與聯調
- [ ] 4.1 對接組員 A 之 `predict_bone_risk()` 與 SHAP 解釋函式
- [ ] 4.2 對接組員 B 之健保審核、圍術期預警、換藥排程與 Copilot SOAP 函式
- [x] 4.3 進行例外處理（如輸入缺值時提示警告，API Key 缺失時無縫降級為 Mock 模式）

### 階段 5：VPS 部署與展示準備
- [x] 5.1 整理最終 `requirements.txt`
- [x] 5.2 撰寫 `ecosystem.config.js`（PM2 啟動設定）
- [x] 5.3 撰寫 `deploy/README_DEPLOY.md` 說明如何在 VPS 上一鍵執行與 Nginx 設定
- [ ] 5.4 於 VPS 上實際部署並測試外部存取流暢度

