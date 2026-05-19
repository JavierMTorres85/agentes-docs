# Agentes Reactivos

## Descripción

Los agentes reactivos son sistemas que responden inmediatamente a estímulos del entorno sin mantener estado interno o planificación compleja. Siguen reglas simples: si ocurre X, haz Y.

## Características Principales

- **Reactividad**: Responden directamente a cambios en el entorno
- **Sin memoria**: No mantienen estado entre reacciones
- **Reglas simples**: Usan lógica if-then o similar
- **Respuesta rápida**: Latencia mínima entre estímulo y acción
- **Determinísticos**: Comportamiento predecible y consistente

## Casos de Uso

1. **Sistemas de control** - Termostatos, sensores de humo
2. **Chatbots basados en reglas** - Responden a palabras clave
3. **Filtros de spam** - Clasifican emails automáticamente
4. **Alertas en tiempo real** - Notificaciones de eventos
5. **Videojuegos simples** - IA enemigos con comportamiento básico

## Patrones de Implementación

### Ciclo Básico (Muy Simple)
```
Estímulo → Regla → Acción
```

### Sistema de Reglas
```
SI condición_1 ENTONCES acción_1
SI condición_2 ENTONCES acción_2
SI condición_3 ENTONCES acción_3
...
```

### Ejemplo Real: Termostato
```
SI temperatura < 18°C ENTONCES encender calefacción
SI temperatura > 24°C ENTONCES encender aire acondicionado
SI temperatura ENTRE 18-24°C ENTONCES no hacer nada
```

## Ventajas

✓ Simplicidad - Fácil de entender y mantener
✓ Velocidad - Respuesta inmediata sin cálculos complejos
✓ Predecibilidad - Comportamiento completamente determinístico
✓ Eficiencia - Uso mínimo de recursos
✓ Confiabilidad - Pocos puntos de fallo

## Desafíos

✗ Limitado - No puede manejar situaciones complejas
✗ Inflexible - Difícil adaptar a nuevos escenarios
✗ Escalabilidad - Crece exponencialmente con más reglas
✗ Falta de aprendizaje - No mejora con la experiencia

## Comparación: Reactivo vs Autónomo

| Aspecto | Reactivo | Autónomo |
|---------|----------|----------|
| **Complejidad** | Muy simple | Compleja |
| **Velocidad** | Ultra-rápido | Más lento |
| **Memoria** | No | Sí |
| **Aprendizaje** | No | Sí |
| **Flexibilidad** | Baja | Alta |
| **Mantenimiento** | Fácil | Difícil |

## Ejemplos Famosos

- **Termostatos inteligentes** - Ajustan temperatura automáticamente
- **Sistemas de tráfico** - Semáforos adaptativos
- **Protección antivirus** - Detectan y bloquean amenazas
- **Drones de vigilancia** - Patrullan áreas predefinidas
