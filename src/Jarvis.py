import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from MyWindow import MyWindow
from Audio import Audio

# Forcing a safe connection between threads using QueuedConnection
def icon_signals(icon_notifications, win):
    icon_notifications.word_detected.connect(win.activate, type=Qt.ConnectionType.QueuedConnection)
    icon_notifications.end_petition.connect(win.deactivate, type=Qt.ConnectionType.QueuedConnection)

def incognito_signals(incognito_notifications, win):
    incognito_notifications.activate_incognito.connect(win.activate_incognito, type=Qt.ConnectionType.QueuedConnection)
    incognito_notifications.deactivate_incognito.connect(win.deactivate_incognito, type=Qt.ConnectionType.QueuedConnection)

if __name__ == "__main__":
    position = "LeftVersion"
    app = QApplication(sys.argv)
    
    win = MyWindow(position)

    audio_thread = Audio()
    
    icon_signals(audio_thread.notification, win)
    incognito_signals(audio_thread.interpreter.action.notification, win)
    audio_thread.start()
    
    win.show()
    sys.exit(app.exec())