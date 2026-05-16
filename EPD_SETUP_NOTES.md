# Waveshare 7.3inch e-Paper HAT (E) 安裝與測試筆記

## 1. 環境準備
在 Raspberry Pi 上執行以下步驟以準備執行環境：

### 啟用 SPI 介面
使用 `raspi-config` 非互動式命令啟用 SPI：
```bash
sudo raspi-config nonint do_spi 0
```

### 安裝 Python 依賴
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-numpy python3-gpiozero
sudo pip3 install spidev
```

### 安裝 C 語言相關函式庫
- **BCM2835**: 底層硬體控制
- **WiringPi**: GPIO 控制
- **lg**: 新版系統建議的 GPIO 函式庫

---

## 2. 下載範例程式
從 Waveshare 官方 GitHub 下載完整範例：
```bash
git clone https://github.com/waveshare/e-Paper.git
```

---

## 3. 測試執行紀錄 (Python)
執行命令：
```bash
cd ~/waveshare_epaper/e-Paper/RaspberryPi_JetsonNano/python/examples/
python3 epd_7in3e_test.py
```

### 執行輸出日誌：
```text
INFO:root:epd7in3e Demo
INFO:root:init and Clear
DEBUG:waveshare_epd.epd7in3e:e-Paper busy H
DEBUG:waveshare_epd.epd7in3e:e-Paper busy H release
...
INFO:root:1.Drawing on the image...
INFO:root:2.read bmp file
INFO:root:Clear...
INFO:root:Goto Sleep...
DEBUG:waveshare_epd.epdconfig:spi end
DEBUG:waveshare_epd.epdconfig:close 5V, Module enters 0 power consumption ...
```

---

## 4. 檔案目錄結構
- `~/waveshare_epaper/` : 根目錄
  - `e-Paper/` : 官方範例程式碼
  - `bcm2835-1.71/` : BCM2835 原始碼
  - `WiringPi/` : WiringPi 原始碼
  - `lg-master/` : lg 函式庫原始碼

---
## 5. 測試結果驗證
- **硬體測試**: 成功。
- **螢幕反應**: 螢幕已成功初始化、清除、顯示範例圖片並進入睡眠模式。
- **狀態**: 已確認環境與驅動程式運作正常。

---
*筆記建立日期: 2024-05-15*
