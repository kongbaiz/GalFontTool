from PySide6.QtWidgets import QPushButton, QFrame, QLineEdit, QTextEdit
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDesktopServices, QColor


class IOSButton(QPushButton):
    def __init__(self, text, color="#007AFF", parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())
        self.update_style()

    def set_theme_color(self, c):
        self.base_color = c
        self.update_style()

    def update_style(self, pressed=False):
        base = QColor(self.base_color)
        hover = base.darker(108).name()
        down = base.darker(116).name()
        self.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {base.name()};"
            f"color: #FFFFFF;"
            f"border: 1px solid {base.darker(122).name()};"
            f"border-radius: 5px;"
            f"padding: 5px 12px;"
            f"}}"
            f"QPushButton:hover {{background-color: {hover};}}"
            f"QPushButton:pressed {{background-color: {down};}}"
            f"QPushButton:disabled {{background-color: #C8CDD2; color: #6E7781; border-color: #C8CDD2;}}"
        )

    def enterEvent(self, e):
        super().enterEvent(e)

    def leaveEvent(self, e):
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.update_style(True)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.update_style(False)
        super().mouseReleaseEvent(e)


class IOSCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def update_theme(self, bg, border):
        self.setStyleSheet(
            f"background-color: {bg};"
            f"border: none;"
            f"border-radius: 6px;"
        )


class IOSInput(QLineEdit):
    def __init__(self, ph, default="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(str(ph))
        self.setText(str(default))
        self.setMinimumHeight(30)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent):
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                self.setText(path)
                self.editingFinished.emit()
            e.acceptProposedAction()
        else:
            super().dropEvent(e)

    def update_theme(self, bg, focus_bg, accent, text):
        self.setStyleSheet(
            f"QLineEdit {{"
            f"background-color: {bg};"
            f"color: {text};"
            f"border: 1px solid #C7D0D9;"
            f"border-radius: 5px;"
            f"padding: 0 9px;"
            f"}}"
            f"QLineEdit:focus {{"
            f"background-color: {focus_bg};"
            f"border: 1px solid {accent};"
            f"}}"
            f"QLineEdit:disabled {{background-color: #F1F3F5; color: #8A949E; border-color: #D0D7DE;}}"
        )


class IOSLog(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        anchor = self.anchorAt(e.pos())
        if anchor: QDesktopServices.openUrl(QUrl.fromLocalFile(anchor))

    def update_theme(self, text, bg, scrollbar_style=""):
        self.setStyleSheet(
            f"QTextEdit {{"
            f"background-color: {bg};"
            f"color: {text};"
            f"border: 1px solid #C7D0D9;"
            f"border-radius: 5px;"
            f"padding: 6px;"
            f"}}"
            f"{scrollbar_style}"
        )


class LockToggle(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(50, 28)
        self._accent = "#3A6784"
        self._track_off = "#EEF2F5"
        self._border = "#CAD3DC"
        self._focus = "#9DB7CA"
        self.toggled.connect(lambda _: self.update_style())
        self.update_style()

    def sizeHint(self):
        return QSize(50, 28)

    def set_theme(self, accent, track_off, border, focus):
        self._accent = accent
        self._track_off = track_off
        self._border = border
        self._focus = focus
        self.update_style()

    def update_style(self):
        checked_bg = self._accent
        checked_border = QColor(self._accent).darker(112).name()
        self.setText("锁定" if self.isChecked() else "跟随")
        self.setStyleSheet(
            "QPushButton {"
            f"background-color: {self._track_off};"
            "color: #586776;"
            f"border: 1px solid {self._border};"
            "border-radius: 6px;"
            "padding: 0 8px;"
            "font-size: 12px;"
            "font-weight: 600;"
            "text-align: center;"
            "}"
            "QPushButton:hover { background-color: #E7EDF2; }"
            f"QPushButton:checked {{ background-color: {checked_bg}; color: #FFFFFF; border: 1px solid {checked_border}; }}"
            f"QPushButton:checked:hover {{ background-color: {QColor(self._accent).darker(108).name()}; }}"
            f"QPushButton:focus {{ border: 1px solid {self._focus}; }}"
            "QPushButton:disabled { background-color: #F2F5F7; color: #98A3AD; border-color: #D9E0E6; }"
        )
