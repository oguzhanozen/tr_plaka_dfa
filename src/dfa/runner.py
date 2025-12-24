"""DFA çalıştırıcı ve sonuç veri yapıları."""

from dataclasses import dataclass
from typing import List, Optional

from .alphabet import classify_char, CharClass
from .tr_plate_dfa import State, Q0, is_accepting, next_state_with_char


@dataclass
class Step:
    """DFA'nın tek bir adımını temsil eder."""
    index: int  # Karakterin input içindeki indeksi
    ch: str  # İşlenen karakter
    char_class: CharClass  # Karakterin sınıfı
    from_state: State  # Başlangıç durumu
    to_state: State  # Hedef durum


@dataclass
class RunResult:
    """DFA çalıştırma sonucunu temsil eder."""
    accepted: bool  # Giriş kabul edildi mi?
    final_state: State  # Son durum
    steps: List[Step]  # Tüm adımlar
    fail_index: Optional[int] = None  # Hatanın gerçekleştiği indeks
    fail_char: Optional[str] = None  # Hataya neden olan karakter


def run_dfa(input_string: str) -> RunResult:
    """Verilen girişi DFA üzerinde çalıştırır.
    
    Args:
        input_string: Doğrulanacak plaka metni.
        
    Returns:
        DFA çalıştırma sonucu (kabul durumu, adımlar, hata bilgisi).
    """
    current_state = Q0
    execution_steps: List[Step] = []

    for char_index, character in enumerate(input_string):
        char_classification = classify_char(character)
        next_state = next_state_with_char(
            current_state,
            character,
            char_classification
        )

        execution_steps.append(Step(
            index=char_index,
            ch=character,
            char_class=char_classification,
            from_state=current_state,
            to_state=next_state
        ))

        current_state = next_state
        
        # Ölü duruma geçildiğinde erken çıkış
        if current_state == State.DEAD:
            return RunResult(
                accepted=False,
                final_state=current_state,
                steps=execution_steps,
                fail_index=char_index,
                fail_char=character
            )

    # Giriş tamamen işlendi, kabul edilip edilmediği kontrol edilir
    return RunResult(
        accepted=is_accepting(current_state),
        final_state=current_state,
        steps=execution_steps
    )
