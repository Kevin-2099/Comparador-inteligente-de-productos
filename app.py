from typing import List, Dict
import re
import json
import hashlib
import shelve
import os
import tempfile
import pandas as pd
import gradio as gr

# ─────────────────────────────────────────────
# Dependencia opcional: langdetect
# ─────────────────────────────────────────────
try:
    from langdetect import detect as _langdetect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

# ─────────────────────────────────────────────
# Categorías / keywords
# ─────────────────────────────────────────────
CATEGORIES_ES = {
    "pantalla":       ["pantalla", "amoled", "lcd", "pulgadas", "resolución", "hdr"],
    "cámara":         ["cámara", "camara", "mp", "foto", "fotografía", "night", "noche", "zoom", "sensor"],
    "batería":        ["batería", "mah", "carga", "autonomía", "duración", "inalámbrica"],
    "rendimiento":    ["ram", "procesador", "cpu", "snapdragon", "mediatek", "velocidad", "juego"],
    "almacenamiento": ["almacenamiento", "gb", "rom", "memoria interna"],
    "conectividad":   ["5g", "4g", "wifi", "bluetooth", "nfc", "conexión"],
}
CATEGORIES_EN = {
    "screen":       ["screen", "inch", "amoled", "lcd", "resolution", "hdr"],
    "camera":       ["camera", "mp", "photo", "night", "zoom", "sensor"],
    "battery":      ["battery", "mah", "charge", "fast charging", "wireless"],
    "performance":  ["ram", "processor", "cpu", "snapdragon", "mediatek", "speed", "gaming"],
    "storage":      ["storage", "gb", "rom", "internal memory"],
    "connectivity": ["5g", "4g", "wifi", "bluetooth", "nfc", "connection"],
}

# Palabras de sentimiento
POSITIVE_ES = {"excelente", "increíble", "potente", "brillante", "rápido", "perfecto",
               "superior", "óptimo", "fluido", "nítido", "eficiente", "duradero"}
NEGATIVE_ES  = {"mediocre", "lento", "pobre", "malo", "débil", "insuficiente",
                "deficiente", "limitado", "anticuado", "básico"}
POSITIVE_EN  = {"excellent", "incredible", "powerful", "brilliant", "fast", "perfect",
                "superior", "optimal", "smooth", "crisp", "efficient", "lasting"}
NEGATIVE_EN  = {"mediocre", "slow", "poor", "bad", "weak", "insufficient",
                "lacking", "limited", "outdated", "basic"}

# Patrones de especificaciones
SPEC_PATTERNS_ES = {
    "pantalla":       r'(\d+\.?\d*)\s*(?:pulgadas|")',
    "cámara":         r'(\d+)\s*(?:mp|megapíxeles)',
    "batería":        r'(\d+)\s*(?:mah)',
    "ram":            r'(\d+)\s*(?:gb)\s+(?:de\s+)?ram',
    "almacenamiento": r'(\d+)\s*(?:gb|tb)\s+(?:de\s+)?(?:almacenamiento|rom|memoria)',
}
SPEC_PATTERNS_EN = {
    "screen":   r'(\d+\.?\d*)\s*(?:inch|")',
    "camera":   r'(\d+)\s*(?:mp|megapixels)',
    "battery":  r'(\d+)\s*(?:mah)',
    "ram":      r'(\d+)\s*(?:gb)\s+ram',
    "storage":  r'(\d+)\s*(?:gb|tb)\s+(?:storage|rom|memory)',
}

MIN_EVIDENCE_SENTENCES = 1
CACHE_FILE = os.path.join(tempfile.gettempdir(), "comparador_cache")
MAX_PRODUCTS = 5

# ═════════════════════════════════════════════
# Utilidades
# ═════════════════════════════════════════════
def detect_language(texts: List[str]) -> str:
    if not HAS_LANGDETECT:
        return "es"
    try:
        sample = " ".join(t for t in texts if t.strip())[:500]
        lang = _langdetect(sample)
        return "es" if lang == "es" else "en"
    except Exception:
        return "es"

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())

def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    sents = re.split(r'(?<=[.!?,])\s+', text)
    return [s.strip().strip('"\'') for s in sents if s.strip()]

def detect_categories(sent: str, language: str) -> List[str]:
    cats = []
    kws_dict = CATEGORIES_ES if language == "es" else CATEGORIES_EN
    s = sent.lower()
    for cat, kws in kws_dict.items():
        for kw in kws:
            kw_low = kw.lower()
            if cat in ["conectividad", "connectivity"]:
                if re.search(rf'\b{re.escape(kw_low)}\b', s):
                    cats.append(cat)
                    break
            else:
                if kw_low in s:
                    cats.append(cat)
                    break
    return cats

def extract_specs(text: str, language: str) -> Dict[str, float]:
    patterns = SPEC_PATTERNS_ES if language == "es" else SPEC_PATTERNS_EN
    specs: Dict[str, float] = {}
    t = text.lower()
    for key, pattern in patterns.items():
        match = re.search(pattern, t)
        if match:
            specs[key] = float(match.group(1))
    return specs

def sentiment_score(sentence: str, language: str) -> str:
    words = set(sentence.lower().split())
    pos_w = POSITIVE_ES if language == "es" else POSITIVE_EN
    neg_w = NEGATIVE_ES  if language == "es" else NEGATIVE_EN
    pos = len(words & pos_w)
    neg = len(words & neg_w)
    if pos > neg:
        return "positivo" if language == "es" else "positive"
    if neg > pos:
        return "negativo" if language == "es" else "negative"
    return "neutro" if language == "es" else "neutral"

def sentiments_for_text(sentences: List[str], language: str) -> Dict[str, int]:
    keys = ("positivo", "negativo", "neutro") if language == "es" \
           else ("positive", "negative", "neutral")
    counts: Dict[str, int] = {k: 0 for k in keys}
    for s in sentences:
        counts[sentiment_score(s, language)] += 1
    return counts

def get_colors(scores: List[float]) -> List[str]:
    if not scores:
        return []
    if all(abs(scores[0] - s) < 1e-6 for s in scores):
        return ["grey"] * len(scores)
    max_s = max(scores)
    min_s = min(scores)
    result = []
    for s in scores:
        if abs(s - max_s) < 1e-6:
            result.append("green")
        elif abs(s - min_s) < 1e-6:
            result.append("red")
        else:
            result.append("orange")
    return result

# ═════════════════════════════════════════════
# Scoring numérico
# ═════════════════════════════════════════════
def score_category(sentences_list: List[List[str]], cat: str) -> List[float]:
    scores = []
    for sentences in sentences_list:
        total = 0.0
        for s in sentences:
            nums  = [float(n) for n in re.findall(r'\d+\.?\d*', s)]
            s_low = s.lower()
            if cat in ["pantalla", "screen"]:
                total += nums[0] if nums else 0
                total += sum(n / 1000 for n in nums if n > 1000)
            elif cat in ["cámara", "camera"]:
                # Solo contar MP reales
                mp = re.findall(r'(\d+)\s*mp', s_low)
                total += sum(float(n) for n in mp) if mp else 0
            elif cat in ["batería", "battery"]:
                # Contar mAh + bonus por velocidad de carga
                mah = re.findall(r'(\d{4,5})\s*mah', s_low)
                watt = re.findall(r'(\d+)\s*w\b', s_low)
                total += sum(float(n) for n in mah)
                total += sum(float(n) for n in watt) * 10
            elif cat in ["rendimiento", "performance"]:
                ram_nums = re.findall(r'(\d+)\s*gb\s*ram', s_low)
                total += sum(float(n) for n in ram_nums)
            elif cat in ["almacenamiento", "storage"]:
                storage_nums = re.findall(r'(\d+)\s*(?:gb|tb)\s+(?:de\s+)?(?:almacenamiento|rom|memoria|storage|rom|memory)', s_low)
                total += sum(float(n) for n in storage_nums)
            elif cat in ["conectividad", "connectivity"]:
                g    = re.findall(r'\b(\d+)g\b', s_low)
                wifi = re.findall(r'wifi\s*(\d+)', s_low)
                bt   = re.findall(r'bluetooth\s*(\d+\.?\d*)', s_low)
                total += sum(float(n) for n in g + wifi + bt)
        scores.append(total)
    return scores

# ═════════════════════════════════════════════
# Comparación principal
# ═════════════════════════════════════════════
def compare_by_categories(titles: List[str], texts: List[str], language: str = "es") -> Dict:
    texts      = [clean_text(t) for t in texts]
    sents_list = [split_sentences(t) for t in texts]
    kws_dict   = CATEGORIES_ES if language == "es" else CATEGORIES_EN

    cat_map_list = []
    for sents in sents_list:
        cat_map = {c: [] for c in kws_dict}
        for s in sents:
            for c in detect_categories(s, language):
                cat_map[c].append(s)
        cat_map_list.append(cat_map)

    results = {}
    for cat in kws_dict:
        sentences_per_product = [m.get(cat, []) for m in cat_map_list]
        confidence = [
            "alta" if len(s) >= MIN_EVIDENCE_SENTENCES else "baja"
            for s in sentences_per_product
        ]
        scores = score_category(sentences_per_product, cat)
        results[cat] = {
            "scores":     scores,
            "evidence":   sentences_per_product,
            "confidence": confidence,
        }

    victories = [0] * len(titles)
    for r in results.values():
        scores = r["scores"]
        if not all(abs(scores[0] - s) < 1e-6 for s in scores):
            max_score = max(scores)
            for i, s in enumerate(scores):
                if abs(s - max_score) < 1e-6:
                    victories[i] += 1

    max_v   = max(victories)
    winners = [titles[i] for i, v in enumerate(victories) if v == max_v]
    overall = "Empate" if len(winners) == len(titles) else ", ".join(winners)

    return {"per_category": results, "overall": overall, "victories": victories}

# ═════════════════════════════════════════════
# Caché MD5
# ═════════════════════════════════════════════
def cached_compare(titles: List[str], texts: List[str], language: str) -> Dict:
    key = hashlib.md5((str(titles) + str(texts) + language).encode()).hexdigest()
    try:
        with shelve.open(CACHE_FILE) as db:
            if key in db:
                return db[key]
            result = compare_by_categories(titles, texts, language)
            db[key] = result
            return result
    except Exception:
        return compare_by_categories(titles, texts, language)

# ═════════════════════════════════════════════
# Exportar CSV
# ═════════════════════════════════════════════
def export_csv(titles: List[str], comp: Dict) -> str:
    rows = []
    for cat, info in comp["per_category"].items():
        row = {"Categoría": cat}
        for i, title in enumerate(titles):
            row[f"Score {title}"]     = round(info["scores"][i], 2)
            row[f"Confianza {title}"] = info["confidence"][i]
        rows.append(row)
    df  = pd.DataFrame(rows)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")
    df.to_csv(tmp.name, index=False)
    tmp.close()
    return tmp.name

# ═════════════════════════════════════════════
# Construcción de outputs
# ═════════════════════════════════════════════
def build_outputs(titles: List[str], texts: List[str], language: str):
    comp     = cached_compare(titles, texts, language)
    csv_path = export_csv(titles, comp)

    md = [
        f"# {'Comparación' if language == 'es' else 'Comparison'}: {' vs '.join(titles)}",
        f"**{'Resultado general' if language == 'es' else 'Overall result'}:** {comp['overall']}",
        "",
        f"### {'Sentimiento por texto' if language == 'es' else 'Sentiment per text'}",
    ]
    for title, text in zip(titles, texts):
        sents  = split_sentences(text)
        counts = sentiments_for_text(sents, language)
        md.append(f"**{title}**: " + " · ".join(f"{k}: {v}" for k, v in counts.items()))

    md += ["", f"### {'Especificaciones detectadas' if language == 'es' else 'Detected specs'}"]
    for title, text in zip(titles, texts):
        specs = extract_specs(text, language)
        line  = ", ".join(f"{k}={v}" for k, v in specs.items()) if specs else "—"
        md.append(f"**{title}**: {line}")
    md.append("---")

    html_rows = ["<tr><th>Categoría</th><th>Ganador</th><th>Confianza</th></tr>"]
    for cat, info in comp["per_category"].items():
        scores     = info["scores"]
        confidence = info["confidence"]
        colors     = get_colors(scores)
        winner_text = (
            "Empate" if all(c == "grey" for c in colors)
            else ", ".join(titles[i] for i, c in enumerate(colors) if c == "green")
        )
        conf_text = " / ".join(
            f"<span style='color:{'green' if c == 'alta' else 'orange'}'>{c}</span>"
            for c in confidence
        )
        md.append(f"## {cat.capitalize()}")
        md.append(f"**{'Ganador' if language == 'es' else 'Winner'}:** {winner_text}")
        for i, evid in enumerate(info["evidence"]):
            if evid:
                md.append(f"**{titles[i]} — Evidencia:**")
                for s in evid:
                    sent = sentiment_score(s, language)
                    sent_color = (
                        "green" if sent in ("positivo", "positive") else
                        "red"   if sent in ("negativo", "negative") else
                        "gray"
                    )
                    md.append(
                        f"- <span style='color:{colors[i]}'>{s}</span> "
                        f"<small style='color:{sent_color}'>[{sent}]</small>"
                    )
        html_rows.append(f"<tr><td>{cat}</td><td>{winner_text}</td><td>{conf_text}</td></tr>")
        md.append("")

    html     = ("<table style='width:100%;border-collapse:collapse;font-size:14px;'>"
                + "".join(html_rows) + "</table>")
    json_out = json.dumps(comp, ensure_ascii=False, indent=2)
    return "\n".join(md), html, json_out, csv_path

# ═════════════════════════════════════════════
# Gradio UI
# ═════════════════════════════════════════════
def run_gradio(*args):
    product_count = int(args[0])
    lang_override = args[1]

    titles, texts = [], []
    for i in range(product_count):
        t = args[2 + i * 2]
        x = args[2 + i * 2 + 1]
        if x.strip():
            titles.append(t or f"Producto {chr(65+i)}")
            texts.append(x)

    if len(texts) < 2:
        return "⚠️ Introduce texto en al menos 2 productos.", "", "{}", None

    language = detect_language(texts) if lang_override == "auto" else lang_override
    return build_outputs(titles, texts, language)


def update_rows(n):
    return [gr.update(visible=(i < int(n))) for i in range(MAX_PRODUCTS)]


with gr.Blocks(title="Comparador Inteligente", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Comparador Inteligente\nCompara hasta 5 productos por categorías")

    with gr.Row():
        product_count = gr.Slider(2, MAX_PRODUCTS, value=2, step=1,
                                  label="Número de productos")
        lang_radio = gr.Radio(["auto", "es", "en"], value="auto", label="Idioma",
                              info="auto = detección automática con langdetect")

    product_inputs = []
    product_rows   = []
    for i in range(MAX_PRODUCTS):
        with gr.Row(visible=(i < 2)) as row:
            t_box = gr.Textbox(label=f"Título {chr(65+i)}",
                               value=f"Producto {chr(65+i)}", scale=1)
            x_box = gr.Textbox(label=f"Texto {chr(65+i)}", lines=6, scale=3)
        product_rows.append(row)
        product_inputs.extend([t_box, x_box])

    product_count.change(fn=update_rows, inputs=product_count, outputs=product_rows)

    btn = gr.Button("Comparar", variant="primary")

    with gr.Tabs():
        with gr.Tab("Resumen"):
            md_out = gr.Markdown()
        with gr.Tab("Tabla"):
            html_out = gr.HTML()
        with gr.Tab("JSON"):
            json_out = gr.Textbox(label="JSON completo", lines=20)
        with gr.Tab("Exportar"):
            csv_out = gr.File(label="Descargar CSV")

    btn.click(
        fn=run_gradio,
        inputs=[product_count, lang_radio] + product_inputs,
        outputs=[md_out, html_out, json_out, csv_out],
    )

if __name__ == "__main__":
    demo.launch()
