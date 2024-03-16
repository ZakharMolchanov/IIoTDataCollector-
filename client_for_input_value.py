from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.payload import BinaryPayloadBuilder
import time
import random
import sys
import json
from uuid import UUID



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

print('Start Modbus Client for Input Value')
try:
    client = ModbusClient(host=ip, port=port)
    client.connect()  # Попытка подключения к устройству Modbus
except Exception as e:
    print(f"Не удалось подключиться к устройству, проверьте IP и порт: {e}")
    sys.exit(1)  # Выход из программы в случае ошибки подключения
# Функция для чтения значений температуры (здесь просто генерируются случайные значения)
def read_temperature_values():
    return [random.uniform(0, 100) for _ in
            range(1)]  # Генерация случайных значений температуры в диапазоне от 0 до 100


def write_temperature_values(tags):
    for tag in tags:
        address = tag['register']  # Получаем адрес регистра из параметра "register" словаря тэга
        temperature_values = read_temperature_values()  # Генерируем случайные значения температуры
        temperature = random.choice(temperature_values)  # Выбираем случайное значение температуры
        builder = BinaryPayloadBuilder(byteorder='>', wordorder='<')
        builder.add_16bit_float(temperature)
        payload = builder.build()
        result = client.write_registers(int(address), payload, skip_encode=True, unit=int(address))
        print('Temperature value', temperature, 'written to register:', address)


while True:  # Бесконечный цикл для записи данных каждую секунду
    print('-' * 5, 'New Cycle', '-' * 30)
    time.sleep(1.0)

    # Записываем значения температуры в соответствующие регистры
    write_temperature_values(device_data['tags'])

client.close()
