from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar, QStyle
from PyQt6.QtGui import QIcon
from ui.canvas_panel import CanvasPanel
from ui.control_panel import ControlPanel
from core.deque_ds import DequeDS


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deque")
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.setMinimumSize(1100, 650)
        self.deque = DequeDS()
        self._build_ui()
        self._connect()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.canvas   = CanvasPanel(self.deque)
        self.controls = ControlPanel(self.deque)

        layout.addWidget(self.canvas,   stretch=3)
        layout.addWidget(self.controls, stretch=1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._refresh_status()

    def _connect(self):
        self.controls.mode_changed.connect(self._on_mode)
        self.controls.deque_updated.connect(self._on_update)
        self.controls.reset_canvas.connect(self._on_reset)
        self.controls.peek_front_sig.connect(lambda: self.canvas.peek_highlight("front"))
        self.controls.peek_rear_sig.connect(lambda: self.canvas.peek_highlight("rear"))
        self.controls.peek_release_sig.connect(self.canvas.peek_release)

    def _on_mode(self, mode):
        self.deque.set_mode(mode)
        self.canvas.set_mode(mode)
        self._refresh_status()

    def _on_update(self):
        self.canvas.refresh()
        self._refresh_status()

    def _on_reset(self):
        self.canvas.hard_reset()
        self._refresh_status()

    def _refresh_status(self):
        mode  = self.deque.get_mode().capitalize()
        size  = self.deque.size()
        front = self.deque.peek_front()
        rear  = self.deque.peek_rear()
        self.status.showMessage(
            f"Mode: {mode}  |  Size: {size}  |  Front: {front}  |  Rear: {rear}"
        )