import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from Helper import Helper # <-- Import Helper

class MyWindow(QWidget):
    def __init__(self, position):
        super(MyWindow, self).__init__()
        self.helper = Helper()
        self.position = position
        self.setGeometry(0, 0, 100, 100)
        self.setWindowTitle("Icon")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint 
            | Qt.WindowType.Tool 
            | Qt.WindowType.WindowStaysOnTopHint 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)

        # Use the new path resolution function
        image_path = self.helper.get_absolute_path(f"images/icon/{self.position}/viviBlack.png")

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 100, 100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.label.setPixmap(
                pixmap.scaled(
                    100,
                    100,
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation, 
                )
            )

    def activate_incognito(self):
        self.hide()

    def deactivate_incognito(self):
        self.show()

    def activate(self):
        image_path = self.helper.get_absolute_path(f"images/icon/{self.position}/viviColor.png")
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.label.setPixmap(
                pixmap.scaled(
                    100,
                    100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def deactivate(self):
        image_path = self.helper.get_absolute_path(f"images/icon/{self.position}/viviBlack.png")
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.label.setPixmap(
                pixmap.scaled(
                    100,
                    100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )