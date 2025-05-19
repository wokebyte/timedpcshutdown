from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import QTimer
import sys
import os
from winotify import Notification

class ShutdownTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutdown Timer")
        self.setFixedSize(400, 250)
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0

    def init_ui(self):
        layout = QVBoxLayout()

        # Time input section
        time_layout = QHBoxLayout()
        self.hours_input = QLineEdit("0")
        self.hours_input.setPlaceholderText("Hours")
        self.minutes_input = QLineEdit("0")
        self.minutes_input.setPlaceholderText("Minutes")
        self.seconds_input = QLineEdit("0")
        self.seconds_input.setPlaceholderText("Seconds")

        for input_field in [self.hours_input, self.minutes_input, self.seconds_input]:
            input_field.setFixedWidth(80)
            input_field.setStyleSheet("QLineEdit { padding: 5px; }")

        time_layout.addWidget(QLabel("Hours:"))
        time_layout.addWidget(self.hours_input)
        time_layout.addWidget(QLabel("Minutes:"))
        time_layout.addWidget(self.minutes_input)
        time_layout.addWidget(QLabel("Seconds:"))
        time_layout.addWidget(self.seconds_input)

        # Countdown display
        self.countdown_label = QLabel("00:00:00")
        self.countdown_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #2c3e50;
            qproperty-alignment: AlignCenter;
        """)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("⏳ Start Shutdown")
        self.cancel_btn = QPushButton("❌ Cancel Shutdown")
        self.cancel_btn.setEnabled(False)
        
        for btn in [self.start_btn, self.cancel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)

        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

        # Add components to layout
        layout.addLayout(time_layout)
        layout.addSpacing(20)
        layout.addWidget(self.countdown_label)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Connect signals
        self.start_btn.clicked.connect(self.schedule_shutdown)
        self.cancel_btn.clicked.connect(self.cancel_shutdown)

    def schedule_shutdown(self):
        try:
            hours = int(self.hours_input.text())
            minutes = int(self.minutes_input.text())
            seconds = int(self.seconds_input.text())
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds <= 0:
                QMessageBox.warning(self, "Invalid Time", "Please enter a positive time value.")
                return
                
            os.system(f"shutdown /s /t {total_seconds}")
            self.remaining_seconds = total_seconds
            self.timer.start(1000)  # Update every second
            
            # Show desktop notification
            Notification(
                app_id="Shutdown Timer",
                title="Shutdown Scheduled",
                msg=f"System will shutdown in {hours}h {minutes}m {seconds}s"
            ).show()
            
            self.status_label.setText("Shutdown scheduled successfully!")
            self.cancel_btn.setEnabled(True)
            self.start_btn.setEnabled(False)
            self.update_countdown()  # Update immediately

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numbers in all fields")

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            hours, rem = divmod(self.remaining_seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            self.countdown_label.setText(
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        else:
            self.timer.stop()
            self.countdown_label.setText("00:00:00")

    def cancel_shutdown(self):
        os.system("shutdown /a")
        self.timer.stop()
        self.countdown_label.setText("00:00:00")
        self.status_label.setText("Shutdown cancelled!")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # Show cancellation notification
        Notification(
            app_id="Shutdown Timer",
            title="Shutdown Cancelled",
            msg="System shutdown has been cancelled."
        ).show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShutdownTimer()
    window.show()
    sys.exit(app.exec())
