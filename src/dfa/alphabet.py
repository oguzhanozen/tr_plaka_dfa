"""Türk plaka alfabesi tanımları ve karakter sınıflandırma fonksiyonları."""

from enum import Enum


class CharClass(str, Enum):
    """DFA için karakter sınıflandırması."""
    DIGIT = "DIGIT"
    LETTER = "LETTER"
    SPACE = "SPACE"
    OTHER = "OTHER"


# Türk plakalarında kullanılmayan harfler
# Türkçe karakterler: Ç, Ğ, İ, Ö, Ş, Ü
# Latince karakterler: Q, W, X
FORBIDDEN_LETTERS = set("ÇĞİÖŞÜQWX")

# İzinli harfler (A-Z aralığından yasaklılar çıkarılmış)
ALLOWED_LETTERS = {
    chr(code) for code in range(ord("A"), ord("Z") + 1)
} - FORBIDDEN_LETTERS


def classify_char(ch: str) -> CharClass:
    """Bir karakteri DFA için sınıflandırır.
    
    Args:
        ch: Sınıflandırılacak karakter (tek karakter).
        
    Returns:
        Karakterin sınıfı (DIGIT, LETTER, SPACE veya OTHER).
        
    Raises:
        ValueError: Eğer girdi tek karakter değilse.
    """
    if len(ch) != 1:
        raise ValueError(
            f"classify_char tek bir karakter bekler, alınan: {len(ch)} karakter"
        )

    if ch == " ":
        return CharClass.SPACE
    
    if "0" <= ch <= "9":
        return CharClass.DIGIT

    if ch in ALLOWED_LETTERS:
        return CharClass.LETTER

    return CharClass.OTHER


def is_in_alphabet(text: str) -> bool:
    """Bir metnin tüm karakterlerinin geçerli alfabede olup olmadığını kontrol eder.
    
    Args:
        text: Kontrol edilecek metin.
        
    Returns:
        Tüm karakterler geçerliyse True, aksi halde False.
    """
    return all(classify_char(ch) != CharClass.OTHER for ch in text)
