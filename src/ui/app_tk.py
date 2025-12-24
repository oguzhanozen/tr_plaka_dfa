"""Türk plaka DFA doğrulama uygulaması."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, List

from utils.normalize import normalize_input
from dfa.runner import run_dfa, RunResult, Step
from ui.dfa_view_tk import DFACanvasView

# Uygulama sabitleri
WINDOW_TITLE = "TR Plaka DFA Kontrolü"
WINDOW_GEOMETRY = "1250x720"
DEFAULT_ANIMATION_DELAY_MS = 450
ENTRY_WIDTH = 40
LISTBOX_WIDTH = 160
LISTBOX_HEIGHT = 12


class PlateCheckerApp:
    """Türk plaka formatını DFA ile doğrulayan GUI uygulaması."""

    def __init__(self, root: tk.Tk) -> None:
        """Uygulamayı başlatır.
        
        Args:
            root: Tkinter ana penceresi.
        """
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)

        # Animasyon kontrol değişkenleri
        self._animation_timer_id: Optional[str] = None
        self._is_playing: bool = False
        self._current_steps: List[Step] = []
        self._current_step_index: int = 0
        self._animation_delay_ms: int = DEFAULT_ANIMATION_DELAY_MS

        self._build_ui()

    # ---------- UI Oluşturma ----------
    def _build_ui(self) -> None:
        """Kullanıcı arayüzü bileşenlerini oluşturur."""
        self._create_input_section()
        self._create_control_panel()
        self._create_result_label()
        self._create_dfa_visualization()
        self._create_steps_listbox()
        self._bind_keyboard_shortcuts()

    def _create_input_section(self) -> None:
        """Plaka giriş alanını oluşturur."""
        ttk.Label(
            self.root,
            text="Plaka Giriniz (Örn: 34 ABC 1234)",
            font=("Arial", 12)
        ).pack(pady=8)

        self.entry = ttk.Entry(
            self.root,
            width=ENTRY_WIDTH,
            font=("Arial", 12),
            justify="center"
        )
        self.entry.pack(pady=5)

    def _create_control_panel(self) -> None:
        """Kontrol butonlarını oluşturur."""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=6)

        self.btn_validate = ttk.Button(
            control_frame,
            text="Doğrula (Hazırla)",
            command=self.prepare_validation
        )
        self.btn_validate.pack(side=tk.LEFT, padx=6)

        self.btn_step = ttk.Button(
            control_frame,
            text="İleri Adım (▶︎1)",
            command=self.execute_single_step,
            state="disabled"
        )
        self.btn_step.pack(side=tk.LEFT, padx=6)

        self.btn_play = ttk.Button(
            control_frame,
            text="Başlat / Devam (▶︎)",
            command=self.start_animation,
            state="disabled"
        )
        self.btn_play.pack(side=tk.LEFT, padx=6)

        self.btn_pause = ttk.Button(
            control_frame,
            text="Duraklat (⏸)",
            command=self.pause_animation,
            state="disabled"
        )
        self.btn_pause.pack(side=tk.LEFT, padx=6)

    def _create_result_label(self) -> None:
        """Doğrulama sonucu etiketi oluşturur."""
        self.result_label = ttk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold")
        )
        self.result_label.pack(pady=6)

    def _create_dfa_visualization(self) -> None:
        """DFA görselleştirme canvas'ını oluşturur."""
        graph_frame = ttk.Frame(self.root)
        graph_frame.pack(pady=(1, 8), fill="x")
        self.dfa_view = DFACanvasView(graph_frame, width=1200, height=320)

    def _create_steps_listbox(self) -> None:
        """DFA adımlarını gösteren listbox'ı oluşturur."""
        ttk.Label(
            self.root,
            text="Adımlar",
            font=("Arial", 11, "bold")
        ).pack(pady=(10, 2))
        
        self.steps_box = tk.Listbox(
            self.root,
            width=LISTBOX_WIDTH,
            height=LISTBOX_HEIGHT,
            font=("Consolas", 10)
        )
        self.steps_box.pack(pady=6)

    def _bind_keyboard_shortcuts(self) -> None:
        """Klavye kısayollarını bağlar."""
        self.entry.bind("<Return>", lambda e: self.prepare_validation())

    # ---------- Animasyon Kontrolleri ----------
    def _stop_animation_timer(self) -> None:
        """Animasyon zamanlayıcısını durdurur."""
        if self._animation_timer_id is not None:
            self.root.after_cancel(self._animation_timer_id)
            self._animation_timer_id = None

    def pause_animation(self) -> None:
        """Animasyonu duraklatır."""
        self._is_playing = False
        self._stop_animation_timer()
        self._update_button_states()

    def start_animation(self) -> None:
        """Animasyonu başlatır veya devam ettirir."""
        if not self._current_steps or self._is_animation_complete():
            return

        self._is_playing = True
        self._update_button_states()
        self._animation_tick()

    def _animation_tick(self) -> None:
        """Animasyon döngüsünün bir adımını işler."""
        if not self._is_playing:
            return

        if self._is_animation_complete():
            self._is_playing = False
            self._stop_animation_timer()
            self._update_button_states()
            return

        self._apply_current_step()
        self._current_step_index += 1
        self._animation_timer_id = self.root.after(
            self._animation_delay_ms,
            self._animation_tick
        )

    def execute_single_step(self) -> None:
        """Tek bir DFA adımını çalıştırır."""
        if not self._current_steps or self._is_animation_complete():
            return

        self.pause_animation()
        self._apply_current_step()
        self._current_step_index += 1
        self._update_button_states()

    def _apply_current_step(self) -> None:
        """Geçerli DFA adımını uygular ve görselleştirir."""
        step = self._current_steps[self._current_step_index]
        self.dfa_view.step(step.from_state, step.to_state)
        self._highlight_step_in_listbox(self._current_step_index)

    def _highlight_step_in_listbox(self, index: int) -> None:
        """Listbox'ta belirtilen adımı vurgular."""
        self.steps_box.selection_clear(0, tk.END)
        self.steps_box.selection_set(index)
        self.steps_box.see(index)

    def _is_animation_complete(self) -> bool:
        """Animasyonun tamamlanıp tamamlanmadığını kontrol eder."""
        return self._current_step_index >= len(self._current_steps)

    # ---------- Doğrulama ----------
    def prepare_validation(self) -> None:
        """Plaka doğrulamasını hazırlar ve DFA adımlarını oluşturur."""
        self.pause_animation()
        self._reset_ui()

        raw_input = self.entry.get()
        normalized_input = normalize_input(raw_input)
        validation_result = run_dfa(normalized_input)

        self._display_validation_result(validation_result)
        self._setup_steps_for_animation(validation_result)
        self._update_button_states()

    def _reset_ui(self) -> None:
        """UI elementlerini sıfırlar."""
        self.steps_box.delete(0, tk.END)
        self.dfa_view.reset_path()

    def _display_validation_result(self, result: RunResult) -> None:
        """Doğrulama sonucunu görüntüler."""
        if result.accepted:
            self.result_label.config(
                text="✅ GEÇERLİ PLAKA",
                foreground="green"
            )
        else:
            self.result_label.config(
                text="❌ GEÇERSİZ PLAKA",
                foreground="red"
            )

    def _setup_steps_for_animation(self, result: RunResult) -> None:
        """DFA adımlarını animasyon için hazırlar."""
        self._current_steps = result.steps
        self._current_step_index = 0
        self._populate_steps_listbox(result.steps)

    def _populate_steps_listbox(self, steps: List[Step]) -> None:
        """Adımları listbox'a ekler."""
        for step in steps:
            step_text = (
                f"{step.index + 1}.Adım: '{step.ch}' "
                f"[{step.char_class}] "
                f"{step.from_state} → {step.to_state}"
            )
            self.steps_box.insert(tk.END, step_text)

    # ---------- Buton Durumu Yönetimi ----------
    def _update_button_states(self) -> None:
        """Butonların aktif/pasif durumlarını günceller."""
        has_steps = len(self._current_steps) > 0
        can_continue = has_steps and not self._is_animation_complete()

        new_state = "normal" if can_continue else "disabled"
        self.btn_step.config(state=new_state)
        self.btn_play.config(state=new_state)
        
        pause_state = "normal" if self._is_playing else "disabled"
        self.btn_pause.config(state=pause_state)


def run_app():
    root = tk.Tk()
    PlateCheckerApp(root)
    root.mainloop()
