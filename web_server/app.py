import os
import sys
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from converter import process_image
from PIL import Image

# Setup path for waveshare_epd
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd7in3e

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialize EPD (lazily)
epd = None

def get_epd():
    global epd
    if epd is None:
        epd = epd7in3e.EPD()
    return epd

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("--- 收到上傳請求 ---")
    if 'file' not in request.files:
        print("錯誤: Request 中沒有 file 欄位")
        return jsonify({"error": "沒有選擇檔案"}), 400
    file = request.files['file']
    if file.filename == '':
        print("錯誤: 檔名為空")
        return jsonify({"error": "檔名為空"}), 400
    
    try:
        print(f"收到檔案: {file.filename}")
        # 使用 UUID 產生唯一檔名
        ext = os.path.splitext(file.filename)[1].lower()
        if not ext:
            ext = '.jpg'
        
        unique_id = str(uuid.uuid4())
        filename = unique_id + ext
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"正在儲存檔案至: {filepath}")
        file.save(filepath)
        
        print("開始影像轉換處理 (Converter)...")
        # 預覽圖統一使用 .jpg 格式
        preview_filename = 'preview_' + unique_id + '.jpg'
        preview_path = os.path.join(app.config['UPLOAD_FOLDER'], preview_filename)
        
        process_image(filepath, preview_path)
        print(f"轉換完成: {preview_filename}")
        
        return jsonify({
            "original": filename,
            "preview": preview_filename,
            "preview_url": url_for('uploaded_file', filename=preview_filename)
        })
    except Exception as e:
        print(f"發生異常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/display/<filename>')
def push_to_display(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "找不到檔案"}), 404
        
    try:
        # Load the processed preview image
        img = Image.open(filepath)
        
        # Initialize and display
        current_epd = get_epd()
        current_epd.init()
        current_epd.display(current_epd.getbuffer(img))
        current_epd.sleep()
        return jsonify({"message": "成功推送到電子紙！"})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
