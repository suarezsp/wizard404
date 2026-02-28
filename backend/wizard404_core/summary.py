"""
Resúmenes automáticos extractivos (sin dependencias de LLM).

Genera un resumen de texto como primeras frases o N caracteres para
previsualización rápida en la UI o CLI.
"""


def summarize_text(text: str | None, max_chars: int = 300) -> str:
    """
    Genera un resumen extractivo del texto: primeras frases hasta max_chars.
    Si el texto es None o vacío, devuelve cadena vacía.
    """
    if not text or not text.strip():
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    # Cortar por frases (., !, ?) cuando sea posible
    truncated = text[: max_chars + 1]
    last_sentence = max(
        truncated.rfind(". "),
        truncated.rfind("! "),
        truncated.rfind("? "),
    )
    if last_sentence > max_chars // 2:
        return text[: last_sentence + 1].strip()
    return text[:max_chars].rstrip() + "..."
