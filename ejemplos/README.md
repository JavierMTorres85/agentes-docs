# Agentes Colaborativos MFT Analytics

Sistema de **2 agentes colaborativos** que funcionan en paralelo para procesar y analizar transferencias de archivos en entornos MFT (Managed File Transfer).

## 🎯 Objetivo

- **Agente 1 (Validador)**: Valida 9 parámetros de transferencia
- **Agente 2 (Analizador)**: Procesa datos válidos y genera métricas
- **Dashboard**: Visualización interactiva en tiempo real

## 📊 9 Parámetros Validados

1. **IdConectividad** - Perfil de conexión (IP, user, pwd)
2. **Protocolo** - SFTP, FTP, AS2, HTTP
3. **Ruta origen** - Donde se toman los archivos
4. **Ruta destino** - Donde van los archivos
5. **Tipo operación** - GET o PUT
6. **Borra origen** - Y/N
7. **Fichero procesado** - Nombre del archivo
8. **Nombre cliente** - 8 caracteres para asociar a IdConectividad
9. **Información procesado** - Tamaño, hora inicio, hora fin

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────┐
│  Agente Validador                        │
│  - Valida 9 parámetros                   │
│  - Genera TransferenciaValida            │
└────────────────┬─────────────────────────┘
                 │
            (Queue)
                 │
         ┌───────▼──────────┐
         │ Agente Analizador│
         │ - Agrupa clientes│
         │ - Calcula métricas│
         │ - Detecta inactivos│
         └───────┬──────────┘
                 │
            ┌────▼─────────────────┐
            │ Dashboard Streamlit   │
            │ - Métricas en vivo    │
            │ - Por cliente/usuario │
            │ - Facturación         │
            │ - Housekeeping        │
            └──────────────────────┘
```

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install streamlit plotly pandas
```

### 2. Ejecutar test

```bash
python test_agentes.py
```

Verás:
- Validaciones en tiempo real
- Estadísticas por cliente
- Reporte de facturación
- Usuarios inactivos

### 3. Ejecutar Dashboard

```bash
streamlit run dashboard_mft.py
```

Se abre en `http://localhost:8501`

## 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| `modelos.py` | Esquemas de datos (Transferencia, EstadisticasCliente, etc.) |
| `agentes_mft.py` | Lógica de los 2 agentes colaborativos |
| `datos_muestra.py` | Generador de datos realistas + datos inválidos |
| `test_agentes.py` | Script de prueba con salida en terminal |
| `dashboard_mft.py` | Dashboard interactivo con Streamlit |

## 🎮 Dashboard - Tabs Disponibles

### 1. 🏠 Inicio
- Métricas generales (transferencias, GB, clientes)
- Gráfico de actividad por día

### 2. 👥 Clientes
- Tabla con estadísticas por cliente
- GB transferidos (últimos 30 días vs histórico)
- Usuarios, IPs, perfiles usados
- Gráficos comparativos

### 3. 👤 Usuarios
- Listado de usuarios con IP y cliente
- Filtrable por cliente
- Top 10 usuarios por volumen

### 4. 💰 Facturación
- Tabla de clientes con tarifa actual
- Alertas de upgrade (si pasan límite GB)
- Proyección de costos mensuales
- Automatización de facturación

### 5. ⚙️ Housekeeping
- Detectar usuarios inactivos (configurable en días)
- Análisis de perfiles de conexión
- Recomendaciones de limpieza
- Identificar usuarios no utilizados

## 💡 Casos de Uso Reales

### Auditoría de Transferencias
```python
# Ver todas las transferencias de CLIENT01
reporte = analizador.obtener_reporte_facturacion()
print(reporte["CLIENT01"])
```

### Facturación Automática
```python
# Si cliente > 100 GB/mes → Premium
gb_mes = analizador.obtener_uso_mensual("CLIENT01")
if gb_mes > 100:
    tarifa = "Premium"  # $300/mes
```

### Limpieza de Usuarios Inactivos
```python
# Usuarios sin actividad > 60 días
inactivos = analizador.detectar_usuarios_inactivos(dias_inactividad=60)
for usuario in inactivos:
    print(f"Desactivar: {usuario.usuario}")
```

## 🔄 Flujo de Datos

```
Transferencia Raw
    ↓
Agente Validador (Queue 1)
    - Valida 9 parámetros
    - Genera ValidacionResultado
    ↓ (Queue 2)
Agente Analizador
    - Agrupa por cliente
    - Calcula estadísticas
    - Detecta anomalías
    ↓
Dashboard / Reportes
    - Visualiza métricas
    - Genera alertas
    - Facilita decisiones
```

## 📈 Métricas Generadas

Por **Cliente**:
- Total transferencias
- GB transferidos (histórico, 30d, 7d)
- Usuarios únicos
- IPs únicas
- Perfiles/IdConectividad usados

Por **Usuario**:
- Transferencias realizadas
- GB transferidos
- Último uso
- Días sin actividad

**Sistema**:
- Total GB (30 días, histórico)
- Clientes activos
- Proyección de costos
- Alertas de facturación

## 🔐 Notas de Seguridad

⚠️ **En producción**:
- No almacenar contraseñas en texto plano (usar `python-dotenv` o `secrets`)
- Encriptar datos sensibles (IdConectividad, IP, user)
- Auditar acceso a dashboard
- Validar entrada de usuarios

## 🧪 Testing

El archivo `datos_muestra.py` incluye:
- 50 transferencias válidas realistas
- 6 transferencias inválidas para probar validación
- Datos de clientes históricos (últimos 30 días)

## 📚 Referencias

- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Docs](https://plotly.com/python/)
- [Pandas Docs](https://pandas.pydata.org/docs/)

## 👤 Autor

Sistema creado para análisis MFT con enfoque en facturación y housekeeping.

---

**¿Cómo ejecutar ahora mismo?**

```bash
# Terminal
cd ejemplos

# Ver test en consola
python test_agentes.py

# Ver dashboard
streamlit run dashboard_mft.py
```
