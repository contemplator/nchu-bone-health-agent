# OsteoGuard CDSS — VPS 雲端部署手冊 (Deployment Guide)

本手冊說明如何將 OsteoGuard AI Agent CDSS 部署至已安裝 Node.js 的 VPS 伺服器（如 Ubuntu / Debian）。

---

## 步驟 1：上傳專案程式碼至 VPS

```bash
# 登入 VPS 並建立專案目錄
ssh root@YOUR_VPS_IP
mkdir -p /var/www
cd /var/www

# 複製專案儲存庫
git clone https://github.com/YOUR_ORG/nchu-bone-health-agent.git
cd nchu-bone-health-agent
```

---

## 步驟 2：建立 Python 虛擬環境並安裝套件

```bash
# 安裝 Python venv (若系統尚未安裝)
sudo apt update && sudo apt install -y python3-venv python3-pip

# 建立虛擬環境
python3 -m venv venv

# 啟用並安裝套件
source venv/bin/activate
pip install -r requirements.txt
```

---

## 步驟 3：設定環境變數

```bash
cp .env.example .env
# 編輯 .env 填入您的 OpenAI / Gemini 金鑰 (若採 mock 離線展示則無需填寫)
nano .env
```

---

## 步驟 4：使用 PM2 啟動服務（推薦，適合已有 Node 的 VPS）

```bash
# 全域安裝 PM2 (若尚未安裝)
npm install -g pm2

# 依據 ecosystem.config.js 啟動服務
pm2 start ecosystem.config.js

# 設定開機自動重啟
pm2 save
pm2 startup
```

檢查服務運行狀態：
```bash
pm2 status
pm2 logs osteoguard-cdss
```

---

## 步驟 5：設定 Nginx 反向代理（選填）

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/osteoguard
sudo ln -s /etc/nginx/sites-available/osteoguard /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```
現在您可以直接在瀏覽器輸入您的 VPS IP 或網域名稱訪問系統！

