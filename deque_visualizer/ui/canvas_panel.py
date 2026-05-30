from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPointF, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QPainterPath, QPolygonF, QLinearGradient
)
from core.deque_ds import DequeDS

NW, NH, NS, NR = 150, 90, 45, 13

C_BG_TOP   = QColor("#030710")
C_BG_BOT   = QColor("#020508")
C_GRID     = QColor(60, 120, 255, 10)
C_DEQUE    = QColor("#5BB0FF")
C_STACK    = QColor("#FFB347")
C_QUEUE    = QColor("#47FFB8")
C_DEQUEUE  = QColor("#FF6B6B")
C_ENQUEUE  = QColor("#47FFB8")
C_MUTED    = QColor("#1E3A5F")
C_HEAD     = QColor("#FFB347")
C_TAIL     = QColor("#5BB0FF")
C_TOP_LBL  = QColor("#FFB347")
C_BOT_LBL  = QColor("#5BB0FF")

MODE_COLOR = {"deque": C_DEQUE, "stack": C_STACK, "queue": C_QUEUE}

PH_BOX, PH_TEXT, PH_ARROW, PH_IDLE = 0, 1, 2, 3


class AnimNode:
    def __init__(self, value, spawning=True):
        self.value       = value
        self.alpha       = 0   if spawning else 255
        self.scale       = 0.4 if spawning else 1.0
        self.offset      = 0
        self.progress    = 0.0
        self.phase       = PH_BOX if spawning else PH_IDLE
        self.dying       = False
        self.die_prog    = 0.0
        self.text_alpha  = 0   if spawning else 255
        self.arrow_alpha = 0   if spawning else 255


class CanvasPanel(QWidget):

    FPS = 16

    def __init__(self, deque: DequeDS, parent=None):
        super().__init__(parent)
        self.deque       = deque
        self.mode        = "deque"
        self.nodes       = []
        self.scroll_x    = 0
        self.scroll_y    = 0
        self.highlighted = None
        self._timer      = QTimer()
        self._timer.setInterval(self.FPS)
        self._timer.timeout.connect(self._tick)
        self.setMinimumSize(600, 400)

    def refresh(self):
        self._sync()
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def set_mode(self, m):
        self.mode     = m
        self.scroll_x = 0
        self.scroll_y = 0
        self.update()

    def hard_reset(self):
        self.nodes       = []
        self.scroll_x    = 0
        self.scroll_y    = 0
        self.highlighted = None
        self._timer.stop()
        self.update()

    def peek_highlight(self, end):
        live = [n for n in self.nodes if not n.dying]
        if not live: return
        self.highlighted = live[0] if end == "front" else live[-1]
        self._jump_to(end)
        self.update()

    def peek_release(self):
        self.highlighted = None
        self.scroll_x    = 0
        self.scroll_y    = 0
        self.update()

    def _jump_to(self, end):
        live = [n for n in self.nodes if not n.dying]
        if not live: return
        n       = len(live)
        total_w = n * NW + (n - 1) * NS
        total_h = n * NH + (n - 1) * NS

        if self.mode == "stack":
            idx = live.index(live[0] if end == "front" else live[-1])
            node_center = idx * (NH + NS) + NH // 2
            canvas_center = self.height() // 2
            self.scroll_y = canvas_center - node_center
        else:
            idx = live.index(live[0] if end == "front" else live[-1])
            node_center = idx * (NW + NS) + NW // 2
            canvas_center = self.width() // 2
            self.scroll_x = canvas_center - node_center - (self.width() - total_w) // 2

    def _sync(self):
        current  = self.deque.to_list()
        live     = [n for n in self.nodes if not n.dying]
        old_vals = [n.value for n in live]

        # Don't add a new node if one is still animating in
        still_spawning = any(n.phase != PH_IDLE and not n.dying for n in self.nodes)
        if still_spawning:
            return

        if len(current) > len(old_vals):
            if len(old_vals) == 0:
                nd = AnimNode(current[-1], spawning=True)
                nd.offset = 60
                self.nodes.append(nd)
            elif current[0] != old_vals[0]:
                nd = AnimNode(current[0], spawning=True)
                nd.offset = -60
                self.nodes.insert(0, nd)
            else:
                nd = AnimNode(current[-1], spawning=True)
                nd.offset = 60
                self.nodes.append(nd)
        elif len(current) < len(old_vals):
            if not current or (old_vals and old_vals[0] != current[0]):
                if live: live[0].dying = True
            else:
                if live: live[-1].dying = True

    def _tick(self):
        going = False

        for nd in self.nodes:
            if nd.dying:
                nd.die_prog    = min(1.0, nd.die_prog + 0.04)
                t              = nd.die_prog ** 2
                nd.alpha       = int(255 * (1 - t))
                nd.text_alpha  = nd.alpha
                nd.arrow_alpha = nd.alpha
                nd.scale       = 1.0 - 0.5 * t
                going          = True
                continue

            if nd.phase == PH_BOX:
                nd.progress = min(1.0, nd.progress + 0.025)
                t           = 1 - (1 - nd.progress) ** 3
                nd.alpha    = int(255 * t)
                nd.scale    = 0.4 + 0.6 * t
                nd.offset   = int(nd.offset * (1 - t))
                if nd.progress >= 1.0:
                    nd.alpha = 255; nd.scale = 1.0; nd.offset = 0
                    nd.phase = PH_TEXT; nd.progress = 0.0
                going = True

            elif nd.phase == PH_TEXT:
                nd.progress   = min(1.0, nd.progress + 0.03)
                nd.text_alpha = int(255 * (1 - (1 - nd.progress) ** 2))
                if nd.progress >= 1.0:
                    nd.text_alpha = 255
                    nd.phase = PH_ARROW; nd.progress = 0.0
                going = True

            elif nd.phase == PH_ARROW:
                nd.progress    = min(1.0, nd.progress + 0.025)
                nd.arrow_alpha = int(255 * (1 - (1 - nd.progress) ** 2))
                if nd.progress >= 1.0:
                    nd.arrow_alpha = 255; nd.phase = PH_IDLE
                    # Check if deque has pending nodes not yet shown
                    self._sync()
                going = True

        self.nodes = [n for n in self.nodes
                      if not (n.dying and n.die_prog >= 1.0)]
        if not going:
            self._timer.stop()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        bg = QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0.0, C_BG_TOP)
        bg.setColorAt(1.0, C_BG_BOT)
        p.fillRect(self.rect(), bg)

        p.setPen(QPen(C_GRID, 1))
        for x in range(0, self.width(), 32):
            for y in range(0, self.height(), 32):
                p.drawPoint(x, y)

        nds = self.nodes
        if not nds and self.deque.is_empty():
            p.setPen(QPen(C_MUTED))
            p.setFont(QFont("Consolas", 13))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "Deque is empty.\nUse the controls to add elements.")
        elif self.mode == "stack":
            self._paint_stack(p, nds)
        elif self.mode == "queue":
            self._paint_queue(p, nds)
        else:
            self._paint_deque(p, nds)

        self._paint_badge(p)

    def _paint_deque(self, p, nds):
        n       = len(nds)
        total_w = n * NW + (n - 1) * NS
        max_s   = max(0, (total_w - self.width() + 60) // 2)
        self.scroll_x = max(-max_s, min(max_s, self.scroll_x))
        sx = (self.width() - total_w) // 2 + self.scroll_x
        y  = (self.height() - NH) // 2

        if total_w > self.width() - 60:
            self._paint_scroll_hint(p, "h")

        for i, nd in enumerate(nds):
            x  = sx + i * (NW + NS) + nd.offset
            self._box(p, x, y, C_DEQUE, nd.alpha, nd.scale, nd)
            self._txt(p, x, y, str(nd.value), nd.text_alpha, nd.scale)
            if i < n - 1:
                nx = nds[i + 1]
                x2 = sx + (i + 1) * (NW + NS) + nx.offset
                self._arrow_h_bidi(p, x + NW, y, x2, C_DEQUE,
                                   min(nd.arrow_alpha, nx.arrow_alpha))

        live = [nd for nd in nds if not nd.dying]
        if live:
            hx = sx + nds.index(live[0])  * (NW + NS)
            tx = sx + nds.index(live[-1]) * (NW + NS)
            self._lbl(p, hx, y, "HEAD", above=True,  color=C_HEAD,
                      alpha=live[0].arrow_alpha)
            self._lbl(p, tx, y, "TAIL", above=False, color=C_TAIL,
                      alpha=live[-1].arrow_alpha)

    def _paint_stack(self, p, nds):
        n       = len(nds)
        total_h = n * NH + (n - 1) * NS
        max_s   = max(0, (total_h - self.height() + 60) // 2)
        self.scroll_y = max(-max_s, min(max_s, self.scroll_y))
        sy = (self.height() - total_h) // 2 + self.scroll_y
        x  = (self.width() - NW) // 2

        if total_h > self.height() - 60:
            self._paint_scroll_hint(p, "v")

        for i, nd in enumerate(nds):
            y  = sy + i * (NH + NS) + nd.offset
            self._box(p, x, y, C_STACK, nd.alpha, nd.scale, nd)
            self._txt(p, x, y, str(nd.value), nd.text_alpha, nd.scale)
            if i < n - 1:
                nx = nds[i + 1]
                y2 = sy + (i + 1) * (NH + NS) + nx.offset
                self._arrow_v_one(p, x, y + NH, y2, C_STACK,
                                  min(nd.arrow_alpha, nx.alpha))

        live = [nd for nd in nds if not nd.dying]
        if live:
            sy0 = sy + nds.index(live[0])  * (NH + NS)
            sy1 = sy + nds.index(live[-1]) * (NH + NS)
            self._lbl(p, x, sy0, "TOP",    above=True,  color=C_TOP_LBL,
                      alpha=live[0].arrow_alpha)
            self._lbl(p, x, sy1, "BOTTOM", above=False, color=C_BOT_LBL,
                      alpha=live[-1].arrow_alpha)

    def _paint_queue(self, p, nds):
        n       = len(nds)
        total_w = n * NW + (n - 1) * NS
        max_s   = max(0, (total_w - self.width() + 60) // 2)
        self.scroll_x = max(-max_s, min(max_s, self.scroll_x))
        sx = (self.width() - total_w) // 2 + self.scroll_x
        y  = (self.height() - NH) // 2

        if total_w > self.width() - 60:
            self._paint_scroll_hint(p, "h")

        live = [nd for nd in nds if not nd.dying]

        for i, nd in enumerate(nds):
            x = sx + i * (NW + NS) + nd.offset
            if live and nd == live[0]:    c = C_DEQUEUE
            elif live and nd == live[-1]: c = C_ENQUEUE
            else:                         c = C_QUEUE
            self._box(p, x, y, c, nd.alpha, nd.scale, nd)
            self._txt(p, x, y, str(nd.value), nd.text_alpha, nd.scale)
            if i < n - 1:
                nx = nds[i + 1]
                x2 = sx + (i + 1) * (NW + NS) + nx.offset
                self._arrow_h_one(p, x + NW, y, x2, C_QUEUE,
                                  min(nd.arrow_alpha, nx.arrow_alpha))

        if live:
            hx = sx + nds.index(live[0])  * (NW + NS)
            tx = sx + nds.index(live[-1]) * (NW + NS)
            self._lbl(p, hx, y, "DEQUEUE", above=True,  color=C_DEQUEUE,
                      alpha=live[0].arrow_alpha)
            self._lbl(p, tx, y, "ENQUEUE", above=False, color=C_ENQUEUE,
                      alpha=live[-1].arrow_alpha)

    def _box(self, p, x, y, color, alpha=255, scale=1.0, node=None):
        cx = x + NW / 2; cy = y + NH / 2
        sw = NW * scale;  sh = NH * scale
        rx = cx - sw / 2; ry = cy - sh / 2

        for spread, a in [(14, 12), (8, 22), (4, 40)]:
            gc = QColor(color); gc.setAlpha(int(a * alpha / 255))
            gp = QPainterPath()
            gp.addRoundedRect(rx - spread, ry - spread,
                              sw + spread * 2, sh + spread * 2,
                              float(NR + spread / 2), float(NR + spread / 2))
            p.fillPath(gp, QBrush(gc))

        path = QPainterPath()
        path.addRoundedRect(rx, ry, sw, sh, float(NR), float(NR))

        glass_bg = QColor(8, 20, 50, int(160 * alpha / 255))
        p.fillPath(path, QBrush(glass_bg))

        grad = QLinearGradient(rx, ry, rx, ry + sh)
        g1 = QColor(255, 255, 255, int(22 * alpha / 255))
        g2 = QColor(255, 255, 255, int(4  * alpha / 255))
        g3 = QColor(color.red(), color.green(), color.blue(),
                    int(15 * alpha / 255))
        grad.setColorAt(0.0, g1)
        grad.setColorAt(0.5, g2)
        grad.setColorAt(1.0, g3)
        p.fillPath(path, QBrush(grad))

        sheen = QLinearGradient(rx, ry, rx, ry + sh * 0.35)
        sheen.setColorAt(0.0, QColor(255, 255, 255, int(35 * alpha / 255)))
        sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.fillPath(path, QBrush(sheen))

        is_highlighted = (node is not None and node is self.highlighted
                          and self.highlighted in self.nodes)
        if is_highlighted:
            hc = QColor(255, 255, 255, 70)
            hp = QPainterPath()
            hp.addRoundedRect(rx - 4, ry - 4, sw + 8, sh + 8,
                              float(NR + 3), float(NR + 3))
            p.fillPath(hp, QBrush(hc))
            p.setPen(QPen(QColor(255, 255, 255, 180), 2.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(hp)

        bc = QColor(color); bc.setAlpha(int(200 * alpha / 255))
        p.setPen(QPen(bc, 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        inner = QPainterPath()
        inner.addRoundedRect(rx + 1, ry + 1, sw - 2, sh - 2,
                             float(NR - 1), float(NR - 1))
        p.setPen(QPen(QColor(255, 255, 255, int(12 * alpha / 255)), 0.8))
        p.drawPath(inner)

        hl = QColor(255, 255, 255, int(50 * alpha / 255))
        p.setPen(QPen(hl, 1.0))
        p.drawLine(QPointF(rx + NR, ry + 1.0),
                   QPointF(rx + sw - NR, ry + 1.0))

    def _txt(self, p, x, y, text, alpha=255, scale=1.0):
        cx = x + NW / 2; cy = y + NH / 2
        sw = NW * scale;  sh = NH * scale
        rx = cx - sw / 2; ry = cy - sh / 2
        c  = QColor(255, 255, 255, alpha)
        p.setPen(QPen(c))
        p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        p.drawText(QRect(int(rx), int(ry), int(sw), int(sh)),
                   Qt.AlignmentFlag.AlignCenter, text)

    def _arrow_h_bidi(self, p, x1, y, x2, color, alpha=255):
        if alpha <= 0: return
        ty = y + NH // 3
        by = y + 2 * NH // 3
        c  = QColor(color); c.setAlpha(alpha)
        p.setPen(QPen(c, 1.5)); p.setBrush(QBrush(c))
        p.drawLine(x1, ty, x2, ty); self._arrowhead(p, x2, ty, "r", c)
        p.drawLine(x1, by, x2, by); self._arrowhead(p, x1, by, "l", c)

    def _arrow_h_one(self, p, x1, y, x2, color, alpha=255):
        if alpha <= 0: return
        my = y + NH // 2
        c  = QColor(color); c.setAlpha(alpha)
        p.setPen(QPen(c, 1.5)); p.setBrush(QBrush(c))
        p.drawLine(x1, my, x2, my)
        self._arrowhead(p, x2, my, "r", c)

    def _arrow_v_one(self, p, x, y1, y2, color, alpha=255):
        if alpha <= 0: return
        mx = x + NW // 2
        c  = QColor(color); c.setAlpha(alpha)
        p.setPen(QPen(c, 1.5)); p.setBrush(QBrush(c))
        p.drawLine(mx, y1, mx, y2)
        self._arrowhead(p, mx, y2, "d", c)

    def _arrowhead(self, p, x, y, d, color):
        s = 7.0
        pts = {
            "r": [QPointF(x, y), QPointF(x-s, y-s/2), QPointF(x-s, y+s/2)],
            "l": [QPointF(x, y), QPointF(x+s, y-s/2), QPointF(x+s, y+s/2)],
            "d": [QPointF(x, y), QPointF(x-s/2, y-s), QPointF(x+s/2, y-s)],
            "u": [QPointF(x, y), QPointF(x-s/2, y+s), QPointF(x+s/2, y+s)],
        }
        path = QPainterPath()
        path.addPolygon(QPolygonF(pts[d]))
        p.fillPath(path, QBrush(color))

    def _lbl(self, p, x, y, text, above, color, alpha=255):
        if alpha <= 0: return
        c   = QColor(color); c.setAlpha(alpha)
        mid = x + NW // 2

        if above:
            tri_tip = QPointF(mid, float(y - 5))
            tri_l   = QPointF(mid - 5.0, float(y - 13))
            tri_r   = QPointF(mid + 5.0, float(y - 13))
            text_y  = y - 28
        else:
            tri_tip = QPointF(mid, float(y + NH + 5))
            tri_l   = QPointF(mid - 5.0, float(y + NH + 13))
            tri_r   = QPointF(mid + 5.0, float(y + NH + 13))
            text_y  = y + NH + 15

        tp = QPainterPath()
        tp.addPolygon(QPolygonF([tri_tip, tri_l, tri_r]))
        p.fillPath(tp, QBrush(c))
        p.setPen(QPen(c))
        p.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        p.drawText(QRect(x, text_y, NW, 14),
                   Qt.AlignmentFlag.AlignCenter, text)

    def _paint_scroll_hint(self, p, direction):
        c = QColor(255, 255, 255, 35)
        p.setPen(QPen(c))
        p.setFont(QFont("Consolas", 8))
        text = "◄  scroll  ►" if direction == "h" else "▲  scroll  ▼"
        p.drawText(QRect(0, self.height() - 22, self.width(), 16),
                   Qt.AlignmentFlag.AlignCenter, text)

    def _paint_badge(self, p):
        p.save()
        color = MODE_COLOR.get(self.mode, C_MUTED)
        label = f" {self.mode.upper()} MODE "
        font  = QFont("Consolas", 9, QFont.Weight.Bold)
        p.setFont(font)
        fm  = p.fontMetrics()
        bw  = fm.horizontalAdvance(label) + 24
        bh  = 26
        bx  = float(self.width() - bw - 14)
        by_ = 14.0

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#030710")))
        p.drawRoundedRect(QRectF(bx - 1, by_ - 1, bw + 2, bh + 2), 7, 7)

        fill = QColor(color); fill.setAlpha(45)
        p.setBrush(QBrush(fill))
        p.drawRoundedRect(QRectF(bx, by_, bw, bh), 6, 6)

        p.setPen(QPen(color, 1.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(bx, by_, bw, bh), 6, 6)

        p.setPen(QPen(color))
        p.setFont(font)
        p.drawText(QRectF(bx, by_, bw, bh).toRect(),
                   Qt.AlignmentFlag.AlignCenter, label)
        p.restore()

    def wheelEvent(self, e):
        delta = e.angleDelta().y()
        if self.mode == "stack":
            self.scroll_y += delta // 3
        else:
            self.scroll_x += delta // 3
        self.update()