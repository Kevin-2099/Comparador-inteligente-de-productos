from typing import List, Dict, Tuple
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
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip().strip('"\'') for s in sents if s.strip()]

def detect_categories(sent: str, language: str) -> List[str]:
    cats = []
    kws_dict = CATEGORIES_ES if language == "es" else CATEGORIES_EN
    s = sent.lower()
    for cat, kws in kws_dict.items():
        if any(kw.lower() in s for kw in kws):
            cats.append(cat)
    return cats

def extract_numbers(sent: str) -> List[float]:
    return [float(n) for n in re.findall(r'\d+\.?\d*', sent)]

# -------------------- Scoring --------------------
class CatEvidence:
    def __init__(self, sentences_a, sentences_b, score_a, score_b):
        self.sentences_a = sentences_a
        self.sentences_b = sentences_b
        self.score_a = score_a
        self.score_b = score_b

def score_category(sentences_a: List[str], sentences_b: List[str], cat: str) -> CatEvidence:
    def sum_values(sentences, category):
        total = 0.0
        for s in sentences:
            nums = extract_numbers(s)
            if category in ["pantalla","screen"]:
                inch = nums[0] if nums else 0
                total += inch
                res = [n for n in nums if n > 1000]
                if res:
                    total += sum(res)/1000
            elif category in ["batería","battery"]:
                total += max(nums) if nums else 0
            elif category in ["rendimiento","performance"]:
                total += sum(nums)
            elif category in ["almacenamiento","storage"]:
                total += max(nums) if nums else 0
            elif category in ["cámara","camera"]:
                total += max(nums) if nums else 0
            elif category in ["conectividad","connectivity"]:
                nums_special = []
                s_low = s.lower()
                g = re.findall(r'(\d+)g', s_low)
                nums_special += [float(n) for n in g]
                wifi = re.findall(r'wifi\s*(\d+)', s_low)
                nums_special += [float(n) for n in wifi]
                bt = re.findall(r'bluetooth\s*(\d+\.?\d*)', s_low)
                nums_special += [float(n) for n in bt]
                total += sum(nums_special)
        return total

    score_a = sum_values(sentences_a, cat)
    score_b = sum_values(sentences_b, cat)
    return CatEvidence(sentences_a, sentences_b, score_a, score_b)

def decide_winner(e: CatEvidence, threshold=0.01):
    a = e.score_a
    b = e.score_b
    if abs(a-b) < threshold:
        return "Empate"
    return "A" if a > b else "B"

# -------------------- Comparación --------------------
def compare_by_categories(a_text: str, b_text: str, language="es") -> Dict:
    a_text = clean_text(a_text)
    b_text = clean_text(b_text)
    sents_a = split_sentences(a_text)
    sents_b = split_sentences(b_text)

    kws_dict = CATEGORIES_ES if language=="es" else CATEGORIES_EN
    cat_map_a = {c: [] for c in kws_dict}
    cat_map_b = {c: [] for c in kws_dict}

    for s in sents_a:
        cats = detect_categories(s, language)
        for c in cats:
            cat_map_a.setdefault(c, []).append(s)
    for s in sents_b:
        cats = detect_categories(s, language)
        for c in cats:
            cat_map_b.setdefault(c, []).append(s)

    results = {}
    victories_a = 0
    victories_b = 0

    for cat in cat_map_a.keys():
        ev = score_category(cat_map_a.get(cat, []), cat_map_b.get(cat, []), cat)
        winner = decide_winner(ev)
        results[cat] = {
            "winner": winner,
            "evidence_a": ev.sentences_a,
            "evidence_b": ev.sentences_b
        }
        if winner=="A":
            victories_a +=1
        elif winner=="B":
            victories_b +=1

    # Resultado general basado en victorias
    if victories_a > victories_b:
        overall = "A"
    elif victories_b > victories_a:
        overall = "B"
    else:
        overall = "Empate"

    return {"per_category": results, "overall": overall}

# -------------------- Salida --------------------
def build_outputs(a_title, a_text, b_title, b_text, language="es"):
    comp = compare_by_categories(a_text, b_text, language)
    md = [f"# Comparación: {a_title} vs {b_title}", f"**Resultado general**: {comp['overall']}", "---"]
    html_rows = ["<tr><th>Categoría</th><th>Ganador</th></tr>"]
    for cat, info in comp["per_category"].items():
        md.append(f"## {cat.capitalize()}")
        md.append(f"**Ganador:** {info['winner']}")
        if info['evidence_a']:
            md.append("**A — Evidencia:**")
            for s in info['evidence_a']:
                md.append(f"- {s}")
        if info['evidence_b']:
            md.append("**B — Evidencia:**")
            for s in info['evidence_b']:
                md.append(f"- {s}")
        html_rows.append(f"<tr><td>{cat}</td><td>{info['winner']}</td></tr>")
        md.append("")
    html = "<table style='width:100%; border-collapse:collapse;'>" + "".join(html_rows) + "</table>"
    json_out = json.dumps(comp, ensure_ascii=False, indent=2)
    return "\n".join(md), html, json_out

# -------------------- Gradio --------------------
def run_gradio(a_title, a_text, b_title, b_text, language):
    return build_outputs(a_title or "A", a_text or "", b_title or "B", b_text or "", language)

with gr.Blocks(title="Comparador Inteligente — Multilenguaje") as demo:
    gr.Markdown("# Comparador Inteligente — Comparación por categorías")
    with gr.Row():
        # Columna izquierda: Inputs
        with gr.Column(scale=1):
            a_title = gr.Textbox(label="Título A / Title A", value="Producto A")
            a_text = gr.Textbox(label="Texto A / Text A", lines=10)
            b_title = gr.Textbox(label="Título B / Title B", value="Producto B")
            b_text = gr.Textbox(label="Texto B / Text B", lines=10)
            language = gr.Radio(["es","en"], label="Idioma / Language", value="es")
            btn = gr.Button("Comparar / Compare")
        # Columna derecha: Outputs
        with gr.Column(scale=1):
            md_out = gr.Markdown()
            html_out = gr.HTML()
            json_out = gr.Textbox(label="JSON", lines=20)
    btn.click(fn=run_gradio, inputs=[a_title,a_text,b_title,b_text,language], outputs=[md_out,html_out,json_out])

if __name__ == "__main__":
    demo.launch()
