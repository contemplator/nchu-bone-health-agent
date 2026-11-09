#!/usr/bin/env bash
# ==============================================================================
# OsteoGuard AI Agent — VPS 首次初始化設置腳本 (setup_vps.sh)
# 在 VPS 上執行此腳本，可一鍵準備 Python 虛擬環境、專案目錄與 PM2 程序管理
# ==============================================================================

set -e

echo "🏥 [OsteoGuard CDSS] 開始 VPS 首次環境初始化..."

# 1. 檢查並安裝 Python 基礎編譯與虛擬環境工具
echo "📦 檢查系統套件 (Python3, venv, pip, git)..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

# 2. 檢查 Node.js 與 PM2
if ! command -v pm2 &> /dev/null; then
    echo "⚙️ 未檢測到 PM2，正在透過 npm 全域安裝 PM2..."
    sudo npm install -g pm2
else
    echo "✅ PM2 已就緒：$(pm2 -v)"
fi

# 3. 建立虛擬環境並安裝相依套件
if [ ! -d "venv" ]; then
    echo "🐍 建立專案 Python 虛擬環境 (./venv)..."
    python3 -m venv venv
fi

echo "📥 安裝專案相依套件 (requirements.txt)..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 準備 .env 環境變數檔
if [ ! -f ".env" ]; then
    echo "📄 建立預設 .env 設定檔 (預設 LLM_PROVIDER=mock)..."
    cp .env.example .env
fi

# 5. 首次透過 PM2 啟動服務
echo "🚀 透過 PM2 啟動 OsteoGuard CDSS 服務..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup || true

echo ""
echo "🎉 初始化完成！OsteoGuard AI Agent 已成功常駐於您的 VPS！"
echo "👉 檢查狀態：pm2 status"
echo "👉 查看日誌：pm2 logs osteoguard-cdss"

