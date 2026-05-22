"""
Script de prueba para los agentes colaborativos MFT
Ejecuta validación y análisis con datos de muestra
"""
import sys
from datetime import datetime
from datos_muestra import generar_datos_muestra, DATOS_INVALIDOS
from agentes_mft import ejecutar_sistema


def main():
    print("\n" + "="*70)
    print("SISTEMA MFT ANALYTICS - AGENTES COLABORATIVOS")
    print("="*70)
    print("\nAgente 1: Validador de 9 parámetros")
    print("Agente 2: Analizador y generador de métricas\n")

    # Generar datos de prueba
    print("Generando datos de muestra...")
    datos_validos = generar_datos_muestra(50)
    todos_datos = datos_validos + DATOS_INVALIDOS

    print(f"  ✓ {len(datos_validos)} transferencias válidas")
    print(f"  ✗ {len(DATOS_INVALIDOS)} transferencias inválidas")
    print(f"  Total: {len(todos_datos)} para procesar\n")

    # Ejecutar sistema de agentes
    print("Iniciando agentes...")
    validador, analizador = ejecutar_sistema(todos_datos)

    # Mostrar resultados finales
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)

    print(f"\nTransferencias procesadas: {len(analizador.transferencias_procesadas)}")
    print(f"Clientes activos: {len(analizador.estadisticas_clientes)}")
    print(f"Usuarios únicos: {len(analizador.metricas_usuarios)}")

    # Análisis por cliente
    print("\n" + "-"*70)
    print("ANÁLISIS POR CLIENTE (ÚLTIMOS 30 DÍAS)")
    print("-"*70)

    total_gb_general = 0
    for cliente_id, stats in sorted(analizador.estadisticas_clientes.items()):
        gb_mes = analizador.obtener_uso_mensual(cliente_id)
        total_gb_general += gb_mes
        print(f"\n{cliente_id}:")
        print(f"  Transferencias:    {stats.total_transferencias}")
        print(f"  Total histórico:   {stats.total_gb:.2f} GB")
        print(f"  Uso últimos 30d:   {gb_mes:.2f} GB")
        print(f"  Usuarios únicos:   {len(stats.usuarios_unicos)}")
        print(f"  IPs únicas:        {len(stats.ips_unicas)}")
        print(f"  Perfiles usados:   {', '.join(stats.perfiles_usados)}")

    print(f"\nTotal sistema (30 días): {total_gb_general:.2f} GB")

    # Identificar housekeeping
    print("\n" + "-"*70)
    print("HOUSEKEEPING - USUARIOS INACTIVOS (>7 DÍAS)")
    print("-"*70)

    inactivos = analizador.detectar_usuarios_inactivos(dias_inactividad=7)
    if inactivos:
        for usuario in inactivos[:10]:  # Top 10
            print(f"  {usuario.usuario:<20} {usuario.ip:<20} "
                  f"{usuario.dias_sin_uso} días inactivo")
    else:
        print("  Todos los usuarios están activos")

    # Alertas de facturación
    print("\n" + "-"*70)
    print("ALERTAS DE FACTURACIÓN")
    print("-"*70)

    reporte = analizador.obtener_reporte_facturacion()
    for cliente_id, datos in sorted(reporte.items()):
        gb = datos['gb_mes']
        tarifa = datos['tarifa_actual']
        status = "⚠️  UPGRADE" if tarifa != "Estándar" else "✓"

        print(f"  {cliente_id}: {gb:7.2f} GB -> {tarifa:12} {status}")

    print("\n" + "="*70)
    print("Sistema MFT Analytics listo para dashboard interactivo")
    print("Ejecutar: streamlit run dashboard_mft.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
