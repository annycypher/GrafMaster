"""GrafMaster Web — тестирование функций прямо в браузере.

Запуск локально:  streamlit run web_app.py
Хостинг: Streamlit Community Cloud (постоянная ссылка) или любой streamlit-сервер.
"""
import sys
import tempfile
import urllib.request
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from grafmaster.core import brand_catalog, link_parser, svg_parser, web_renderer  # noqa: E402

st.set_page_config(page_title="GrafMaster Web", page_icon="🎨", layout="wide")
st.title("🎨 GrafMaster — веб-версия")
st.caption("Тестируйте функции: извлечение товара по ссылке и сборка карточки по шаблону бренда.")

TAB_EXTRACT, TAB_BUILD, TAB_TEMPLATES = st.tabs(
    ["🔗 Извлечение по ссылке", "🃏 Сборка карточки", "🗂 Шаблоны брендов"])


def _svg_viewer(svg_text: str, height: int = 640):
    import html as _html
    encoded = _html.escape(svg_text)
    st.components.v1.html(
        f"""<div style="background:#111318;padding:8px;border-radius:12px">
        <svg id="card" xmlns="http://www.w3.org/2000/svg" width="450" height="600"
             style="background:#fff;border-radius:8px;display:block;margin:0 auto">{encoded}</svg>
        <div style="text-align:center;margin-top:8px">
          <button onclick="toPng()"
            style="background:#a855f7;color:#fff;border:0;padding:10px 18px;border-radius:10px;
                   font-size:15px;cursor:pointer">⬇ Скачать PNG (900×1200)</button>
        </div>
        <script>
        function toPng(){{
          var s=document.getElementById('card');
          var xml=new XMLSerializer().serializeToString(s);
          var b64=btoa(unescape(encodeURIComponent(xml)));
          var img=new Image();
          img.onload=function(){{
            var c=document.createElement('canvas'); c.width=900; c.height=1200;
            var ctx=c.getContext('2d'); ctx.fillStyle='#fff'; ctx.fillRect(0,0,900,1200);
            ctx.drawImage(img,0,0,900,1200);
            var a=document.createElement('a');
            a.href=c.toDataURL('image/png'); a.download='card.png'; a.click();
          }};
          img.src='data:image/svg+xml;base64,'+b64;
        }}
        </script>
        </div>""",
        height=height, scrolling=True)


# ---------- Вкладка 1: извлечение по ссылке ----------
with TAB_EXTRACT:
    st.subheader("Извлечение товара по ссылке (название, характеристики, фото)")
    urls = st.text_area("Ссылки на товары (по одной на строку):",
                        placeholder="https://kumtigey.ru/catalog/...")
    if st.button("🔍 Извлечь данные"):
        for url in [u.strip() for u in urls.splitlines() if u.strip()]:
            try:
                data = link_parser.extract_product(url)
                st.success(f"✅ {data.name}")
                st.write(f"Характеристик: {len(data.characteristics)}")
                if data.characteristics:
                    st.table(dict(data.characteristics))
                if data.images:
                    img_url = data.images[0]
                    st.image(img_url, width=240)
                    req = urllib.request.Request(
                        img_url, headers={"User-Agent": link_parser.UA})
                    raw = urllib.request.urlopen(req, timeout=30).read()
                    st.download_button("⬇ Скачать фото", raw, file_name="photo.jpg",
                                       mime="image/jpeg")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Ошибка для {url}: {exc}")


# ---------- Вкладка 2: сборка карточки ----------
with TAB_BUILD:
    st.subheader("Сборка карточки по шаблону бренда (SVG → PNG в браузере)")
    brands = brand_catalog.discover_brands()
    brand = st.selectbox("Бренд", brands)
    template_path = brand_catalog.template_for_brand(brand)
    if template_path is None:
        st.warning("Шаблон не найден")
    else:
        template = svg_parser.parse_svg(str(template_path))
        svg_text = Path(template_path).read_text(encoding="utf-8")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Название товара", value=template.name or "ТОВАР")
            uploaded = st.file_uploader("Фото товара (белый фон)",
                                        type=["png", "jpg", "jpeg"])
            labels = [l.text for l in template.layers
                      if l.kind == "text" and l.text
                      and not any(c.isdigit() for c in l.text)
                      and 100 < l.y < template.height * 0.55]
            default = [{"Характеристика": lb, "Значение": ""} for lb in labels[:8]]
            chars = st.data_editor(
                default, num_rows="dynamic",
                column_config={
                    "Характеристика": st.column_config.TextColumn("Характеристика"),
                    "Значение": st.column_config.TextColumn("Значение")},
                use_container_width=True)

        if st.button("🃏 Собрать карточку"):
            photo_path = None
            if uploaded is not None:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(uploaded.getvalue())
                    photo_path = tmp.name
            items = [(r["Характеристика"], r["Значение"]) for r in chars
                     if r.get("Характеристика")]
            with col2:
                st.markdown("### Результат (SVG → PNG в браузере)")
                try:
                    out_svg = web_renderer.substitute_svg(
                        template, svg_text, name, items, photo_path)
                    _svg_viewer(out_svg)
                    st.download_button("⬇ Скачать SVG (редактируемый)",
                                       out_svg, file_name=f"{brand}_card.svg",
                                       mime="image/svg+xml")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Ошибка сборки: {exc}")


# ---------- Вкладка 3: шаблоны ----------
with TAB_TEMPLATES:
    st.subheader("Шаблоны брендов (SVG)")
    for brand_name in brands:
        p = brand_catalog.template_for_brand(brand_name)
        if p:
            st.markdown(f"**{brand_name}** — `{p.name}`")
            svg_txt = Path(p).read_text(encoding="utf-8")
            _svg_viewer(svg_txt, height=420)
