#!/usr/bin/env python3
"""Valida un resource pack de Minecraft (carpeta o .zip): JSON, referencias de items->modelos->texturas, pack.mcmeta y overlays.

Uso: validar_pack.py <ruta-carpeta-o-zip> [--json salida.json]
Sale con codigo 1 si hay errores graves (JSON roto, modelos o texturas inexistentes, mcmeta incoherente).
"""
import json
import pathlib
import re
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict

# versiones de juego -> formato de resource pack (major). Fuente: version.json de cada servidor (pack_version.resource_major).
FORMATOS = {"1.21-1.21.1": 34, "1.21.2-1.21.3": 42, "1.21.4": 46, "1.21.5": 55, "1.21.6": 63, "1.21.7-1.21.8": 64,
            "1.21.9-1.21.10": 69, "1.21.11": 75, "26.1": 84, "26.2": 88}
VANILLA = {"builtin/generated", "builtin/entity", "builtin/missing"}


def cargar(ruta):
    p = pathlib.Path(ruta)
    if p.is_dir():
        return p
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="pack_"))
    with zipfile.ZipFile(p) as z:
        z.extractall(tmp)
    return tmp


def recurso(ns_ruta, tipo, ext):
    ns, _, ruta = (ns_ruta if ":" in ns_ruta else "minecraft:" + ns_ruta).partition(":")
    return ns, f"{tipo}/{ruta}{ext}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    raiz = cargar(sys.argv[1])
    errores, avisos = [], []
    mcmeta = raiz / "pack.mcmeta"
    base = [raiz]
    if mcmeta.is_file():
        try:
            meta = json.loads(mcmeta.read_text(encoding="utf-8"))
            pack = meta.get("pack", {})
            mn = pack.get("min_format", [pack.get("supported_formats", {}).get("min_inclusive", pack.get("pack_format", 0)), 0])
            mx = pack.get("max_format", [pack.get("supported_formats", {}).get("max_inclusive", pack.get("pack_format", 0)), 0])
            mn = mn[0] if isinstance(mn, list) else mn
            mx = mx[0] if isinstance(mx, list) else mx
            print(f"pack.mcmeta: formatos {mn}..{mx}")
            for nombre, f in FORMATOS.items():
                estado = "OK " if mn <= f <= mx else "NO "
                print(f"   {estado} {nombre} (formato {f})")
            if mx < FORMATOS["26.2"]:
                errores.append(f"max_format {mx} no cubre 26.2 (88)")
            for o in meta.get("overlays", {}).get("entries", []):
                d = raiz / o["directory"]
                if not d.is_dir():
                    errores.append(f"overlay {o['directory']} declarado pero la carpeta no existe")
                else:
                    base.append(d)
            decl = {o["directory"] for o in meta.get("overlays", {}).get("entries", [])}
            for d in raiz.glob("overlay_*"):
                if d.name not in decl:
                    avisos.append(f"carpeta {d.name} existe pero no esta declarada en overlays (el juego la ignora)")
            if mn > FORMATOS["1.21.5"]:
                avisos.append(f"el pack base empieza en formato {mn}: los clientes 1.21.5 (55) y 1.21.6 (63) lo marcan incompatible")
        except json.JSONDecodeError as e:
            errores.append(f"pack.mcmeta invalido: {e}")
    else:
        errores.append("falta pack.mcmeta")
    if not (raiz / "pack.png").is_file():
        avisos.append("falta pack.png")

    # indices de recursos existentes (base + overlays)
    modelos, texturas, items = set(), set(), {}
    for b in base:
        for f in b.glob("assets/*/models/**/*.json"):
            ns = f.relative_to(b / "assets").parts[0]
            modelos.add((ns, str(f.relative_to(b / "assets" / ns / "models").with_suffix("")).replace("\\", "/")))
        for f in b.glob("assets/*/textures/**/*.png"):
            ns = f.relative_to(b / "assets").parts[0]
            texturas.add((ns, str(f.relative_to(b / "assets" / ns / "textures").with_suffix("")).replace("\\", "/")))
        for f in b.glob("assets/*/items/**/*.json"):
            ns = f.relative_to(b / "assets").parts[0]
            items[(ns, str(f.relative_to(b / "assets" / ns / "items").with_suffix("")).replace("\\", "/"))] = f

    json_rotos = 0
    todos_json = list(raiz.glob("assets/**/*.json")) + [f for b in base[1:] for f in b.glob("assets/**/*.json")]
    for f in todos_json:
        try:
            json.loads(f.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            json_rotos += 1
            errores.append(f"JSON invalido {f.relative_to(raiz)}: {str(e)[:60]}")

    def par(ref):
        ns, _, r = (ref if ":" in ref else "minecraft:" + ref).partition(":")
        return ns, r

    faltan_modelo = defaultdict(set)
    refs_item = 0

    def visitar(nodo, origen):
        nonlocal refs_item
        if isinstance(nodo, dict):
            if nodo.get("type") in ("model", "minecraft:model") and isinstance(nodo.get("model"), str):
                refs_item += 1
                ns, r = par(nodo["model"])
                if (ns, r) not in modelos and f"{ns}:{r}" not in VANILLA and ns != "minecraft":
                    faltan_modelo[origen].add(f"{ns}:{r}")
            for v in nodo.values():
                visitar(v, origen)
        elif isinstance(nodo, list):
            for v in nodo:
                visitar(v, origen)

    for (ns, nombre), f in items.items():
        try:
            visitar(json.loads(f.read_text(encoding="utf-8-sig")), f"{ns}:{nombre}")
        except json.JSONDecodeError:
            pass

    faltan_tex = defaultdict(set)
    for b in base:
        for f in b.glob("assets/*/models/**/*.json"):
            try:
                m = json.loads(f.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                continue
            for k, v in (m.get("textures") or {}).items():
                if isinstance(v, str) and not v.startswith("#"):
                    ns, r = par(v)
                    if (ns, r) not in texturas and ns != "minecraft":
                        faltan_tex[str(f.relative_to(b))].add(f"{ns}:{r}")
            padre = m.get("parent")
            if isinstance(padre, str):
                ns, r = par(padre)
                if ns != "minecraft" and (ns, r) not in modelos and f"{ns}:{r}" not in VANILLA:
                    faltan_modelo[str(f.relative_to(b))].add(f"parent {ns}:{r}")

    print(f"items definidos: {len(items)} | referencias a modelos: {refs_item} | modelos: {len(modelos)} | texturas: {len(texturas)}")
    print(f"JSON rotos: {json_rotos} | items/modelos con referencias a modelos inexistentes: {len(faltan_modelo)} | modelos con texturas inexistentes: {len(faltan_tex)}")
    for k, v in list(faltan_modelo.items())[:15]:
        print("  FALTA MODELO en", k, "->", sorted(v)[:3])
    for k, v in list(faltan_tex.items())[:15]:
        print("  FALTA TEXTURA en", k, "->", sorted(v)[:3])
    if faltan_modelo:
        errores.append(f"{len(faltan_modelo)} archivos referencian modelos inexistentes")
    if faltan_tex:
        avisos.append(f"{len(faltan_tex)} modelos referencian texturas inexistentes (se veria el cubo morado)")
    for a in avisos:
        print("AVISO:", a)
    for e in errores:
        print("ERROR:", e)
    if "--json" in sys.argv:
        pathlib.Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps({"errores": errores, "avisos": avisos, "items": len(items), "modelos": len(modelos), "texturas": len(texturas),
                        "faltan_modelo": {k: sorted(v) for k, v in faltan_modelo.items()},
                        "faltan_textura": {k: sorted(v) for k, v in faltan_tex.items()}}, indent=1), encoding="utf-8")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
