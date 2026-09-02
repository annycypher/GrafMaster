"""Разбор SVG-шаблонов пользователя (копия в assets/templates)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grafmaster.core import svg_parser  # noqa: E402

BASE = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\assets\templates")

for p in sorted(BASE.glob("*.svg")):
    print("=" * 60)
    print("FILE:", p.name, "|", p.stat().st_size, "bytes")
    try:
        t = svg_parser.parse_svg(p)
        print("NAME:", t.name)
        print("SIZE:", t.width, "x", t.height)
        print("LAYERS:", len(t.layers))
        kinds = {}
        for l in t.layers:
            kinds[l.kind] = kinds.get(l.kind, 0) + 1
        print("KINDS:", kinds)
        for layer in t.layers:
            if layer.kind in ("photo", "icon") or layer.text:
                txt = layer.text[:40] if layer.text else (layer.href.split("/")[-1] if layer.href else "")
                print(f"  z={layer.z:3d} {layer.kind:6s} "
                      f"({int(layer.x)},{int(layer.y)},{int(layer.w)}x{int(layer.h)}) "
                      f"'{txt}' {layer.fill} fs={layer.font_size}")
        print("PHOTO:", t.photo)
    except Exception as exc:  # noqa: BLE001
        print("ERROR:", exc)

