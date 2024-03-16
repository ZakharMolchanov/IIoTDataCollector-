from flask import Flask, render_template, request, redirect, url_for

import secrets
from db_classes import db, Device, Setting, DescriptionDevice, Tag
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException
import uuid
import subprocess
import json



app = Flask(__name__)
app.config[
        'SQLALCHEMY_DATABASE_URI'] = secrets.postgresConn


db.init_app(app)
processes = []
#Остановка всех процессов
def stop_all_processes():
    for process in processes:
        process.terminate()

@app.route('/')
def index():
    devices = Device.query.all()
    return render_template('index.html', devices=devices)

#Запуск сбора данных с устройства
@app.route('/start_processing/<device_id>', methods=['POST'])
def start_processing(device_id):
    try:
        # Получаем данные об устройстве из базы данных или другого источника
        device = Device.query.filter_by(device_id=device_id).first()
        settings = Setting.query.filter_by(device_id=device_id).first()
        tags = Tag.query.filter_by(device_id=device_id).all()
        # Дополнительно получайте другие необходимые данные

        # Преобразуем объекты UUID в строки
        device_id_str = str(device.device_id)
        # Преобразуем объекты Tag в словари с нужными атрибутами
        tags_serializable = [{'tag_id'     : str(tag.tag_id),
                              'tag_name'   : tag.tag_name,
                              'description': tag.description,
                              'register'   : tag.register}
                             for tag in tags]

        # Формируем данные для передачи в client_for_input_value.py
        device_data = {
                'device_id'  : device_id_str,
                'device_name': device.device_name,
                'ip'         : settings.ip,
                'port'       : settings.port,
                'slave_id'   : settings.slave_id,
                'tags'       : tags_serializable,
        }

        # Запускаем файлы emulator.py, client_for_input_value.py, influx_client.py
        processes.append(subprocess.Popen(['python', 'emulator.py']))
        processes.append(subprocess.Popen(['python', 'client_for_input_value.py', json.dumps(device_data)]))
        processes.append(subprocess.Popen(['python', 'influx_client.py', json.dumps(device_data)]))

        # После успешного запуска процессов, перенаправляем пользователя на страницу устройства
        return f'<script>alert("Сбор данных начат,для просмотра данных перейдите в InfluxDB: http://localhost:8086/"); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'
    except Exception as e:
        return f'<script>alert("{str(e)}"); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'

#Остановка сбора данных
@app.route('/stop_processing/<device_id>', methods=['POST'])
def stop_processing(device_id):
    try:
        # Останавливаем нужные процессы
        stop_all_processes()  # Остановить все процессы Python, можно уточнить критерии
        return f'<script>alert("Cбор данных успешно остановлен"); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'
    except Exception as e:
        return f'<script>alert("{str(e)}"); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'

#Удаление переменной у устройства
@app.route('/delete_tag/<tag_id>', methods=['POST'])
def delete_tag(tag_id):
    # Здесь вы можете добавить код для удаления переменной с заданным tag_id
    # Пример кода:
    tag = Tag.query.filter_by(tag_id=tag_id).first()
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return redirect(url_for('device_details', device_id=tag.device_id))
    else:
        return "Тег не найден"

# Обновление основной информации о устройстве
@app.route('/update_device_info/<device_id>', methods=['POST'])
def update_device_info(device_id):
    # Получаем объект устройства
    device = Device.query.filter_by(device_id=device_id).first()
    if device:
        # Обновляем информацию об устройстве
        device.device_name = request.form['device_name']
        device.latitude = request.form['latitude']
        device.longitude = request.form['longitude']
        db.session.commit()
        return redirect(url_for('device_details', device_id=device_id))
    else:
        return "Устройство не найдено"

#Поиск устройства
@app.route('/search_device', methods=['GET'])
def search_device():
    search_query = request.args.get('search_query')
    devices = Device.query.filter(Device.device_name.ilike(f'%{search_query}%')).all()
    return render_template('index.html', devices=devices)

#Добавление переменной к устройству
@app.route('/add_tag/<device_id>', methods=['POST'])
def add_tag(device_id):
    # Получаем данные из формы
    tag_name = request.form['tag_name']
    description = request.form['description']
    register = request.form['register']
    tag_id = request.form.get('tag_id')  # Получаем ID тега, если он есть

    if tag_id:  # Если есть ID тега, значит это обновление существующего тега
        tag = Tag.query.filter_by(tag_id=tag_id).first()  # Проверяем, существует ли тег с таким ID
        if tag:  # Если тег существует, обновляем его атрибуты
            tag.tag_name = tag_name
            tag.description = description
            tag.register = register
            db.session.commit()  # Применяем изменения в базе данных
        else:
            return "Тег не найден"  # Если тег не найден, вы можете вернуть сообщение об ошибке
    else:  # Если ID тега отсутствует, значит это добавление нового тега
        new_tag = Tag(
                tag_id=str(uuid.uuid4()),
                device_id=device_id,
                tag_name=tag_name,
                description=description,
                register=register
        )
        db.session.add(new_tag)
        db.session.commit()

    return redirect(url_for('device_details', device_id=device_id))

#Удаление устройства
@app.route('/delete_device/<device_id>', methods=['POST'])
def delete_device(device_id):
    # Ищем устройство по его идентификатору
    device = Device.query.filter_by(device_id=device_id).first()

    # Если устройство найдено, удаляем его из базы данных
    if device:
        db.session.delete(device)
        db.session.commit()

    # Перенаправляем пользователя на главную страницу
    return redirect(url_for('index'))

#Создание устройства
@app.route('/create_device', methods=['POST'])
def create_device():
    # Получаем данные из формы
    device_name = request.form['device_name']
    latitude = request.form.get('latitude', None)
    longitude = request.form.get('longitude', None)

    # Генерируем уникальный идентификатор UUID для нового устройства
    device_id = str(uuid.uuid4())

    # Создаем новое устройство с уникальным идентификатором
    new_device = Device(device_id=device_id, device_name=device_name)

    # Проверяем, были ли переданы широта и долгота и добавляем их к устройству, если они существуют
    if latitude:
        new_device.latitude = latitude
    if longitude:
        new_device.longitude = longitude

    db.session.add(new_device)
    db.session.commit()

    return redirect(url_for('index'))

# Рендер страницы устройства
@app.route('/device/<device_id>')
def device_details(device_id):
    # Получаем информацию об устройстве по его идентификатору
    device = Device.query.filter_by(device_id=device_id).first()
    if device:
        settings = Setting.query.filter_by(device_id=device_id).first()
        tags = Tag.query.filter_by(device_id=device_id).all()
        descriptions = DescriptionDevice.query.filter_by(device_id=device_id).all()
        return render_template('device.html', device=device, settings=settings, tags=tags, descriptions=descriptions)
    else:
        return "Устройство не найдено"

#Обновление  устройства
@app.route('/update_device/<device_id>', methods=['GET', 'POST'])
def update_device(device_id):
    # Получаем объект устройства
    device = Device.query.filter_by(device_id=device_id).first()

    if request.method == 'POST':
        if device:
            # Обновляем информацию об устройстве
            device.device_name = request.form['device_name']
            device.latitude = request.form['latitude']
            device.longitude = request.form['longitude']
            db.session.commit()
            return redirect(url_for('device_details', device_id=device_id))
        else:
            return "Устройство не найдено"
    else:
        if device:
            # Отображаем форму для изменения устройства
            return render_template('update_device.html', device=device)
        else:
            return "Устройство не найдено"

#Добавление/ изменение информации об устройстве
@app.route('/add_or_edit_description/<device_id>', methods=['POST'])
def add_or_edit_description(device_id):
    # Получаем данные из формы
    description_name = request.form['description_name']
    content = request.form['content']

    # Проверяем, существует ли уже описание для данного устройства
    existing_description = DescriptionDevice.query.filter_by(device_id=device_id,
                                                             description_name=description_name).first()
    if existing_description:
        # Если описание уже существует, обновляем его содержимое
        existing_description.content = content
    else:
        # Иначе создаем новое описание
        new_description = DescriptionDevice(
                description_id=str(uuid.uuid4()),
                device_id=device_id,
                description_name=description_name,
                content=content
        )
        db.session.add(new_description)

    db.session.commit()

    return redirect(url_for('device_details', device_id=device_id))

#Добавление/обновление настроек+ проверка подключения к modbus устройству
@app.route('/update_settings/<device_id>', methods=['POST'])
def update_settings(device_id):
    ip = request.form['ip']
    port = request.form['port']
    slave_id = request.form['slave_id']
    try:
        client = ModbusClient(host=ip, port=port)
        if client.connect():  # Попытка подключения к устройству Modbus
            # Получаем объект устройства и обновляем его настройки
            device = Device.query.filter_by(device_id=device_id).first()
            if device:
                settings = Setting.query.filter_by(device_id=device_id).first()
                if not settings:
                    # Если настройки отсутствуют, создаем новую запись настроек
                    settings = Setting(device_id=device_id, ip=ip, port=port, slave_id=slave_id)
                    db.session.add(settings)
                else:
                    # Если настройки уже существуют, обновляем их значения
                    settings.ip = ip
                    settings.port = port
                    settings.slave_id = slave_id
                db.session.commit()
                return redirect(url_for('device_details', device_id=device_id))
        else:
            return f'<script>alert("Не удалось подключиться к устройству, проверьте IP адрес и порт"); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'
    except ConnectionException as e:  # Обработка исключения ConnectionException
        print(f"Не удалось подключиться к устройству, проверьте IP и порт: {e}")
        return f'<script>alert(""); window.location.href = "{url_for("device_details", device_id=device_id)}";</script>'
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return "Произошла ошибка при обновлении настроек устройства."

    return "Не удалось обновить настройки устройства."


if __name__ == '__main__':
    app.run(debug=True)
