"""
Скрипт для генерации финального отчета по практике
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_final_report():
    """Генерация финального отчета по практике"""
    filename = "Отчет_Практика_Подсчет_багажа.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=1  # Центрирование
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    indent_style = ParagraphStyle(
        'IndentStyle',
        parent=styles['Normal'],
        leftIndent=0.5*inch
    )
    
    # Титульная страница
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("ОТЧЕТ ПО ПРАКТИКЕ", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Применение искусственных нейронных сетей для решения задач классификации, детектирования и сегментации в компьютерном зрении", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Вариант 17: Подсчет багажа на ленте в аэропорту", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    
    story.append(PageBreak())
    
    # Содержание
    story.append(Paragraph("СОДЕРЖАНИЕ", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_items = [
        "1. Цель практики",
        "2. Ознакомление с вариантом",
        "3. Подбор архитектуры нейронной сети",
        "4. Реализация веб-интерфейса",
        "5. Интеграция предобученной модели",
        "6. Вывод статистики в веб-интерфейсе",
        "7. Заключение"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Раздел 1: Цель практики
    story.append(Paragraph("1. ЦЕЛЬ ПРАКТИКИ", heading_style))
    story.append(Paragraph(
        "Целью данной практики является освоение полного цикла разработки системы искусственного интеллекта "
        "для обработки изображений: от выбора архитектуры нейронной сети до внедрения модели в веб-приложение "
        "с визуализацией результатов. В рамках практики решается задача автоматического подсчета багажа на "
        "ленте в аэропорту с использованием методов компьютерного зрения и глубокого обучения.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 2: Ознакомление с вариантом
    story.append(Paragraph("2. ОЗНАКОМЛЕНИЕ С ВАРИАНТОМ", heading_style))
    story.append(Paragraph(
        "Выбран вариант 17: «Подсчет багажа на ленте в аэропорту». Данная задача относится к классу задач "
        "детектирования объектов в компьютерном зрении. Необходимо разработать систему, способную автоматически "
        "обнаруживать и подсчитывать багаж (чемоданы, сумки, рюкзаки) на изображениях или видео с ленты транспортера.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Задача имеет практическое применение в аэропортах для автоматизации процессов учета багажа, "
        "повышения эффективности работы служб и снижения вероятности ошибок при ручном подсчете.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 3: Подбор архитектуры нейронной сети
    story.append(Paragraph("3. ПОДБОР АРХИТЕКТУРЫ НЕЙРОННОЙ СЕТИ", heading_style))
    story.append(Paragraph(
        "Для решения задачи детектирования багажа была выбрана архитектура YOLO (You Only Look Once) версии 8. "
        "YOLO является state-of-the-art архитектурой для задач детектирования объектов в реальном времени.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Преимущества YOLOv8:</b>", styles['Normal']))
    advantages = [
        "Высокая скорость обработки (real-time детектирование)",
        "Точность детектирования объектов",
        "Единая нейронная сеть для детектирования (end-to-end обучение)",
        "Хорошая работа с различными размерами объектов",
        "Наличие предобученных моделей на датасете COCO"
    ]
    
    for adv in advantages:
        story.append(Paragraph(f"• {adv}", indent_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Использована предобученная модель YOLOv8n (nano версия), которая обеспечивает баланс между "
        "скоростью и точностью. Модель обучена на датасете COCO (Common Objects in Context), который "
        "включает классы объектов, связанных с багажом: чемоданы, сумки, рюкзаки.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 4: Реализация веб-интерфейса
    story.append(Paragraph("4. РЕАЛИЗАЦИЯ ВЕБ-ИНТЕРФЕЙСА", heading_style))
    story.append(Paragraph(
        "Веб-интерфейс реализован с использованием современных веб-технологий: HTML5, CSS3 и JavaScript. "
        "Интерфейс предоставляет следующие возможности:",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    features = [
        "Загрузка изображений через файловый диалог",
        "Захват изображений с веб-камеры в реальном времени",
        "Кнопка запуска обработки изображения",
        "Визуализация результатов детектирования с отображением bounding boxes",
        "Отображение статистики: количество обнаруженного багажа, список объектов",
        "Просмотр истории всех запросов",
        "Генерация отчетов в форматах PDF и Excel"
    ]
    
    for feature in features:
        story.append(Paragraph(f"• {feature}", indent_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Интерфейс имеет современный дизайн с градиентным фоном, карточками для отображения статистики "
        "и удобной навигацией. Все операции выполняются асинхронно без перезагрузки страницы.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 5: Интеграция предобученной модели
    story.append(Paragraph("5. ИНТЕГРАЦИЯ ПРЕДОБУЧЕННОЙ МОДЕЛИ", heading_style))
    story.append(Paragraph(
        "Backend приложения реализован на Flask (Python). Интеграция модели YOLOv8 выполнена с использованием "
        "библиотеки Ultralytics, которая предоставляет удобный API для работы с предобученными моделями.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Процесс обработки изображения:</b>", styles['Normal']))
    process_steps = [
        "Загрузка изображения на сервер",
        "Передача изображения в модель YOLOv8",
        "Детектирование объектов, относящихся к классам багажа",
        "Фильтрация результатов по классам: suitcase, handbag, backpack, bag",
        "Отрисовка bounding boxes на изображении",
        "Подсчет общего количества обнаруженного багажа",
        "Возврат результатов клиенту"
    ]
    
    for i, step in enumerate(process_steps, 1):
        story.append(Paragraph(f"{i}. {step}", indent_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Модель автоматически загружается при первом запуске приложения. Для обработки используется "
        "OpenCV для работы с изображениями и отрисовки результатов детектирования.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 6: Вывод статистики в веб-интерфейсе
    story.append(Paragraph("6. ВЫВОД СТАТИСТИКИ В ВЕБ-ИНТЕРФЕЙСЕ", heading_style))
    story.append(Paragraph(
        "Система сохраняет историю всех запросов в файл JSON (history.json). Каждая запись содержит:",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.1*inch))
    
    history_fields = [
        "Уникальный идентификатор запроса",
        "Временная метка",
        "Имя обработанного файла",
        "Количество обнаруженного багажа",
        "Список всех обнаруженных объектов с координатами и уверенностью",
        "Путь к сохраненному результату"
    ]
    
    for field in history_fields:
        story.append(Paragraph(f"• {field}", indent_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "<b>Генерация отчетов:</b>", styles['Normal']
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Реализована генерация отчетов в двух форматах:",
        styles['Normal']
    ))
    story.append(Paragraph(
        "• <b>PDF отчет</b> - создается с использованием библиотеки ReportLab. Содержит общую статистику "
        "(всего запросов, общее количество багажа, среднее значение) и детальную историю последних 10 запросов.",
        indent_style
    ))
    story.append(Paragraph(
        "• <b>Excel отчет</b> - создается с использованием Pandas и OpenPyXL. Содержит таблицу со всеми "
        "запросами и итоговую строку с суммарной статистикой.",
        indent_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Раздел 7: Заключение
    story.append(Paragraph("7. ЗАКЛЮЧЕНИЕ", heading_style))
    story.append(Paragraph(
        "В рамках практики была успешно разработана система автоматического подсчета багажа на ленте в аэропорту. "
        "Система использует предобученную модель YOLOv8 для детектирования объектов и предоставляет удобный "
        "веб-интерфейс для взаимодействия с пользователем.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "<b>Достигнутые результаты:</b>", styles['Normal']
    ))
    results = [
        "Реализован полный цикл разработки системы ИИ для обработки изображений",
        "Интегрирована предобученная модель YOLOv8 для детектирования багажа",
        "Создан современный веб-интерфейс с поддержкой загрузки файлов и работы с камерой",
        "Реализована система сохранения истории запросов",
        "Добавлена генерация отчетов в форматах PDF и Excel"
    ]
    
    for result in results:
        story.append(Paragraph(f"• {result}", indent_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Система готова к использованию и может быть развернута в производственной среде. "
        "Для повышения точности в будущем можно дообучить модель на специализированном датасете "
        "изображений багажа из аэропортов.",
        styles['Normal']
    ))
    
    # Сборка документа
    doc.build(story)
    print(f"Отчет успешно создан: {filename}")

if __name__ == '__main__':
    generate_final_report()
