"""
Modelos de datos para Sistema MFT Analytics
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoOperacion(Enum):
    GET = "GET"
    PUT = "PUT"


class Protocolo(Enum):
    SFTP = "SFTP"
    FTP = "FTP"
    AS2 = "AS2"
    HTTP = "HTTP"


@dataclass
class IdConectividad:
    """Perfil de conexión embebido"""
    id: str
    protocolo: Protocolo
    ip: str
    user: str
    pwd: str  # En prod, usar secretos


@dataclass
class Transferencia:
    """Registro de transferencia de archivo"""
    id_conectividad: str
    protocolo: str
    ruta_origen: str
    ruta_destino: str
    tipo_operacion: TipoOperacion
    borra_origen: bool
    cliente_id: str  # 8 caracteres
    fichero: str
    tamaño_bytes: int
    hora_inicio: datetime
    hora_fin: datetime
    estado: str = "exitoso"  # exitoso, error, pendiente

    @property
    def duracion_segundos(self) -> float:
        return (self.hora_fin - self.hora_inicio).total_seconds()

    @property
    def velocidad_mbps(self) -> float:
        """Velocidad en MB/s"""
        if self.duracion_segundos > 0:
            return (self.tamaño_bytes / 1024 / 1024) / self.duracion_segundos
        return 0


@dataclass
class ValidacionResultado:
    """Resultado de validación de parámetros"""
    valido: bool
    errores: list = field(default_factory=list)
    datos_validados: Optional[Transferencia] = None

    def agregar_error(self, campo: str, mensaje: str):
        self.errores.append(f"{campo}: {mensaje}")
        self.valido = False


@dataclass
class EstadisticasCliente:
    """Estadísticas por cliente"""
    cliente_id: str
    total_transferencias: int
    total_bytes: float
    usuarios_unicos: set = field(default_factory=set)
    ips_unicas: set = field(default_factory=set)
    perfiles_usados: set = field(default_factory=set)
    fecha_ultimo_uso: datetime = None
    fecha_primer_uso: datetime = None

    @property
    def total_gb(self) -> float:
        return self.total_bytes / 1024 / 1024 / 1024


@dataclass
class MetricasUsuario:
    """Métricas por usuario/IP"""
    usuario: str
    ip: str
    cliente_id: str
    transferencias: int
    total_bytes: float
    ultimo_uso: datetime
    dias_sin_uso: int = 0

    @property
    def total_gb(self) -> float:
        return self.total_bytes / 1024 / 1024 / 1024
