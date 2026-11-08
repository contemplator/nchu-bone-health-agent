"""
OsteoGuard AI Agent — API 與四大臨床案例自動化測試
"""
import pytest
from fastapi.testclient import TestClient
from app import app
from src.schemas import PatientCaseRequest

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "OsteoGuard AI Agent" in response.text


def test_case1_spinal_fusion_alert():
    """案例一：嚴重骨鬆 + 脊椎融合術 -> 應觸發螺釘鬆脫高危預警與骨水泥建議"""
    payload = {
        "patient_id": "PT-SPINE-2026",
        "age": 72,
        "gender": "Female",
        "height_cm": 152.0,
        "weight_kg": 46.0,
        "total_femur_bmd": 0.580,
        "total_femur_bmc": 19.5,
        "total_femur_area": 33.6,
        "femoral_neck_bmd": 0.470,
        "femoral_neck_bmc": 2.2,
        "femoral_neck_area": 4.8,
        "trochanter_bmd": 0.440,
        "intertrochanter_bmd": 0.650,
        "lowest_t_score": -3.4,
        "lowest_site": "Femoral Neck",
        "surgery_type": "Spinal_Fusion",
        "fracture_history": ["L2_Compression_Fracture", "Previous_T12_Fracture"],
        "comorbidities": ["Osteoarthritis"],
        "medication_history": {
            "current_drug": "None"
        },
        "upcoming_dental_proc": False,
        "recent_cardiovascular_event": False
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["surgical_alert"]["has_alert"] is True
    assert data["surgical_alert"]["risk_level"] == "CRITICAL"
    assert "椎弓根螺釘鬆脫" in data["surgical_alert"]["title"]
    assert data["who_diagnosis"]["tier"] == "Severe_Osteoporosis"
    assert "APPROVED_SECOND_LINE" in data["nhi_compliance"]["status"]


def test_case2_evenity_switch_schedule():
    """案例二：Evenity 滿 11 個月 -> 甘特圖提示換藥排程"""
    payload = {
        "patient_id": "PT-SWITCH-8821",
        "age": 68,
        "gender": "Male",
        "height_cm": 165.0,
        "weight_kg": 58.0,
        "total_femur_bmd": 0.630,
        "total_femur_bmc": 22.8,
        "total_femur_area": 36.2,
        "femoral_neck_bmd": 0.510,
        "femoral_neck_bmc": 2.7,
        "femoral_neck_area": 5.3,
        "trochanter_bmd": 0.480,
        "intertrochanter_bmd": 0.710,
        "lowest_t_score": -3.1,
        "lowest_site": "Femoral Neck",
        "surgery_type": "None",
        "fracture_history": ["T12_Compression_Fracture", "Distal_Radius_Fracture"],
        "comorbidities": [],
        "medication_history": {
            "current_drug": "Evenity",
            "last_dose_date": "2026-03-10"
        },
        "upcoming_dental_proc": False,
        "recent_cardiovascular_event": False
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sequential_therapy"]["switch_schedule"] is not None
    assert data["sequential_therapy"]["switch_schedule"]["switch_action_required"] is True


def test_case3_prolia_overdue_and_mronj():
    """案例三：Prolia 逾期 35 天 + 拔牙 -> 觸發反彈性骨折紅色警報與牙科 MRONJ 護欄"""
    payload = {
        "patient_id": "PT-DENTAL-5542",
        "age": 65,
        "gender": "Female",
        "height_cm": 158.0,
        "weight_kg": 50.0,
        "total_femur_bmd": 0.670,
        "total_femur_bmc": 23.5,
        "total_femur_area": 35.1,
        "femoral_neck_bmd": 0.540,
        "femoral_neck_bmc": 2.9,
        "femoral_neck_area": 5.4,
        "trochanter_bmd": 0.500,
        "intertrochanter_bmd": 0.740,
        "lowest_t_score": -2.8,
        "lowest_site": "Femoral Neck",
        "surgery_type": "None",
        "fracture_history": ["Wrist_Colles_Fracture"],
        "comorbidities": [],
        "medication_history": {
            "current_drug": "Prolia",
            "last_dose_date": "2025-08-15"
        },
        "upcoming_dental_proc": True,
        "recent_cardiovascular_event": False
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sequential_therapy"]["alert_type"] == "OVERDUE_CRITICAL"
    assert "反彈性脊椎骨折" in data["sequential_therapy"]["alert_message"]
    assert "MRONJ" in data["patient_safety"]["dental_guard"]


def test_case4_primary_prevention_clause_c():
    """案例四：未骨折 + RA + 類固醇 -> 健保 5.6.1 條款 C 初級預防通過"""
    payload = {
        "patient_id": "PT-PRIMARY-1092",
        "age": 58,
        "gender": "Female",
        "height_cm": 160.0,
        "weight_kg": 53.0,
        "total_femur_bmd": 0.690,
        "total_femur_bmc": 24.5,
        "total_femur_area": 35.5,
        "femoral_neck_bmd": 0.560,
        "femoral_neck_bmc": 3.0,
        "femoral_neck_area": 5.3,
        "trochanter_bmd": 0.520,
        "intertrochanter_bmd": 0.770,
        "lowest_t_score": -2.6,
        "lowest_site": "Femoral Neck",
        "surgery_type": "None",
        "fracture_history": [],
        "comorbidities": ["Rheumatoid_Arthritis", "Steroid_Use"],
        "medication_history": {
            "current_drug": "None"
        },
        "upcoming_dental_proc": False,
        "recent_cardiovascular_event": False
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nhi_compliance"]["status"] == "APPROVED_FIRST_LINE"
    assert "5.6.1 條款 C" in data["nhi_compliance"]["reimbursement_reason"]


def test_copilot_chat():
    payload = {
        "patient_case": {
            "patient_id": "PT-TEST-001",
            "age": 70,
            "gender": "Female",
            "height_cm": 155.0,
            "weight_kg": 48.0,
            "total_femur_bmd": 0.60,
            "total_femur_bmc": 20.0,
            "total_femur_area": 33.0,
            "femoral_neck_bmd": 0.50,
            "femoral_neck_bmc": 2.5,
            "femoral_neck_area": 5.0,
            "trochanter_bmd": 0.45,
            "intertrochanter_bmd": 0.68,
            "lowest_t_score": -3.2,
            "lowest_site": "Femoral Neck",
            "surgery_type": "Spinal_Fusion",
            "fracture_history": [],
            "comorbidities": []
        },
        "message": "請問這名病患預計做脊椎手術，螺釘鬆脫風險如何？需要使用骨水泥嗎？"
    }
    response = client.post("/api/copilot/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "骨水泥" in data["reply"]
    assert len(data["sources"]) > 0
