"""Быстрый прогон: ссылка -> извлечение -> 7 карточек 900×1200."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grafmaster.core import card_builder, link_parser  # noqa: E402

URL = ("https://kumtigey.ru/catalog/sadovo_ogorodnaya_tekhnika/"
       "pily_tsepnye/benzopila_geos_max_csp346_227520/?ysclid=mtihisz85j322957550")
OUT = Path(r"C:\Users\Anna\.cline\data\workspaces\chat\GrafMaster\output")
PHOTOS = OUT / "photos"
CARDS = OUT / "cards"
PLATE = "#E10C13"  # красная плашка, как в примере бензопилы


def main() -> None:
    data = link_parser.extract_product(URL)
    print("NAME:", data.name)
    print("CHARS total:", len(data.characteristics))
    photo = None
    if data.images:
        folder = PHOTOS / link_parser.safe_dir_name(data.name)
        photo = link_parser.download_image(data.images[0], folder)
        print("PHOTO:", photo)
    chars = card_builder.pick_chars(data.characteristics)
    print("USED CHARS:")
    for t, v in chars:
        print("  -", t, "=", v)
    out = CARDS / link_parser.safe_dir_name(data.name)
    files = card_builder.build_set(data.name, chars, photo, out, plate=PLATE)
    for f in files:
        print("SAVED:", f)


if __name__ == "__main__":
    main()
