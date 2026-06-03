from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFrame, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator


class ControlPanel(QWidget):

    mode_changed   = pyqtSignal(str)
    deque_updated  = pyqtSignal()
    reset_canvas   = pyqtSignal()
    peek_front_sig = pyqtSignal()
    peek_rear_sig  = pyqtSignal()
    peek_release_sig = pyqtSignal()

    def __init__(self, deque, parent=None):
        super().__init__(parent)
        self.deque = deque
        self.setFixedWidth(235)
        self._ops  = 0
        self._build_ui()

    def _build_ui(self):
        L = QVBoxLayout(self)
        L.setContentsMargins(12, 12, 12, 12)
        L.setSpacing(10)

        L.addWidget(self._section("MODE"))
        L.addLayout(self._mode_row())
        L.addWidget(self._div())

        L.addWidget(self._section("INPUT VALUE"))
        self.inp = QLineEdit(placeholderText="Enter integer...")
        self.inp.setValidator(QIntValidator(-9999, 9999))
        self.inp.setFont(QFont("Consolas", 10))
        self.inp.returnPressed.connect(self._on_enter)
        L.addWidget(self.inp)

        L.addWidget(self._section("ADD"))
        self.b_af = QPushButton("◄  Add Front")
        self.b_ar = QPushButton("Add Rear  ►")
        L.addLayout(self._row(self.b_af, self.b_ar))

        L.addWidget(self._section("REMOVE"))
        self.b_rf = QPushButton("◄  Rem Front")
        self.b_rr = QPushButton("Rem Rear  ►")
        L.addLayout(self._row(self.b_rf, self.b_rr))

        L.addWidget(self._section("PEEK"))
        self.b_pf = QPushButton("◄  Peek Front")
        self.b_pr = QPushButton("Peek Rear  ►")
        self.b_pf.setObjectName("peekFront")
        self.b_pr.setObjectName("peekRear")
        L.addLayout(self._row(self.b_pf, self.b_pr))

        L.addWidget(self._div())
        self.b_reset = QPushButton("⟳   Reset Canvas")
        L.addWidget(self.b_reset)

        L.addWidget(self._div())
        L.addWidget(self._section("STATISTICS"))
        self.lbl_ops   = self._stat("Operations", "0")
        self.lbl_size  = self._stat("Size",       "0")
        self.lbl_front = self._stat("Front",      "—")
        self.lbl_rear  = self._stat("Rear",       "—")
        for w in (self.lbl_ops, self.lbl_size, self.lbl_front, self.lbl_rear):
            L.addWidget(w)

        L.addStretch()
        self._wire()
        self._apply_mode("deque")

    def _mode_row(self):
        self.b_deque = QPushButton("Deque")
        self.b_stack = QPushButton("Stack")
        self.b_queue = QPushButton("Queue")
        grp = QButtonGroup(self)
        for b in (self.b_deque, self.b_stack, self.b_queue):
            b.setCheckable(True)
            b.setFont(QFont("Consolas", 9))
            grp.addButton(b)
        grp.setExclusive(True)
        self.b_deque.setChecked(True)
        return self._row(self.b_deque, self.b_stack, self.b_queue)

    def _wire(self):
        self.b_af.clicked.connect(self._add_front)
        self.b_ar.clicked.connect(self._add_rear)
        self.b_rf.clicked.connect(self._rem_front)
        self.b_rr.clicked.connect(self._rem_rear)
        self.b_pf.pressed.connect(self._peek_front)
        self.b_pf.released.connect(self._peek_front_release)
        self.b_pr.pressed.connect(self._peek_rear)
        self.b_pr.released.connect(self._peek_rear_release)
        self.b_reset.clicked.connect(self._confirm_reset)
        self.b_deque.clicked.connect(lambda: self._set_mode("deque"))
        self.b_stack.clicked.connect(lambda: self._set_mode("stack"))
        self.b_queue.clicked.connect(lambda: self._set_mode("queue"))

    def _set_mode(self, mode):
        self.deque.set_mode(mode)
        self._apply_mode(mode)
        self.mode_changed.emit(mode)
        self.deque_updated.emit()

    def _apply_mode(self, mode):
        self.b_af.setEnabled(mode != "queue")
        self.b_ar.setEnabled(mode != "stack")
        self.b_rf.setEnabled(True)
        self.b_rr.setEnabled(mode == "deque")
        self.b_pf.setEnabled(True)
        self.b_pr.setEnabled(mode == "deque")

    def _confirm_reset(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Reset Canvas")
        msg.setText("Clear all nodes and reset to default?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #070B14; }
            QLabel { color: #CCD6F0; font-family: Consolas; font-size: 12px; }
            QPushButton {
                background-color: #111827; color: #8AAAD0;
                border: 1px solid #1E3A5F; border-radius: 6px;
                padding: 6px 20px; font-family: Consolas;
            }
            QPushButton:hover {
                background-color: #1A2A4A; border-color: #3D8EF0; color: #EEF4FF;
            }
        """)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._do_reset()

    def _do_reset(self):
        self.deque.clear()
        self.inp.clear()
        self._ops = 0
        self.b_deque.setChecked(True)
        self._apply_mode("deque")
        self._update_stats()
        self.reset_canvas.emit()
        self.mode_changed.emit("deque")

    def _on_enter(self):
        self._add_rear() if self.deque.get_mode() == "queue" else self._add_front()

    def _val(self):
        t = self.inp.text().strip()
        return int(t) if t else None

    def _add_front(self):
        v = self._val()
        if v is None: return
        self.deque.add_front(v); self.inp.clear()
        self._ops += 1; self._update_stats(); self.deque_updated.emit()

    def _add_rear(self):
        v = self._val()
        if v is None: return
        self.deque.add_rear(v); self.inp.clear()
        self._ops += 1; self._update_stats(); self.deque_updated.emit()

    def _rem_front(self):
        self.deque.remove_front()
        self._ops += 1; self._update_stats(); self.deque_updated.emit()

    def _rem_rear(self):
        self.deque.remove_rear()
        self._ops += 1; self._update_stats(); self.deque_updated.emit()

    def _peek_front(self):
        if self.deque.peek_front() is None: return
        self.peek_front_sig.emit()

    def _peek_front_release(self):
        self.peek_release_sig.emit()

    def _peek_rear(self):
        if self.deque.peek_rear() is None: return
        self.peek_rear_sig.emit()

    def _peek_rear_release(self):
        self.peek_release_sig.emit()

    def _update_stats(self):
        front = self.deque.peek_front()
        rear  = self.deque.peek_rear()
        self._set_stat(self.lbl_ops,   "Operations", str(self._ops))
        self._set_stat(self.lbl_size,  "Size",       str(self.deque.size()))
        self._set_stat(self.lbl_front, "Front",      str(front) if front is not None else "—")
        self._set_stat(self.lbl_rear,  "Rear",       str(rear)  if rear  is not None else "—")

    def _row(self, *widgets):
        h = QHBoxLayout(); h.setSpacing(6)
        for w in widgets: h.addWidget(w)
        return h

    def _section(self, text):
        l = QLabel(text)
        l.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        l.setStyleSheet("color: #3D8EF0; letter-spacing: 2px; padding-top: 4px;")
        return l

    def _div(self):
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("color: #152035; margin: 2px 0;")
        return f

    def _stat(self, key, val):
        l = QLabel(f"{key:<12}: {val}")
        l.setFont(QFont("Consolas", 9))
        l.setStyleSheet("color: #4A6A8A;")
        return l

    def _set_stat(self, label, key, val):
        label.setText(f"{key:<12}: {val}")