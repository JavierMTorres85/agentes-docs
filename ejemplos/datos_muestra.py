"""
Datos de muestra para testing del sistema MFT
"""
from datetime import datetime, timedelta
import random


def generar_datos_muestra(num_transferencias: int = 50) -> list:
    """Genera datos realistas para testing"""

    clientes = ["CLIENT01", "CLIENT02", "CLIENT03", "CLIENT04", "CLIENT05"]
    perfiles = ["SFTP_PROD", "SFTP_TEST", "FTP_LEGACY", "AS2_PARTNER1", "HTTP_API"]
    protocolos = ["SFTP", "SFTP", "FTP", "AS2", "HTTP"]
    rutas_origen = [
        "/data/entrada/",
        "/var/sftp/inbox/",
        "C:\\FTP\\In\\",
        "/as2/incoming/",
        "/api/uploads/"
    ]
    rutas_destino = [
        "/data/salida/",
        "/var/sftp/outbox/",
        "C:\\FTP\\Out\\",
        "/as2/outgoing/",
        "/api/processed/"
    ]

    transferencias = []
    fecha_base = datetime.now() - timedelta(days=30)

    for i in range(num_transferencias):
        hora_inicio = fecha_base + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        duracion_minutos = random.randint(1, 120)
        hora_fin = hora_inicio + timedelta(minutes=duracion_minutos)

        tamaño_mb = random.choice([10, 50, 100, 250, 500, 1000, 5000, 10000])

        trans = {
            "id_conectividad": random.choice(perfiles),
            "protocolo": random.choice(protocolos),
            "ruta_origen": random.choice(rutas_origen),
            "ruta_destino": random.choice(rutas_destino),
            "tipo_operacion": random.choice(["GET", "PUT"]),
            "borra_origen": random.choice(["Y", "N"]),
            "cliente_id": random.choice(clientes),
            "fichero": f"archivo_{i}.dat",
            "tamaño_bytes": tamaño_mb * 1024 * 1024,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
        }
        transferencias.append(trans)

    return transferencias


# Datos inválidos para testing de validación
DATOS_INVALIDOS = [
    {
        "id_conectividad": "INVALID",  # No existe
        "protocolo": "SFTP",
        "ruta_origen": "/data/in/",
        "ruta_destino": "/data/out/",
        "tipo_operacion": "GET",
        "borra_origen": "Y",
        "cliente_id": "CLIENT01",
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
    {
        "id_conectividad": "SFTP_PROD",
        "protocolo": "INVALID",  # Protocolo inválido
        "ruta_origen": "/data/in/",
        "ruta_destino": "/data/out/",
        "tipo_operacion": "GET",
        "borra_origen": "Y",
        "cliente_id": "CLIENT01",
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
    {
        "id_conectividad": "SFTP_PROD",
        "protocolo": "SFTP",
        "ruta_origen": "invalida",  # Ruta sin / o \
        "ruta_destino": "/data/out/",
        "tipo_operacion": "GET",
        "borra_origen": "Y",
        "cliente_id": "CLIENT01",
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
    {
        "id_conectividad": "SFTP_PROD",
        "protocolo": "SFTP",
        "ruta_origen": "/data/in/",
        "ruta_destino": "/data/out/",
        "tipo_operacion": "INVALID",  # GET o PUT
        "borra_origen": "Y",
        "cliente_id": "CLIENT01",
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
    {
        "id_conectividad": "SFTP_PROD",
        "protocolo": "SFTP",
        "ruta_origen": "/data/in/",
        "ruta_destino": "/data/out/",
        "tipo_operacion": "GET",
        "borra_origen": "X",  # Y o N
        "cliente_id": "CLIENT01",
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
    {
        "id_conectividad": "SFTP_PROD",
        "protocolo": "SFTP",
        "ruta_origen": "/data/in/",
        "ruta_destino": "/data/out/",
        "tipo_operacion": "GET",
        "borra_origen": "Y",
        "cliente_id": "TOOLONG",  # Debe tener exactamente 8 caracteres
        "fichero": "test.txt",
        "tamaño_bytes": 1024,
        "hora_inicio": datetime.now(),
        "hora_fin": datetime.now() + timedelta(minutes=5),
    },
]


if __name__ == "__main__":
    datos = generar_datos_muestra(5)
    for d in datos:
        print(d)
