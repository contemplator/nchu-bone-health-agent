# 🦴 OsteoGuard AI Agent — Plan B 執行手冊
## 醫療領域知識庫與智慧 Agent 推理模組 (Domain Knowledge & Reasoning Agent)

> **適用對象**：負責 Plan B 的 Antigravity IDE 帳號 / 開發者  
> **目標分支**：`feat/knowledge-and-agent`  
> **核心職責**：建立醫療指引知識庫（WHO 診斷標準、分級運動處方、鈣質與維生素 D 營養指引）、設計臨床安全護欄（Clinical Guardrails）、整合 LangChain / LLM 建構可解釋性智慧代理人（AI Agent），產出個人化衛教報告與互動問答。

---

### 📌 模組目標與交付清單 (Deliverables)

1. [ ] **建立醫療知識庫套件 `src/knowledge_base/`**：
   - `who_criteria.py`：WHO 骨質疏鬆診斷標準（T-score $\ge -1.0$ 正常、$-2.5 < T < -1.0$ 骨量減少、$T \le -2.5$ 骨質疏鬆）、最低部位原則（Minimum T-score）、年齡分水嶺判斷（50 歲以上 T-score vs 50 歲以下 Z-score）。
   - `exercise_guidelines.py`：風險分級運動處方庫（低/中風險：漸進負重阻抗；高風險：**嚴禁高衝擊跳躍與脊椎前彎扭轉**，優先防跌平衡訓練）。
   - `nutrition_guidelines.py`：鈣質（1,000–1,200 mg/日，單次不超過 500 mg）與維生素 D（800–1,000 IU/日）飲食與補充品指引。
2. [ ] **建立 `src/agent.py`**：
   - 整合 LangChain 與 LLM（支援 OpenAI GPT-4o / GPT-4o-mini 或 Google Gemini，並內建「無 API Key 時的結構化規則引擎 Fallback」，保證永遠不中斷報錯）。
   - 設計 System Prompt 與安全護欄（嚴禁直接給予處方藥物建議、要求高風險個案務必轉介專科醫師）。
   - 提供標準對外函式：
     - `generate_agent_report(patient_dict: dict, ml_result: dict, user_question: str = "") -> dict`
     - `chat_with_agent(chat_history: list, user_message: str, patient_context: dict) -> str`

---

### 💻 Step 1：Git 分支建立與套件準備

請在您的 Antigravity IDE 終端機執行：

```bash
# 1. 切換至獨立特徵分支
git checkout -b feat/knowledge-and-agent

# 2. 安裝必要套件 (LangChain 與 LLM 支援套件)
pip install langchain langchain-openai langchain-community python-dotenv
```

---

### 💻 Step 2：建立醫療知識庫模組 (`src/knowledge_base/`)

建立目錄 `src/knowledge_base/`，並依序新增下列檔案：

#### 1. `src/knowledge_base/__init__.py`
```python
"""
src/knowledge_base/__init__.py
"""
from .who_criteria import evaluate_who_criteria
from .exercise_guidelines import get_exercise_prescription
from .nutrition_guidelines import get_nutrition_guidelines

__all__ = ["evaluate_who_criteria", "get_exercise_prescription", "get_nutrition_guidelines"]
```

#### 2. `src/knowledge_base/who_criteria.py`
```python
"""
src/knowledge_base/who_criteria.py - WHO 與 ISCD 骨質疏鬆診斷評估準則
"""

def evaluate_who_criteria(femoral_neck_bmd: float, total_femur_bmd: float, age: int = 60, hip_fracture_history: bool = False) -> dict:
    """
    依據 NHANES III 20-29 歲健康白人女性常模換算 WHO T-score:
    - Femoral Neck: Mean = 0.858, SD = 0.120
    - Total Femur:  Mean = 0.942, SD = 0.122
    """
    t_neck = round((femoral_neck_bmd - 0.858) / 0.120, 2)
    t_total = round((total_femur_bmd - 0.942) / 0.122, 2)
    
    # 最低部位原則 (Minimum T-score Rule)
    min_t = min(t_neck, t_total)
    
    if min_t >= -1.0:
        tier = "Normal (骨量正常)"
        risk_level = "Low"
    elif min_t > -2.5:
        tier = "Osteopenia (骨量減少 / 骨質缺乏)"
        risk_level = "Moderate"
    else:
        if hip_fracture_history:
            tier = "Severe Osteoporosis (重度骨質疏鬆併骨折病史)"
        else:
            tier = "Osteoporosis (骨質疏鬆症)"
        risk_level = "High"
        
    age_note = "檢測年齡 >= 50 歲，符合 WHO T-score 診斷準則" if age >= 50 else "檢測年齡 < 50 歲，臨床建議另行參考同齡 Z-score 評估"
    
    return {
        "t_score_femoral_neck": t_neck,
        "t_score_total_femur": t_total,
        "min_t_score": min_t,
        "who_tier": tier,
        "risk_level": risk_level,
        "fracture_alert": hip_fracture_history or (min_t <= -2.5),
        "age_guideline_note": age_note
    }
```

#### 3. `src/knowledge_base/exercise_guidelines.py`
```python
"""
src/knowledge_base/exercise_guidelines.py - 分級運動處方庫與動作安全禁忌
"""

def get_exercise_prescription(risk_level: str) -> dict:
    if risk_level == "High":
        return {
            "title": "高風險等級：防跌平衡與低衝擊安全處方",
            "recommended": [
                "低衝擊負重步行：每日 20-30 分鐘平地快走，維持骨骼微應變刺激。",
                "防跌平衡與本體感覺訓練：太極拳、扶椅單腳站立（每次 10-15 秒，需有人陪同或扶穩固定物）。",
                "坐姿/抗阻肌力訓練：彈力帶坐姿划船、坐姿抬腿，強化核心與下肢肌群以預防跌倒。"
            ],
            "strict_contraindications": [
                "❌ 嚴禁高衝擊跳躍與奔跑（避免跟腱與股骨承受過大瞬間衝擊力）。",
                "❌ 嚴禁過度向前彎腰觸地動作（避免造成脊椎壓迫性骨折）。",
                "❌ 嚴禁負重下爆發性軀幹旋轉動作（如劇烈高爾夫揮桿或負重轉體）。"
            ],
            "fall_prevention_tips": "居家環境應加裝浴室扶手、移除地面鬆脫踏墊、維持室內充足照明。"
        }
    elif risk_level == "Moderate":
        return {
            "title": "中風險等級（骨量減少）：骨質強化與動態阻抗處方",
            "recommended": [
                "規律負重運動：快走、登山杖健走、爬樓梯（每日 30 分鐘）。",
                "漸進式阻抗訓練：每週 2-3 次輕中度啞鈴深蹲、推胸訓練，增進骨礦物質沉積。",
                "平衡協調訓練：瑜珈溫和伸展、單腳站立、踏步練習。"
            ],
            "strict_contraindications": [
                "⚠️ 避免未暖身進行大重量硬舉或爆發性負重轉體。"
            ],
            "fall_prevention_tips": "運動時穿著具良好防滑與支撐性之運動鞋。"
        }
    else:
        return {
            "title": "低風險等級（骨量正常）：骨骼儲備與全方位體能強化",
            "recommended": [
                "多元負重有氧運動：慢跑、跳繩、網球、登山等高地心引力刺激運動。",
                "中高強度阻抗訓練：深蹲、硬舉、肩推，每週 2-3 次提升骨峰值與肌力儲備。",
                "核心與全身協調訓練：游泳、各類球類運動。"
            ],
            "strict_contraindications": [
                "維持標準動作姿勢，避免運動傷害即可。"
            ],
            "fall_prevention_tips": "保持規律運動習慣，定期每 2 年追蹤骨密度。"
        }
```

#### 4. `src/knowledge_base/nutrition_guidelines.py`
```python
"""
src/knowledge_base/nutrition_guidelines.py - 鈣質與維生素 D 臨床營養指引
"""

def get_nutrition_guidelines(age: int = 60, gender: str = "女") -> dict:
    calcium_rec = "1,200 mg / 日" if (age >= 50 or "女" in str(gender)) else "1,000 mg / 日"
    vit_d_rec = "800 - 1,000 IU / 日"
    
    return {
        "calcium": {
            "daily_target": calcium_rec,
            "dietary_sources": "優酪乳、低脂鮮乳、傳統板豆腐、深綠色蔬菜（芥藍、地瓜葉）、小魚乾、黑芝麻。",
            "supplement_rules": "若由補充劑攝取，單次吸收上限約 500-600 mg，應分次隨餐服用；每日總攝取上限不超過 2,000-2,500 mg。"
        },
        "vitamin_d": {
            "daily_target": vit_d_rec,
            "dietary_sources": "鮭魚、鯖魚、沙丁魚、日曬乾黑木耳、強化蛋黃與菇類。",
            "sunlight_advice": "每週 3-4 次於上午 9-10 點或下午 3-4 點接受 15 分鐘溫和日照（避開正午紫外線暴曬）。"
        },
        "lifestyle_warnings": [
            "避免每日過量飲用濃咖啡（>3 杯）與碳酸飲料，以免增加尿鈣流失。",
            "戒菸並限制酒精攝取（每日酒精量男性不超過 2 當量，女性不超過 1 當量）。"
        ]
    }
```

---

### 💻 Step 3：實作 `src/agent.py`

建立 `src/agent.py`，整合知識庫與 LLM 推理：

```python
"""
src/agent.py - OsteoGuard 領域智慧代理人核心邏輯
"""
import os
import json
from dotenv import load_dotenv
from .knowledge_base.who_criteria import evaluate_who_criteria
from .knowledge_base.exercise_guidelines import get_exercise_prescription
from .knowledge_base.nutrition_guidelines import get_nutrition_guidelines

load_dotenv()

SYSTEM_GUARDRAIL_PROMPT = """
你是由國家中興大學開發的「OsteoGuard 骨骼守護者 AI 智慧醫療代理人」。
你的職責是結合醫學領域知識（WHO 準則、ISCD 規範、台灣骨質疏鬆指引）與機器學習預測數據，向民眾解釋骨密度檢測結果，並開立個人化生活健康建議。

【安全護欄與臨床原則（嚴格遵守）】：
1. 你是健康決策支援與衛教系統，絕非替代主治醫師的臨床診斷工具。
2. 絕對不可以開立特定處方藥物（如雙磷酸鹽類、RANKL抑制劑或荷爾蒙藥物）。
3. 若患者屬於高風險或具有骨折病史，必須以明確警示標籤建議前往骨科或新陳代謝科專科門診。
4. 針對高風險患者的運動建議，必須明確列出「運動安全禁忌（禁止彎腰扭轉、跳躍）」。
5. 語氣溫暖、專業、邏輯清晰、易於理解，善用列點與 Emoji。
"""

def generate_agent_report(patient_dict: dict, ml_result: dict, user_question: str = "") -> dict:
    """
    整合特徵、ML 預測結果與醫療知識庫，產出個人化衛教報告
    """
    age = int(patient_dict.get('Age', 65))
    gender = str(patient_dict.get('Gender', '女 (Female)'))
    fn_bmd = float(patient_dict.get('Femoral_Neck_BMD', 0.65))
    tf_bmd = float(patient_dict.get('Total_Femur_BMD', 0.75))
    hip_fx = "Yes" in str(patient_dict.get('History_Hip_Fracture', 'No'))
    
    # 1. 醫療知識庫規則查核
    who_res = evaluate_who_criteria(fn_bmd, tf_bmd, age=age, hip_fracture_history=hip_fx)
    risk_level = ml_result.get("risk_level", who_res["risk_level"])
    exercise_pres = get_exercise_prescription(risk_level)
    nutrition_pres = get_nutrition_guidelines(age, gender)
    
    # 2. 嘗試呼叫 LLM 增強說明 (若有 API Key)
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    llm_explanation = None
    
    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            prompt = f"""
            {SYSTEM_GUARDRAIL_PROMPT}
            
            受試者資料：
            - 年齡：{age} 歲，性別：{gender}
            - 股骨頸 BMD: {fn_bmd} (T-score: {who_res['t_score_femoral_neck']})
            - 全髖部 BMD: {tf_bmd} (T-score: {who_res['t_score_total_femur']})
            - WHO 判定分類：{who_res['who_tier']}
            - 機器學習預測風險：{risk_level} (機率：{ml_result.get('probabilities', {})})
            - 骨折病史：{'有' if hip_fx else '無'}
            - 使用者提問：{user_question if user_question else '請為我綜合解讀此報告並提供本週照護重點。'}
            
            請以專業醫師與衛教師口吻，撰寫一份個人化骨骼健康分析與叮嚀（約 300-400 字）。
            """
            resp = llm.invoke(prompt)
            llm_explanation = resp.content
        except Exception as e:
            print(f"LLM call failed, fallback to structured rule template: {e}")
            
    # 3. 若無 API Key 或呼叫失敗，啟用高品質結構化模組 Fallback
    if not llm_explanation:
        llm_explanation = f"""
### 📋 OsteoGuard AI 骨骼健康臨床綜合解讀
親愛的受試者您好，根據您的骨密度數值與機器學習風險模型評估：
- **WHO 骨密度分級**：您的最低 T-score 為 **{who_res['min_t_score']}**，判定為 **{who_res['who_tier']}**。
- **解剖部位弱點提示**：您的股骨頸 T-score ({who_res['t_score_femoral_neck']}) 需要特別注意，此處為人體承受體重槓桿力量的核心樞紐，骨密較薄弱時易增加跌倒骨折風險。
- **照護方針建議**：請參閱下方為您規劃的專屬運動處方與鈣質/維生素 D 補充計畫。{'特別提醒：由於偵測到高風險因子，請務必避免劇烈彎腰轉體動作，並儘速至骨科門診複診！' if who_res['fracture_alert'] else '請持續維持良好生活型態與肌力運動！'}
        """

    return {
        "who_evaluation": who_res,
        "exercise_prescription": exercise_pres,
        "nutrition_guidelines": nutrition_pres,
        "llm_report": llm_explanation,
        "risk_level": risk_level
    }

def chat_with_agent(chat_history: list, user_message: str, patient_context: dict) -> str:
    """
    提供給 Plan C Streamlit 聊天室的對話介面
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
            
            messages = [SystemMessage(content=SYSTEM_GUARDRAIL_PROMPT + f"\n當前個案背景: {json.dumps(patient_context, ensure_ascii=False)}")]
            for msg in chat_history[-4:]: # 最近 4 輪對話
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            messages.append(HumanMessage(content=user_message))
            
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            return llm.invoke(messages).content
        except Exception as e:
            return f"智慧代理人回覆（離線模式）：收到您的問題「{user_message}」。針對骨骼健康，建議優先攝取每日足量鈣質（1,000-1,200mg）並維持每週 2-3 次低衝擊肌力訓練，若有不適請諮詢專業醫師。"
    else:
        return f"【OsteoGuard 智慧回覆】您詢問的「{user_message}」非常重要！骨骼保養貴在持之以恆，請依照報告中的運動禁忌指引，避免重衝擊動作，並配合適度日照促進鈣質吸收。"
```

---

### 🧪 Step 4：自我驗證測試 (Verification)

請撰寫一個簡單測試確認知識庫與 Agent 回傳正常：

```bash
# 執行測試指令
python -c "
from src.agent import generate_agent_report
dummy_patient = {'Age': 68, 'Gender': '女 (Female)', 'Femoral_Neck_BMD': 0.54, 'Total_Femur_BMD': 0.75, 'History_Hip_Fracture': 'No'}
dummy_ml = {'risk_level': 'High', 'predicted_category': 'Osteoporosis (骨質疏鬆)'}
report = generate_agent_report(dummy_patient, dummy_ml)
print('✅ Test Passed! WHO Tier:', report['who_evaluation']['who_tier'])
print('✅ Exercise Title:', report['exercise_prescription']['title'])
"
```

---

### 🚀 Step 5：Commit 與 Push 到 GitHub

```bash
git add src/knowledge_base/ src/agent.py
git commit -m "feat(agent): 建立醫療知識庫(WHO/運動/營養)與 OsteoGuard 推理 Agent"
git push -u origin feat/knowledge-and-agent
```
完成後即可至 GitHub 發起 Pull Request 合併至 `main`！
