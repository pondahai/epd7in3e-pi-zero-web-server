# Waveshare 7.3inch e-Paper (E) Web Server

這是一個專為 **Raspberry Pi Zero** 開發的專案。透過 Flask 建立網頁伺服器，讓使用者能夠透過手機或電腦的瀏覽器上傳任意全彩圖片，並利用 **Floyd-Steinberg 抖動演算法 (Dithering)** 完美轉換並推送到支援 7 色顯示的 Waveshare 7.3 吋電子紙 (e-Paper) 上。

## 🌟 功能說明

*   **網頁介面上傳**：跨平台支援，無需透過指令，手機、電腦瀏覽器即可操作。
*   **影像即時預覽**：上傳後立即顯示色彩降維處理後的 7 色預覽圖。
*   **智慧影像處理**：
    *   針對超大圖片自動縮放節省記憶體。
    *   自動增強飽和度、對比度與銳利度，讓電子紙顯示效果更鮮豔。
    *   實作 Floyd-Steinberg 抖動演算法，將全彩平滑過渡至 7 色（黑、白、黃、紅、橘、藍、綠）。
*   **低資源消耗**：針對運算能力較弱的 Raspberry Pi Zero (ARMv6) 進行最佳化。

---

## 🚀 第一次安裝指南

### 1. 系統環境準備
首先，需透過 `raspi-config` 啟用 Raspberry Pi 的 SPI 介面：
```bash
sudo raspi-config nonint do_spi 0
```

### 2. 安裝 Python 依賴
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy python3-gpiozero
sudo pip3 install Flask Pillow spidev --break-system-packages
```

### 3. 安裝底層 C 語言函式庫
電子紙驅動需要以下三個硬體控制函式庫才能穩定運作。

**A. BCM2835**
```bash
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
cd ..
```

**B. WiringPi**
```bash
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
cd ..
```

**C. lg Library (新版 Raspberry Pi OS 必備)**
```bash
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
make && sudo make install
cd ..
```

### 4. 下載本專案與官方驅動
將本專案 clone 到你的樹莓派中，並在專案目錄下下載 Waveshare 官方提供的 e-Paper 驅動函式庫：
```bash
git clone <你的_GITHUB_REPO_URL> waveshare_epaper
cd waveshare_epaper

# 下載 Waveshare 官方驅動
git clone https://github.com/waveshare/e-Paper.git
```
*(注意：若正確設定 `.gitignore`，`e-Paper` 等大型依賴將不會隨專案上傳，需使用者自行 clone)*

---

## 💻 使用方法

### 1. 啟動伺服器
進入網頁伺服器目錄並啟動 Flask 應用程式：
```bash
cd ~/waveshare_epaper/web_server
python3 app.py
```
> 若要讓其在背景持續運行，可以使用 `nohup python3 app.py &`。

### 2. 存取網頁介面
1. 確認手機或電腦與樹莓派連接在 **同一個區域網路 (Wi-Fi)**。
2. 打開瀏覽器，輸入樹莓派的 IP 位址及 Port 5000，例如：
   `http://192.168.0.x:5000`

### 3. 上傳與推送
1. 在網頁中點擊「選擇檔案」上傳照片，接著點擊「開始轉換圖片」。
2. 系統會自動進行影像處理並顯示 **轉換預覽圖**。
3. 確認效果滿意後，點擊「推送至電子紙螢幕」。
4. 電子紙將會閃爍約 15 秒進行更新，完成後即可欣賞完美顯示的作品！

---
*詳細的開發筆記與 Gemini CLI 安裝紀錄，請參考 `PI_ZERO_EPAPER_GUIDE.md` 與 `EPD_SETUP_NOTES.md`*