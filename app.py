from flask import Flask, render_template, request, jsonify, send_from_directory
import base64
import os
from datetime import datetime

app = Flask(__name__)

# إنشاء مجلد لحفظ الصور
UPLOAD_FOLDER = 'captured_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# الحصول على المسار الكامل للمجلد
UPLOAD_FOLDER_ABSOLUTE = os.path.abspath(UPLOAD_FOLDER)

@app.route('/')
def index():
    """الصفحة الرئيسية التي تحتوي على الرابط"""
    return render_template('index.html')

@app.route('/capture')
def capture():
    """صفحة التقاط الصورة"""
    return render_template('capture.html')

@app.route('/save_image', methods=['POST'])
def save_image():
    """حفظ الصورة المرسلة من الكاميرا"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'لم يتم إرسال صورة'}), 400
        
        # إزالة البادئة base64
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # تحويل base64 إلى bytes
        image_bytes = base64.b64decode(image_data)
        
        # إنشاء اسم ملف فريد
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'photo_{timestamp}.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # حفظ الصورة
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # طباعة معلومات الحفظ في console
        absolute_path = os.path.abspath(filepath)
        file_size = os.path.getsize(filepath)
        print("\n" + "=" * 60)
        print("📸 تم حفظ صورة جديدة!")
        print(f"📁 المسار الكامل: {absolute_path}")
        print(f"📂 المجلد: {UPLOAD_FOLDER_ABSOLUTE}")
        print(f"📄 اسم الملف: {filename}")
        print(f"📊 حجم الملف: {file_size / 1024:.2f} KB")
        print(f"🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ الصورة بنجاح',
            'filename': filename,
            'path': absolute_path,
            'folder': UPLOAD_FOLDER_ABSOLUTE,
            'size': file_size
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

@app.route('/images')
def list_images():
    """عرض قائمة الصور المحفوظة"""
    try:
        images = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in sorted(os.listdir(UPLOAD_FOLDER), reverse=True):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    absolute_path = os.path.abspath(filepath)
                    file_size = os.path.getsize(filepath)
                    file_time = os.path.getmtime(filepath)
                    
                    images.append({
                        'filename': filename,
                        'path': absolute_path,
                        'folder': UPLOAD_FOLDER_ABSOLUTE,
                        'size': file_size,
                        'size_kb': round(file_size / 1024, 2),
                        'time': datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S'),
                        'url': f'/image/{filename}'
                    })
        
        return render_template('images.html', images=images, folder_path=UPLOAD_FOLDER_ABSOLUTE)
    except Exception as e:
        return f'خطأ: {str(e)}', 500

@app.route('/image/<filename>')
def get_image(filename):
    """عرض صورة محددة"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/images')
def api_images():
    """API لعرض قائمة الصور"""
    try:
        images = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in sorted(os.listdir(UPLOAD_FOLDER), reverse=True):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    absolute_path = os.path.abspath(filepath)
                    file_size = os.path.getsize(filepath)
                    file_time = os.path.getmtime(filepath)
                    
                    images.append({
                        'filename': filename,
                        'path': absolute_path,
                        'folder': UPLOAD_FOLDER_ABSOLUTE,
                        'size': file_size,
                        'size_kb': round(file_size / 1024, 2),
                        'time': datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S'),
                        'url': f'/image/{filename}'
                    })
        
        return jsonify({
            'success': True,
            'folder': UPLOAD_FOLDER_ABSOLUTE,
            'count': len(images),
            'images': images
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


