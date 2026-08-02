#!/usr/bin/env python3
"""Convert embedded native MathML (<math>...</math>, from an old Word/MathType
export) into LaTeX wrapped in \\(...\\), so it renders through the same KaTeX
pipeline as the rest of the site instead of the browser's native MathML
layout. Native MathML uses a serif math font that never matches the site's
sans-serif body type, and its default operator spacing splits things like
"0.1" into "0 . 1" — cosmetic bugs that plain CSS can't override (Chromium
ignores font-family/margin overrides on MathML operator boxes).

Run from repo root: python3 _mathml_to_latex.py
Rewrites exam-data/*.json in place (q/o/exp fields for fmt=="html" rows).
Any <math> block that fails to parse/convert is left untouched — no data
loss, just one fewer question gets the fix.
"""
import json
import os
import re
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
EXAMS = ["jee", "neet", "board", "defence", "ssc-cgl"]

FUNC_NAMES = {
    "sin", "cos", "tan", "cot", "sec", "csc", "cosec", "log", "ln", "lim",
    "exp", "min", "max", "det", "gcd", "arg", "sinh", "cosh", "tanh",
}
FUNC_MAP = {"cosec": "csc"}
BIGOP_LATEX = {"\\lim", "\\max", "\\min", "\\sup", "\\inf", "\\det", "\\sum",
               "\\prod", "\\int", "\\bigcup", "\\bigcap", "\\gcd"}

OP_MAP = {
    "→": "\\to ", "⇒": "\\Rightarrow ", "⇔": "\\Leftrightarrow ",
    "∞": "\\infty ", "∑": "\\sum ", "∏": "\\prod ", "∫": "\\int ",
    "≥": "\\geq ", "≤": "\\leq ", "≠": "\\neq ", "±": "\\pm ",
    "×": "\\times ", "÷": "\\div ", "·": "\\cdot ", "∈": "\\in ",
    "∉": "\\notin ", "∀": "\\forall ", "∃": "\\exists ", "∂": "\\partial ",
    "∇": "\\nabla ", "≈": "\\approx ", "∝": "\\propto ", "≡": "\\equiv ",
    "∪": "\\cup ", "∩": "\\cap ", "⊆": "\\subseteq ", "⊂": "\\subset ",
    "°": "^\\circ ", "…": "\\ldots ", "×": "\\times ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
}
GREEK_MAP = {
    "α": "\\alpha ", "β": "\\beta ", "γ": "\\gamma ", "δ": "\\delta ",
    "ε": "\\epsilon ", "ζ": "\\zeta ", "η": "\\eta ", "θ": "\\theta ",
    "λ": "\\lambda ", "μ": "\\mu ", "ν": "\\nu ", "ξ": "\\xi ",
    "π": "\\pi ", "ρ": "\\rho ", "σ": "\\sigma ", "τ": "\\tau ",
    "φ": "\\phi ", "χ": "\\chi ", "ψ": "\\psi ", "ω": "\\omega ",
    "Δ": "\\Delta ", "Σ": "\\Sigma ", "Ω": "\\Omega ", "Φ": "\\Phi ",
    "Θ": "\\Theta ", "Λ": "\\Lambda ", "Ψ": "\\Psi ", "Γ": "\\Gamma ",
}


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def esc_text(s):
    return s.replace("\\", "").replace("{", "").replace("}", "")


def convert_children(node):
    return "".join(convert_node(c) for c in node)


def convert_node(node):
    tag = local(node.tag)
    text = (node.text or "").strip()

    if tag in ("mrow", "mstyle", "mpadded", "maction", "semantics"):
        return convert_children(node)
    if tag in ("annotation", "annotation-xml"):
        return ""
    if tag == "none":
        return ""

    if tag == "mi":
        variant = node.get("mathvariant")
        t = text
        if t in GREEK_MAP:
            return GREEK_MAP[t]
        if t in FUNC_NAMES:
            return "\\" + FUNC_MAP.get(t, t) + " "
        if variant == "normal" or len(t) > 1:
            return "\\mathrm{" + esc_text(t) + "}"
        return t

    if tag == "mn":
        return text

    if tag == "mo":
        t = text
        if t in FUNC_NAMES:
            return "\\" + FUNC_MAP.get(t, t) + " "
        if t in OP_MAP:
            return OP_MAP[t]
        if t in GREEK_MAP:
            return GREEK_MAP[t]
        if t in ("(", ")", "[", "]", "{", "}", "|"):
            return t
        return t

    if tag == "mtext":
        return "\\text{" + esc_text("".join(node.itertext())) + "}"

    if tag == "mspace":
        if node.get("linebreak"):
            return "\\\\ "
        return "\\ "

    if tag == "msup":
        ch = list(node)
        if len(ch) != 2:
            return convert_children(node)
        return "{" + convert_node(ch[0]) + "}^{" + convert_node(ch[1]) + "}"

    if tag == "msub":
        ch = list(node)
        if len(ch) != 2:
            return convert_children(node)
        return "{" + convert_node(ch[0]) + "}_{" + convert_node(ch[1]) + "}"

    if tag == "msubsup":
        ch = list(node)
        if len(ch) != 3:
            return convert_children(node)
        return "{" + convert_node(ch[0]) + "}_{" + convert_node(ch[1]) + "}^{" + convert_node(ch[2]) + "}"

    if tag == "mfrac":
        ch = list(node)
        if len(ch) != 2:
            return convert_children(node)
        return "\\frac{" + convert_node(ch[0]) + "}{" + convert_node(ch[1]) + "}"

    if tag == "msqrt":
        return "\\sqrt{" + convert_children(node) + "}"

    if tag == "mroot":
        ch = list(node)
        if len(ch) != 2:
            return "\\sqrt{" + convert_children(node) + "}"
        return "\\sqrt[" + convert_node(ch[1]) + "]{" + convert_node(ch[0]) + "}"

    if tag == "munder":
        ch = list(node)
        if len(ch) != 2:
            return convert_children(node)
        base, under = convert_node(ch[0]), convert_node(ch[1])
        if base.strip() in BIGOP_LATEX:
            return base + "_{" + under + "}"
        return "\\underset{" + under + "}{" + base + "}"

    if tag == "mover":
        ch = list(node)
        if len(ch) != 2:
            return convert_children(node)
        base, over = convert_node(ch[0]), convert_node(ch[1])
        if base.strip() in BIGOP_LATEX:
            return base + "^{" + over + "}"
        if over.strip() in ("→", "\\to", "\\rightarrow"):
            return "\\vec{" + base + "}"
        return "\\overset{" + over + "}{" + base + "}"

    if tag == "munderover":
        ch = list(node)
        if len(ch) != 3:
            return convert_children(node)
        base, under, over = convert_node(ch[0]), convert_node(ch[1]), convert_node(ch[2])
        if base.strip() in BIGOP_LATEX:
            return base + "_{" + under + "}^{" + over + "}"
        return "\\overset{" + over + "}{\\underset{" + under + "}{" + base + "}}"

    if tag == "mmultiscripts":
        ch = list(node)
        if not ch:
            return ""
        base = convert_node(ch[0])
        rest = ch[1:]
        pre_idx = None
        for i, c in enumerate(rest):
            if local(c.tag) == "mprescripts":
                pre_idx = i
                break
        if pre_idx is not None:
            # MathML spec: scripts BEFORE <mprescripts/> are postscripts,
            # scripts AFTER it are prescripts.
            post, pre = rest[:pre_idx], rest[pre_idx + 1:]
        else:
            pre, post = [], rest
        out = base
        # postscripts: pairs of (sub, sup)
        for i in range(0, len(post) - 1, 2):
            sub, sup = convert_node(post[i]), convert_node(post[i + 1])
            if sub:
                out += "_{" + sub + "}"
            if sup:
                out += "^{" + sup + "}"
        # prescripts: pairs of (sub, sup) rendered before the base
        pre_str = ""
        for i in range(0, len(pre) - 1, 2):
            sub, sup = convert_node(pre[i]), convert_node(pre[i + 1])
            piece = "{}"
            if sub:
                piece += "_{" + sub + "}"
            if sup:
                piece += "^{" + sup + "}"
            pre_str += piece
        return pre_str + out

    if tag == "mfenced":
        openc = node.get("open", "(")
        closec = node.get("close", ")")
        sep = node.get("separators", ",")
        parts = [convert_node(c) for c in node]
        sep_char = sep[0] if sep else ","
        inner = (sep_char + " ").join(parts)
        lo = "\\left" + openc if openc else "\\left."
        lc = "\\right" + closec if closec else "\\right."
        return lo + inner + lc

    if tag == "mtable":
        rows = []
        for tr in node:
            if local(tr.tag) != "mtr":
                continue
            cells = [convert_node(td) for td in tr if local(td.tag) == "mtd"]
            rows.append(" & ".join(cells))
        return "\\begin{matrix}" + " \\\\ ".join(rows) + "\\end{matrix}"

    if tag == "menclose":
        return convert_children(node)

    # unknown tag — best effort, just recurse into children
    return convert_children(node)


def mathml_to_latex(math_str):
    cleaned = re.sub(r'\sxmlns="[^"]*"', "", math_str)
    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError:
        return None
    try:
        latex = convert_node(root).strip()
    except Exception:
        return None
    if not latex:
        return None
    # collapse runs of the LaTeX spacing commands we emit between tokens
    latex = re.sub(r"(\\ |\\\\ ){2,}", lambda m: m.group(1), latex)
    return "\\(" + latex + "\\)"


MATH_RE = re.compile(r"<math\b.*?</math>", re.DOTALL)


def convert_html_field(html):
    if not html or "<math" not in html:
        return html, 0
    converted = 0

    def repl(m):
        nonlocal converted
        latex = mathml_to_latex(m.group(0))
        if latex is None:
            return m.group(0)
        converted += 1
        return latex

    return MATH_RE.sub(repl, html), converted


def main():
    total_converted = 0
    total_left = 0
    for exam in EXAMS:
        path = os.path.join(ROOT, "exam-data", f"{exam}.json")
        if not os.path.exists(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        exam_converted = 0
        for x in data:
            if x.get("fmt") != "html":
                continue
            x["q"], c = convert_html_field(x.get("q", ""))
            exam_converted += c
            new_o = []
            for o in x.get("o", []):
                o2, c = convert_html_field(o)
                new_o.append(o2)
                exam_converted += c
            x["o"] = new_o
            x["exp"], c = convert_html_field(x.get("exp", ""))
            exam_converted += c
        left = sum(1 for x in data if x.get("fmt") == "html" and "<math" in json.dumps(x))
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"{exam}: converted {exam_converted} math blocks, {left} questions still have unconverted <math>")
        total_converted += exam_converted
        total_left += left
    print(f"TOTAL: {total_converted} converted, {total_left} questions with leftover <math>")


if __name__ == "__main__":
    main()
