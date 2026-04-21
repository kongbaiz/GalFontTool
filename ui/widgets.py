from PyQt6.QtWidgets import QPushButton, QFrame, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDesktopServices


class IOSButton(QPushButton):
    def __init__(self, text, color="#007AFF", parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(45)

    def set_theme_color(self, color):
        self.base_color = color

    def update_style(self, pressed=False):
        return


class IOSCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

    def update_theme(self, bg, border):
        return


class IOSInput(QLineEdit):
    def __init__(self, placeholder, default="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(str(placeholder))
        self.setText(str(default))
        self.setFixedHeight(38)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                self.setText(urls[0].toLocalFile())
                self.editingFinished.emit()
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def update_theme(self, bg, focus_bg, accent, text):
        return


class IOSLog(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        anchor = self.anchorAt(event.pos())
        if anchor:
            QDesktopServices.openUrl(QUrl.fromLocalFile(anchor))

    def update_theme(self, text, bg, scrollbar_style=""):
        return
