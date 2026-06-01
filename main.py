import sys
import math
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit,
                             QPushButton, QHBoxLayout, QVBoxLayout,
                             QDialog, QFrame, QLabel, QTextEdit,
                             QFileDialog, QAction, QMenu)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QTime, QPointF, QPoint
from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QPainterPath,
                         QBrush, QLinearGradient, QRadialGradient, QPolygon)

try:
    from pet import Pet
    from ollama_client import ask_ollama
except ImportError:
    class Pet:
        def idle_quip(self): return "mew? just keeping an eye on things."
        def pet_responses(self): return ["purrrrr...", "*happy tail wags*", "meow!"]
        def get_system_prompt(self): return "You are Jiji, a witty black cat. Never use markdown, bullet points, headers, or bold text. Plain conversational text only."
        def get_mood(self): return "normal"
    def ask_ollama(q, s): return "i'm thinking with my big pixel brain!"

C_INK       = QColor("#0e0e12")
C_BODY      = QColor("#1a1a22")
C_LAVENDER  = QColor("#9b87c0")
C_LAV_LIGHT = QColor("#ede8f8")
C_EYE       = QColor("#d4e87a")
C_EYE_GLOW  = QColor("#eeff88")

FRAME_IDLE = [
    "                                        ",
    "            kk       kk                 ",
    "           kppk     kppk                ",
    "           kppk     kppk                ",
    "          kpppk     kpppk               ",
    "          kpppk     kpppk               ",
    "          kpppk     kpppk               ",
    "          kpppk     kpppk               ",
    "          kpppkkkkkkkpppk               ",
    "         kkppkkdddddkkppkk              ",
    "         kddpdddddddddpddk              ",
    "        kdddddddddddddddddk             ",
    "        kddkyyyykdkyyyykddk             ",
    "    k k kdkkyyyyykkyyyyykkdk k k        ",
    "     k  kdyyyyyyykyyyyyyydk   k         ",
    "   kk   kdyykkyykyykkyyydk     kk       ",
    "        kdyykkyykyykkyyydk              ",
    "    k k kdyykkyypkyykkyyydk  k k        ",
    "     k  kdyyyyyyykyyyyyyydk   k         ",
    "        kddkyyyykdkyyyykddk             ",
    "         kddkkkkkkkkkkkddk              ",
    "          kdddddddddddddk               ",
    "           kkkkkkkkkkkkk                ",
    "             kdddddddk                  ",
    "             kdddddddk                  ",
    "            kdddddddddk                 ",
    "            kdddddddddk           kk    ",
    "           kdddddddddddk         kkk    ",
    "           kddkkdddddkdk        kkk     ",
    "           kddkkdddddkdk       kkk      ",
    "           kddkkdddddkdk      kkk       ",
    "           kddkkdddddkdk    kkk         ",
    "           kddkkdddddkdkkkkkkk          ",
    "           kddkkdddddkdkkkkkk           ",
    "           kddkkdddddkdk                ",
    "          kkddkkdddddkdkk               ",
    "          kkddkkddkkddkkk               ",
    "         kddkdkkddkkdkddk               ",
    "         kkkkkkkkkkkkkkkk               ",
    "                                        ",
]

FRAME_BLINK = FRAME_IDLE[:12] + [
    "        kdddddddddddddddddk             ",
    "    k k kddddddddddddddddddk k k        ",
    "     k  kddddddddddddddddddk   k        ",
    "   kk   kddkkkkkdddkkkkkddk     kk      ",
    "        kddddddddddddddddddk            ",
    "    k k kdddddddpddddddddddk  k k       ",
    "     k  kddddddddddddddddddk   k        ",
    "        kdddddddddddddddddk             ",
] + FRAME_IDLE[20:]

FRAME_HAPPY = FRAME_IDLE[:12] + [
    "        kdddddddddddddddddk             ",
    "    k k kddddddddddddddddddk k k        ",
    "     k  kddkkkdddddddkkkdddk   k        ",
    "   kk   kdkdddkdddddkdddkddk    kk      ",
    "        kddddddddddddddddddk            ",
    "    k k kdddddddpddddddddddk  k k       ",
    "     k  kddddddddddddddddddk   k        ",
    "        kdddddddddddddddddk             ",
] + FRAME_IDLE[20:]

FRAME_WALK_1 = FRAME_IDLE[:34] + [
    "           kkddkkdddddkdk               ",
    "          kkddkkddkkddkkk               ",
    "          kddkdkkkkkdkddk               ",
    "          kkkkkk   kkkkkk               ",
    "                                        ",
    "                                        ",
]

FRAME_WALK_2 = FRAME_IDLE[:34] + [
    "            kkddkkdddddkdk              ",
    "              kkddkkddkk                ",
    "              kdkkkkkkdk                ",
    "              kkkk  kkkk                ",
    "                                        ",
    "                                        ",
]

FRAME_SLEEP_1 = ["                                        "]*2 + FRAME_BLINK[:-2]
FRAME_SLEEP_2 = ["                                        "]*3 + FRAME_BLINK[:-3]


class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 200) # Increased height to prevent cutoff
        self._text = ""
        self._visible_chars = 0
        self._dots = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._type_next_char)
        self._dot_timer = QTimer()
        self._dot_timer.timeout.connect(self._animate_dots)

    def setText(self, text):
        self._text = text.lower() if text else ""
        self._visible_chars = 0
        self._timer.stop()
        self._dot_timer.stop()
        if text == "hmm...":
            self._dot_timer.start(400)
        elif text:
            self._timer.start(28)
        self.update()

    def _animate_dots(self):
        self._dots = (self._dots + 1) % 4
        self.update()

    def _type_next_char(self):
        if self._visible_chars < len(self._text):
            self._visible_chars += 1
            self.update()
        else:
            self._timer.stop()

    def paintEvent(self, event):
        if not self._text: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False) # True pixel art look

        bg = QColor(26, 22, 38, 245)
        border = QColor(139, 120, 167, 200)
        
        # Draw a custom "aesthetic" pixel oval/bubble shape
        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 2))
        
        # Main bubble body
        path = QPainterPath()
        path.addRoundedRect(20, 20, 260, 100, 40, 40)
        p.drawPath(path)

        # Three trailing thought bubbles
        p.drawEllipse(145, 125, 14, 14)
        p.drawEllipse(155, 145, 10, 10)
        p.drawEllipse(160, 160, 6, 6)

        # Text rendering with adjusted padding to avoid edges
        font = QFont("Segoe UI", 11)
        font.setLetterSpacing(QFont.PercentageSpacing, 102)
        p.setFont(font)
        p.setPen(QColor(220, 215, 235))
        
        # Centered text area inside the bubble
        p.drawText(40, 30, 220, 80, Qt.TextWordWrap | Qt.AlignCenter, 
                   "hmm..." if self._text == "hmm..." else self._text[:self._visible_chars])
        p.end()


class JijiSprite(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._state = "idle"
        self._tick = 0
        self.facing_left = True
        self._glow_alpha = 0
        self._glow_dir = 1
        self.colors = {
            ' ': Qt.transparent,
            'k': C_INK,
            'd': C_BODY,
            'p': C_LAVENDER,
            'y': C_EYE,
        }
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(140)

    def setState(self, state):
        if self._state != state:
            self._state = state
            self.update()

    def _on_tick(self):
        self._tick += 1
        if self._state == "happy":
            self._glow_alpha = max(0, min(80, self._glow_alpha + self._glow_dir * 8))
            if self._glow_alpha >= 80: self._glow_dir = -1
            if self._glow_alpha <= 0:  self._glow_dir = 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        scale = self.width() / 40
        frame = FRAME_IDLE
        y_offset = 0

        if self._state == "sleeping":
            frame = FRAME_SLEEP_1 if (self._tick // 4) % 2 == 0 else FRAME_SLEEP_2
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setFont(QFont("Segoe UI", 8))
            alpha = 80 + int(80 * abs(math.sin(self._tick * 0.1)))
            p.setOpacity(alpha / 255)
            p.setPen(QPen(C_LAV_LIGHT, 1))
            p.drawText(108, 18 + int(math.sin(self._tick * 0.08) * 3), "z z z")
            p.setOpacity(1.0)
            p.setRenderHint(QPainter.Antialiasing, False)

        elif self._state == "walking":
            frame = FRAME_WALK_1 if (self._tick % 4) < 2 else FRAME_WALK_2

        elif self._state == "happy":
            frame = FRAME_HAPPY
            y_offset = -int(abs(math.sin(self._tick * 0.9)) * 4)
            p.setRenderHint(QPainter.Antialiasing, True)
            glow = QRadialGradient(80, 90, 55)
            glow.setColorAt(0, QColor(196, 181, 232, self._glow_alpha))
            glow.setColorAt(1, QColor(196, 181, 232, 0))
            p.fillRect(0, 0, 160, 160, glow)
            for i, (sx, sy) in enumerate([(20, 25), (135, 30), (18, 110), (140, 100)]):
                alpha = int(abs(math.sin(self._tick * 0.3 + i)) * 180)
                p.setPen(QPen(QColor(255, 230, 100, alpha), 1.5))
                sz = 4
                p.drawLine(sx - sz, sy, sx + sz, sy)
                p.drawLine(sx, sy - sz, sx, sy + sz)
            p.setRenderHint(QPainter.Antialiasing, False)

        elif self._state == "idle":
            if self._tick % 30 in (0, 1):
                frame = FRAME_BLINK

        elif self._state == "thinking":
            y_offset = int(math.sin(self._tick * 0.5) * 2)
            p.setRenderHint(QPainter.Antialiasing, True)
            for i in range(3):
                a = int(abs(math.sin(self._tick * 0.25 + i * 1.1)) * 200)
                dy = 18 - int(math.sin(self._tick * 0.2 + i) * 5)
                p.setBrush(QBrush(QColor(196, 181, 232, a)))
                p.setPen(Qt.NoPen)
                r = 4 + i
                p.drawEllipse(100 + i * 14, dy, r, r)
            p.setRenderHint(QPainter.Antialiasing, False)

        for y_idx, row_str in enumerate(frame):
            for x_idx, char in enumerate(row_str):
                if char != ' ' and char in self.colors:
                    draw_x = (39 - x_idx) if not self.facing_left else x_idx
                    color = self.colors[char]
                    if char == 'y' and self._state == "happy":
                        color = C_EYE_GLOW
                    p.fillRect(
                        QRect(int(draw_x * scale), int(y_idx * scale + y_offset),
                              math.ceil(scale), math.ceil(scale)),
                        color
                    )
        p.end()


class ChatModal(QDialog):
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, 540)
        self._last_response = ""
        self._build_ui()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1c1828, stop:1 #14111e);
                border: 1.5px solid #3d3356;
                border-radius: 24px;
            }
        """)

        fl = QVBoxLayout(self.frame)
        fl.setContentsMargins(28, 24, 28, 24)
        fl.setSpacing(16)

        # header
        header = QHBoxLayout()
        cat = QLabel("🐱")
        cat.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        title = QLabel("ask jiji")
        title.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: bold;
            color: #ede8f8; background: transparent; border: none; letter-spacing: 3px;
        """)
        close = QPushButton("✕")
        close.setFixedSize(32, 32)
        close.setStyleSheet("""
            QPushButton { background: #2a2040; color: #6b5a94; border: none; border-radius: 16px; font-size: 12px; }
            QPushButton:hover { background: #3d3356; color: #ede8f8; }
        """)
        close.clicked.connect(self.reject)
        header.addWidget(cat)
        header.addSpacing(8)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #2a2040; border: none;")

        # Response area upgraded to QTextEdit for clipping fixes and highlighting text!
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        self.response_box.setMinimumHeight(300)
        self.response_box.setStyleSheet("""
            QTextEdit { 
                background: #100d1a; 
                border: 1px solid #2a2040; 
                border-radius: 14px; 
                padding: 16px; 
                font-family: 'Segoe UI'; 
                font-size: 13px; 
                color: #ede8f8; 
            }
            QScrollBar:vertical { background: #1c1828; width: 6px; border-radius: 3px; margin: 0px; }
            QScrollBar::handle:vertical { background: #3d3356; border-radius: 3px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        self.response_box.setPlainText("waiting for your question... ✨")

        # input
        self.input = QLineEdit()
        self.input.setFixedHeight(48)
        self.input.setPlaceholderText("type something...")
        self.input.setStyleSheet("""
            QLineEdit {
                background: #100d1a; border: 1.5px solid #2a2040; border-radius: 12px;
                padding: 0 16px; font-family: 'Segoe UI'; font-size: 13px; color: #e8e2f5;
            }
            QLineEdit:focus { border-color: #6b5a94; background: #140f22; }
        """)

        # buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.save_btn = QPushButton("💾  save response")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setVisible(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #1a1628; color: #7a6a94; border: 1px solid #2a2040;
                border-radius: 10px; font-family: 'Segoe UI'; font-size: 11px; padding: 0 14px;
            }
            QPushButton:hover { background: #241e38; color: #ede8f8; }
        """)
        self.save_btn.clicked.connect(self._save_response)

        self.cancel_btn = QPushButton("close")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #1a1628; color: #5a4a74; border: 1px solid #2a2040;
                border-radius: 10px; font-family: 'Segoe UI'; font-size: 11px; padding: 0 18px;
            }
            QPushButton:hover { background: #241e38; color: #9b87c0; }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        self.ask_btn = QPushButton("ask jiji  →")
        self.ask_btn.setFixedHeight(40)
        self.ask_btn.setAutoDefault(False)
        self.ask_btn.setDefault(False)
        self.ask_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #5a4a7a, stop:1 #9b87c0);
                color: #f0eaff; border: none; border-radius: 10px;
                font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;
                padding: 0 24px; letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6b5a94, stop:1 #b09ad4);
            }
            QPushButton:pressed { background: #3d2e5e; }
        """)
        self.ask_btn.clicked.connect(self._on_submit)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.ask_btn)

        self.mood_label = QLabel("she's ready  🌙")
        self.mood_label.setStyleSheet("""
            QLabel { font-family: 'Segoe UI'; font-size: 10px; color: #3d3356; background: transparent; border: none; }
        """)

        fl.addLayout(header)
        fl.addWidget(div)
        fl.addWidget(self.response_box)
        fl.addWidget(self.input)
        fl.addLayout(btn_row)
        fl.addWidget(self.mood_label)
        outer.addWidget(self.frame)

    def set_response(self, text):
        self._last_response = text
        self.response_box.setPlainText(text.lower())
        self.mood_label.setText("she answered  ✨")
        self.save_btn.setVisible(True)

    def set_thinking(self):
        self.response_box.setPlainText("hmm, let me think... 🌙")
        self.mood_label.setText("thinking...")
        self.save_btn.setVisible(False)

    def set_ready(self, mood="normal"):
        hints = {
            "sleepy":  "she's half asleep  😴",
            "hyper":   "she's very energetic rn  ⚡",
            "relaxed": "she's in a chill mood  🌙",
            "normal":  "she's ready  🌙"
        }
        self.mood_label.setText(hints.get(mood, "she's ready  🌙"))

    def _on_submit(self):
        text = self.input.text().strip()
        if text:
            self.submitted.emit(text)
            self.input.clear()
            self.set_thinking()

    def _save_response(self):
        if not self._last_response:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "save jiji's response", "response.md",
            "Markdown (*.md);;Text (*.txt);;All Files (*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._last_response)
            self.mood_label.setText("saved!  ✨")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        shadow = QRadialGradient(240, 280, 260)
        shadow.setColorAt(0, QColor(0, 0, 0, 55))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(self.rect(), shadow)
        p.end()

    def accept(self):
        # Prevents hitting 'Enter' from automatically closing the window!
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.pet = Pet()
        self._drag_pos = None
        self.walk_speed = 3
        self.walk_direction = -1
        self._clipboard_pending = "" # Holds copied text to send to Jiji
        
        self._setup_window()
        self._build_ui()
        self._setup_timers()

    def _setup_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(160, 160)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 200, screen.height() - 200)

    def _build_ui(self):
        self._sprite = JijiSprite(self)
        self._sprite.move(0, 0)
        self._bubble = SpeechBubble()
        self._bubble.hide()
        self._modal = ChatModal(self)
        self._modal.submitted.connect(self._on_question)

    def _setup_timers(self):
        self._movement_timer = QTimer()
        self._movement_timer.timeout.connect(self._handle_movement_tick)
        self._movement_timer.start(50)

        self._env_timer = QTimer()
        self._env_timer.timeout.connect(self._handle_environment_tick)
        self._env_timer.start(5000)

        self._bubble_timer = QTimer()
        self._bubble_timer.setSingleShot(True)
        self._bubble_timer.timeout.connect(self._bubble.hide)

        self._quip_counter = 0
        QTimer.singleShot(2000, self._start_walking)

    def _start_walking(self):
        if self._sprite._state not in ("sleeping", "thinking", "happy"):
            self._sprite.setState("walking")
            self.walk_direction = random.choice([-1, 1])
            self._sprite.facing_left = (self.walk_direction == -1)

    def _handle_movement_tick(self):
        if self._sprite._state != "walking" or self._modal.isVisible():
            return
        screen = QApplication.primaryScreen().geometry()
        geo = self.geometry()
        next_x = geo.x() + (self.walk_direction * self.walk_speed)
        
        if next_x < 20:
            next_x = 20
            self.walk_direction = 1
            self._sprite.facing_left = False
        elif next_x > screen.width() - 180:
            next_x = screen.width() - 180
            self.walk_direction = -1
            self._sprite.facing_left = True
            
        self.move(next_x, geo.y())
        if self._bubble.isVisible():
            self._bubble.move(next_x - 80, geo.y() - 130)

    def _handle_environment_tick(self):
        if self._modal.isVisible():
            return

        hour = QTime.currentTime().hour()

        if hour >= 23 or hour < 6:
            if self._sprite._state != "sleeping":
                self._sprite.setState("sleeping")
                self._bubble.hide()
                self._show_bubble("zzz... goodnight.", 4000)
            return

        if self._sprite._state == "sleeping":
            self._sprite.setState("idle")
            self._show_bubble("oh. you're up. fine, me too.", 4000)

        if self._sprite._state in ("idle", "walking"):
            roll = random.random()
            if roll < 0.4:
                if self._sprite._state == "idle":
                    self._sprite.setState("walking")
                    self.walk_direction = random.choice([-1, 1])
                    self._sprite.facing_left = (self.walk_direction == -1)
            elif roll < 0.7:
                if self._sprite._state == "walking":
                    self._sprite.setState("idle")

        self._quip_counter += 1
        if self._quip_counter >= 15:
            self._quip_counter = 0
            self._idle_quip()

    def _show_bubble(self, text, base_reading_time=5000):
        if self._sprite._state == "sleeping" and text != "zzz... goodnight.":
            return
            
        self._bubble.setText(text)
        geo = self.geometry()
        self._bubble.move(geo.x() - 80, geo.y() - 130)
        
        self._bubble.show()
        self._bubble.raise_()
        self._bubble_timer.stop()
        self._bubble_timer.start(len(text) * 28 + max(base_reading_time, len(text) * 60))

    def _idle_quip(self):
        quip = self.pet.idle_quip()
        if quip:
            self._show_bubble(quip)

    def _on_question(self, question):
        if self._sprite._state == "sleeping":
            return
        self._sprite.setState("thinking")
        
        # Merge the pending clipboard text if you used the right-click option!
        if self._clipboard_pending:
            question = f"{question}\n\n[Attached Text]:\n{self._clipboard_pending}"
            self._clipboard_pending = ""

        import threading
        def fetch():
            response = ask_ollama(question, self.pet.get_system_prompt())
            self._pending_response = response
            QTimer.singleShot(0, self._deliver_response)
        threading.Thread(target=fetch, daemon=True).start()

    def _deliver_response(self):
        response = getattr(self, "_pending_response", "...i got nothing.")
        self._sprite.setState("happy")
        if self._modal.isVisible():
            self._modal.set_response(response)
            self._modal.set_ready(self.pet.get_mood())
        else:
            self._show_bubble(response, 6000)
        QTimer.singleShot(2500, lambda: self._sprite.setState("idle")
                          if self._sprite._state != "sleeping" else None)

    def _open_chat_modal(self):
        self._modal._center_on_screen()
        self._modal.set_ready(self.pet.get_mood())
        self._sprite.setState("idle")
        self._modal.show()
        self._modal.raise_()
        self._modal.activateWindow()
        self._modal.input.setFocus()

    def _ask_clipboard(self):
        clip = QApplication.clipboard().text().strip()
        if not clip:
            self._show_bubble("your clipboard is empty!", 3000)
            return
        
        self._clipboard_pending = clip
        self._open_chat_modal()
        self._modal.input.setText("explain this text")
        self._modal.input.selectAll()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._sprite.setState("idle")
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self._sprite._state != "sleeping":
            self._open_chat_modal()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            new_pos = event.globalPos() - self._drag_pos
            self.move(new_pos)
            self._bubble.move(new_pos.x() - 80, new_pos.y() - 130)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _show_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #1c1828; border: 1px solid #3d3356; border-radius: 12px;
                padding: 6px; font-family: 'Segoe UI'; font-size: 11px;
            }
            QMenu::item { padding: 8px 20px; border-radius: 6px; color: #b8aace; }
            QMenu::item:selected { background: #2a2040; color: #e8e2f5; }
            QMenu::separator { background: #2a2040; height: 1px; margin: 4px 8px; }
        """)
        
        pet_action  = QAction("🐾  pet jiji", self)
        ask_action  = QAction("💬  ask something", self)
        clip_action = QAction("📋  ask about clipboard", self)
        shoo_action = QAction("👋  shoo (hide)", self)
        quit_action = QAction("✕   quit", self)

        if self._sprite._state == "sleeping":
            pet_action.setEnabled(False)
            ask_action.setEnabled(False)
            clip_action.setEnabled(False)

        pet_action.triggered.connect(self._pet_jiji)
        ask_action.triggered.connect(self._open_chat_modal)
        clip_action.triggered.connect(self._ask_clipboard)
        shoo_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.quit)

        menu.addAction(pet_action)
        menu.addAction(ask_action)
        menu.addAction(clip_action)
        menu.addSeparator()
        menu.addAction(shoo_action)
        menu.addAction(quit_action)
        menu.exec_(pos)

    def _pet_jiji(self):
        self._sprite.setState("happy")
        self._show_bubble(random.choice(self.pet.pet_responses()), 4000)
        QTimer.singleShot(2000, lambda: self._sprite.setState("idle")
                          if self._sprite._state != "sleeping" else None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = DesktopPet()
    window.show()
    sys.exit(app.exec_())