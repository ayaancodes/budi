import sys
from PyQt5.QtCore import qInstallMessageHandler

# Suppress Qt debug output
def qt_message_handler(mode, context, message):
    pass
qInstallMessageHandler(qt_message_handler)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QLabel
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QColor
from pynput import keyboard
import audio_transcriber

class AudioRecorder(QThread):
    def __init__(self, transcriber):
        super().__init__()
        self.transcriber = transcriber
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            self.transcriber.record_chunk()
            self.msleep(50)  # Sleep for 50ms between chunks

    def stop(self):
        self.is_running = False

class BudiWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mic_muted = False
        self.is_talking = False
        self.ctrl_pressed = False
        self.audio_transcriber = audio_transcriber.AudioTranscriber()
        self.recorder = None
        
        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=False
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Budi')
        self.setGeometry(300, 300, 250, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add close button at the top right
        close_button = QPushButton('×')  # Using × symbol
        close_button.setStyleSheet('''
            QPushButton {
                background-color: transparent;
                color: #666666;
                font-size: 20px;
                font-weight: bold;
                border: none;
                padding: 5px;
                max-width: 30px;
            }
            QPushButton:hover {
                color: #FF6B6B;
            }
        ''')
        close_button.clicked.connect(self.close)
        
        # Create a horizontal layout for the close button
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Push button to the right
        top_layout.addWidget(close_button)
        layout.addLayout(top_layout)

        # Add icon
        icon_label = QLabel()
        pixmap = QPixmap('icon.png')
        scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Status label
        self.status_label = QLabel('Status: Microphone Active')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Push-to-talk indicator
        self.talk_indicator = QLabel('●')
        self.talk_indicator.setAlignment(Qt.AlignCenter)
        self.talk_indicator.setStyleSheet('color: #666666; font-size: 24px;')  # Gray dot by default
        layout.addWidget(self.talk_indicator)

        # Mute/Unmute button
        self.mute_button = QPushButton('Mute Microphone')
        self.mute_button.setStyleSheet('''
            QPushButton {
                background-color: #666666;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        ''')
        self.mute_button.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mute_button)

        # Hotkey info label
        hotkey_label = QLabel('Push-to-talk: Hold Ctrl+B')
        hotkey_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hotkey_label)

        # Keep window on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def on_press(self, key):
        try:
            # Only handle Ctrl and B, ignore other keys
            if key == keyboard.Key.ctrl:
                self.ctrl_pressed = True
            elif hasattr(key, 'char') and key.char == 'b' and self.ctrl_pressed and not self.is_talking:
                self.start_talking()
        except Exception as e:
            # Don't print errors for system key combinations
            pass

    def on_release(self, key):
        try:
            # Only handle Ctrl and B, ignore other keys
            if key == keyboard.Key.ctrl:
                self.ctrl_pressed = False
                if self.is_talking:
                    self.stop_talking()
            elif hasattr(key, 'char') and key.char == 'b':
                if self.is_talking:
                    self.stop_talking()
                self.ctrl_pressed = False  # Reset ctrl state when b is released
        except Exception as e:
            # Don't print errors for system key combinations
            pass

    def toggle_mic(self):
        self.mic_muted = not self.mic_muted
        if self.mic_muted:
            self.audio_transcriber.stop_listening()
            self.mute_button.setText('Unmute Microphone')
            self.status_label.setText('Status: Microphone Muted')
            self.mute_button.setStyleSheet('''
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #FF8888;
                }
            ''')
        else:
            self.mute_button.setText('Mute Microphone')
            self.status_label.setText('Status: Microphone Active')
            self.mute_button.setStyleSheet('''
                QPushButton {
                    background-color: #666666;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
            ''')

    def start_talking(self):
        if not self.mic_muted:
            self.is_talking = True
            self.talk_indicator.setStyleSheet('color: #2ECC71; font-size: 24px;')  # Green dot
            self.audio_transcriber.start_listening()
            # Start recording in a separate thread
            self.recorder = AudioRecorder(self.audio_transcriber)
            self.recorder.start()

    def stop_talking(self):
        if self.is_talking:
            self.is_talking = False
            self.talk_indicator.setStyleSheet('color: #666666; font-size: 24px;')
            if self.recorder:
                self.recorder.stop()
                self.recorder.wait()  # Wait for thread to finish
                self.recorder = None
            self.audio_transcriber.stop_listening()

    def closeEvent(self, event):
        if self.recorder:
            self.recorder.stop()
            self.recorder.wait()
        self.audio_transcriber.stop_listening()
        self.keyboard_listener.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = BudiWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()