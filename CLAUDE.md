# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito del Proyecto

Documentación educativa sobre tipos de agentes de IA: autónomos, reactivos, de orquestación y colaborativos. Incluye descripción de características, casos de uso, patrones de implementación y comparativas.

## Estructura del Proyecto

```
agentes-docs/
├── docs/                         # Documentación detallada
│   ├── agentes-autonomos.md      # Agentes con decisión independiente
│   ├── agentes-reactivos.md      # Agentes basados en reglas
│   ├── agentes-orquestacion.md   # Coordinadores de agentes
│   └── agentes-colaborativos.md  # Agentes que cooperan
├── ejemplos/                     # Ejemplos de código (futuro)
├── README.md                     # Inicio rápido
└── CLAUDE.md                     # Este archivo
```

## Tareas Comunes

### Agregar nueva documentación
```bash
# Crear nuevo archivo en docs/
# Seguir estructura de archivos existentes:
# - Descripción clara
# - Características principales (bulleted list)
# - Casos de uso (numbered list)
# - Patrones de implementación
# - Ventajas/Desafíos
# - Ejemplos reales
```

### Actualizar tabla comparativa
- Tablas están duplicadas en cada documento
- Al actualizar una, actualizar todas las referencias

### Agregar ejemplos de código
- Crear archivo `ejemplos/tipo-agente-ejemplo.py` (o .js, etc.)
- Referenciar desde documentación con enlace

## Arquitectura de Contenido

Cada documento de tipo de agente sigue patrón consistente:

1. **Descripción** (1-2 párrafos)
2. **Características Principales** (bulleted list)
3. **Casos de Uso** (numbered list)
4. **Patrones de Implementación** (diagramas ASCII + explicación)
5. **Ventajas/Desafíos** (checkmarks/x-marks)
6. **Ejemplos Famosos**
7. **Comparativas** (tablas con otros tipos)

## Notas Especiales

- Mantener tono educativo y accesible
- Usar diagramas ASCII para visualizaciones
- Las tablas comparativas deben estar sincronizadas en todos los docs
- Evitar jerga innecesaria; explicar conceptos cuando sea primera mención
- Ejemplos reales ayudan a entender casos de uso

## Próximos Pasos

- [ ] Agregar ejemplos de código funcionales en `ejemplos/`
- [ ] Crear diagramas más complejos si es necesario
- [ ] Agregar ejercicios o preguntas de repaso
- [ ] Vincular con recursos externos (papers, artículos, etc.)

## Contribuyentes

- Javier Torres (@JavierMTorres85)
