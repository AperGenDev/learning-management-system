"""Перегенерация Python-кода из recommendation.proto.

Запуск: python -m grpc_contracts.generate

пакет grpcio-tools. 
"""

import os
from pathlib import Path

from grpc_tools import protoc #компилятор Protocol Buffers

ROOT = Path(__file__).resolve().parent.parent
PROTO = "grpc_contracts/recommendation.proto"


def main() -> None:
    os.chdir(ROOT) # перейти в корень проекта
    code = protoc.main([
        "grpc_tools.protoc",# имя программы (так требует protoc)
        "-I.",   # где искать .proto-файлы: в текущей папке (корне)
        "--python_out=.", # куда положить файл с сообщениями (_pb2.py)
        "--grpc_python_out=.", # куда положить файл с клиентом и сервером (_pb2_grpc.py)
        PROTO, # что компилировать
    ])
    if code != 0:
        raise SystemExit(f"protoc завершился с ошибкой (код {code})")
    print("Сгенерированы grpc_contracts/recommendation_pb2.py и recommendation_pb2_grpc.py")


if __name__ == "__main__":
    main()
