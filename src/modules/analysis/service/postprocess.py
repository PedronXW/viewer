import itertools
import re

# mapeamento de confusões comuns em OCR
OCR_CONFUSIONS = {
    "0": "O",
    "O": "0",
    "1": "I",
    "I": "1",
    "5": "S",
    "S": "5",
    "8": "B",
    "B": "8",
    "2": "Z",
    "Z": "2",
}

# padrões brasileiros
PLATE_PATTERNS = [
    r"[A-Z]{3}[0-9]{4}",         # Antiga (ABC1234)
    r"[A-Z]{3}[0-9][A-Z][0-9]{2}",  # Mercosul (ABC1D23)
    r"[A-Z]{2}[0-9]{2}[A-Z][0-9]{2}", # Outras variações (MX09C95)
]


def generate_variants(segment: str, max_variants: int = 32):
    """
    Gera variações do texto substituindo caracteres confusos.
    Limita o número de combinações para evitar explosão.
    """
    chars = []
    for c in segment:
        if c in OCR_CONFUSIONS:
            chars.append([c, OCR_CONFUSIONS[c]])
        else:
            chars.append([c])

    variants = []
    for combo in itertools.product(*chars):
        variant = "".join(combo)
        variants.append(variant)
        if len(variants) >= max_variants:
            break
    return variants


def correct_ocr(text: str) -> str:
    if not text:
        return ""

    # limpeza básica
    text = text.upper().replace(" ", "").replace("-", "")
    text = re.sub(r"[^A-Z0-9]", "", text)  # mantém só letras/números

    # percorre janelas de tamanho 6 a 8 caracteres (tamanho típico de placa)
    for size in range(8, 5, -1):  # 8, 7, 6
        for i in range(len(text) - size + 1):
            segment = text[i : i + size]

            # gera variações tolerantes a confusão
            for variant in generate_variants(segment):
                for pattern in PLATE_PATTERNS:
                    if re.fullmatch(pattern, variant):
                        return variant  # achou uma placa válida

    return ""