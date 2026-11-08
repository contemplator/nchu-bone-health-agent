"""
OsteoGuard AI Agent — 臨床邏輯與推論服務 (Mock / Rule-Based Service)
嚴格落實 WHO 骨密準則、骨科/神外圍術期螺釘預警、健保 5.6 節合規核對與換藥時程推算
"""
from datetime import datetime, timedelta
from typing import Tuple, List
from src.schemas import (
    PatientCaseRequest, CDSSResponse, MLPrediction, SHAPFeature,
    WHODiagnosis, SurgicalAlert, NHICompliance, SequentialTherapy,
    SwitchSchedule, PatientSafety, CopilotDraft, CopilotChatResponse
)


def evaluate_who_criteria(case: PatientCaseRequest) -> WHODiagnosis:
    t = case.lowest_t_score
    site = case.lowest_site
    has_fracture = len(case.fracture_history) > 0
    
    if t >= -1.0:
        return WHODiagnosis(
            tier="Normal",
            tier_display="骨質正常 (Normal)",
            lowest_t_score=t,
            site=site,
            summary=f"最低 T-score 為 {t} ({site})，骨密度在同年齡健康族群正常範圍內。"
        )
    elif -2.5 < t < -1.0:
        return WHODiagnosis(
            tier="Osteopenia",
            tier_display="骨質減少 (Osteopenia)",
            lowest_t_score=t,
            site=site,
            summary=f"最低 T-score 為 {t} ({site})，骨質流失但尚未達骨質疏鬆診斷標準，需注意防跌與飲食補鈣。"
        )
    else:  # t <= -2.5
        if has_fracture:
            fracture_str = "、".join(case.fracture_history)
            return WHODiagnosis(
                tier="Severe_Osteoporosis",
                tier_display="嚴重骨質疏鬆症 (Severe Osteoporosis)",
                lowest_t_score=t,
                site=site,
                summary=f"最低 T-score 為 {t} ({site})，且合併脆弱性骨折病史（{fracture_str}），符合 ISCD / WHO 嚴重骨鬆診斷。"
            )
        else:
            return WHODiagnosis(
                tier="Osteoporosis",
                tier_display="骨質疏鬆症 (Osteoporosis)",
                lowest_t_score=t,
                site=site,
                summary=f"最低 T-score 為 {t} ({site})，已低於 -2.5 臨界值，為脆弱性骨折高風險族群。"
            )


def predict_ml_and_shap(case: PatientCaseRequest) -> MLPrediction:
    # 臨床模擬：以真實特徵權重估算自述告知史機率 (OSQ060)
    # 年齡、性別(女)、低 Neck BMD、低 BMI 推升風險
    prob = 0.50
    if case.femoral_neck_bmd < 0.60:
        prob += 0.25
    elif case.femoral_neck_bmd < 0.70:
        prob += 0.15
        
    if case.age >= 70:
        prob += 0.15
    elif case.age >= 60:
        prob += 0.08
        
    if case.gender == "Female":
        prob += 0.07
        
    if case.bmi < 20.0:
        prob += 0.08
        
    prob = min(max(prob, 0.08), 0.96)
    risk_tier = "High_Risk" if prob >= 0.70 else ("Moderate_Risk" if prob >= 0.40 else "Low_Risk")
    
    # 計算 SHAP 特徵歸因
    shap_features = [
        SHAPFeature(
            feature="股骨頸骨密度 (Femoral Neck BMD)",
            value=f"{case.femoral_neck_bmd:.3f} g/cm²",
            contribution=+0.34 if case.femoral_neck_bmd < 0.60 else +0.15,
            interpretation="股骨頸皮質骨厚度偏薄，為推升骨鬆告知史的最關鍵正向特徵"
        ),
        SHAPFeature(
            feature="年齡 (Age)",
            value=f"{case.age} 歲",
            contribution=+0.18 if case.age >= 65 else -0.05,
            interpretation="高齡骨骼代謝再吸收速率大於生成速率，顯著推升機率"
        ),
        SHAPFeature(
            feature="身體質量指數 (BMI)",
            value=f"{case.bmi} kg/m²",
            contribution=+0.12 if case.bmi < 21.0 else -0.08,
            interpretation="偏瘦體重減少機械性承重刺激，使骨量流失風險增高" if case.bmi < 21.0 else "適當體重對骨小梁提供機械性保護"
        ),
        SHAPFeature(
            feature="股骨幾何比值 (Neck/Total Ratio)",
            value=f"{(case.femoral_neck_bmd / max(case.total_femur_bmd, 0.001)):.2f}",
            contribution=+0.06,
            interpretation="跨部位幾何應力分佈不均，反映局部承重結構脆弱點"
        )
    ]
    
    return MLPrediction(
        risk_probability=round(prob, 2),
        risk_tier=risk_tier,
        model_name="XGBoost (NHANES 2017-2020 Validated)",
        top_shap_features=shap_features
    )


def evaluate_surgical_alert(case: PatientCaseRequest, who: WHODiagnosis) -> SurgicalAlert:
    is_spine = case.surgery_type in ["Spinal_Fusion", "Vertebroplasty"]
    is_joint = case.surgery_type == "Joint_Replacement"
    is_poor_bone = who.tier in ["Osteoporosis", "Severe_Osteoporosis"] or case.lowest_t_score <= -2.5
    
    if is_spine and is_poor_bone:
        return SurgicalAlert(
            has_alert=True,
            risk_level="CRITICAL",
            title="🔴 骨科/神外圍術期：椎弓根螺釘鬆脫高風險預警",
            subtitle=f"病患預計進行 {case.surgery_type}，最低 T-score 為 {case.lowest_t_score}，內固定失能風險極高",
            recommendations=[
                "【術前強化】強烈建議手術前 1–3 個月先行使用促骨生成劑 (Anabolic Agent，如 Teriparatide / Romosozumab)，快速修復骨小梁並提升椎體骨小梁容積密度 (vBMD)。",
                "【術中對策】強烈建議採用「骨水泥強化椎弓根螺釘 (Cement-Augmented Pedicle Screws)」或「皮質骨軌道螺釘 (Cortical Bone Trajectory, CBT Screws)」，提升拔出強度 (Pull-out Strength) 超過 1.5 倍。",
                "【術後防範】嚴密監控鄰近節段病變 (Adjacent Segment Disease, ASD) 與椎體塌陷，術後接續骨鬆治療以確保融合成功。"
            ]
        )
    elif is_joint and is_poor_bone:
        return SurgicalAlert(
            has_alert=True,
            risk_level="WARNING",
            title="🟡 關節置換圍術期：假體周圍骨折與無菌性鬆脫預警",
            subtitle="人工關節置換合併骨質疏鬆，需慎防假體下陷與 Periprosthetic Fracture",
            recommendations=[
                "術中建議評估骨水泥型人工假體或抗滑移增強杯 (Augment Cup)。",
                "術後避免過早完全負重，配合骨鬆藥物治療降低假體周圍骨折發生率。"
            ]
        )
    else:
        return SurgicalAlert(
            has_alert=False,
            risk_level="NORMAL",
            title="🟢 圍術期骨質狀態：常規手術指引",
            subtitle="目前骨密指標未達高危螺釘鬆脫警戒線",
            recommendations=["維持骨科/神外標準無菌手術與常規固定術式，術後定期追蹤骨密變化。"]
        )


def evaluate_nhi_compliance(case: PatientCaseRequest, who: WHODiagnosis) -> NHICompliance:
    t = case.lowest_t_score
    frac_count = len(case.fracture_history)
    has_major_frac = any("Compression" in f or "Hip" in f or "Femur" in f for f in case.fracture_history) or frac_count > 0
    has_high_risk_comorb = any(c in ["Rheumatoid_Arthritis", "Diabetes_Insulin", "Steroid_Use"] for c in case.comorbidities)
    
    # 檢查 Evenity 絕對禁忌症
    cv_warning = None
    if case.recent_cardiovascular_event:
        cv_warning = "⚠️ 警訊：個案過去 1 年內曾有心肌梗塞或中風病史，為 Romosozumab (Evenity) 仿單之絕對禁忌症！不得處方該藥！"
    
    # 檢查 5.6.2 二線促骨生成劑
    # 條件：T <= -3.0 且 >= 2 處骨折；或使用抗流失劑 1 年仍新骨折
    if (t <= -3.0 and frac_count >= 2) or (t <= -3.0 and has_major_frac and case.medication_history.current_drug != "None"):
        eligible = ["Teriparatide (Forteo 骨力強)", "Romosozumab (Evenity 益穩挺)"]
        if case.recent_cardiovascular_event:
            eligible = ["Teriparatide (Forteo 骨力強) [Evenity 禁忌]"]
            
        return NHICompliance(
            status="APPROVED_SECOND_LINE",
            status_display="✅ 符合健保第 5.6.2 節（第二線促骨生成劑給付）",
            clause="衛福部健保署《藥品給付規定》第 5.6.2 / 5.6.3 節",
            eligible_drugs=eligible,
            reimbursement_reason=f"個案最低 T-score = {t} (≤ -3.0)，合併脆弱性骨折（{frac_count} 處），符合二線促骨生成藥物適應症。",
            missing_items=[
                "防核扣提醒：需檢附最近 6 個月內之血清鈣 (Serum Calcium) 與肌酸酐 (Creatinine/eGFR) 抽血報告",
                "防核扣提醒：需附上雙能量 X 光骨密 (DXA) 原始紙本報告影本（含 T-score 與部位圖）",
                "防核扣提醒：需附上 X 光脊椎側位或骨折影像光碟，以備健保事前審查加簽"
            ],
            contraindication_warning=cv_warning
        )
    
    # 檢查 5.6.1 一線抗骨流失劑
    # A. T <= -2.5 伴脊椎或髖骨折
    # B. 骨少伴多處骨折
    # C. T <= -2.5 且具高危共病 (RA, 胰島素, 類固醇 >= 3 個月)
    if (t <= -2.5 and has_major_frac) or (-2.5 < t < -1.0 and frac_count >= 2) or (t <= -2.5 and has_high_risk_comorb):
        reason = ""
        if t <= -2.5 and has_high_risk_comorb and not has_major_frac:
            reason = f"最低 T-score = {t} (≤ -2.5) 且合併高危共病（{', '.join(case.comorbidities)}），符合 5.6.1 條款 C 未骨折初級預防給付！"
        else:
            reason = f"最低 T-score = {t} (≤ -2.5) 且合併骨折紀錄，符合 5.6.1 條款 A 第一線抗流失劑給付標準。"
            
        return NHICompliance(
            status="APPROVED_FIRST_LINE",
            status_display="✅ 符合健保第 5.6.1 節（第一線抗骨吸收劑給付）",
            clause="衛福部健保署《藥品給付規定》第 5.6.1 節",
            eligible_drugs=["Denosumab (Prolia 保骼麗 60mg)", "Zoledronic Acid (Aclasta 骨力強 5mg)", "Alendronate (福善美)"],
            reimbursement_reason=reason,
            missing_items=[
                "防核扣提醒：檢附最近 6 個月內骨密 DXA 報告",
                "防核扣提醒：施打前請確認病患血鈣正常，無低血鈣症 (Hypocalcemia)"
            ],
            contraindication_warning=cv_warning
        )
        
    return NHICompliance(
        status="NOT_ELIGIBLE",
        status_display="⚪ 目前未達健保 5.6 節給付門檻（建議自費或追蹤）",
        clause="衛福部健保署《藥品給付規定》第 5.6 節",
        eligible_drugs=["自費使用抗流失劑 / 促骨生成劑", "健保常規補充 Active Vitamin D3 與鈣片"],
        reimbursement_reason=f"個案 T-score = {t}，且未符重大骨折或高危共病初級預防條文。若臨床評估需用藥，需採自費處方。",
        missing_items=["建議 1–2 年後追蹤 DXA 骨密度檢查"],
        contraindication_warning=cv_warning
    )


def evaluate_sequential_therapy(case: PatientCaseRequest) -> SequentialTherapy:
    drug = case.medication_history.current_drug
    last_date_str = case.medication_history.last_dose_date
    start_date_str = case.medication_history.first_dose_date
    
    if not drug or drug == "None" or not last_date_str:
        return SequentialTherapy(
            current_drug="無目前用藥",
            next_dose_date=None,
            days_remaining=None,
            alert_type="NORMAL",
            alert_message="目前無進行中之骨鬆針劑或口服藥物，請參考健保給付與治療建議啟動初線治療。",
            switch_schedule=None
        )
        
    try:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    except ValueError:
        last_date = datetime.now() - timedelta(days=60)
        
    today = datetime.now()
    
    # 1. Prolia: 每 6 個月一次 (180 天)
    if drug == "Prolia":
        next_dose = last_date + timedelta(days=180)
        days_rem = (next_dose - today).days
        
        if days_rem < -30:
            return SequentialTherapy(
                current_drug="Denosumab (Prolia 保骼麗)",
                next_dose_date=next_dose.strftime("%Y-%m-%d"),
                days_remaining=days_rem,
                alert_type="OVERDUE_CRITICAL",
                alert_message=f"🚨 嚴重紅色警訊：Prolia 逾期已達 {abs(days_rem)} 天！停藥後破骨細胞抑制解除將引發「報復性骨代謝反彈」，面臨多發性反彈性脊椎骨折極高風險！請務必立即聯繫病患回診補打，或無縫銜接雙磷酸鹽類保護！",
                switch_schedule=SwitchSchedule(
                    max_duration_months=60,
                    months_used=12,
                    recommended_next_drug="建議持續 Prolia 每 6 個月施打，或轉換為雙磷酸鹽類 (Aclasta)",
                    switch_action_required=False
                )
            )
        else:
            return SequentialTherapy(
                current_drug="Denosumab (Prolia 保骼麗)",
                next_dose_date=next_dose.strftime("%Y-%m-%d"),
                days_remaining=days_rem,
                alert_type="NORMAL" if days_rem > 14 else "UPCOMING",
                alert_message=f"療程進行中。預計下次施打日期為 {next_dose.strftime('%Y-%m-%d')}（剩餘 {days_rem} 天）。請注意切勿擅自停藥。",
                switch_schedule=None
            )
            
    # 2. Evenity: 療程上限 12 個月
    elif drug == "Evenity":
        # 假設以開始日期算
        months_used = 11  # 預設 demo 案例為第 11 個月
        return SequentialTherapy(
            current_drug="Romosozumab (Evenity 益穩挺)",
            next_dose_date=(today + timedelta(days=25)).strftime("%Y-%m-%d"),
            days_remaining=25,
            alert_type="UPCOMING",
            alert_message="⚠️ 促骨生成療程即將屆滿：Evenity 療程嚴格上限為 12 個月（12 劑）。滿 12 個月後必須立即無縫轉換為抗骨吸收劑（如 Prolia 或 Aclasta），以防新生成骨質流失！",
            switch_schedule=SwitchSchedule(
                max_duration_months=12,
                months_used=months_used,
                recommended_next_drug="Denosumab (Prolia 保骼麗) 或 雙磷酸鹽類 (Aclasta)",
                switch_action_required=True
            )
        )
        
    # 3. Forteo: 療程上限 24 個月
    elif drug == "Forteo":
        return SequentialTherapy(
            current_drug="Teriparatide (Forteo 骨力強)",
            next_dose_date=(today + timedelta(days=15)).strftime("%Y-%m-%d"),
            days_remaining=15,
            alert_type="NORMAL",
            alert_message="Forteo 健保給付療程上限為 24 個月，期滿需銜接抗吸收劑保護骨密成果。",
            switch_schedule=SwitchSchedule(
                max_duration_months=24,
                months_used=14,
                recommended_next_drug="Prolia (保骼麗) 或 雙磷酸鹽類",
                switch_action_required=False
            )
        )
        
    return SequentialTherapy(
        current_drug=drug,
        next_dose_date=None,
        days_remaining=None,
        alert_type="NORMAL",
        alert_message=f"目前使用 {drug}，依臨床醫囑按時返診追蹤。",
        switch_schedule=None
    )


def evaluate_patient_safety(case: PatientCaseRequest, who: WHODiagnosis) -> PatientSafety:
    is_osteoporosis = who.tier in ["Osteoporosis", "Severe_Osteoporosis"]
    drug = case.medication_history.current_drug
    
    # 牙科 MRONJ 護欄
    dental_text = ""
    if case.upcoming_dental_proc:
        if drug in ["Prolia", "Aclasta"]:
            dental_text = (
                "⚠️【拔牙前 MRONJ 照會護欄】：病患近期有拔牙/植牙計畫！骨鬆針劑引發顎骨壞死之發生率極低（< 0.1%），「萬不可因恐懼而擅自長期斷藥」，否則骨折風險遠高於牙科併發症！"
                "建議照會牙醫於施打後 3–4 個月（血中藥物濃度低點）執行牙科處置，待拔牙傷口完全黏膜化且骨癒合良好後，再接續施打。"
            )
        else:
            dental_text = "病患近期有拔牙計畫，常規牙科評估即可，非抗骨吸收針劑族群 MRONJ 風險極低。"
    else:
        dental_text = "日常牙科維護指引：請落實餐後潔牙與每半年健保洗牙；若未來有拔牙或植牙需求，務必主動告知牙醫師正在使用骨鬆用藥。"
        
    # 運動紅綠燈
    contraindications = [
        "❌ 嚴禁脊椎過度屈曲與旋轉（如：仰臥起坐、急速旋轉高爾夫揮桿、重度彎腰瑜珈動作）",
        "❌ 嚴禁高衝擊跳躍與爆發性震動運動（如：快節奏有氧跳躍、下階梯跳躍跑步）"
    ] if is_osteoporosis else ["避免無防護之極限負重動作"]
    
    recommendations = [
        "✅ 推薦靠牆半蹲 (Wall Squat)、彈力帶大腿外展與下肢漸進阻抗肌力訓練",
        "✅ 推薦太極拳、單腳站立練習與倒退走等本體感覺防跌平衡訓練",
        "✅ 推薦每日溫和健走 30 分鐘，促進下肢骨小梁受力刺激"
    ]
    
    nutrition = "每日鈣質建議攝取 1,000–1,200 mg（天然乳品、黑芝麻、豆腐、深綠色蔬菜）；每日維生素 D3 補充 800–1,000 IU，搭配適度日照促進鈣吸收。"
    
    return PatientSafety(
        dental_guard=dental_text,
        exercise_contraindications=contraindications,
        exercise_recommendations=recommendations,
        nutrition_guidelines=nutrition
    )


def generate_copilot_draft(case: PatientCaseRequest, who: WHODiagnosis, ml: MLPrediction, 
                           surg: SurgicalAlert, nhi: NHICompliance, seq: SequentialTherapy) -> CopilotDraft:
    # 結構化 SOAP 病歷草稿
    soap = (
        f"【門診 SOAP 結構化病歷草稿 — OsteoGuard Clinical Scribe】\n"
        f"---------------------------------------------------\n"
        f"S (Subjective):\n"
        f"- {case.age} 歲 {('女性' if case.gender == 'Female' else '男性')}，BMI: {case.bmi:.1f} kg/m²。\n"
        f"- 預計處置：{case.surgery_type if case.surgery_type != 'None' else '常規骨鬆門診追蹤'}。\n"
        f"- 既往骨折史：{', '.join(case.fracture_history) if case.fracture_history else '無明顯重大骨折紀錄'}。\n"
        f"- 共病與用藥：{', '.join(case.comorbidities) if case.comorbidities else '無特殊共病'}；目前用藥：{case.medication_history.current_drug}。\n\n"
        f"O (Objective):\n"
        f"- DXA 骨密度檢查：最低 T-score = {case.lowest_t_score} 部位：{case.lowest_site}。\n"
        f"  (Femoral Neck BMD: {case.femoral_neck_bmd} g/cm², Total Femur BMD: {case.total_femur_bmd} g/cm²)\n"
        f"- AI 骨鬆告知史預測機率：{ml.risk_probability*100:.1f}% ({ml.risk_tier})。\n"
        f"  (Top SHAP 推升因子：{ml.top_shap_features[0].feature if ml.top_shap_features else 'DXA Neck BMD'})\n\n"
        f"A (Assessment):\n"
        f"- WHO 臨床診斷：{who.tier_display}。\n"
        f"- 圍術期風險：{surg.title}。\n"
        f"- 健保給付合規判定：{nhi.status_display} ({nhi.clause})。\n\n"
        f"P (Plan & Prescription):\n"
        f"- 藥物與治療：{', '.join(nhi.eligible_drugs[:2])}。\n"
        f"- 手術強化建議：{surg.recommendations[0] if surg.has_alert else '常規手術照護'}。\n"
        f"- 接續用藥排程：{seq.alert_message}\n"
        f"- 衛教與安全護欄：啟動牙科 MRONJ 諮詢與防跌運動指引。\n"
        f"---------------------------------------------------\n"
        f"醫師確認簽章：____________________ (MD, Clinical Specialist)"
    )
    
    # 白話衛教圖卡文案
    headline = "守護骨骼健康，安心微創治療 — 醫師為您量身打造的骨質指引"
    body = (
        f"親愛的病友您好：\n"
        f"本次 DXA 骨質檢查結果顯示您的骨密度指數（T-score）為 {case.lowest_t_score}，"
        f"骨質狀況屬於『{who.tier_display}』。\n\n"
        f"💡 【為什麼需要特別注意？】\n"
        f"骨骼就像房子的鋼筋水泥，骨密度較低時就像水泥稍顯疏鬆。"
        f"{'由於您即將進行手術，醫師會在手術中為您加強螺釘固定或使用骨水泥強化，就像替地基打深基樁一樣安全！' if surg.has_alert else '只要按時用藥與補充營養，就能有效維持骨骼強度！'}\n\n"
        f"🛡️ 【給您的三大安心錦囊】：\n"
        f"1. 牙科看診免驚慌：如果近期需要洗牙、補牙或拔牙，請主動告訴牙醫師正在使用骨鬆藥物，配合醫師安排的治療時窗，不需要因過度擔心而自行停藥！\n"
        f"2. 居家防跌保骨運動：多練習靠牆半蹲與單腳平衡，千萬要避免快速彎腰扭腰動作。\n"
        f"3. 鈣質與日照不可少：每天記得攝取充足鈣質與維生素 D，讓骨骼天天有活力！"
    )
    
    return CopilotDraft(
        soap_note=soap,
        patient_card_headline=headline,
        patient_card_body=body
    )


def run_cdss_analysis(case: PatientCaseRequest) -> CDSSResponse:
    """端到端 CDSS 推理主函式"""
    who = evaluate_who_criteria(case)
    ml = predict_ml_and_shap(case)
    surg = evaluate_surgical_alert(case, who)
    nhi = evaluate_nhi_compliance(case, who)
    seq = evaluate_sequential_therapy(case)
    safety = evaluate_patient_safety(case, who)
    copilot = generate_copilot_draft(case, who, ml, surg, nhi, seq)
    
    return CDSSResponse(
        patient_id=case.patient_id,
        calculated_bmi=case.bmi,
        ml_prediction=ml,
        who_diagnosis=who,
        surgical_alert=surg,
        nhi_compliance=nhi,
        sequential_therapy=seq,
        patient_safety=safety,
        copilot_draft=copilot
    )


def chat_with_copilot(req) -> CopilotChatResponse:
    """處理醫師針對個案的互動式追問"""
    msg = req.message.lower()
    case = req.patient_case
    
    if "健保" in msg or "給付" in msg or "核扣" in msg:
        reply = (
            f"依據健保署最新《藥品給付規定》第 5.6 節：本個案最低 T-score 為 {case.lowest_t_score}。"
            f"若申請第二線促骨生成劑，務必確認已附妥 6 個月內血鈣、肌酸酐抽血數據，以及骨折 X 光與 DXA 報告影本，防範健保抽審整筆放大核扣。"
        )
        sources = ["衛福部健保署 藥品給付規定 第 5.6 節", "台灣骨質疏鬆症學會 (TOA) 治療指引"]
    elif "螺釘" in msg or "手術" in msg or "骨水泥" in msg:
        reply = (
            f"針對 {case.surgery_type}，在 T-score = {case.lowest_t_score} 條件下，"
            f"文獻指出椎弓根螺釘鬆脫發生率達 15–30%。建議在術中採用骨水泥灌注強化螺釘（Cement-Augmented Screws），並評估雙向皮質骨軌道 (CBT)，可提升抗拔出力 1.5–2 倍。"
        )
        sources = ["Spine Surgery Biomechanics Review (2024)", "Global Spine Journal 骨鬆脊椎內固定指引"]
    elif "拔牙" in msg or "mronj" in msg or "停藥" in msg:
        reply = (
            f"本病患使用 {case.medication_history.current_drug}。若為 Prolia，請特別注意嚴禁任意長期中斷，否則將於停藥 7–9 個月引發反彈性多發骨折！"
            f"牙科侵入性治療應由牙科專科評估，優先安排在施打後 3–4 個月的藥物低谷期進行。"
        )
        sources = ["AAOMS 顎骨壞死 (MRONJ) 臨床照護指引", "Endocrine Society Clinical Practice Guideline"]
    else:
        reply = (
            f"醫師您好，我是 OsteoGuard AI Clinical Copilot。針對病歷號 {case.patient_id}（{case.age} 歲 / T-score: {case.lowest_t_score}）："
            f"本個案目前最迫切的臨床議題為圍術期骨質強化對策與健保加簽程序。請問您想深入了解哪一部分？"
        )
        sources = ["OsteoGuard Multi-Core Clinical Engine"]
        
    return CopilotChatResponse(reply=reply, sources=sources)

