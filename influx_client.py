from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
import time
import random
from influxdb_client.client.exceptions import InfluxDBError
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import sys
import json
from uuid import UUID

reg = 0

# Получаем аргументы командной строки
device_data_json = sys.argv[1]

# Преобразуем JSON строку обратно в словарь
device_data = json.loads(device_data_json)

# Преобразуем строки UUID обратно в объекты UUID
device_id = UUID(device_data['device_id'])

# Используем данные об устройстве
device_name = device_data['device_name']
ip = device_data['ip']
port = device_data['port']
slave_id = device_data['slave_id']
tags = device_data['tags']

print('Запуск клиента Modbus для получения данных')
try:
    client = ModbusClient(host=ip, port=port)
    client.connect()  # Попытка подключения к устройству Modbus
except Exception as e:
    print(f"Не удалось подключиться к устройству, проверьте IP и порт: {e}")
    sys.exit(1)  # Выход из программы в случае ошибки подключения


def create_bucket_if_not_exists(device_name):
    token = "YFojuG3FHNnmPa2MXfJK5bfke7KM6JE-1M1QxDsDaS9JqVUvTA2byRvscYIe7GX-y8BHnoHn5I4ORTDJlYhoXw=="
    org = "-"
    url = "http://localhost:8086"

    try:
        client = InfluxDBClient(url=url, token=token, org=org)
        # Получение списка бакетов
        buckets_response = client.buckets_api().find_buckets(org=org)
        bucket_names = [bucket.name for bucket in buckets_response.buckets]
        if device_name not in bucket_names:
            # Если бакет с указанным именем не существует, создаем его
            print(f"Создание бакета для устройства '{device_name}'")
            bucket = client.buckets_api().create_bucket(bucket_name=device_name, retention_rules=[], org=org)
            print(f"Бакет '{device_name}' успешно создан")
        else:
            print(f"Бакет для устройства '{device_name}' уже существует")
    except InfluxDBError as e:
        print(f"Ошибка при создании бакета: {e}")


# Вызов функции для создания бакета, если он не существует
create_bucket_if_not_exists(device_name)


# Функция для чтения значений температуры из регистров и записи их в InfluxDB
def read_and_write_measurements_values(write_api, client, tags):
    try:
        for tag in tags:
            # Получение адреса регистра из параметра "register" тега
            address = int(tag['register'])

            # Чтение значения из регистра
            rd = client.read_holding_registers(address, 2).registers
            decoder = BinaryPayloadDecoder.fromRegisters(rd, byteorder='>', wordorder='<')
            value = round(decoder.decode_16bit_float(), 2)
            print('Прочитанное значение:', value)

            # Генерация времени и создание точки для записи в InfluxDB
            random_offset = random.randint(0, 999999999)
            current_time_ns = time.time_ns()
            point_time_ns = current_time_ns + random_offset
            point = Point(tag['tag_name']).field("value", value).time(point_time_ns, WritePrecision.NS)

            # Запись точки в бакет InfluxDB
            write_api.write(bucket=device_name, org="-", record=point)
    except Exception as e:
        print(f"Ошибка: {e}")


# Вызов функции с передачей write_api и имени устройства
def run_influx_client():
    token = "YFojuG3FHNnmPa2MXfJK5bfke7KM6JE-1M1QxDsDaS9JqVUvTA2byRvscYIe7GX-y8BHnoHn5I4ORTDJlYhoXw=="
    org = "-"
    url = "http://localhost:8086"

    try:
        write_client = InfluxDBClient(url=url, token=token, org=org)
        print(True)  # Выводим True, если подключение удалось
    except Exception as e:
        print(False)  # Выводим False, если произошла ошибка при подключении
        print(f"Ошибка при подключении: {e}")

    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    return write_api


write_api = run_influx_client()

while True:
    time.sleep(1.0)
    read_and_write_measurements_values(write_api, client, tags)

client.close()
