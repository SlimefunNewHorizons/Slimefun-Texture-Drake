#!/usr/bin/env python3
"""Empaqueta pack/ en dist/DrakesCraft-Slimefun-Texture-<version>.zip (orden estable, sin metadatos de fecha) y imprime SHA-1/SHA-256.

Uso: python tools/build.py [version]      (por defecto la de VERSION)
El servidor Java pide el SHA-1 del zip en `resource-pack-sha1` de server.properties.
"""
import hashlib
import pathlib
import sys
import zipfile

raiz = pathlib.Path(__file__).resolve().parent.parent
version = sys.argv[1] if len(sys.argv) > 1 else (raiz / "VERSION").read_text().strip()
destino = raiz / "dist" / f"DrakesCraft-Slimefun-Texture-{version}.zip"
destino.parent.mkdir(exist_ok=True)
archivos = sorted(p for p in (raiz / "pack").rglob("*") if p.is_file())
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in archivos:
        info = zipfile.ZipInfo(p.relative_to(raiz / "pack").as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, p.read_bytes())
datos = destino.read_bytes()
print(destino.name, len(datos), "bytes,", len(archivos), "archivos")
print("SHA-1  ", hashlib.sha1(datos).hexdigest())
print("SHA-256", hashlib.sha256(datos).hexdigest())
