from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QFont


class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        s = self.size()
        # Draw overlay background
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(QColor("#333333"))
        qp.setBrush(QColor(30, 30, 30, 120))
        qp.drawRect(0, 0, s.width(), s.height())

        # Draw popup
        qp.setPen(QColor(200, 200, 200, 255))
        qp.setBrush(QColor(240, 240, 240, 255))
        popupWidth = 300
        popupHeight = 120
        ow = int(s.width()/2-popupWidth/2)
        oh = int(s.height()/2-popupHeight/2)
        qp.drawRoundedRect(ow, oh, popupWidth, popupHeight, 5, 5)
        
        # Draw text
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        qp.setFont(font)
        qp.setPen(QColor(70, 70, 70))
        tolw, tolh = 55, -5
        qp.drawText(ow + int(popupWidth/2) - tolw, oh + int(popupHeight/2) - tolh, "Loading ...")

        qp.end()


