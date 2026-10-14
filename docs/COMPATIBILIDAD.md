# Compatibilidad de versiones (resultado de la revision del 2026-10-14)

## Estado
- El pack de produccion (`Slimefun 1.21.5+ v2.4`, SHA-1 `eb865aadedba8a284c2948d82f4c1f52504318b9`, el mismo que sirve `latest.zip` en Star)
  esta **internamente sano**: 0 JSON rotos, 7,618 referencias de item→modelo y todas existen, 0 modelos con textura inexistente.
- **Defecto corregido en 2.5.0**: `pack.mcmeta` declaraba `min 64` aunque el nombre y la descripcion dicen "1.21.5+". Los clientes 1.21.5
  (formato 55) y 1.21.6 (63) lo marcaban incompatible. Ahora la base cubre 55 → 500 (26.2 = 88).
- Los overlays `overlay_1_21_6_plus` (55+), `overlay_1_21_11` (75+) y `overlay_26_1_2` (84+) no se tocaron.

## Por que no cubre 1.21 – 1.21.4
Las definiciones de item usan `minecraft:select` con `property: minecraft:component` (componente `custom_data`), que **aparecio en 1.21.5**.
En 1.21.4 el juego no conoce esa propiedad (y antes de 1.21.4 ni siquiera existe `assets/minecraft/items/`). Un overlay no puede "borrar"
archivos, asi que no hay forma de que el mismo zip sirva a la vez a 1.21.4 y 1.21.5+ sin duplicar y reescribir las 327 definiciones.

### Opciones si hace falta soportar esas versiones
1. **1.21 – 1.21.1**: `legacy/jackstar-1.21-1.21.1/` (pack format 34, `models/item` + `custom_model_data`). Necesita que el core Slimefun asigne
   CustomModelData con `plugins/Slimefun/item-models.yml` (hay una tabla de referencia en esa carpeta). Distribuirlo como paquete aparte.
2. **1.21.2 – 1.21.4**: no hay pack. Habria que generar un overlay con `models/item/<base>.json` + `overrides` (CMD) a partir de las
   definiciones modernas y de `item-models.yml`; no esta hecho ni probado.
3. Lo normal en DrakesCraft: los clientes con Via* mas viejos que 1.21.5 reciben el servidor sin texturas Slimefun (siguen jugando).

## Tabla de formatos (version.json de cada servidor)
| Version | resource pack format |
|---|---|
| 1.21 – 1.21.1 | 34 |
| 1.21.2 – 1.21.3 | 42 |
| 1.21.4 | 46 |
| 1.21.5 | 55 |
| 1.21.6 | 63 |
| 1.21.7 – 1.21.8 | 64 |
| 1.21.9 – 1.21.10 | 69 |
| 1.21.11 | 75 |
| 26.1 | 84 |
| 26.2 | 88 (`pack_version.resource_major`, leido del jar de Paper 26.2 en el staging de Star) |

## Que no se pudo comprobar aqui
No hay un cliente de Minecraft en esta sesion: la validacion es estatica (estructura, JSON, referencias y rangos de formato). Falta
mirar el pack en un cliente real de 1.21.5, 1.21.11 y 26.2 antes de desplegarlo a produccion.
