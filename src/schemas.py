"""
OsteoGuard AI Agent — Pydantic 資料契約與型別定義 (Schemas)
嚴格對齊 plan/README.md 之系統標準規範
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# 輸入物件 (Request Models)
# ==============================================================================

class MedicationHistory(BaseModel):
    current_drug: str = Field("None", description="目前用藥：None | Prolia | Evenity | Forteo | Aclasta")
    first_dose_date: Optional[str] = Field(None, description="首次施打日期 (YYYY-MM-DD)")
    last_dose_date: Optional[str] = Field(None, description="最近施打日期 (YYYY-MM-DD)")


class PatientCaseRequest(BaseModel):
    patient_id: str = Field("PT-2026-DEMO", description="病患編號/病歷號")
    age: int = Field(68, ge=18, le=120, description="年齡")
    gender: str = Field("Female", description="性別：Female | Male")
    height_cm: float = Field(156.0, ge=100.0, le=220.0, description="身高 (cm)")
    weight_kg: float = Field(48.5, ge=30.0, le=200.0, description="體重 (kg)")
    
    # 近端股骨 DXA 數值
    total_femur_bmd: float = Field(0.650, description="全髖部 BMD (g/cm^2)")
    total_femur_bmc: float = Field(22.1, description="全髖部 BMC (g)")
    total_femur_area: float = Field(34.0, description="全髖部 Area (cm^2)")
    femoral_neck_bmd: float = Field(0.520, description="股骨頸 BMD (g/cm^2)")
    femoral_neck_bmc: float = Field(2.8, description="股骨頸 BMC (g)")
    femoral_neck_area: float = Field(5.4, description="股骨頸 Area (cm^2)")
    trochanter_bmd: float = Field(0.490, description="大轉子 BMD (g/cm^2)")
    intertrochanter_bmd: float = Field(0.720, description="轉子間 BMD (g/cm^2)")
    
    # 臨床判讀與病史
    lowest_t_score: float = Field(-3.2, description="各部位最低 T-score")
    lowest_site: str = Field("Femoral Neck", description="最低 T-score 部位：Femoral Neck | Total Femur | Lumbar Spine")
    surgery_type: str = Field("Spinal_Fusion", description="預計手術：None | Spinal_Fusion | Vertebroplasty | Joint_Replacement")
    fracture_history: List[str] = Field(default_factory=list, description="骨折史清單，例如：['L1_Compression_Fracture']")
    comorbidities: List[str] = Field(default_factory=list, description="高危共病清單，例如：['Rheumatoid_Arthritis', 'Diabetes_Insulin', 'Steroid_Use']")
    
    # 用藥與臨床安全警示
    medication_history: MedicationHistory = Field(default_factory=MedicationHistory)
    upcoming_dental_proc: bool = Field(False, description="近期 3 個月內是否有拔牙或植牙計畫")
    recent_cardiovascular_event: bool = Field(False, description="過去 1 年內是否有心肌梗塞或腦中風 (Evenity 絕對禁忌症)")

    @property
    def bmi(self) -> float:
        h_m = self.height_cm / 100.0
        return round(self.weight_kg / (h_m * h_m), 1) if h_m > 0 else 0.0


# ==============================================================================
# 輸出物件 (Response Models)
# ==============================================================================

class SHAPFeature(BaseModel):
    feature: str = Field(..., description="特徵名稱")
    value: str = Field(..., description="數值或說明")
    contribution: float = Field(..., description="SHAP 貢獻值 (正值推升風險，負值降低風險)")
    interpretation: str = Field(..., description="臨床白話解釋")


class MLPrediction(BaseModel):
    risk_probability: float = Field(..., description="AI 預測骨鬆告知史機率 (0.0 ~ 1.0)")
    risk_tier: str = Field(..., description="風險等級：Low_Risk | Moderate_Risk | High_Risk")
    model_name: str = Field("XGBoost (NHANES 2017-2020 Validated)", description="使用之預測模型")
    top_shap_features: List[SHAPFeature] = Field(default_factory=list, description="前三大風險因子與保護因子")


class WHODiagnosis(BaseModel):
    tier: str = Field(..., description="WHO 診斷分級：Normal | Osteopenia | Osteoporosis | Severe_Osteoporosis")
    tier_display: str = Field(..., description="中文分級顯示名稱")
    lowest_t_score: float = Field(..., description="最低 T-score")
    site: str = Field(..., description="最低部位名稱")
    summary: str = Field(..., description="臨床診斷摘要")


class SurgicalAlert(BaseModel):
    has_alert: bool = Field(False, description="是否觸發圍術期手術警報")
    risk_level: str = Field("NORMAL", description="警報層級：NORMAL | WARNING | CRITICAL")
    title: str = Field("", description="警報標題")
    subtitle: str = Field("", description="警報副標題")
    recommendations: List[str] = Field(default_factory=list, description="圍術期骨水泥與螺釘強化對策")


class NHICompliance(BaseModel):
    status: str = Field(..., description="給付審核結論：APPROVED_FIRST_LINE | APPROVED_SECOND_LINE | NOT_ELIGIBLE")
    status_display: str = Field(..., description="中文狀態顯示")
    clause: str = Field(..., description="健保給付規定條號，如 5.6.1 或 5.6.2")
    eligible_drugs: List[str] = Field(default_factory=list, description="符合給付之藥品建議清單")
    reimbursement_reason: str = Field(..., description="健保核准或不符條款依據")
    missing_items: List[str] = Field(default_factory=list, description="防核扣抽血與報告缺件清單")
    contraindication_warning: Optional[str] = Field(None, description="禁忌症警告（如 Evenity 一年內心血管事件）")


class SwitchSchedule(BaseModel):
    max_duration_months: int = Field(..., description="目前藥物健保/法規療程上限月數")
    months_used: int = Field(..., description="已施打/使用月數")
    recommended_next_drug: str = Field(..., description="期滿強制轉換之接續藥物")
    switch_action_required: bool = Field(False, description="是否已屆期滿需立即換藥")


class SequentialTherapy(BaseModel):
    current_drug: str = Field(..., description="目前用藥")
    next_dose_date: Optional[str] = Field(None, description="預計下次施打日期")
    days_remaining: Optional[int] = Field(None, description="距離下次施打剩餘天數 (負值為逾期)")
    alert_type: str = Field("NORMAL", description="狀態：NORMAL | UPCOMING | OVERDUE_CRITICAL")
    alert_message: str = Field("", description="狀態說明或反彈性骨折危急警報")
    switch_schedule: Optional[SwitchSchedule] = Field(None, description="接續換藥甘特時程")


class PatientSafety(BaseModel):
    dental_guard: str = Field(..., description="拔牙與植牙 MRONJ 安全照會建議")
    exercise_contraindications: List[str] = Field(default_factory=list, description="紅燈禁忌運動")
    exercise_recommendations: List[str] = Field(default_factory=list, description="綠燈推薦防跌運動")
    nutrition_guidelines: str = Field(..., description="每日鈣質與維生素 D 基礎代謝指引")


class CopilotDraft(BaseModel):
    soap_note: str = Field(..., description="門診 SOAP 結構化病歷草稿")
    patient_card_headline: str = Field(..., description="病患白話衛教圖卡大標題")
    patient_card_body: str = Field(..., description="病患衛教溝通重點（無醫學晦澀術語）")


class CDSSResponse(BaseModel):
    patient_id: str
    calculated_bmi: float
    ml_prediction: MLPrediction
    who_diagnosis: WHODiagnosis
    surgical_alert: SurgicalAlert
    nhi_compliance: NHICompliance
    sequential_therapy: SequentialTherapy
    patient_safety: PatientSafety
    copilot_draft: CopilotDraft


# ==============================================================================
# 對話互動物件 (Chat Models)
# ==============================================================================

class CopilotChatRequest(BaseModel):
    patient_case: PatientCaseRequest
    message: str = Field(..., description="醫師提問內容")


class CopilotChatResponse(BaseModel):
    reply: str = Field(..., description="AI Copilot 回覆內容")
    sources: List[str] = Field(default_factory=list, description="參考法規或指引來源依據")

