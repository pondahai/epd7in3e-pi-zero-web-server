# 樹莓派 Zero 終極開發指南：Gemini CLI 助理 × 7.3 吋多色電子紙網頁伺服器

這是一份從零開始的完整實戰筆記。涵蓋了如何在資源受限的 **Raspberry Pi Zero (ARMv6)** 上安裝 Google Gemini CLI 打造 AI 開發環境，接著一步步設定 **Waveshare 7.3inch e-Paper HAT (E)** 電子紙驅動，最後部署一套支援 **Floyd-Steinberg 抖動演算法** 的 Flask 網頁伺服器，讓您能透過手機上傳任意全彩圖片，並完美模擬顯示在 7 色電子紙上。

---

## 🟡 第一階段：樹莓派 Zero (ARMv6) 安裝 Gemini CLI 完整筆記

### 📌 核心挑戰與解決方案總結
1. **權限問題 (`EACCES`)：** 改用 NVM (Node Version Manager) 將 Node.js 裝在使用者的家目錄，從此不需要 `sudo`。
2. **架構不支援 (ARMv6)：** 官方已不提供 ARMv6 的二進位檔。我們需指定「非官方鏡像站 (Unofficial Builds)」下載社群編譯好的版本，避免 Pi Zero 進入遙不可及的原始碼編譯。
3. **版本要求 (`EBADENGINE`)：** `@google/gemini-cli` 底層套件依賴 Node 20 以上的新語法，必須直接安裝 **v20** 版本。

### 🛠️ 完整安裝步驟

#### Step 1: 安裝 NVM (Node Version Manager)
下載並安裝 NVM 來接管 Node.js 版本控制：
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```
更新終端機環境變數（讓 `nvm` 指令立即生效）：
```bash
source ~/.bashrc
```

#### Step 2: 透過非官方鏡像站安裝 Node.js v20
為了避免抓不到官方檔案而卡死在原始碼編譯，必須在指令前方加上 `NVM_NODEJS_ORG_MIRROR` 環境變數，強迫 NVM 去社群維護的站點抓取已編譯好的 ARMv6 版本：
```bash
nvm cache clear
NVM_NODEJS_ORG_MIRROR=https://unofficial-builds.nodejs.org/download/release nvm install v20
```

#### Step 3: 確認安裝與版本
確保 Node.js 已經順利裝上，且版本在 v20 或以上：
```bash
node -v
npm -v
```

#### Step 4: 安裝 Google Gemini CLI
使用 `npm` 全域安裝，記得加上 `@google/` 前綴：
```bash
npm install -g @google/gemini-cli
```
*⚠️ **Pi Zero 專屬提醒**：Pi Zero 單核心運算較慢，這個步驟會停滯在解壓縮與寫入狀態達 3 到 5 分鐘，請耐心等待，**絕對不要按下 `Ctrl+C` 中斷**。*

#### Step 5: 啟動 Gemini
```bash
gemini
```

---

## 🔵 第二階段：7.3inch e-Paper (E) 環境準備與驅動安裝

有了 Gemini CLI 作為助手，接下來準備電子紙的執行環境。

### Step 1: 建立專案目錄與啟用 SPI
```bash
mkdir -p ~/waveshare_epaper
cd ~/waveshare_epaper

# 非互動式啟用 Raspberry Pi 的 SPI 介面
sudo raspi-config nonint do_spi 0
```

### Step 2: 安裝 Python 依賴與相關套件
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-numpy python3-gpiozero
sudo pip3 install spidev --break-system-packages
```

### Step 3: 安裝底層 C 語言函式庫
電子紙驅動需要以下三個函式庫才能穩定運作：

**1. BCM2835**
```bash
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
cd ..
```

**2. WiringPi**
```bash
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
cd ..
```

**3. lg Library (新版 Raspberry Pi OS 必須)**
```bash
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
make && sudo make install
cd ..
```

### Step 4: 下載 Waveshare 官方驅動
```bash
git clone https://github.com/waveshare/e-Paper.git
```

---

## 🟢 第三階段：部署影像轉換網頁伺服器

為了將任意全彩圖片顯示在只支援 7 色（黑、白、黃、紅、藍、綠、橘/黑）的電子紙上，我們建立一個基於 Flask 的網頁伺服器，並使用 **Floyd-Steinberg 抖動演算法 (Dithering)** 進行色彩降維與誤差擴散。

### Step 1: 安裝 Web 伺服器依賴
```bash
pip3 install flask pillow --break-system-packages
```

### Step 2: 建立專案結構
```bash
mkdir -p ~/waveshare_epaper/web_server/static/uploads
mkdir -p ~/waveshare_epaper/web_server/templates
```

### Step 3: 伺服器程式碼架構
在 `~/waveshare_epaper/web_server/` 中，我們建立了兩個核心 Python 檔案：
1. **`converter.py`**：負責使用 PIL (`Pillow`) 定義 7 色調色盤，並將圖片 Resize 到 800x480 後套用 Floyd-Steinberg 抖動演算法。
2. **`app.py`**：Flask 後端，提供圖片上傳介面 (`index.html`)、預覽介面 (`preview.html`)，並在使用者確認後，呼叫 `waveshare_epd` 驅動將轉換後的圖片寫入 SPI 更新螢幕。
   *(註：啟動 Flask 時需關閉 Debug 模式 `debug=False`，並將硬體初始化延遲到推送當下，以避免 GPIO 腳位被佔用引發 `GPIO busy` 錯誤。)*

### Step 4: 啟動伺服器
進入網頁目錄並執行：
```bash
cd ~/waveshare_epaper/web_server
python3 app.py
```
> *若要讓其在背景持續運行，可以使用 `nohup python3 app.py &` 或透過 `systemd` 設定為開機自動啟動。*

### Step 5: 實際操作
1. 打開手機或電腦的瀏覽器。
2. 確保設備與樹莓派在同一區域網路內。
3. 輸入網址：`http://<樹莓派的IP位址>:5000` (例如：`http://192.168.0.23:5000`)。
4. 點擊上傳圖片，預覽 Dithering 效果，確認後點擊「推送至電子紙」。
5. 欣賞電子紙上展現出驚豔的仿全彩視覺效果！

---
*文件編寫：Gemini CLI & User 共同完成*