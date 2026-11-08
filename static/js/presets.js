/**
 * OsteoGuard AI Agent — 4 組經典臨床示範案例 (Presets)
 * 供組員本地開發除錯、評審展示與一鍵快速載入使用
 */

const CLINICAL_PRESETS = {
    case1: {
        id: "case1",
        label: "案例一：嚴重骨鬆 + 脊椎融合術",
        badge: "圍術期高危螺釘警訊",
        badgeColor: "bg-red-500",
        description: "72歲女性，股骨頸 T=-3.4，預計進行脊椎融合手術，有兩處脊椎壓迫性骨折史。展示高危螺釘鬆脫警報、骨水泥螺釘對策與健保二線促骨生成審查。",
        data: {
            patient_id: "PT-SPINE-2026",
            age: 72,
            gender: "Female",
            height_cm: 152.0,
            weight_kg: 46.0,
            total_femur_bmd: 0.580,
            total_femur_bmc: 19.5,
            total_femur_area: 33.6,
            femoral_neck_bmd: 0.470,
            femoral_neck_bmc: 2.2,
            femoral_neck_area: 4.8,
            trochanter_bmd: 0.440,
            intertrochanter_bmd: 0.650,
            lowest_t_score: -3.4,
            lowest_site: "Femoral Neck",
            surgery_type: "Spinal_Fusion",
            fracture_history: ["L2_Compression_Fracture", "Previous_T12_Fracture"],
            comorbidities: ["Osteoarthritis"],
            medication_history: {
                current_drug: "None",
                first_dose_date: "",
                last_dose_date: ""
            },
            upcoming_dental_proc: false,
            recent_cardiovascular_event: false
        }
    },

    case2: {
        id: "case2",
        label: "案例二：促骨生成屆期換藥",
        badge: "Evenity 12個月強制限換",
        badgeColor: "bg-amber-500",
        description: "68歲男性，股骨頸 T=-3.1，使用 Evenity 治療已滿 11 個月。展示促骨生成劑屆期滿甘特圖、自動計算剩餘天數與無縫銜接抗吸收劑排程。",
        data: {
            patient_id: "PT-SWITCH-8821",
            age: 68,
            gender: "Male",
            height_cm: 165.0,
            weight_kg: 58.0,
            total_femur_bmd: 0.630,
            total_femur_bmc: 22.8,
            total_femur_area: 36.2,
            femoral_neck_bmd: 0.510,
            femoral_neck_bmc: 2.7,
            femoral_neck_area: 5.3,
            trochanter_bmd: 0.480,
            intertrochanter_bmd: 0.710,
            lowest_t_score: -3.1,
            lowest_site: "Femoral Neck",
            surgery_type: "None",
            fracture_history: ["T12_Compression_Fracture", "Distal_Radius_Fracture"],
            comorbidities: ["Hypertension"],
            medication_history: {
                current_drug: "Evenity",
                first_dose_date: "2025-04-10",
                last_dose_date: "2026-03-10"
            },
            upcoming_dental_proc: false,
            recent_cardiovascular_event: false
        }
    },

    case3: {
        id: "case3",
        label: "案例三：拔牙恐慌停藥逾期",
        badge: "Prolia 逾期反彈 + MRONJ 護欄",
        badgeColor: "bg-purple-600",
        description: "65歲女性，使用 Prolia，因害怕拔牙下巴壞死擅自停藥已逾期 35 天。展示 Prolia 逾期報復性反彈骨折警報、牙科 MRONJ 照會溝通與安撫指引。",
        data: {
            patient_id: "PT-DENTAL-5542",
            age: 65,
            gender: "Female",
            height_cm: 158.0,
            weight_kg: 50.0,
            total_femur_bmd: 0.670,
            total_femur_bmc: 23.5,
            total_femur_area: 35.1,
            femoral_neck_bmd: 0.540,
            femoral_neck_bmc: 2.9,
            femoral_neck_area: 5.4,
            trochanter_bmd: 0.500,
            intertrochanter_bmd: 0.740,
            lowest_t_score: -2.8,
            lowest_site: "Femoral Neck",
            surgery_type: "None",
            fracture_history: ["Wrist_Colles_Fracture"],
            comorbidities: [],
            medication_history: {
                current_drug: "Prolia",
                first_dose_date: "2025-01-15",
                last_dose_date: "2025-08-15"
            },
            upcoming_dental_proc: true,
            recent_cardiovascular_event: false
        }
    },

    case4: {
        id: "case4",
        label: "案例四：未骨折高危初級預防",
        badge: "健保 5.6.1 條款 C 初級預防",
        badgeColor: "bg-teal-600",
        description: "58歲女性，股骨頸 T=-2.6，無骨折病史，但罹患類風濕性關節炎 (RA) 且長期使用類固醇。展示健保 5.6.1 條款 C 針對高危共病未骨折個案之初級預防核准判定。",
        data: {
            patient_id: "PT-PRIMARY-1092",
            age: 58,
            gender: "Female",
            height_cm: 160.0,
            weight_kg: 53.0,
            total_femur_bmd: 0.690,
            total_femur_bmc: 24.5,
            total_femur_area: 35.5,
            femoral_neck_bmd: 0.560,
            femoral_neck_bmc: 3.0,
            femoral_neck_area: 5.3,
            trochanter_bmd: 0.520,
            intertrochanter_bmd: 0.770,
            lowest_t_score: -2.6,
            lowest_site: "Femoral Neck",
            surgery_type: "None",
            fracture_history: [],
            comorbidities: ["Rheumatoid_Arthritis", "Steroid_Use"],
            medication_history: {
                current_drug: "None",
                first_dose_date: "",
                last_dose_date: ""
            },
            upcoming_dental_proc: false,
            recent_cardiovascular_event: false
        }
    }
};

window.CLINICAL_PRESETS = CLINICAL_PRESETS;
