from typing import List, Dict
import re
import json
import gradio as gr

# -------------------- Keywords por idioma --------------------
CATEGORIES_ES = {
    "pantalla": ["pantalla", "amoled", "lcd", "pulgadas", "resolución", "hdr"],
    "cámara": ["cámara", "camara", "mp", "foto", "fotografía", "night", "noche", "zoom", "sensor"],
    "batería": ["batería", "mah", "carga", "autonomía", "duración", "inalámbrica"],
    "rendimiento": ["ram", "procesador", "cpu", "snapdragon", "mediatek", "velocidad", "juego"],
    "almacenamiento": ["almacenamiento", "gb", "rom", "memoria interna"],
    "conectividad": ["5g", "4g", "wifi", "bluetooth", "nfc", "conexión"]
}

CATEGORIES_EN = {
    "screen": ["screen", "inch", "amoled", "lcd", "resolution", "hdr"],
    "camera": ["camera", "mp", "photo", "night", "zoom", "sensor"],
    "battery": ["battery", "mah", "charge", "fast charging", "wireless"],
    "performance": ["ram", "processor", "cpu", "snapdragon", "mediatek", "speed", "gaming"],
    "storage": ["storage", "gb", "rom", "internal memory"],
    "connectivity": ["5g", "4g", "wifi", "bluetooth", "nfc", "connection"]
}

# -------------------- Utilities --------------------
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

def extract_numbers(sent: str) -> List[float]:
    return [float(n) for n in re.findall(r'\d+\.?\d*', sent)]

# -------------------- Scoring --------------------
class CatEvidence:
    def __init__(self, sentences_list, scores_list):
        self.sentences_list = sentences_list
        self.scores_list = scores_list

def score_category(sentences_list: List[List[str]], cat: str) -> CatEvidence:
    scores = []
    for sentences in sentences_list:
        total = 0.0
        for s in sentences:
            nums = extract_numbers(s)
            s_low = s.lower()

            if cat in ["pantalla", "screen"]:
                inch = nums[0] if nums else 0
                total += inch
                res = [n for n in nums if n > 1000]
                if res:
                    total += sum(res) / 1000

            elif cat in ["batería", "battery", "almacenamiento", "storage", "cámara", "camera"]:
                total += max(nums) if nums else 0

            elif cat in ["rendimiento", "performance"]:
                total += sum(nums)

            elif cat in ["conectividad", "connectivity"]:
                nums_special = []
                g = re.findall(r'\b(\d+)g\b', s_low)
                nums_special += [float(n) for n in g]
                wifi = re.findall(r'wifi\s*(\d+)', s_low)
                nums_special += [float(n) for n in wifi]
                bt = re.findall(r'bluetooth\s*(\d+\.?\d*)', s_low)
                nums_special += [float(n) for n in bt]
                total += sum(nums_special)

        scores.append(total)

    return CatEvidence(sentences_list, scores)

# -------------------- Colores --------------------
def get_colors(scores: List[float]) -> List[str]:
    if not scores:
        return []
    if all(abs(scores[0] - s) < 1e-6 for s in scores):
        return ["grey"] * len(scores)

    max_score = max(scores)
    min_score = min(scores)

    colors = []
    for s in scores:
        if abs(s - max_score) < 1e-6:
            colors.append("green")
        elif abs(s - min_score) < 1e-6:
            colors.append("red")
        else:
            colors.append("orange")
    return colors

# -------------------- Comparación --------------------
def compare_by_categories(texts: List[str], language="es") -> Dict:
    texts = [clean_text(t) for t in texts]
    sents_list = [split_sentences(t) for t in texts]

    kws_dict = CATEGORIES_ES if language == "es" else CATEGORIES_EN
    cat_map_list = []

    for sents in sents_list:
        cat_map = {c: [] for c in kws_dict}
        for s in sents:
            for c in detect_categories(s, language):
                cat_map[c].append(s)
        cat_map_list.append(cat_map)

    results = {}
    for cat in kws_dict:
        sentences_per_text = [m.get(cat, []) for m in cat_map_list]
        ev = score_category(sentences_per_text, cat)
        results[cat] = {
            "scores": ev.scores_list,
            "evidence": ev.sentences_list
        }

    victories = [0] * len(texts)
    for r in results.values():
        scores = r["scores"]
        if not all(abs(scores[0] - s) < 1e-6 for s in scores):
            max_score = max(scores)
            for i, s in enumerate(scores):
                if abs(s - max_score) < 1e-6:
                    victories[i] += 1

    max_v = max(victories)
    winners = [chr(65 + i) for i, v in enumerate(victories) if v == max_v]
    overall = "Empate" if len(winners) == len(texts) else ", ".join(winners)

    return {"per_category": results, "overall": overall}

# -------------------- Salida --------------------
def build_outputs(titles: List[str], texts: List[str], language="es"):
    comp = compare_by_categories(texts, language)

    md = [
        f"# Comparación: {' vs '.join(titles)}",
        f"**Resultado general**: {comp['overall']}",
        "---"
    ]

    html_rows = ["<tr><th>Categoría</th><th>Ganador</th></tr>"]

    for cat, info in comp["per_category"].items():
        scores = info["scores"]
        colors = get_colors(scores)

        if all(c == "grey" for c in colors):
            winner_text = "Empate"
        else:
            winner_text = ", ".join(chr(65 + i) for i, c in enumerate(colors) if c == "green")

        md.append(f"## {cat.capitalize()}")
        md.append(f"**Ganador:** {winner_text}")

        for i, evid in enumerate(info["evidence"]):
            if evid:
                md.append(f"**{chr(65 + i)} — Evidencia:**")
                for s in evid:
                    md.append(f"- <span style='color:{colors[i]}'>{s}</span>")

        html_rows.append(f"<tr><td>{cat}</td><td>{winner_text}</td></tr>")
        md.append("")

    html = "<table style='width:100%; border-collapse:collapse;'>" + "".join(html_rows) + "</table>"
    json_out = json.dumps(comp, ensure_ascii=False, indent=2)

    return "\n".join(md), html, json_out

# -------------------- Gradio --------------------
def run_gradio(a_title, a_text, b_title, b_text, c_title, c_text, language):
    titles = [a_title, b_title]
    texts = [a_text, b_text]

    if c_text.strip():
        titles.append(c_title)
        texts.append(c_text)

    return build_outputs(titles, texts, language)

with gr.Blocks(title="Comparador Inteligente — Multilenguaje") as demo:
    gr.Markdown("# Comparador Inteligente — Comparación por categorías")

    with gr.Row():
        with gr.Column(scale=1):
            a_title = gr.Textbox(label="Título A", value="Producto A")
            a_text = gr.Textbox(label="Texto A", lines=5)
            b_title = gr.Textbox(label="Título B", value="Producto B")
            b_text = gr.Textbox(label="Texto B", lines=5)
            c_title = gr.Textbox(label="Título C (opcional)", value="Producto C")
            c_text = gr.Textbox(label="Texto C (opcional)", lines=5)
            language = gr.Radio(["es", "en"], label="Idioma", value="es")
            btn = gr.Button("Comparar")

        with gr.Column(scale=1):
            md_out = gr.Markdown()
            html_out = gr.HTML()
            json_out = gr.Textbox(label="JSON", lines=20)

    btn.click(
        fn=run_gradio,
        inputs=[a_title, a_text, b_title, b_text, c_title, c_text, language],
        outputs=[md_out, html_out, json_out]
    )

if __name__ == "__main__":
    demo.launch()
