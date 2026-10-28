# OsteoGuard AI Agent：基於 NHANES 骨密度資料之骨質疏鬆風險評估與健康管理智慧代理人

> **Final Project Proposal Document**  
> **專題核心公式**：`AI Agent + Domain Knowledge + Data Analytics + Real-World Application`

---

## 1. Abstract 摘要（A–F 六段式結構）

### **A. Attention Getter — Motivation（研究動機與證據）**
隨著全球與台灣在 2025–2026 年正式邁入超高齡社會（65 歲以上人口占比突破 20%），骨質疏鬆症（Osteoporosis）已成為威脅長者健康與醫療財政的隱形殺手。根據國際骨質疏鬆基金會（IOF）與美國國家健康與營養調查（NHANES 2017–2020 Pre-pandemic DXA Femur Dataset）統計，50 歲以上族群接受股骨雙能量 X 光吸光測定法（DXA）檢測之超過 4,500 名受試者中，有顯著比例面臨骨量減少（Osteopenia）或骨質疏鬆風險；一旦發生髖骨骨折，一年內死亡率高達 20%–30%，且高達 50% 患者將永久喪失獨立行走能力。因此，如何透過 AI 結合臨床實證資料進行早期風險預警與衛教介入，是當前智慧醫療與預防醫學迫切的核心議題。

### **B. But — Challenge（現有挑戰與研究缺口）**
然而，現有的骨質疏鬆篩檢與臨床照護流程面臨多重挑戰：第一，DXA 檢測報告包含股骨頸（Femoral Neck）、全髖部（Total Femur）、轉子間（Intertrochanter）等多部位之骨礦物質密度（BMD）、骨礦物質含量（BMC）與骨骼面積（Bone Area），高度依賴專科醫師整合解讀，一般民眾難以理解抽象數值背後的臨床意義；第二，傳統機器學習模型僅輸出單一分類機率（黑盒子預測），缺乏可解釋性（Explainability）與臨床準則對齊；第三，通用型大型語言模型（LLM Chatbot）雖具備流暢對話能力，但缺乏精確數據分析能力與醫療實證約束，容易產生醫療幻覺（Hallucination），無法針對個別患者的生理指標提供客製化且安全的運動與營養處方。

### **C. Cure — Proposed Solution（解決方案）**
為了解決上述問題，本專題提出一個新的 **OsteoGuard AI Agent（骨骼守護者智慧代理人）** 系統。本系統不單純只是訓練分類模型或建置一般聊天機器人，而是整合「骨密度數據分析引擎」、「可解釋性機器學習模型」與「醫療領域知識庫（RAG）」之領域智慧代理人（Domain AI Agent），能一站式完成骨密度風險分析、骨質疏鬆風險分級、骨折風險預警、醫療知識推理，以及個人化運動與營養建議生成，並支援互動式智慧問答。

### **D. Development — Method（系統方法與整合架構）**
在系統開發上，OsteoGuard AI Agent 以 NHANES 2017–2020 DXA Femur Dataset 為核心數據基礎，擷取 Total Femur BMD、Femoral Neck BMD、Trochanter BMD、Intertrochanter BMD、BMC 與 Bone Area 等關鍵特徵進行資料前處理與特徵工程。系統底層訓練並比較 Logistic Regression、Random Forest 與 XGBoost 三種機器學習風險預測模型，並導入 SHAP（SHapley Additive exPlanations）提供特徵歸因解釋；上層則透過 LangChain 與 OpenAI API 建構具備規劃與推理能力的 Agent，結合 WHO 骨質疏鬆診斷標準、臨床骨密度評估準則、運動處方指引與鈣質/維生素 D 營養建議等領域知識（Domain Knowledge），進行多步推理與安全護欄檢核，最終透過 Streamlit 介面呈現視覺化風險報告與互動問答。

### **E. Experiments — Evaluation（實驗與驗證設計）**
本專題預計採用 NHANES 2017–2020 DXA 股骨資料集（共 4,593 位受試者，篩選出 3,545 筆有效 DXA 掃描紀錄）進行實證評估。實驗將以 Logistic Regression、Random Forest 與 XGBoost 作為相互比較的 Baseline Models，透過 K-Fold Cross Validation 驗證模型穩定度，並採用 Accuracy、Precision、Recall、F1-Score 與 ROC-AUC 作為量化評估指標；此外，將結合 SHAP 可解釋性分析與典型臨床個案研究（Case Study），驗證 AI Agent 在不同風險分級下所生成的醫療解釋與個人化建議之準確性與臨床合理性。

### **F. Findings — Expected Outcomes（預期成果）**
本專題預期完成一套端到端（End-to-End）可實際運作的 OsteoGuard AI Agent 決策支援系統，預期成果包含：（1）高準確率且具 SHAP 解釋能力之骨質疏鬆風險預測與骨折預警模組；（2）融合 WHO 臨床準則與營養運動指南之醫療知識推理系統；（3）能將複雜 DXA 指標轉譯為白話衛教報告與個人化生活處方的互動式 Streamlit Web 應用。本系統預期能有效彌平專業醫療檢測與民眾自主健康管理之間的鴻溝，展現 Domain AI Agent 在智慧醫療與高齡照護場域的實務價值。

---

## 2. Introduction 緒論（Why is this project worth doing?）

### **A. Attention Getter：高齡化浪潮下的骨骼健康危機**
根據世界衛生組織（WHO）與國際骨質疏鬆基金會（IOF）發布之全球骨骼健康報告，全球 50 歲以上女性約每 3 人就有 1 人、男性約每 5 人就有 1 人在餘生中會遭遇骨質疏鬆性骨折。在美國國家健康與營養調查（NHANES 2017–2020）公開資料集中，針對逾 4,500 名中高齡受試者進行的雙能量 X 光吸光測定法（DXA）掃描顯示，股骨頸（Femoral Neck）與全髖部（Total Femur）骨密度隨年齡增長呈現顯著衰退趨勢。台灣於 2025 年正式進入超高齡社會，髖部骨折發生率更位居亞洲前茅。由於骨質流失過程無聲無息，多數患者往往在發生跌倒骨折後才首次確診，造成沉重的家庭照護與健保醫療負擔。

### **B. Background：應用領域、目標使用者與技術背景**
在臨床實務上，DXA（Dual-Energy X-ray Absorptiometry）是目前診斷骨質疏鬆症的黃金標準（Gold Standard），透過測量特定骨骼部位（如 Total Femur、Femoral Neck、Trochanter、Intertrochanter）的骨礦物質含量（BMC, g）與投射面積（Bone Area, $\text{cm}^2$），計算出面積骨密度（BMD, $\text{g/cm}^2$），並對照年輕成人常模轉換為 T-score。
本系統的目標應用場域涵蓋**智慧醫療、預防醫學、高齡照護、個人健康管理與社區健康篩檢**：
- **一般民眾與高齡長者**：取得健檢 DXA 報告後，需要白話、易懂的風險解讀與日常飲食（鈣、維生素 D）、負重運動建議。
- **基層醫護與個管師**：在社區篩檢或門診衛教時，需要快速整合多項骨密度指標、識別高風險個案並自動生成結構化衛教單張的決策支援工具。

### **C. Problem：核心待解決問題定義**
儘管 DXA 檢測技術成熟，但從「獲得檢測數據」到「落實個人化健康管理」之間存在巨大的斷層：
1. **多維度指標整合不易**：單次股骨 DXA 掃描即產生四個解剖區域的 BMD、BMC 與 Bone Area 等十餘項數值，非專科人員難以綜合判斷局部結構弱點（如股骨頸單獨退化 vs. 轉子間退化）。
2. **檢測報告晦澀難懂**：傳統報告僅列出冰冷的數字與統計落點，民眾無法得知「這些數值對我未來骨折意味著什麼？」以及「我明天起床該如何調整飲食與運動？」。
3. **缺乏動態互動與推理解釋**：現有衛教單張為千篇一律的公版文字，無法根據個別受試者的具體特徵貢獻度進行個人化建議與追問解答。

### **D. Existing Limitations：現有方法的不足與挑戰**
1. **傳統臨床判讀與 FRAX 工具**：高度依賴專科醫師人工解讀，且傳統統計量表僅考慮單一部位（Femoral Neck BMD），忽略了 BMC、Bone Area 幾何特徵與其他股骨分區的交互影響。
2. **單純機器學習模型（Pure ML Models）**：過去研究雖使用 Logistic Regression、Random Forest 或 XGBoost 預測骨鬆風險，但輸出僅為機率值或類別標籤，缺乏臨床指引推論能力，也無法與使用者進行自然語言溝通。
3. **通用型對話機器人（Pure LLM Chatbots）**：直接將健檢數據輸入通用 LLM（如未受約束的 ChatGPT），常出現數值計算錯誤、引用非標準診斷閾值，甚至給出高跌倒風險患者不安全的劇烈運動建議。

### **E. Innovation：本專題之創新性與差異化**
本專題提出的 **OsteoGuard AI Agent** 跳脫「單純訓練 ML 模型」或「單純串接 LLM API」的框架，採用 **Neuro-Symbolic / Hybrid AI Agent 架構**：
- **精準分析與語言推理分工**：由經過 NHANES 3,545 筆真實臨床數據驗證的 ML 模型（LR / RF / XGBoost）負責嚴謹的數值風險預測，再由 LLM Agent 負責意圖理解、工具調度與報告生成。
- **Explainable AI (SHAP) 驅動的衛教解釋**：將 SHAP 特徵重要度（例如：指出該個案主要是 Femoral Neck BMD 偏低拉高風險）注入 Agent 的推理上下文，讓 AI 不僅告知風險等級，更能解釋「為什麼」。
- **領域知識庫（Domain Knowledge）護欄**：強制將 WHO 骨質疏鬆診斷標準、運動處方禁忌症與每日營養攝取上限編入知識推理層，確保建議具備臨床依據。

### **F. Contributions：本專題預期主要貢獻**
1. **資料與分析貢獻**：完成 NHANES 2017–2020 DXA Femur Dataset（4,593 名受試者、3,545 筆有效掃描）之完整清理、特徵工程與探索性資料分析（EDA），建立多部位股骨指標預測基準。
2. **模型與可解釋性貢獻**：實作並系統性比較 Logistic Regression、Random Forest 與 XGBoost 在骨鬆風險分級上的表現，並結合 SHAP 量化各解剖部位（Total Femur、Femoral Neck、Trochanter、Intertrochanter）之影響力。
3. **領域代理人架構貢獻**：設計並實作結合「ML 預測工具 + WHO/臨床知識庫推理 + 個人化運動營養處方生成」的 OsteoGuard AI Agent，並透過 Streamlit 提供完整互動式決策支援介面。

---

## 3. Related Work 相關研究（1/2 AI Technology + 1/2 Domain Know-how）

本研究同時立基於「AI 與代理人技術（AI Technology）」以及「骨質疏鬆臨床醫學與營養運動科學（Domain Know-how）」兩大支柱：

### **3.1 AI Technology：機器學習骨鬆預測、可解釋性 AI 與醫療 LLM Agent**
在醫療表格數據（Tabular Data）預測領域，集成樹模型（如 Random Forest 與 XGBoost）在處理非線性生理特徵交互作用上展現優於傳統線性模型（Logistic Regression）的效能，但臨床導入的最大障礙在於模型黑箱問題。Lundberg 與 Lee 提出的 **SHAP（SHapley Additive exPlanations）** 基於賽局理論計算各特徵對單一預測的邊際貢獻，使醫師與患者能直觀理解各生理指標如何推升或降低風險。近年（2024–2026）研究進一步從單一預測模型轉向 **Medical AI Agents**，透過 LangChain 等框架賦予大型語言模型（LLM）呼叫外部 ML 模型（Tool Calling）與檢索結構化臨床指引（RAG）的能力，有效解決純 LLM 在數值運算與專業醫療診斷上的幻覺問題。

### **3.2 Domain Know-how：DXA 股骨生物力學、WHO 診斷準則與非藥物介入處方**
在骨科與代謝性骨病領域，**世界衛生組織（WHO）** 定義了以 DXA 測量之骨密度 T-score 作為診斷標準：正常（$T \ge -1.0$）、骨量減少/骨質缺乏（$-2.5 < T < -1.0$）、骨質疏鬆症（$T \le -2.5$），以及合併骨折之嚴重骨質疏鬆症。臨床解剖學指出，近端股骨（Proximal Femur）包含股骨頸（Femoral Neck）、大轉子（Trochanter）與轉子間區（Intertrochanter），其中股骨頸皮質骨較薄且承受高剪力，是預測髖部骨折最敏感的指標；而 BMC（骨礦物質含量）與 Bone Area（骨骼投射面積）則反映了骨骼的幾何尺寸與巨觀結構強度。在預防與管理方面，臨床實證指引（如 IOF 與北美停經學會 NAMS 指南）強調非藥物介入必須包含**充足鈣質（1,000–1,200 mg/日）與維生素 D（800–1,000 IU/日）攝取**，並搭配依風險分級量身設計的**負重運動（Weight-bearing exercise）、肌力阻抗訓練與平衡防跌訓練**。

### **3.3 Article Summary Table（文獻彙整表）**

| Ref. | Year | Problem | AI Method | Domain Knowledge | Dataset | Findings | Limitation |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **[1]** Kanis et al. (WHO / IOF Guidelines) | 2019–2024 | 骨質疏鬆診斷標準化與骨折風險臨床分級 | 統計流行病學模型與臨床閾值決策規則 | WHO T-score 分級標準、股骨頸 BMD 參考基準、鈣/維生素 D 與運動介入指引 | 多國世代追蹤與流行病學資料庫 | 確立 Femoral Neck BMD 為國際標準診斷部位，並證實營養與負重運動可減緩骨流失 | 僅依賴單一指標閾值，未整合多部位 DXA 特徵與自動化個人衛教生成 |
| **[2]** NHANES / CDC NCHS Report | 2021–2024 | 美國中高齡人口近端股骨骨密度分佈與流行病學監測 | 雙能量 X 光吸光測定（DXA）影像品質控制與加權統計分析 | 近端股骨四區（Total, Neck, Troch, Intertroch）之 BMD、BMC 與 Bone Area 量測規範 | NHANES 2017–2020 Pre-pandemic DXA Femur (N=4,593) | 提供具代表性之多部位股骨 BMD/BMC/Area 基準數據，揭示高齡骨鬆盛行率 | 僅提供原始調查數據與群體統計，缺乏個人化風險預測工具與臨床解釋系統 |
| **[3]** Shim et al. / Tabular ML for Osteoporosis | 2022–2025 | 利用機器學習模型預測骨質疏鬆風險 | Logistic Regression, Random Forest, XGBoost 等監督式學習分類器 | 人口學特徵與臨床骨密度相關指標篩選 | 國民健康營養調查世代資料（NHANES / KNHANES） | XGBoost 與 Random Forest 在骨鬆風險分類之 ROC-AUC 顯著優於傳統線性迴歸 | 模型為黑盒子，僅輸出機率值，一般民眾無法理解，亦無後續健康管理建議 |
| **[4]** Lundberg et al. & Clinical XAI Studies | 2020–2025 | 醫療機器學習模型缺乏臨床可解釋性與信任度 | TreeSHAP / KernelSHAP 局部與全域特徵歸因分析 | 臨床風險因子貢獻度量化與個別病患特徵解釋 | 醫療結構化电子病歷與生理檢測資料集 | SHAP 能準確識別影響個別病患風險的關鍵生理指標，提升臨床醫師採納意願 | 視覺化圖表（如 Waterfall plot）對非專業患者仍過於抽象，缺乏自然語言轉譯 |
| **[5]** Med-Agent / Healthcare LLM Frameworks | 2025–2026 | 通用 LLM 在醫療衛教與臨床決策上的幻覺與數值推理缺陷 | LLM Agent + Tool Use + Retrieval-Augmented Generation (RAG) | 臨床實踐指南（Clinical Practice Guidelines）與結構化衛教知識庫 | 醫療問答基準測試與臨床個案情境 | 結合外部工具與領域知識庫的 Agent 能大幅降低醫療幻覺並提升個人化建議品質 | 多集中於一般內科問答，缺乏針對 DXA 骨密度多維指標與運動營養處方之專用 Agent |
| **[6]** Koh et al. (Osteoporosis Exercise & Nutrition Consensus) | 2023–2025 | 不同骨鬆風險等級患者之安全運動處方與營養補充策略制定 | 系統性文獻回顧與臨床決策樹（Clinical Pathway） | 負重衝擊運動、阻抗肌力訓練、防跌平衡訓練、高風險脊椎屈曲禁忌症、鈣與維生素 D 協同代謝 | 停經後婦女與高齡骨量減少/骨鬆臨床試驗資料 | 證實需依據骨密度嚴重度分級調整運動強度（如嚴重骨鬆應避免高衝擊與過度彎腰轉體） | 需由專業復健師或營養師人工評估開立，難以在社區篩檢或個人端大規模普及 |

### **3.4 Research Gap 歸納**

> **Existing Research → Limitations → Research Gap → Our Project**
> - **Existing Research**：臨床上已有成熟的 DXA 檢測數據（NHANES）與 WHO 診斷/衛教指南，AI 領域亦已證實 XGBoost/RF 搭配 SHAP 可有效預測並解釋表格型醫療數據，且 LLM Agent 技術日益成熟。
> - **Limitations**：現有 ML 模型停留在「輸出風險分數」，缺乏衛教溝通能力；而一般 LLM Chatbot 缺乏「精準骨密度數值分析」與「分級運動營養處方安全約束」。
> - **Research Gap**：目前缺乏一個能將 **NHANES 多部位股骨 DXA 指標（BMD/BMC/Area）**、**可解釋性機器學習（LR/RF/XGBoost + SHAP）** 與 **WHO 骨鬆醫療知識推理** 緊密結合成單一閉環工作流的領域智慧代理人。
> - **Our Project (OsteoGuard AI Agent)**：透過 AI Agent 串聯「資料驗證 $\rightarrow$ ML 風險預測與 SHAP 歸因 $\rightarrow$ WHO 知識庫推理 $\rightarrow$ 個人化運動與營養建議生成 $\rightarrow$ 互動式問答」，真正落實可解釋、可信任且具行動指導價值的智慧骨骼健康管理。

---

## 4. Deep Research：三大核心問題

針對「骨質疏鬆臨床篩檢、DXA 生物力學解讀與智慧健康管理」領域，本團隊進行深度領域調研，回答以下三大核心問題：

### **Q1. 這個領域的專家普遍認同的五個核心思維模式是什麼？**

#### **思維模式 1：骨骼健康不等於單一密度數字，而是「密度（BMD）× 幾何結構（Area/BMC）× 微觀品質」的綜合體現**
- **意義**：許多外行人只看單一 BMD 數值，但臨床專家明白面積骨密度（$\text{BMD} = \text{BMC} / \text{Bone Area}$）受限於二維投影。相同的 BMD 下，骨骼截面積（Bone Area）較小或股骨頸皮質骨較薄者，其抗彎曲與抗剪力強度截然不同。
- **證據**：NHANES DXA Femur 資料集同時記錄了 Total Femur、Femoral Neck、Trochanter 與 Intertrochanter 四區的 BMD、BMC 與 Bone Area；生物力學研究證實結合 BMC 與 Area 能更完整反映骨骼結構強度。
- **如何影響系統設計**：OsteoGuard AI Agent 的特徵工程與 ML 模型不單只取單一部位 BMD，而是同時納入四個解剖分區的 BMD、BMC 與 Bone Area（以及衍生比例特徵），讓模型捕捉骨骼密度與幾何結構的交互關係。

#### **思維模式 2：「木桶短板效應（Lowest Site Rule）」與解剖部位特異性（Site-Specific Vulnerability）**
- **意義**：在臨床判讀近端股骨時，專家不會將各部位 BMD 取平均，而是採取「最低部位決定風險基準」原則，特別重視股骨頸（Femoral Neck）與全髖部（Total Femur）。
- **證據**：WHO 與國際臨床骨密學會（ISCD）明確規範，診斷時以股骨頸或全髖部較低者的 T-score 為準；因為股骨頸位於關節囊內、血液供應脆弱且承受高機械應力，一旦此處骨密度低落，發生致命性股骨頸骨折的風險極高。
- **如何影響系統設計**：在系統的「風險評估與知識推理層（Reasoning Layer）」中，除了參考 ML 模型的整體預測機率外，我們設計了明確的 WHO 規則檢核機制，針對 Femoral Neck BMD 異常偏低者觸發專項骨折預警（Fracture Alert）。

#### **思維模式 3：預防勝於治療，且「鈣質、維生素 D 與機械負重刺激」具有不可分割的生理協同作用**
- **意義**：專家認為骨質疏鬆管理絕非「單純吃鈣片」就能解決。沒有足夠的維生素 D，腸道對鈣質的吸收率極低；而沒有透過負重運動產生機械應力（Wolff's Law 沃夫定律），補充的鈣質也無法有效促進成骨細胞（Osteoblasts）進行骨質沉積。
- **證據**：多項隨機對照試驗（RCT）與 IOF 臨床指南指出，單獨補鈣對降低骨折率效果有限，必須採取「鈣 + 維生素 D + 規律負重與肌力訓練」的三合一整合介入。
- **如何影響系統設計**：OsteoGuard AI Agent 的知識庫推理模組強制將建議拆分為「個人化營養建議（鈣質飲食來源 + 維生素 D 日照與補充）」與「個人化運動處方（負重 + 肌力 + 平衡）」雙軌並陳，不會給出片面的單一建議。

#### **思維模式 4：運動處方的「風險分級安全邊界（Risk-Stratified Exercise Safety）」**
- **意義**：雖然運動有益骨密，但專家極度重視「不同骨鬆程度對應不同的運動禁忌」。對健康或輕度骨量減少者，跳躍、慢跑等高衝擊負重運動能刺激骨生成；但對已達嚴重骨質疏鬆或高骨折風險者，高衝擊運動或過度脊椎前彎/扭轉動作（如仰臥起坐、高爾夫急轉體）反而會直接誘發壓迫性骨折或跌倒髖部骨折。
- **證據**：美國運動醫學會（ACSM）與物理治療骨鬆運動指引嚴格區分「預防期（高/中衝擊負重）」與「高風險期（低衝擊負重、姿勢穩定與防跌平衡訓練優先）」。
- **如何影響系統設計**：Agent 在生成運動建議（模块 G）前，必須先讀取前一步驟的「骨質疏鬆風險分級（模块 E）」結果。若判定為高風險等級，系統規則會自動過濾高衝擊運動，改為推薦安全肌力與防跌平衡訓練，並附上居家防跌警語。

#### **思維模式 5：可解釋性與風險溝通是決定患者「醫囑順從性（Adherence）」的關鍵**
- **意義**：骨質疏鬆是「沉默的疾病」，在骨折發生前毫無痛感，導致患者對生活型態調整或定期追蹤的順從性極低。臨床專家深知，唯有將抽象的 BMD/T-score 轉化為患者聽得懂的具體部位風險解釋與可執行的日常微習慣，才能真正改變行為。
- **證據**：預防醫學研究顯示，提供視覺化且個人化的 DXA 報告解讀，能顯著提升患者後續補充鈣/維生素 D 與參與規律運動的比例。
- **如何影響系統設計**：本系統整合 **Explainable AI (SHAP)** 與 **LLM 自然語言生成**，將模型內部特徵貢獻度轉譯為結構化風險報告與互動問答，讓使用者不僅看到「高風險」，更能看懂「因為您的股骨頸 BMD 與 BMC 低於標準，導致髖部支撐力下降，因此建議...」。

---

### **Q2. 這個領域專家爭論最激烈的三個問題是什麼？**

#### **爭論一：骨鬆與骨折風險評估應以「純 BMD 指標（WHO T-score）」為核心，還是「多維度臨床因子與骨骼幾何複合模型」？**
- **觀點 A（BMD 核心派）**：主張以 DXA 測得之 Femoral Neck / Total Femur BMD（及對應 T-score）作為唯一核心診斷與分級依據，因其量測標準化程度最高、重現性最好，且全球臨床試驗藥物適應症皆以此為基準。
- **觀點 B（多維度複合模型派）**：主張單看 BMD 會漏掉超過半數實際發生骨折的「骨量減少（Osteopenia）」患者；應同時整合 BMC、Bone Area 等骨骼幾何參數以及多部位（Trochanter、Intertrochanter）退化特徵，透過機器學習捕捉非線性結構弱點。
- **雙方最有力的證據**：
  - 觀點 A 證據：BMD 每下降 1 個標準差（SD），骨折風險即呈指數型翻倍（約 1.5–2.6 倍），是單一最強預測因子。
  - 觀點 B 證據：流行病學數據顯示，絕對數量上發生髖部骨折的患者中，有相當大比例其 T-score 落在 $-1.0$ 到 $-2.5$ 之間（尚未達 $-2.5$ 骨鬆門檻），顯示單一 BMD 閾值敏感度不足。
- **目前共識**：WHO T-score 仍是不可取代的臨床診斷基準，但結合多部位 DXA 特徵（BMD + BMC + Area）與機器學習模型，能提供更細膩的早期風險預警。
- **尚未解決的問題**：如何將多特徵 ML 模型的複合風險分數與傳統 WHO 分級無縫對接，避免臨床判讀混淆？（*本專題透過將 ML 預測與 WHO 診斷標準雙軌整合於 Reasoning Layer 來回應此問題*）。

#### **爭論二：在臨床醫療決策支援中，應採用「高可解釋性的傳統統計模型（Logistic Regression）」還是「高準確率的複雜集成模型（XGBoost / Random Forest）」？**
- **觀點 A（白盒統計模型派）**：醫療領域人命關天，主張使用 Logistic Regression，因為每個特徵的 Odds Ratio（勝算比）清晰透明，完全符合循證醫學（Evidence-Based Medicine）的線性因果直覺。
- **觀點 B（高效能樹模型 + XAI 派）**：人體骨骼生理指標（如不同部位的 BMD、BMC 與面積比值）存在高度共線性與非線性交互作用，主張採用 Random Forest 或 XGBoost 以取得最佳 ROC-AUC 與 Recall（減少漏診），再以事後解釋技術（Post-hoc XAI 如 SHAP）補足透明度。
- **雙方最有力的證據**：
  - 觀點 A 證據：FDA 與臨床指南長期偏好結構簡單、可直接在紙本公式驗算的邏輯迴歸模型，避免複雜模型在分布外數據（Out-of-Distribution）產生不可預期的跳躍。
  - 觀點 B 證據：在 NHANES 等大型醫療表格資料集競賽與實證研究中，XGBoost 與 Random Forest 的分類效能穩定優於線性模型，且 TreeSHAP 已能精確算出單一預測的特徵加總貢獻。
- **目前共識**：不應盲目追求黑盒高分，也不應犧牲預測準確度；最佳實踐是**同時訓練 Baseline 線性模型（Logistic Regression）與樹模型（RF、XGBoost）進行對照驗證**，並強制搭配 SHAP 解釋。
- **尚未解決的問題**：當 SHAP 的局部特徵歸因與臨床直覺發生衝突（例如因特徵高度共線性導致某部位 BMD 的 SHAP 值符號反轉）時，該如何向患者解釋？

#### **爭論三：醫療健康管理 AI Agent 應給予 LLM 多大的自主生成自由度？（「嚴格規則模版 Rule-Based」vs.「開放式生成 Agentic LLM」）**
- **觀點 A（嚴格臨床規則與專家系統派）**：認為醫療建議（運動與營養劑量）容錯率極低，所有輸出應由預先寫死的 If-Else 規則樹與固定衛教模版決定，LLM 最多只能做文字潤飾。
- **觀點 B（自主推理 LLM Agent 派）**：認為固定模版僵化冰冷，無法處理使用者多變的生活情境問答（例如：「我不喝牛奶又膝蓋痛，該怎麼補鈣和運動？」）；應賦予 LLM Agent 動態檢索知識庫並綜合推理生成個人化方案的能力。
- **雙方最有力的證據**：
  - 觀點 A 證據：多篇醫療 AI 評估論文指出，無約束的 LLM 在醫療問答中可能編造不存在的臨床數據或給出超過安全上限的補充劑量。
  - 觀點 B 證據：具備 RAG（檢索增強生成）與結構化 Prompt 約束的領域 Agent，在病患同理心、衛教易讀性與長尾情境應對上遠勝傳統專家系統。
- **目前共識**：採用 **Neuro-Symbolic 混合防護架構**——診斷分級與高風險禁忌由確定性程式與 ML 模型把關，而衛教轉譯與情境配適則由受領域知識庫（RAG）嚴格約束的 LLM Agent 執行。
- **尚未解決的問題**：如何量化評估 AI Agent 生成之個人化健康建議的「臨床忠實度（Clinical Faithfulness）」與「安全性」？

---

### **Q3. 設計 10 個深度理解問題（判斷真正深入了解 vs. 死記硬背）**

以下 10 個問題涵蓋 *Why, What-if, Trade-off, Failure Case, Evidence, Comparison, Design Decision, Real-world Scenario* 八大推理層次：

1. **[Why / 生物力學與解剖學]**  
   *問題*：為什麼在 NHANES DXA 股骨檢測中，臨床醫師與 WHO 標準特別看重「股骨頸（Femoral Neck）BMD」，而不是只看面積最大、數值最穩定的「全髖部（Total Femur）BMD」或「轉子間（Intertrochanter）BMD」？  
   *深度理解重點*：股骨頸解剖結構狹窄、皮質骨薄、承受人體站立與跌倒時極大的彎曲力矩與剪力，且位於關節囊內（一旦骨折極易引發缺血性股骨頭壞死），因此在骨折預警上具有不可被平均稀釋的臨床特異性。

2. **[What-if / 特徵物理意義與共線性]**  
   *問題*：已知 $\text{BMD} = \text{BMC} / \text{Bone Area}$。如果兩位受試者的 Total Femur BMD 完全相同（皆為 $0.75\text{ g/cm}^2$），但受試者 A 的 Bone Area 與 BMC 都遠小於受試者 B，這在生物力學與我們的 ML 模型特徵工程中代表什麼意義？  
   *深度理解重點*：DXA 測量的是二維投影面積骨密度（areal BMD）而非真實三維體積密度。骨架較小者（Bone Area 小）在二維投影下 BMD 常被低估，但其骨骼截面慣性矩（抗彎強度）也確實較小；模型同時納入 BMC 與 Bone Area 有助於校正體型幾何差異。

3. **[Trade-off / 評估指標選擇]**  
   *問題*：在訓練 OsteoGuard AI Agent 的骨質疏鬆高風險篩檢模型時，若必須在 Precision（精確率）與 Recall（召回率/敏感度）之間做取捨，你會優先最佳化哪一個指標？為什麼？這會帶來什麼代價？  
   *深度理解重點*：在預防醫學與社區篩檢場域，應優先確保高 **Recall（敏感度）**，因為將高骨折風險者漏判為正常（False Negative）可能導致長者錯失防跌與治療良機而發生致命髖部骨折；其代價是 False Positive 增加（部分臨界骨量減少者被高度預警），但後續僅需轉介醫師複查與加強安全生活管理，傷害遠小於漏診。

4. **[Failure Case / 資料前處理與臨床異常值]**  
   *問題*：在處理 NHANES 2017–2020 DXA 資料集時（4,593 位受試者中僅 3,545 筆有效掃描），什麼臨床情況會導致 DXA 掃描無效或使特定部位 BMD 出現極端假性偏高（Artifact）？若未妥善處理會如何誤導 AI Agent？  
   *深度理解重點*：曾接受人工髖關節置換術、嚴重退化性關節炎骨刺增生、血管鈣化或金屬植入物，會導致無效掃描或 X 光吸收異常升高（造成 BMD 假性正常）。若系統未在「資料驗證（Data Validation）」階段檢查各部位（如 Neck vs. Trochanter）之合理比值與異常值，Agent 可能會對高風險患者給出錯誤的安心報告。

5. **[Comparison / 模型特性比較]**  
   *問題*：本專題同時採用 Logistic Regression、Random Forest 與 XGBoost。既然在表格資料中高度相關的樹模型（XGBoost）通常準確率最高，為什麼我們仍堅持保留 Logistic Regression 與 Random Forest 進行比較？  
   *深度理解重點*：由於四個股骨部位的 BMD、BMC、Area 之間存在高度多重共線性（Multicollinearity），Logistic Regression 可檢驗線性可分性與基準效能，Random Forest（Bagging）可降低變異數並抗過擬合，而 XGBoost（Boosting）擅長捕捉殘差與非線性邊界；三者對照加上 K-Fold 交叉驗證，才能證明複雜模型是否真的帶來實質增益而非過擬合。

6. **[Evidence / 可解釋性 AI 陷阱]**  
   *問題*：當我們使用 SHAP 解釋 XGBoost 模型對某位患者的預測時，若發現該患者的 Femoral Neck BMD 與 Intertrochanter BMD 都很低，但 SHAP 卻顯示只有 Femoral Neck BMD 有極大的正向風險貢獻，而 Intertrochanter BMD 貢獻接近零，這是否代表該患者轉子間骨骼很健康？  
   *深度理解重點*：不是。這是樹模型在面對高度共線性特徵時，傾向優先挑選資訊獲利最高之特徵（Femoral Neck）進行分裂的現象。因此 Agent 在「知識庫推理」時，不能只盲目念出 SHAP 數值，必須結合各部位原始數值與臨床基準進行綜合解讀。

7. **[Design Decision / 架構設計抉擇]**  
   *問題*：為什麼 OsteoGuard AI Agent 要設計成「先經過 ML 模型預測與風險分級，再進入領域知識庫推理與 LLM 生成」，而不是直接把使用者的 BMD/BMC/Area 數值放進 Prompt 讓 OpenAI API（LLM）直接判斷骨鬆風險並給建議？  
   *深度理解重點*：直接讓 LLM 處理連續浮點數特徵不僅缺乏在 NHANES 3,545 筆群體分布上的統計校準（Calibration），且每次生成的風險判定可能不一致（Non-deterministic）並產生幻覺；將「數值預測/分級」交給確定性的 ML 與 WHO 規則，將「知識整合與自然語言溝通」交給 LLM Agent，才能兼顧統計嚴謹度與互動體驗。

8. **[Real-world Scenario / 臨床處方衝突處理]**  
   *問題*：假設一位 72 歲女性受試者經模型判定為「高骨質疏鬆與骨折風險」，她向 AI Agent 提問：「我聽說跳繩跟慢跑最能增加骨密度，而且我買了高劑量鈣片打算每天吃 2,500 mg，這樣好嗎？」Agent 應該如何推理並回應？  
   *深度理解重點*：Agent 必須識別兩大臨床危險：（1）對高骨折風險長者，跳繩等高衝擊運動極易引發跌倒與骨折，應改為低衝擊負重、阻抗訓練與平衡防跌運動；（2）每日鈣質攝取上限約為 2,000–2,500 mg（建議量 1,000–1,200 mg），單次吸收有限且過量補鈣會增加腎結石與心血管鈣化風險，並提醒需搭配維生素 D。

9. **[What-if / 族群與分佈偏移 Domain Shift]**  
   *問題*：我們的模型是基於美國 NHANES 2017–2020 資料集訓練的，如果未來將 OsteoGuard AI Agent 直接部署到台灣社區健康篩檢供台灣長者使用，可能會遇到什麼資料分佈偏移（Distribution Shift）問題？系統應如何緩解？  
   *深度理解重點*：亞洲人（台灣族群）的平均體型、骨骼面積（Bone Area）與基準 BMD 普遍低於歐美非裔族群。若直接套用未經校正的絕對 BMC/Area 門檻可能高估風險；系統設計上應透過相對比例特徵、T-score 標準化概念，並在輸出報告中標註資料來源限制與台灣臨床轉介建議。

10. **[Design Decision / 醫療倫理與責任邊界]**  
    *問題*：作為一個醫療健康領域的 AI Agent，「決策支援（Decision Support）」與「醫療診斷處方（Medical Diagnosis）」的法律與倫理界線在哪裡？這如何在系統流程中體現？  
    *深度理解重點*：AI Agent 定位為「健康風險評估、衛教解釋與臨床決策支援工具」，絕不可取代醫師開立處方藥（如雙磷酸鹽類、Denosumab 等抗骨鬆藥物）。在系統輸出層（Application Layer），必須明確區分生活型態建議（運動/營養）與專科醫療轉介警語，當檢測出高骨折預警時，強制提示尋求骨科或家醫科醫師進行臨床確診。

---

## 5. Proposed Scheme / Proposed Design（系統設計）

為完全符合「Domain AI Agent」之設計要求，並忠實呈現 **OsteoGuard AI Agent** 的六層核心架構與九步運作流程，本節將系統模組進行 **①–⑧ 標準化編號對應**，並提供完整 **System Architecture**、**Flowchart** 與 **Pseudocode**。

### **5.1 System Architecture（系統架構圖與模組說明）**

以下系統架構圖保留本專題原有的六大核心分層（Data Layer、Analytics Layer、AI Layer、Domain Knowledge、Reasoning Layer、Application Layer），並標註 **①–⑧ 代理人核心模組編號**：

```mermaid
flowchart TD

A["① 使用者 User (臨床/健檢應用場域)"] --> B["② OsteoGuard AI Agent (Query & Planner 互動入口)"]

subgraph Data_Layer ["④ Data Layer (資料擷取與驗證層)"]
C["NHANES DXA Dataset (2017-2020)"]
D["BMD (Total / Neck / Troch / Intertroch)"]
E["BMC (Bone Mineral Content)"]
F["Bone Area (骨骼面積)"]
end

subgraph Analytics_Layer ["⑤ Analytics Layer (資料分析與特徵工程層)"]
G["資料前處理与驗證 (Data Preprocessing)"]
H["特徵工程 (Feature Engineering)"]
I["探索性資料分析 (EDA 分析)"]
end

subgraph AI_Layer ["⑤ AI Layer (機器學習風險預測層)"]
J["Logistic Regression"]
K["Random Forest"]
L["XGBoost"]
M["風險預測模型 (Risk Prediction &的分級)"]
end

subgraph Domain_Knowledge ["⑥ Domain Knowledge (醫療領域知識庫)"]
N["WHO 骨質疏鬆診斷標準"]
O["骨質疏鬆臨床知識庫"]
P["分級運動處方建議庫"]
Q["鈣質與維生素 D 營養建議庫"]
end

subgraph Reasoning_Layer ["③ & ⑦ Reasoning Layer (知識推理與可解釋決策層)"]
R["骨密與骨折風險評估 (Risk Assessment)"]
S["醫療知識庫推理 (Knowledge Reasoning)"]
T["個人化運動與營養建議生成 (Personalized Recommendation)"]
U["Explainable AI (SHAP 特徵歸因解釋)"]
end

subgraph Application_Layer ["⑧ Application Layer (應用輸出與互動層)"]
V["個人化風險報告 (Risk Report)"]
W["骨折風險預警 (Fracture Warning)"]
X["個人化健康建議 (Health Advice)"]
Y["智慧問答與決策支援 (Interactive QA & Decision Support)"]
end

B --> D
B --> E
B --> F
C --> G
D --> G
E --> G
F --> G

G --> H --> I
I --> J
I --> K
I --> L

J --> M
K --> M
L --> M

M --> R
N --> S
O --> S
P --> S
Q --> S

R --> S --> T --> U

U --> V
U --> W
U --> X
U --> Y
Y -. "使用者追問回饋 (Multi-turn QA)" .-> B
```

#### **各主要模組（①–⑧）詳細說明：**
- **① User / Application Scenario（使用者與應用場域）**：涵蓋接受 DXA 骨密度檢測之一般中高齡民眾、家屬，以及社區篩檢或預防醫學門診之醫護個管人員。
- **② Query / Input & OsteoGuard AI Agent Interface（查詢與輸入入口）**：透過 Streamlit 建構之互動介面，接收使用者輸入之近端股骨 DXA 檢測數值（Total Femur、Femoral Neck、Trochanter、Intertrochanter 之 BMD、BMC、Bone Area）與自然語言健康提問。
- **③ Planner & Reasoning Coordinator（代理人規劃與協調中樞）**：基於 LangChain 與 OpenAI API 實作之 Agent 核心，負責解析使用者意圖，依序調度「資料驗證」、「ML 風險預測工具」、「SHAP 解釋器」與「醫療知識庫檢索（RAG）」。
- **④ Data Layer（資料擷取與驗證層）**：以 NHANES 2017–2020 DXA Femur Dataset（4,593 位受試者、3,545 筆有效掃描）為底層基準資料庫，負責驗證輸入之 BMD、BMC 與 Bone Area 數值完整性與生理合理範圍。
- **⑤ Analytics & AI Layer（資料分析與機器學習引擎）**：執行缺失值處理、衍生特徵計算（Feature Engineering）與 EDA 分佈對照；平行整合 **Logistic Regression**、**Random Forest** 與 **XGBoost** 三大監督式學習模型，輸出骨質疏鬆風險機率與風險分級。
- **⑥ Domain Knowledge Integration（領域知識庫層）**：結構化儲存四大領域知識——**WHO 骨質疏鬆診斷標準**、**骨質疏鬆病理知識庫**、**分級運動處方建議**（負重、肌力、防跌禁忌）以及**鈣質與維生素 D 營養建議**。
- **⑦ Reasoning & Decision Layer（推理、建議生成與 XAI 層）**：將 ML 預測之骨鬆風險分級（`R`）與領域知識庫進行交叉推理（`S`），生成安全合規之個人化運動與營養處方（`T`），並結合 **SHAP（Explainable AI, `U`）** 量化各解剖部位指標對該名使用者風險的正負向影響。
- **⑧ Output & Interaction Layer（輸出與多輪互動層）**：向使用者輸出四大核心成果——**風險報告（`V`）**、**骨折預警（`W`）**、**個人化健康建議（`X`）** 與 **決策支援智慧問答（`Y`）**，支援使用者針對報告內容進行多輪自然語言追問。

---

### **5.2 AI Agent Flowchart（運作流程圖）**

為了完整呈現 `Input → Processing → AI/Analytics → Decision → Output` 的處理邏輯，我們在原有的九步驟核心主幹（`使用者輸入資料 → 資料驗證 → 特徵工程 → 機器學習模型 → 骨質疏鬆風險分級 → 知識庫推理 → 產生個人化建議 → AI Agent回覆 → 健康管理報告`）基礎上，明確標示條件判斷（Decision）、異常處理迴圈（Exception Loop）與使用者互動迴圈（Human Interaction）：

```mermaid
flowchart TD
    A["1. 使用者輸入資料<br/>(DXA BMD / BMC / Bone Area & 提問)"] --> B{"2. 資料驗證<br/>(數值完整性與生理範圍檢核)"}
    
    B -- "驗證失敗 (Exception:<br/>缺失值或異常極端值)" --> B_ERR["提示修正輸入或標記掃描異常<br/>(Request Valid Input)"]
    B_ERR --> A
    
    B -- "驗證通過 (Valid)" --> C["3. 特徵工程 (Feature Engineering)<br/>計算多部位比值與標準化特徵"]
    C --> D["4. 機器學習模型推論<br/>(Logistic Regression / Random Forest / XGBoost)<br/>+ SHAP 特徵貢獻度計算"]
    
    D --> E{"5. 骨質疏鬆風險分級<br/>(Risk Stratification & WHO 基準比對)"}
    
    E -- "Low Risk (正常範圍)" --> F1["檢索：一般骨骼保養與初級預防知識"]
    E -- "Moderate Risk (骨量減少預警)" --> F2["檢索：骨流失減緩、強化負重與營養知識"]
    E -- "High Risk (骨質疏鬆 / 骨折高危)" --> F3["觸發：骨折風險預警 (Fracture Warning)<br/>檢索：高風險安全運動禁忌與專科轉介指引"]
    
    F1 --> F["6. 知識庫推理 (Domain Knowledge Reasoning)<br/>整合 WHO 標準 + SHAP 關鍵弱點部位解釋"]
    F2 --> F
    F3 --> F
    
    F --> G["7. 產生個人化建議<br/>(個人化運動處方 + 鈣質與維生素 D 營養建議)"]
    G --> H["8. AI Agent 回覆生成<br/>(LangChain + OpenAI API 整合 XAI 解釋與安全護欄)"]
    H --> I["9. 輸出健康管理報告 & 視覺化圖表<br/>(風險報告 / 骨折預警 / 健康建議 / 決策支援)"]
    
    I --> J{"使用者是否繼續追問？<br/>(Interactive Q&A Loop)"}
    J -- "是 (輸入追問 Query)" --> F
    J -- "否 (結束互動)" --> K(["完成健康管理諮詢流程"])
```

---

### **5.3 Pseudocode（核心演算法）**

以下提供具備行號之 **OsteoGuard AI Agent** 核心演算法 Pseudocode，涵蓋資料驗證、多模型推論、SHAP 解釋、領域知識推理與互動式個人化建議生成：

```text
Algorithm 1: OsteoGuard Domain AI Agent for Osteoporosis Risk & Health Management
Input : User DXA Features X_user = {BMD_sites, BMC_sites, Area_sites}, User Query Q
        Trained Models M = {M_LR, M_RF, M_XGB}, NHANES Reference Stats D_ref
        Domain Knowledge Base KB = {KB_WHO, KB_Osteo, KB_Exercise, KB_Nutrition}
Output: Comprehensive Health Management Report R_final (Risk Tier, Fracture Alert, XAI Explanation, Personalized Advice)

01: Receive user input data X_user and natural language query Q
02: // Step 1 & 2: Data Validation & Preprocessing
03: is_valid, validation_msg <- ValidatePhysiologicalBounds(X_user, D_ref)
04: if is_valid == False then
05:     return PromptUserCorrection(validation_msg)
06: end if
07: // Step 3: Feature Engineering
08: X_feat <- ComputeEngineeredFeatures(X_user, D_ref)  // Site ratios, regional BMD/BMC/Area alignments
09: // Step 4: Machine Learning Inference & Explainable AI (SHAP)
10: P_LR  <- M_LR.predict_proba(X_feat)
11: P_RF  <- M_RF.predict_proba(X_feat)
12: P_XGB <- M_XGB.predict_proba(X_feat)
13: P_risk <- SelectOptimalEnsembleOrBestModel(P_LR, P_RF, P_XGB)
14: shap_values, top_risk_factors <- ComputeSHAPExplanation(M_XGB, X_feat)
15: // Step 5: Osteoporosis Risk Stratification & WHO Rule Alignment
16: who_status, min_site <- CheckWHODiagnosticCriteria(X_user.BMD_sites, KB_WHO)
17: risk_tier, fracture_warning <- DetermineRiskTier(P_risk, who_status)
18: // Step 6: Domain Knowledge Reasoning
19: retrieved_rules <- RetrieveDomainKnowledge(KB, risk_tier, min_site, top_risk_factors, Q)
20: if risk_tier == "High_Risk" then
21:     exercise_constraints <- FilterHighImpactAndSpinalFlexion(KB_Exercise)
22: else
23:     exercise_constraints <- StandardWeightBearingProtocol(KB_Exercise, risk_tier)
24: end if
25: nutrition_plan <- FormulateCalciumVitaminDPlan(KB_Nutrition, risk_tier, Q)
26: // Step 7, 8 & 9: Personalized Recommendation & Agent Response Generation
27: prompt_context <- BuildAgentPrompt(P_risk, risk_tier, fracture_warning, shap_values, retrieved_rules, exercise_constraints, nutrition_plan, Q)
28: agent_response <- LLM_Agent_Generate(prompt_context)
29: R_final <- FormatHealthManagementReport(agent_response, P_risk, risk_tier, fracture_warning, shap_values)
30: Present R_final on Streamlit Dashboard and listen for follow-up user queries
31: return R_final
```

---

## 6. Experimental Design & Expected Outcomes（實驗規劃與預期成果）

### **6.1 Dataset（資料集說明）**
- **資料來源**：美國國家健康與營養調查 **NHANES 2017–2020 Pre-pandemic DXA Femur Dataset**（檔案代碼：`P_DXXFEM`）。
- **資料規模**：共包含 **4,593 位受試者**，經排除金屬植入物、掃描不完整或無效紀錄後，取得 **3,545 筆有效 DXA 掃描樣本**。
- **核心使用特徵**：
  1. `Total Femur BMD`（全髖部骨礦物質密度, $\text{g/cm}^2$）
  2. `Femoral Neck BMD`（股骨頸骨礦物質密度, $\text{g/cm}^2$）
  3. `Trochanter BMD`（大轉子骨礦物質密度, $\text{g/cm}^2$）
  4. `Intertrochanter BMD`（轉子間骨礦物質密度, $\text{g/cm}^2$）
  5. `Bone Mineral Content (BMC)`（各部位骨礦物質含量, $\text{g}$）
  6. `Bone Area`（各部位骨骼投射面積, $\text{cm}^2$）

### **6.2 Baseline Models & Evaluation Metrics（基準模型與評估指標）**
- **比較模型（Baseline Models）**：
  1. **Logistic Regression**：線性可解釋基準模型。
  2. **Random Forest**：Bagging 集成決策樹模型。
  3. **XGBoost**：Gradient Boosting 高效能樹模型。
- **量化評估指標（Evaluation Metrics）**：
  - **Accuracy**（整體分類準確率）
  - **Precision**（精確率：預測為高風險中實際為高風險之比例）
  - **Recall / Sensitivity**（召回率：實際高風險個案被成功攔截之比例，醫療篩檢關鍵指標）
  - **F1-Score**（Precision 與 Recall 之調和平均數）
  - **ROC-AUC**（受試者工作特徵曲線下面積，衡量不同閾值下之整體鑑別力）
- **驗證方式（Validation Plan）**：
  - **K-Fold Cross Validation**（例如 5-Fold 或 10-Fold 交叉驗證，確保模型非因特定切分而過擬合）。
  - **Explainable AI 分析**：使用 SHAP Summary Plot 與 Individual Waterfall Plot 驗證特徵重要度是否符合骨科生物力學認知。
  - **Case Study（臨床情境個案測試）**：設計低風險、中度骨量減少、重度股骨頸骨鬆合併高骨折風險等代表性案例，端到端驗證 OsteoGuard AI Agent 的報告品質與問答正確性。

### **6.3 Expected Outcomes（預期成果）**
（*註：目前處於 Proposal 階段，以下為預期成果，絕不虛構未執行之實驗數據*）
1. ✅ **骨質疏鬆風險預測系統**：完成三大 ML 模型訓練與交叉驗證比較，預期 XGBoost 與 Random Forest 能有效捕捉多部位 BMD/BMC/Area 的非線性關係，達到優異的 ROC-AUC 與高 Recall 表現。
2. ✅ **Explainable AI 解釋機制**：透過 SHAP 視覺化呈現個別受試者之脆弱骨骼部位（如股骨頸 vs. 轉子間），提升系統可信度。
3. ✅ **醫療知識推理與骨折風險預警功能**：準確對齊 WHO 診斷標準，當關鍵部位低於安全閾值時自動觸發骨折預警。
4. ✅ **個人化健康建議與 AI Agent 智慧問答功能**：透過 LangChain + OpenAI API + Streamlit 打造互動平台，根據風險分級生成客製化運動處方與鈣質/維生素 D 營養方案。

---

## 7. References 參考文獻

1. **Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS).** (2021). *National Health and Nutrition Examination Survey (NHANES) 2017–March 2020 Pre-pandemic Data Files: Dual-Energy X-ray Absorptiometry - Femur (P_DXXFEM)*. U.S. Department of Health and Human Services. https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/P_DXXFEM.htm
2. **Kanis, J. A., Cooper, C., Rizzoli, R., & Reginster, J. Y.** (2019). European guidance for the diagnosis and management of osteoporosis in postmenopausal women. *Osteoporosis International*, 30(1), 3–44. (WHO Diagnostic Criteria & IOF Clinical Guidelines)
3. **LeBoff, M. S., Greenspan, S. L., Insogna, K. L., Lewiecki, E. M., Saag, K. G., Singer, A. J., & Siris, E. S.** (2022). The clinician's guide to prevention and treatment of osteoporosis. *Osteoporosis International*, 33(10), 2049–2102.
4. **Lundberg, S. M., & Lee, S. I.** (2017). A unified approach to interpreting model predictions (SHAP). *Advances in Neural Information Processing Systems (NeurIPS)*, 30.
5. **Chen, T., & Guestrin, C.** (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794.
6. **Brooke-Wavell, K., Skelton, D. A., Barker, K. L., Clark, E. M., De Biase, S., Arnold, S., ... & Tobias, J. H.** (2022). Strong, steady and straight: UK consensus statement on physical activity and exercise for osteoporosis. *British Journal of Sports Medicine*, 56(15), 837–846.
