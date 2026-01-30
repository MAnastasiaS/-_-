from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import os
import json
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
import base64
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# Настройки
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
HISTORY_FILE = 'history.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Загрузка предобученной модели YOLO
# Используем YOLOv8, которая хорошо детектирует объекты (включая сумки, чемоданы)
model = YOLO('yolov8n.pt')  # nano версия для быстрой работы

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_history():
    """Загрузка истории запросов"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(entry):
    """Сохранение записи в историю"""
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def detect_luggage(image_path):
    """Детектирование багажа на изображении"""
    try:
        # Классы YOLO, связанные с багажом
        luggage_classes = ['suitcase', 'handbag', 'backpack', 'bag', 'sports ball']
        luggage_class_ids = [24, 26, 27, 28, 32]  # ID классов в COCO dataset
        
        # Загрузка изображения
        img = cv2.imread(image_path)
        if img is None:
            return None, [], 0, "Ошибка загрузки изображения"
        
        # Детектирование объектов
        results = model(image_path)
        
        detected_objects = []
        luggage_count = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Проверяем, является ли объект багажом
                    if cls_id in luggage_class_ids or result.names[cls_id] in luggage_classes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detected_objects.append({
                            'class': result.names[cls_id],
                            'confidence': round(conf, 2),
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })
                        luggage_count += 1
        
        # Рисуем bounding boxes на изображении
        result_img = img.copy()
        for obj in detected_objects:
            x1, y1, x2, y2 = obj['bbox']
            cv2.rectangle(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{obj['class']} {obj['confidence']:.2f}"
            cv2.putText(result_img, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result_img, detected_objects, luggage_count, None
    except Exception as e:
        return None, [], 0, f"Ошибка обработки: {str(e)}"

# Обработчики ошибок для возврата JSON вместо HTML
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ресурс не найден'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Возвращаем JSON для всех исключений
    return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_image():
    """Обработка загруженного изображения"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        # Сохранение файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Обработка изображения
        try:
            result_img, detected_objects, luggage_count, error_msg = detect_luggage(filepath)
            
            if result_img is None:
                return jsonify({'error': error_msg or 'Ошибка обработки изображения'}), 500
        except Exception as e:
            return jsonify({'error': f'Ошибка при обработке: {str(e)}'}), 500
        
        # Сохранение результата
        result_filename = f"result_{unique_filename}"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        cv2.imwrite(result_path, result_img)
        
        # Сохранение в историю
        history_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'luggage_count': luggage_count,
            'detected_objects': detected_objects,
            'result_path': result_path
        }
        save_history(history_entry)
        
        # Кодирование результата в base64 для отправки
        _, buffer = cv2.imencode('.jpg', result_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'luggage_count': luggage_count,
            'detected_objects': detected_objects,
            'result_image': f"data:image/jpeg;base64,{img_base64}",
            'history_id': history_entry['id']
        })
    
    return jsonify({'error': 'Неподдерживаемый формат файла'}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    """Получение истории запросов"""
    history = load_history()
    return jsonify(history)

@app.route('/api/history/<history_id>', methods=['GET'])
def get_history_item(history_id):
    """Получение конкретной записи из истории"""
    history = load_history()
    for entry in history:
        if entry['id'] == history_id:
            return jsonify(entry)
    return jsonify({'error': 'Запись не найдена'}), 404

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Генерация PDF отчета"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Требуется JSON формат'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Неверный формат данных'}), 400
        
        report_type = data.get('type', 'pdf')
        
        history = load_history()
        if not history:
            return jsonify({'error': 'История пуста'}), 400
        
        if report_type == 'pdf':
            return generate_pdf_report(history)
        elif report_type == 'excel':
            return generate_excel_report(history)
        else:
            return jsonify({'error': 'Неподдерживаемый тип отчета'}), 400
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации отчета: {str(e)}'}), 500

def generate_pdf_report(history):
    """Генерация PDF отчета"""
    try:
        filename = f"luggage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
    
        # Заголовок
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30
        )
        story.append(Paragraph("Отчет по подсчету багажа", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Общая статистика
        total_requests = len(history)
        total_luggage = sum(entry.get('luggage_count', 0) for entry in history)
        avg_luggage = total_luggage / total_requests if total_requests > 0 else 0
        
        stats_data = [
            ['Параметр', 'Значение'],
            ['Всего запросов', str(total_requests)],
            ['Всего обнаружено багажа', str(total_luggage)],
            ['Среднее количество на запрос', f"{avg_luggage:.2f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Общая статистика", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Детальная история
        story.append(Paragraph("Детальная история", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        for entry in history[-10:]:  # Последние 10 записей
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            story.append(Paragraph(f"<b>Запрос от {timestamp}</b>", styles['Normal']))
            story.append(Paragraph(f"Файл: {entry['filename']}", styles['Normal']))
            story.append(Paragraph(f"Обнаружено багажа: {entry['luggage_count']}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        from flask import jsonify
        return jsonify({'error': f'Ошибка генерации PDF: {str(e)}'}), 500

def generate_excel_report(history):
    """Генерация Excel отчета"""
    try:
        filename = f"luggage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        
        # Подготовка данных
        data = []
        for entry in history:
            data.append({
                'Дата и время': datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                'Файл': entry['filename'],
                'Количество багажа': entry['luggage_count'],
                'Объекты': ', '.join([obj['class'] for obj in entry.get('detected_objects', [])])
            })
        
        df = pd.DataFrame(data)
        
        # Добавление итоговой строки
        total_row = pd.DataFrame([{
            'Дата и время': 'ИТОГО',
            'Файл': '',
            'Количество багажа': df['Количество багажа'].sum(),
            'Объекты': f"Всего запросов: {len(df)}"
        }])
        df = pd.concat([df, total_row], ignore_index=True)
        
        # Сохранение в Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Отчет', index=False)
            
            # Форматирование
            worksheet = writer.sheets['Отчет']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        from flask import jsonify
        return jsonify({'error': f'Ошибка генерации Excel: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)