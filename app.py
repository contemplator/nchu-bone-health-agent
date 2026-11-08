"""
OsteoGuard AI Agent — 臨床決策支援系統 (CDSS) FastAPI 主應用程式
專為骨科與神經外科醫師設計之端到端骨鬆智慧代理人
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.schemas import PatientCaseRequest, CDSSResponse, CopilotChatRequest, CopilotChatResponse
from src.mock_service import run_cdss_analysis, chat_with_copilot

# 載入環境變數
load_dotenv()

app = FastAPI(
    title="OsteoGuard AI Agent CDSS",
    description="骨科與神經外科骨鬆個案管理智慧代理人 (Clinical Decision Support System)",
    version="1.0.0"
)

# 允許跨域請求（便於本地開發與多端口通訊）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態檔案與模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ==============================================================================
# 頁面與 API 路由 (Routes)
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """渲染 OsteoGuard 現代醫療 CDSS 儀表板首頁"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": "OsteoGuard AI Agent"}
    )


@app.get("/api/health")
async def health_check():
    """服務健康檢查"""
    return {
        "status": "healthy",
        "service": "OsteoGuard CDSS Engine",
        "llm_provider": os.getenv("LLM_PROVIDER", "mock"),
        "version": "1.0.0"
    }


@app.post("/api/analyze", response_model=CDSSResponse)
async def analyze_patient_case(case: PatientCaseRequest):
    """
    接收個案臨床與 DXA 數據，執行端到端 CDSS 推理：
    1. WHO 骨密判讀與最低部位原則
    2. ML 骨鬆告知史機率與 SHAP 特徵歸因
    3. 骨科/神外圍術期螺釘鬆脫高危預警 (骨水泥與螺釘強化對策)
    4. 台灣健保第 5.6 節合規審核 (防核扣缺件檢核)
    5. 接續換藥時程推算與甘特排程 (Prolia 逾期反彈警訊)
    6. 牙科拔牙 MRONJ 護欄、分級運動與 SOAP 病歷草稿
    """
    try:
        # 當前串接標準推理服務 (Module 1 與 Module 2 完成後可無縫對接底層真實模型)
        result = run_cdss_analysis(case)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CDSS 分析處理失敗：{str(e)}")


@app.post("/api/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat(req: CopilotChatRequest):
    """
    支援臨床醫師針對個案進行多輪追問與互動式法規/手術對策諮詢
    """
    try:
        response = chat_with_copilot(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot 追問處理失敗：{str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"🚀 啟動 OsteoGuard CDSS 醫療儀表板：http://localhost:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
