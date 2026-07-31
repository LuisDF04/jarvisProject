from PyQt6.QtCore import QObject, pyqtSignal

class Notifications(QObject):
    
    word_detected = pyqtSignal()
    end_petition = pyqtSignal()
    activate_incognito = pyqtSignal()
    deactivate_incognito = pyqtSignal()

    def __init__(self):
        super().__init__()

    def emit_word_detected(self):
        self.word_detected.emit()

    def emit_end_petition(self):
        self.end_petition.emit()

    def emit_incognito_activate(self):
        self.activate_incognito.emit()

    def emit_incognito_deactivate(self):
        self.deactivate_incognito.emit()