"""Giriş metni normalizasyon fonksiyonları."""


def normalize_input(raw_input: str) -> str:
    """Plaka girişini DFA için normalize eder.
    
    Normalizasyon adımları:
    1. Küçük harfleri büyüğe çevirir
    2. Satır sonu karakterlerini (\\r, \\n) temizler
    
    Önemli: İç boşluklara kasıtlı olarak dokunulmaz.
    Bu sayede çift boşluk gibi format hataları DFA tarafından yakalanabilir.
    
    Args:
        raw_input: Ham plaka girişi.
        
    Returns:
        Normalize edilmiş plaka metni.
    """
    if raw_input is None:
        return ""
    
    # Satır sonu karakterlerini temizle ve büyük harfe çevir
    return raw_input.replace("\r", "").replace("\n", "").upper()
