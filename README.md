<!-- credits:start -->
> **Credits & license.** Port and maintenance by [JackStar6677-1](https://github.com/JackStar6677-1) and [DrakesCraft Labs](https://github.com/SlimefunNewHorizons). Original authors: [Den4enko](https://github.com/Den4enko) (upstream [Den4enko/Slimefun-Resourcepack](https://github.com/Den4enko/Slimefun-Resourcepack)), [Raulh22](https://github.com/Raulh22), [LoneDev](https://github.com/LoneDev), [Caribax](https://github.com/Caribax), [ybw0014](https://github.com/ybw0014), [SofiaRedmond](https://github.com/SofiaRedmond), [Keeywe](https://github.com/Keeywe), [haiman233](https://github.com/haiman233), [RelativoBR](https://github.com/RelativoBR), [Filosofas154](https://github.com/Filosofas154), [JustAHuman-xD](https://github.com/JustAHuman-xD), [AlmostPanda](https://github.com/AlmostPanda). Upstream license: **GNU General Public License v3.0** (see [LICENSE](LICENSE)). Details: [docs/UPSTREAM_ATTRIBUTION.md](docs/UPSTREAM_ATTRIBUTION.md) · Policy: [Rights & Attribution](https://github.com/SlimefunNewHorizons/.github/blob/main/RIGHTS_AND_ATTRIBUTION.md). Independent community project, not affiliated with or endorsed by the original authors or the official Slimefun team.
>
> **Créditos y licencia.** Port y mantenimiento por [JackStar6677-1](https://github.com/JackStar6677-1) y [DrakesCraft Labs](https://github.com/SlimefunNewHorizons). Autores originales: [Den4enko](https://github.com/Den4enko) (upstream [Den4enko/Slimefun-Resourcepack](https://github.com/Den4enko/Slimefun-Resourcepack)), [Raulh22](https://github.com/Raulh22), [LoneDev](https://github.com/LoneDev), [Caribax](https://github.com/Caribax), [ybw0014](https://github.com/ybw0014), [SofiaRedmond](https://github.com/SofiaRedmond), [Keeywe](https://github.com/Keeywe), [haiman233](https://github.com/haiman233), [RelativoBR](https://github.com/RelativoBR), [Filosofas154](https://github.com/Filosofas154), [JustAHuman-xD](https://github.com/JustAHuman-xD), [AlmostPanda](https://github.com/AlmostPanda). Licencia original: **GNU General Public License v3.0**. Detalle en [docs/UPSTREAM_ATTRIBUTION.md](docs/UPSTREAM_ATTRIBUTION.md).
<!-- credits:end -->

<div align="center">

  <img src="https://raw.githubusercontent.com/SlimefunNewHorizons/Slimefun-Texture-Drake/main/banner.svg" alt="Slimefun Texture banner" width="920" />

# Slimefun Texture · Drake edition

**The Slimefun resource pack that runs on DrakesCraft: every Slimefun item and the addons we ship, for Minecraft Java 1.21.5 → 26.2.**

<p>
  <a href="https://github.com/SlimefunNewHorizons/Slimefun-Texture-Drake"><img src="https://img.shields.io/badge/GitHub-Slimefun--Texture--Drake-181717?style=for-the-badge&logo=github" alt="GitHub"/></a>
  <img src="https://img.shields.io/badge/Minecraft-1.21.5_→_26.2-38BDF8?style=for-the-badge&logo=minecraft&logoColor=white" alt="Minecraft 1.21.5 to 26.2"/>
  <img src="https://img.shields.io/badge/pack_format-55_→_88+-22C55E?style=for-the-badge" alt="pack format"/>
  <img src="https://img.shields.io/badge/items-327-F59E0B?style=for-the-badge" alt="327 item definitions"/>
</p>

</div>

> ### 🏰 Join the official DrakesCraft community
> * 🎮 **Server IP**: `mc.drakescraft.cl` *(Java 1.21.11 & Bedrock)*
> * 💬 **Discord**: [discord.gg/drakescraft](https://discord.gg/rv3vtXZTk7)
> * 🌐 **Website & guides**: [web.drakescraft.cl](https://web.drakescraft.cl)

## What is in the pack

| | |
|---|---|
| **Item definitions** (`assets/minecraft/items`) | 327 — one per vanilla base item, each *selects* the Slimefun model from the item's own data |
| **Models / textures** | 4,070 models, 2,818 textures across Slimefun and 17 addon namespaces |
| **Addons covered** | InfinityExpansion (1 & 2), FluffyMachines, FoxyMachines, Gastronomicon, Liquid, SimpleUtils, SlimefunWarfare, SlimeTinker, Supreme, Cultivation, ExoticGarden, ExtraGear, ElectricSpawners, DyedBackpacks, SlimyTreeTaps, Bump… |
| **Overlays** | `overlay_1_21_6_plus` (55+), `overlay_1_21_11` (75+), `overlay_26_1_2` (84+) |

### How items get their texture
There is **no server-side CustomModelData table**. Each vanilla item definition uses a `minecraft:select` on the
`minecraft:custom_data` component and matches `PublicBukkitValues → slimefun:slimefun_item` (the Slimefun item ID). That is why
the pack needs Minecraft **1.21.5 or newer** and works unchanged on every newer version.

## Supported versions

| Minecraft | pack format | status |
|---|---|---|
| 1.21 – 1.21.4 | 34 – 46 | ❌ not supported by this pack (see [docs/COMPATIBILIDAD.md](docs/COMPATIBILIDAD.md); `legacy/` has the old 1.21–1.21.1 pack) |
| 1.21.5 – 1.21.6 | 55 – 63 | ✅ (was excluded by the previous `min 64`) |
| 1.21.7 – 1.21.8 | 64 | ✅ |
| 1.21.9 – 1.21.10 | 69 | ✅ |
| 1.21.11 | 75 | ✅ (overlay) |
| 26.1 – 26.2 | 84 – 88 | ✅ (overlay; `max_format` 500 covers future versions) |

Format numbers come from each server's `version.json` (`pack_version.resource_major`; 26.2 = 88).

## Build, validate, deploy

```bash
python tools/validar_pack.py pack                 # JSON, item → model → texture references, mcmeta vs the version table
python tools/build.py                             # dist/DrakesCraft-Slimefun-Texture-<VERSION>.zip + SHA-1 / SHA-256
```

`validar_pack.py` fails on broken JSON, missing models/textures, overlays that are declared but absent, or a `max_format` that does
not reach 26.2. CI runs it on every push and attaches the zip to each release.

**Deploying to DrakesCraft** (Star): copy the zip to `/opt/stacks/drakescraft-web/packs/latest.zip`, write its SHA-1 to
`latest.sha1`, keep the previous pair as `*.backup-pre-<reason>-<date>` (nginx container `drakescraft-pack` serves them). Players
download again only because the hash changes — **do it together with a planned restart/announcement, not in the middle of a session**.

## Credits & license

This pack is a community effort; authors credited in `pack/pack.mcmeta`: Raulh22, Den4enko, LoneDev, Caribax, ybw0014, DragonMysterious,
AnsonYK, Sofia Redmond, Jerry, haiman, RelativoBR, Filosofas154, JustAHuman-xD, MathMelo, Pandicka (see the file for links).
Art assets belong to their authors; this repository only packages them for the DrakesCraft server. If you are an author and want
something changed or removed, open an issue. Tooling in `tools/` is MIT-licensed.

Maintained by [JackStar6677-1](https://github.com/JackStar6677-1) under [DrakesCraft Labs](https://github.com/SlimefunNewHorizons).
