"""Türk plaka formatı için Deterministik Sonlu Otomat (DFA) tanımı.

Türk plaka formatı:
- İl kodu: 01-81 arası iki rakam
- Boşluk
- 1-3 harf (yasaklı harfler hariç)
- Boşluk  
- 2-4 rakam

Örnek: "34 ABC 1234"
"""

from enum import Enum
from .alphabet import CharClass

# İl kodu aralığı sabitleri
MIN_PROVINCE_CODE = 1
MAX_PROVINCE_CODE = 81


class State(str, Enum):
    """DFA durumları."""
    # Başlangıç
    Q0 = "q0"

    # İl kodu ilk rakamı (0, 1-7, 8 için ayrı durumlar)
    Q1_0 = "q1_0"  # İlk rakam '0' (01-09 olmalı)
    Q1_1_7 = "q1_1_7"  # İlk rakam 1-7 arası (10-79 olmalı)
    Q1_8 = "q1_8"  # İlk rakam '8' (80-81 olmalı)

    # İl kodu tamamlandı
    Q2 = "q2"
    
    # İlk boşluk okundu
    Q3 = "q3"

    # Harf kısmı (1-3 harf)
    Q4 = "q4"  # 1. harf
    Q5 = "q5"  # 2. harf
    Q6 = "q6"  # 3. harf
    
    # İkinci boşluk okundu
    Q7 = "q7"

    # Son rakam kısmı (2-4 rakam)
    Q8 = "q8"  # 1. rakam (henüz kabul değil)
    Q9 = "q9"  # 2. rakam (kabul)
    Q10 = "q10"  # 3. rakam (kabul)
    Q11 = "q11"  # 4. rakam (kabul)

    # Ölü durum
    DEAD = "qDead"


# Başlangıç durumu
Q0 = State.Q0

# Kabul durumları (2-4 rakam için Q9, Q10, Q11)
ACCEPTING_STATES = {State.Q9, State.Q10, State.Q11}

# Durum geçiş tablosu (İl kodu sonrası format için)
TRANSITIONS = {
    # İl kodundan ilk boşluğa
    (State.Q2, CharClass.SPACE): State.Q3,

    # İlk boşluktan harflere
    (State.Q3, CharClass.LETTER): State.Q4,
    
    # Harf geçişleri
    (State.Q4, CharClass.LETTER): State.Q5,
    (State.Q5, CharClass.LETTER): State.Q6,

    # Harflerden ikinci boşluğa (1-3 harf desteklenir)
    (State.Q4, CharClass.SPACE): State.Q7,
    (State.Q5, CharClass.SPACE): State.Q7,
    (State.Q6, CharClass.SPACE): State.Q7,

    # İkinci boşluktan son rakamlara (2-4 rakam)
    (State.Q7, CharClass.DIGIT): State.Q8,
    (State.Q8, CharClass.DIGIT): State.Q9,
    (State.Q9, CharClass.DIGIT): State.Q10,
    (State.Q10, CharClass.DIGIT): State.Q11,
}


def is_accepting(state: State) -> bool:
    """Bir durumun kabul durumu olup olmadığını kontrol eder.
    
    Args:
        state: Kontrol edilecek durum.
        
    Returns:
        Durum kabul durumuysa True, aksi halde False.
    """
    return state in ACCEPTING_STATES


def next_state_with_char(state: State, ch: str, cc: CharClass) -> State:
    """Geçerli durum, karakter ve karakter sınıfına göre sonraki durumu hesaplar.
    
    İl kodu kısmı (01-81) için karakter değerine göre özel geçiş yapar.
    Diğer kısımlar için TRANSITIONS tablosunu kullanır.
    
    Args:
        state: Geçerli durum.
        ch: İşlenen karakter.
        cc: Karakterin sınıfı.
        
    Returns:
        Sonraki durum (geçersiz giriş için DEAD durumu).
    """
    # İl kodu ilk rakamı (01-81 aralığı için özel kontrol)
    if state == State.Q0:
        return _handle_first_province_digit(ch, cc)
    
    if state == State.Q1_0:
        return _handle_second_province_digit_from_0(ch, cc)
    
    if state == State.Q1_1_7:
        return _handle_second_province_digit_from_1_7(ch, cc)
    
    if state == State.Q1_8:
        return _handle_second_province_digit_from_8(ch, cc)

    # İl kodu sonrası format kontrolleri (genel geçiş tablosu)
    return TRANSITIONS.get((state, cc), State.DEAD)


def _handle_first_province_digit(ch: str, cc: CharClass) -> State:
    """İl kodu ilk rakamını işler (01-81 aralığı)."""
    if cc != CharClass.DIGIT:
        return State.DEAD
    
    if ch == "0":
        return State.Q1_0  # 01-09 olmalı
    if "1" <= ch <= "7":
        return State.Q1_1_7  # 10-79 olmalı
    if ch == "8":
        return State.Q1_8  # 80-81 olmalı
    
    return State.DEAD  # '9' geçersiz (90-99 yok)


def _handle_second_province_digit_from_0(ch: str, cc: CharClass) -> State:
    """İl kodu ikinci rakamını işler (ilk rakam 0 ise, 01-09)."""
    if cc != CharClass.DIGIT:
        return State.DEAD
    
    # 01-09 arası geçerli (00 geçersiz)
    return State.Q2 if "1" <= ch <= "9" else State.DEAD


def _handle_second_province_digit_from_1_7(ch: str, cc: CharClass) -> State:
    """İl kodu ikinci rakamını işler (ilk rakam 1-7 ise, 10-79)."""
    if cc != CharClass.DIGIT:
        return State.DEAD
    
    # Herhangi bir rakam geçerli (10-79)
    return State.Q2


def _handle_second_province_digit_from_8(ch: str, cc: CharClass) -> State:
    """İl kodu ikinci rakamını işler (ilk rakam 8 ise, 80-81)."""
    if cc != CharClass.DIGIT:
        return State.DEAD
    
    # Sadece 0 ve 1 geçerli (80-81), 82-89 geçersiz
    return State.Q2 if ch in ("0", "1") else State.DEAD
