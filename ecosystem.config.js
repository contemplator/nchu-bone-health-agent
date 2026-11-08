// ==============================================================================
// OsteoGuard AI Agent — PM2 雲端程序管理設定檔 (ecosystem.config.js)
// 適用於已有 Node.js / PM2 環境之 VPS 伺服器
// ==============================================================================

module.exports = {
  apps: [
    {
      name: "osteoguard-cdss",
      script: "./venv/bin/uvicorn",
      args: "app:app --host 0.0.0.0 --port 8000 --workers 2",
      cwd: "/var/www/nchu-bone-health-agent", // 請替換為您在 VPS 上的實際部署路徑
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PORT: 8000,
        HOST: "0.0.0.0",
        LLM_PROVIDER: "mock", // 或切換為 "openai" / "gemini"
        PYTHONPATH: "."
      }
    }
  ]
};

