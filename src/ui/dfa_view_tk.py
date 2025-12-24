"""DFA durumlarını ve geçişlerini görselleştiren canvas bileşeni."""
import tkinter as tk
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Set

from dfa.tr_plate_dfa import State, is_accepting

# Görselleştirme sabitleri
DEFAULT_CANVAS_WIDTH = 1200
DEFAULT_CANVAS_HEIGHT = 320
DEFAULT_MARGIN = 26
DEFAULT_SHIFT_RIGHT = 40
DEFAULT_SCALE_FACTOR = 0.90
DEFAULT_STATE_RADIUS = 22.0
MIN_STATE_RADIUS = 11.0
ACCEPT_STATE_INNER_OFFSET = 5
STATE_FONT_SIZE_BASE = 9
STATE_FONT_SIZE_RATIO = 22.0
LABEL_Y_OFFSET = -10
START_ARROW_LENGTH_FACTOR = 3.0
START_ARROW_OFFSET = 1.05
EDGE_WIDTH_NORMAL = 2
EDGE_WIDTH_TRAVERSED = 3
STATE_OUTLINE_WIDTH_NORMAL = 2
STATE_OUTLINE_WIDTH_ACTIVE = 5


@dataclass(frozen=True)
class Edge:
    """DFA'da iki durum arasındaki geçişi temsil eder."""
    src: State
    dst: State
    label: str


class DFACanvasView:
    """DFA durumlarını ve geçişlerini canvas üzerinde görselleştirir."""

    def __init__(
        self,
        parent: tk.Widget,
        width: int = DEFAULT_CANVAS_WIDTH,
        height: int = DEFAULT_CANVAS_HEIGHT,
        margin: int = DEFAULT_MARGIN,
        shift_right: int = DEFAULT_SHIFT_RIGHT,
        scale_factor: float = DEFAULT_SCALE_FACTOR
    ) -> None:
        """DFA canvas görünümünü başlatır.
        
        Args:
            parent: Üst widget.
            width: Canvas genişliği.
            height: Canvas yüksekliği.
            margin: Kenar boşluğu.
            shift_right: Sağa kayma miktarı.
            scale_factor: Ölçekleme faktörü.
        """
        self._canvas_width = width
        self._canvas_height = height
        self._margin = margin
        self._shift_right = shift_right
        self._scale_factor = scale_factor

        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg="white",
            highlightthickness=1
        )
        self.canvas.pack(pady=8)

        # Durum koordinatları (temel layout)
        self._base_state_positions: Dict[State, Tuple[float, float]] = {
            State.Q0: (60, 160),
            State.Q1_0: (170, 80),
            State.Q1_1_7: (170, 160),
            State.Q1_8: (170, 240),
            State.Q2: (300, 160),
            State.Q3: (390, 160),
            State.Q4: (500, 160),
            State.Q5: (580, 80),
            State.Q6: (780, 80),
            State.Q7: (670, 160),
            State.Q8: (780, 160),
            State.Q9: (870, 160),
            State.Q10: (960, 160),
            State.Q11: (915, 240),
            State.DEAD: (520, 240),
        }

        # DFA geçiş okları (DEAD durumuna geçişler dahil değil)
        self._edges: List[Edge] = self._create_edges()

        # Çizim parametreleri
        self._base_state_radius = DEFAULT_STATE_RADIUS
        self._current_state_radius = DEFAULT_STATE_RADIUS
        self._scaled_state_positions: Dict[State, Tuple[float, float]] = {}

        # Animasyon durumu
        self._active_state: Optional[State] = None
        self._traversed_edges: Set[Tuple[State, State]] = set()

        self._recompute_layout()
        self.draw()

    def _create_edges(self) -> List[Edge]:
        """DFA geçiş oklarını oluşturur."""
        return [
            # Başlangıçtan il kodu ilk rakamına
            Edge(State.Q0, State.Q1_0, "0"),
            Edge(State.Q0, State.Q1_1_7, "1-7"),
            Edge(State.Q0, State.Q1_8, "8"),
            # İl kodu ikinci rakamı
            Edge(State.Q1_0, State.Q2, "1-9"),
            Edge(State.Q1_1_7, State.Q2, "0-9"),
            Edge(State.Q1_8, State.Q2, "0-1"),
            # Boşluk ve harf geçişleri
            Edge(State.Q2, State.Q3, "Boşluk"),
            Edge(State.Q3, State.Q4, "A-Z"),
            Edge(State.Q4, State.Q5, "A-Z"),
            Edge(State.Q5, State.Q6, "A-Z"),
            # Harflerden boşluğa
            Edge(State.Q4, State.Q7, "Boşluk"),
            Edge(State.Q5, State.Q7, "Boşluk"),
            Edge(State.Q6, State.Q7, "Boşluk"),
            # Son rakamlar
            Edge(State.Q7, State.Q8, "0-9"),
            Edge(State.Q8, State.Q9, "0-9"),
            Edge(State.Q9, State.Q10, "0-9"),
            Edge(State.Q10, State.Q11, "0-9"),
        ]

    # ---------- Layout Hesaplama ----------
    def _recompute_layout(self) -> None:
        """Durum pozisyonlarını canvas boyutuna göre yeniden hesaplar."""
        layout_bounds = self._calculate_layout_bounds()
        scale = self._calculate_scale_factor(layout_bounds)
        
        self._current_state_radius = max(
            MIN_STATE_RADIUS,
            self._base_state_radius * scale
        )
        self._scaled_state_positions = self._scale_positions(
            layout_bounds,
            scale
        )

    def _calculate_layout_bounds(self) -> Tuple[float, float, float, float]:
        """Temel layout'un sınırlarını hesaplar.
        
        Returns:
            (min_x, max_x, min_y, max_y) tuple'ı.
        """
        x_coords = [pos[0] for pos in self._base_state_positions.values()]
        y_coords = [pos[1] for pos in self._base_state_positions.values()]
        return min(x_coords), max(x_coords), min(y_coords), max(y_coords)

    def _calculate_scale_factor(self, bounds: Tuple[float, float, float, float]) -> float:
        """Canvas boyutuna göre ölçekleme faktörünü hesaplar.
        
        Args:
            bounds: Layout sınırları (min_x, max_x, min_y, max_y).
            
        Returns:
            Ölçekleme faktörü.
        """
        min_x, max_x, min_y, max_y = bounds
        layout_width = max_x - min_x
        layout_height = max_y - min_y

        available_width = self._canvas_width - 2 * self._margin - self._shift_right
        available_height = self._canvas_height - 2 * self._margin

        return min(
            available_width / layout_width,
            available_height / layout_height
        ) * self._scale_factor

    def _scale_positions(
        self,
        bounds: Tuple[float, float, float, float],
        scale: float
    ) -> Dict[State, Tuple[float, float]]:
        """Durum pozisyonlarını ölçekler.
        
        Args:
            bounds: Layout sınırları.
            scale: Ölçekleme faktörü.
            
        Returns:
            Ölçeklenmiş pozisyonlar.
        """
        min_x, _, min_y, _ = bounds
        return {
            state: (
                (x - min_x) * scale + self._margin + self._shift_right,
                (y - min_y) * scale + self._margin
            )
            for state, (x, y) in self._base_state_positions.items()
        }

    # ---------- Public API ----------
    def reset_path(self) -> None:
        """Geçilen yolu ve aktif durumu sıfırlar."""
        self._traversed_edges.clear()
        self._active_state = None
        self.draw()

    def step(self, from_state: State, to_state: State) -> None:
        """Bir DFA adımını görselleştirir.
        
        Args:
            from_state: Başlangıç durumu.
            to_state: Hedef durum.
        """
        self._traversed_edges.add((from_state, to_state))
        self._active_state = to_state
        self.draw()

    # ---------- Çizim ----------
    def draw(self) -> None:
        """DFA'yı canvas üzerinde çizer."""
        self.canvas.delete("all")
        self._draw_all_edges()
        self._draw_all_states()
        self._draw_start_arrow()
        self._draw_title()

    def _draw_all_edges(self) -> None:
        """Tüm DFA geçişlerini çizer."""
        for edge in self._edges:
            self._draw_edge(edge)

    def _draw_all_states(self) -> None:
        """Tüm DFA durumlarını çizer."""
        for state, (x, y) in self._scaled_state_positions.items():
            self._draw_state(state, x, y)

    def _draw_title(self) -> None:
        """Başlığı çizer."""
        self.canvas.create_text(
            10, 10,
            anchor="nw",
            text="DFA Görselleştirmesi",
            font=("Arial", 8, "bold")
        )

    def _draw_start_arrow(self) -> None:
        """Başlangıç durumuna giriş okunu çizer."""
        start_x, start_y = self._scaled_state_positions[State.Q0]
        radius = self._current_state_radius
        
        arrow_start_x = start_x - START_ARROW_LENGTH_FACTOR * radius
        arrow_end_x = start_x - START_ARROW_OFFSET * radius
        
        self.canvas.create_line(
            arrow_start_x, start_y,
            arrow_end_x, start_y,
            arrow=tk.LAST,
            width=EDGE_WIDTH_NORMAL,
            fill="gray60"
        )

    def _draw_state(self, state: State, x: float, y: float) -> None:
        """Bir DFA durumunu çizer.
        
        Args:
            state: Çizilecek durum.
            x: X koordinatı.
            y: Y koordinatı.
        """
        radius = self._current_state_radius
        is_active = (state == self._active_state)
        is_accepting_state = is_accepting(state)
        is_dead = (state == State.DEAD)

        outline_color = self._get_state_outline_color(is_dead, is_active)
        outline_width = (
            STATE_OUTLINE_WIDTH_ACTIVE if is_active
            else STATE_OUTLINE_WIDTH_NORMAL
        )

        # Dış çember
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            outline=outline_color,
            width=outline_width
        )

        # Kabul durumu veya ölü durum için iç çember
        if is_accepting_state or is_dead:
            self._draw_inner_circle(
                x, y, radius,
                "green" if is_accepting_state else "red"
            )

        # Durum etiketi
        self._draw_state_label(state, x, y, radius)

    def _get_state_outline_color(self, is_dead: bool, is_active: bool) -> str:
        """Durum çember rengini belirler."""
        if is_dead:
            return "red"
        return "blue" if is_active else "gray40"

    def _draw_inner_circle(self, x: float, y: float, radius: float, color: str) -> None:
        """Kabul/ölü durumlar için iç çemberi çizer."""
        inner_radius = radius - ACCEPT_STATE_INNER_OFFSET
        self.canvas.create_oval(
            x - inner_radius, y - inner_radius,
            x + inner_radius, y + inner_radius,
            outline=color,
            width=EDGE_WIDTH_NORMAL
        )

    def _draw_state_label(self, state: State, x: float, y: float, radius: float) -> None:
        """Durum etiketini çizer."""
        font_size = max(
            7,
            int(STATE_FONT_SIZE_BASE * (radius / STATE_FONT_SIZE_RATIO))
        )
        self.canvas.create_text(
            x, y,
            text=state.value,
            font=("Arial", font_size, "bold")
        )

    def _draw_edge(self, edge: Edge) -> None:
        """Bir DFA geçiş okunu çizer.
        
        Args:
            edge: Çizilecek geçiş.
        """
        src_x, src_y = self._scaled_state_positions[edge.src]
        dst_x, dst_y = self._scaled_state_positions[edge.dst]

        # Ok uçlarını hesapla
        arrow_coords = self._calculate_arrow_coordinates(
            src_x, src_y, dst_x, dst_y
        )
        if arrow_coords is None:
            return

        start_x, start_y, end_x, end_y = arrow_coords
        is_traversed = (edge.src, edge.dst) in self._traversed_edges

        # Ok rengini ve kalınlığını belirle
        color = "blue" if is_traversed else "gray60"
        width = EDGE_WIDTH_TRAVERSED if is_traversed else EDGE_WIDTH_NORMAL

        # Oku çiz
        self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            arrow=tk.LAST,
            width=width,
            fill=color
        )

        # Etiket çiz
        self._draw_edge_label(start_x, start_y, end_x, end_y, edge.label, color)

    def _calculate_arrow_coordinates(
        self,
        src_x: float,
        src_y: float,
        dst_x: float,
        dst_y: float
    ) -> Optional[Tuple[float, float, float, float]]:
        """Ok koordinatlarını hesaplar.
        
        Args:
            src_x, src_y: Başlangıç koordinatları.
            dst_x, dst_y: Hedef koordinatları.
            
        Returns:
            (start_x, start_y, end_x, end_y) veya None.
        """
        radius = self._current_state_radius
        delta_x = dst_x - src_x
        delta_y = dst_y - src_y
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5

        if distance == 0:
            return None

        # Birim vektör
        unit_x = delta_x / distance
        unit_y = delta_y / distance

        # Ok uçlarını durum çemberinin dışında başlat/bitir
        start_x = src_x + unit_x * radius
        start_y = src_y + unit_y * radius
        end_x = dst_x - unit_x * radius
        end_y = dst_y - unit_y * radius

        return start_x, start_y, end_x, end_y

    def _draw_edge_label(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        label: str,
        color: str
    ) -> None:
        """Geçiş etiketini çizer.
        
        Args:
            start_x, start_y: Başlangıç koordinatları.
            end_x, end_y: Bitiş koordinatları.
            label: Etiket metni.
            color: Etiket rengi.
        """
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        self.canvas.create_text(
            mid_x, mid_y + LABEL_Y_OFFSET,
            text=label,
            font=("Arial", 8),
            fill=color
        )
