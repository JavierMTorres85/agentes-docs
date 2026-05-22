"""
Agentes Colaborativos para MFT Analytics
Agente 1: Validador de parámetros
Agente 2: Analizador y generador de métricas
"""
import queue
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from modelos import (
    Transferencia, ValidacionResultado, TipoOperacion,
    Protocolo, EstadisticasCliente, MetricasUsuario
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgenteValidador:
    """
    Agente 1: Valida los 9 parámetros de transferencia
    - IdConectividad
    - Protocolo
    - Ruta origen
    - Ruta destino
    - Tipo operación
    - Borra origen
    - Fichero procesado
    - Nombre cliente
    - Información de procesado (tamaño, timestamps)
    """

    def __init__(self, cola_entrada: queue.Queue, cola_salida: queue.Queue):
        self.cola_entrada = cola_entrada
        self.cola_salida = cola_salida
        self.perfiles_protocolo = self._cargar_perfiles()

    def _cargar_perfiles(self) -> Dict[str, List[str]]:
        """Cargar perfiles válidos por protocolo"""
        return {
            "SFTP": ["SFTP_PROD", "SFTP_TEST", "SFTP_DR"],
            "FTP": ["FTP_LEGACY", "FTP_SECURE"],
            "AS2": ["AS2_PARTNER1", "AS2_PARTNER2"],
            "HTTP": ["HTTP_API", "HTTP_REST"]
        }

    def validar_id_conectividad(self, id_conectividad: str) -> bool:
        """Valida que IdConectividad exista"""
        return id_conectividad in ["SFTP_PROD", "SFTP_TEST", "FTP_LEGACY",
                                    "AS2_PARTNER1", "HTTP_API"]

    def validar_protocolo(self, protocolo: str) -> bool:
        """Valida que protocolo sea válido"""
        try:
            Protocolo[protocolo]
            return True
        except KeyError:
            return False

    def validar_ruta(self, ruta: str) -> bool:
        """Valida formato de ruta"""
        return ruta and len(ruta) > 0 and ("/" in ruta or "\\" in ruta)

    def validar_tipo_operacion(self, tipo: str) -> bool:
        """Valida tipo de operación (GET o PUT)"""
        return tipo in ["GET", "PUT"]

    def validar_borra_origen(self, valor: str) -> bool:
        """Valida booleano Y/N"""
        return valor.upper() in ["Y", "N"]

    def validar_nombre_cliente(self, nombre: str) -> bool:
        """Valida nombre de cliente (8 caracteres)"""
        return len(nombre) == 8 and nombre.isalnum()

    def validar_transferencia(self, datos: dict) -> ValidacionResultado:
        """Valida todos los parámetros"""
        resultado = ValidacionResultado(valido=True)

        # Validar IdConectividad
        if not self.validar_id_conectividad(datos.get("id_conectividad")):
            resultado.agregar_error("IdConectividad", "No existe en perfiles")

        # Validar Protocolo
        if not self.validar_protocolo(datos.get("protocolo")):
            resultado.agregar_error("Protocolo", "Protocolo inválido")

        # Validar Ruta origen
        if not self.validar_ruta(datos.get("ruta_origen")):
            resultado.agregar_error("Ruta origen", "Formato inválido")

        # Validar Ruta destino
        if not self.validar_ruta(datos.get("ruta_destino")):
            resultado.agregar_error("Ruta destino", "Formato inválido")

        # Validar Tipo operación
        if not self.validar_tipo_operacion(datos.get("tipo_operacion")):
            resultado.agregar_error("Tipo operación", "Debe ser GET o PUT")

        # Validar Borra origen
        if not self.validar_borra_origen(datos.get("borra_origen", "N")):
            resultado.agregar_error("Borra origen", "Debe ser Y o N")

        # Validar Nombre cliente
        if not self.validar_nombre_cliente(datos.get("cliente_id")):
            resultado.agregar_error("Cliente ID", "Debe tener 8 caracteres alfanuméricos")

        # Validar tamaño y timestamps
        try:
            tamaño = int(datos.get("tamaño_bytes", 0))
            if tamaño <= 0:
                resultado.agregar_error("Tamaño", "Debe ser > 0")
        except:
            resultado.agregar_error("Tamaño", "Debe ser número")

        try:
            hora_inicio = datos.get("hora_inicio")
            hora_fin = datos.get("hora_fin")
            if hora_inicio >= hora_fin:
                resultado.agregar_error("Timestamps", "hora_inicio debe ser < hora_fin")
        except:
            resultado.agregar_error("Timestamps", "Formato inválido")

        # Si todo válido, crear objeto Transferencia
        if resultado.valido:
            try:
                resultado.datos_validados = Transferencia(
                    id_conectividad=datos["id_conectividad"],
                    protocolo=datos["protocolo"],
                    ruta_origen=datos["ruta_origen"],
                    ruta_destino=datos["ruta_destino"],
                    tipo_operacion=TipoOperacion[datos["tipo_operacion"]],
                    borra_origen=datos["borra_origen"].upper() == "Y",
                    cliente_id=datos["cliente_id"],
                    fichero=datos.get("fichero", ""),
                    tamaño_bytes=int(datos["tamaño_bytes"]),
                    hora_inicio=datos["hora_inicio"],
                    hora_fin=datos["hora_fin"]
                )
            except Exception as e:
                resultado.agregar_error("Construcción", str(e))

        return resultado

    def ejecutar(self):
        """Ejecuta el agente validador continuamente"""
        logger.info("✓ Agente Validador iniciado")

        while True:
            try:
                datos = self.cola_entrada.get(timeout=5)

                if datos is None:  # Señal de parada
                    break

                logger.info(f"Validando transferencia: {datos.get('cliente_id')}")
                resultado = self.validar_transferencia(datos)

                if resultado.valido:
                    logger.info(f"✓ Validado: {datos['cliente_id']}")
                else:
                    logger.warning(f"✗ Errores: {resultado.errores}")

                self.cola_salida.put(resultado)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en Validador: {e}")


class AgenteAnalizador:
    """
    Agente 2: Analiza transferencias válidas y genera métricas
    - Agrupa por cliente
    - Calcula GB diarios/semanales/mensuales
    - Identifica usuarios no utilizados
    - Prepara datos para facturación
    """

    def __init__(self, cola_entrada: queue.Queue):
        self.cola_entrada = cola_entrada
        self.estadisticas_clientes: Dict[str, EstadisticasCliente] = {}
        self.metricas_usuarios: Dict[str, MetricasUsuario] = {}
        self.transferencias_procesadas: List[Transferencia] = []

    def procesar_transferencia(self, validacion: ValidacionResultado):
        """Procesa una transferencia válida"""

        if not validacion.valido or not validacion.datos_validados:
            return

        trans = validacion.datos_validados
        self.transferencias_procesadas.append(trans)

        # Actualizar estadísticas del cliente
        if trans.cliente_id not in self.estadisticas_clientes:
            self.estadisticas_clientes[trans.cliente_id] = EstadisticasCliente(
                cliente_id=trans.cliente_id
            )

        stats = self.estadisticas_clientes[trans.cliente_id]
        stats.total_transferencias += 1
        stats.total_bytes += trans.tamaño_bytes
        stats.fecha_ultimo_uso = trans.hora_fin

        # Extraer usuario e IP de IdConectividad (simulado)
        usuario = f"user_{trans.id_conectividad[:3]}"
        ip = f"192.168.{hash(trans.id_conectividad) % 256}.{hash(trans.cliente_id) % 256}"

        stats.usuarios_unicos.add(usuario)
        stats.ips_unicas.add(ip)
        stats.perfiles_usados.add(trans.id_conectividad)

        # Actualizar métricas de usuario
        key_usuario = f"{usuario}_{ip}"
        if key_usuario not in self.metricas_usuarios:
            self.metricas_usuarios[key_usuario] = MetricasUsuario(
                usuario=usuario,
                ip=ip,
                cliente_id=trans.cliente_id,
                transferencias=0,
                total_bytes=0,
                ultimo_uso=trans.hora_fin
            )

        met = self.metricas_usuarios[key_usuario]
        met.transferencias += 1
        met.total_bytes += trans.tamaño_bytes
        met.ultimo_uso = trans.hora_fin

        logger.info(f"✓ Analizado {trans.cliente_id}: {trans.tamaño_bytes/1024/1024:.2f} MB")

    def obtener_uso_mensual(self, cliente_id: str, meses_atras: int = 1) -> float:
        """Obtiene uso en GB del último mes"""
        if cliente_id not in self.estadisticas_clientes:
            return 0

        fecha_limite = datetime.now() - timedelta(days=30 * meses_atras)
        total = sum(
            t.tamaño_bytes for t in self.transferencias_procesadas
            if t.cliente_id == cliente_id and t.hora_fin > fecha_limite
        )
        return total / 1024 / 1024 / 1024

    def detectar_usuarios_inactivos(self, dias_inactividad: int = 30) -> List[MetricasUsuario]:
        """Detecta usuarios sin usar en X días"""
        inactivos = []
        fecha_limite = datetime.now() - timedelta(days=dias_inactividad)

        for usuario in self.metricas_usuarios.values():
            if usuario.ultimo_uso < fecha_limite:
                usuario.dias_sin_uso = (datetime.now() - usuario.ultimo_uso).days
                inactivos.append(usuario)

        return inactivos

    def obtener_reporte_facturacion(self) -> Dict:
        """Genera reporte para facturación"""
        reporte = {}

        for cliente_id, stats in self.estadisticas_clientes.items():
            gb_mes = self.obtener_uso_mensual(cliente_id)

            # Lógica de tarifas (ejemplo)
            tarifa_actual = "Estándar"
            if gb_mes > 100:
                tarifa_actual = "Premium"
            elif gb_mes > 500:
                tarifa_actual = "Enterprise"

            reporte[cliente_id] = {
                "gb_mes": round(gb_mes, 2),
                "usuarios": len(stats.usuarios_unicos),
                "ips": len(stats.ips_unicas),
                "perfiles": list(stats.perfiles_usados),
                "tarifa_actual": tarifa_actual,
                "transferencias_mes": sum(
                    1 for t in self.transferencias_procesadas
                    if t.cliente_id == cliente_id
                )
            }

        return reporte

    def ejecutar(self):
        """Ejecuta el agente analizador continuamente"""
        logger.info("✓ Agente Analizador iniciado")

        while True:
            try:
                validacion = self.cola_entrada.get(timeout=5)

                if validacion is None:
                    break

                self.procesar_transferencia(validacion)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en Analizador: {e}")


def ejecutar_sistema(transferencias_test: List[dict]):
    """Ejecuta los agentes en paralelo"""

    cola_validador_analizador = queue.Queue()
    cola_resultado = queue.Queue()

    # Crear agentes
    validador = AgenteValidador(queue.Queue(), cola_validador_analizador)
    analizador = AgenteAnalizador(cola_validador_analizador)

    # Iniciar threads
    thread_validador = threading.Thread(target=validador.ejecutar, daemon=False)
    thread_analizador = threading.Thread(target=analizador.ejecutar, daemon=False)

    thread_validador.start()
    thread_analizador.start()

    # Enviar datos al validador
    for trans in transferencias_test:
        validador.cola_entrada.put(trans)

    # Esperar procesamiento
    threading.Event().wait(timeout=3)

    # Obtener resultados
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE CLIENTES")
    print("="*60)
    for cliente_id, stats in analizador.estadisticas_clientes.items():
        print(f"\nCliente: {cliente_id}")
        print(f"  Transferencias: {stats.total_transferencias}")
        print(f"  Total: {stats.total_gb:.2f} GB")
        print(f"  Usuarios: {len(stats.usuarios_unicos)}")
        print(f"  IPs: {len(stats.ips_unicas)}")

    print("\n" + "="*60)
    print("REPORTE DE FACTURACIÓN")
    print("="*60)
    reporte = analizador.obtener_reporte_facturacion()
    for cliente, datos in reporte.items():
        print(f"\n{cliente}:")
        print(f"  GB/mes: {datos['gb_mes']}")
        print(f"  Tarifa: {datos['tarifa_actual']}")
        print(f"  Usuarios: {datos['usuarios']}")

    print("\n" + "="*60)
    print("USUARIOS INACTIVOS (>30 días)")
    print("="*60)
    inactivos = analizador.detectar_usuarios_inactivos()
    for usuario in inactivos:
        print(f"  {usuario.usuario} ({usuario.ip}): {usuario.dias_sin_uso} días")

    # Parar agentes
    validador.cola_entrada.put(None)
    cola_validador_analizador.put(None)

    return validador, analizador
