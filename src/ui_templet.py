from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QWidget,
)

class UiTemplet:
    def setup_ui(self, main_window):
        main_window.setWindowTitle("Audio Converter")

        # 1. 열
        self.input_label = QLabel("Input Audio:")
        self.input_line_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")

        input_layout = QHBoxLayout()  # QHBoxLayout로 변경
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(self.browse_button)

        # 2. 열
        self.waveform_label = QLabel("Waveform:")
        self.waveform_view = QGraphicsView()
        self.waveform_scene = QGraphicsScene()
        self.waveform_view.setScene(self.waveform_scene)

        waveform_layout = QVBoxLayout()
        waveform_layout.addWidget(self.waveform_label)
        waveform_layout.addWidget(self.waveform_view)

        # 3. 열
        self.convert_button = QPushButton("Convert")
        self.save_button = QPushButton("Save")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.convert_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.save_button, alignment=Qt.AlignRight)

        # 전체 레이아웃 설정
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(waveform_layout)
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        main_window.setCentralWidget(central_widget)
