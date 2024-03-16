# Modbus сервер (TCP)
from pymodbus.server import StartTcpServer  # Импорт функции для запуска TCP-сервера Modbus
from pymodbus.datastore import ModbusSequentialDataBlock  # Импорт класса для создания последовательного блока данных Modbus
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext  # Импорт контекстов для хранения данных

def run_async_server():
    nreg = 200  # Количество регистров
    # Инициализация хранилища данных
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [15]*nreg),  # Дискретные входы
        co=ModbusSequentialDataBlock(0, [16]*nreg),  # Катушки
        hr=ModbusSequentialDataBlock(0, [17]*nreg),  # Регистры хранения
        ir=ModbusSequentialDataBlock(0, [18]*nreg))  # Входные регистры
    context = ModbusServerContext(slaves=store, single=True)  # Создание контекста сервера

    # Запуск TCP-сервера
    StartTcpServer(context=context, host='localhost', address=("127.0.0.1", 502))  # Запуск сервера на локальном хосте и порту 502

if __name__ == "__main__":
    print('Modbus сервер запущен на локальном хосте порт 502')
    run_async_server()  # Запуск функции для запуска сервера
