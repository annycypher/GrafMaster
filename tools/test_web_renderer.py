"""Проверка web_renderer: подстановка названия и характеристик в SVG."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grafmaster.core import brand_catalog, svg_parser, web_renderer  # noqa: E402

p = brand_catalog.template_for_brand("GEOS")
t = svg_parser.parse_svg(str(p))
svg = Path(p).read_text(encoding="utf-8")

out = web_renderer.substitute_svg(
    t, svg, "BENZOPILA GEOS MAX",
    [("Power", "2000 W"), ("Tank", "0.5 l")], photo_path=None)

print("TITLE_OK:", "BENZOPILA GEOS MAX" in out)
print("POWER_OK:", "2000" in out and "Power" in out)
print("LEN:", len(out))

# сохраним результат для просмотра
Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\output\web_test.svg").write_text(
    out, encoding="utf-8")
print("SAVED: output/web_test.svg")
