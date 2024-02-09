import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
)
import matplotlib.pyplot as plt
import librosa
import music21


class AudioConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()  # QMainWindow 초기화

        self.init_ui()  # AudioConverterApp 초기화
        # 결과 악보를 저장할 변수
        self.score = None

    def init_ui(self):
        self.setWindowTitle("Audio Converter")

        # 1. 열
        input_label = QLabel("Input Audio:")
        self.input_line_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        # 2. 열
        waveform_label = QLabel("Waveform:")
        self.waveform_view = QGraphicsView()
        self.waveform_scene = QGraphicsScene()
        self.waveform_view.setScene(self.waveform_scene)

        # 3. 열
        convert_button = QPushButton("Convert")
        convert_button.clicked.connect(self.convert_audio)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_result)

        # 전체 레이아웃 설정
        layout = QHBoxLayout()
        column_layouts = QVBoxLayout(), QVBoxLayout(), QVBoxLayout()
        layout.addLayout(column_layouts[0])
        layout.addLayout(column_layouts[1])
        layout.addLayout(column_layouts[2])

        column_layouts[0].addWidget(input_label)
        column_layouts[0].addWidget(self.input_line_edit)
        column_layouts[0].addWidget(self.browse_button)

        column_layouts[1].addWidget(waveform_label)
        column_layouts[1].addWidget(self.waveform_view)

        column_layouts[2].addWidget(convert_button)
        column_layouts[2].addWidget(save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio Files (*.m4a *.mp3 *.wav *.ogg *.flac *.aac)")
        file_dialog.exec_()
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            self.input_line_edit.setText(file_paths[0])

            # Display waveform
            self.display_waveform(file_paths[0])

    def display_waveform(self, audio_path):
        y, sr = librosa.load(audio_path)
        plt = music21.graph.plot.HistogramPitchClass(
            music21.note.Note(pitch=0), data=[y], title="Waveform", xMax=sr
        )
        plt.xlimits = (0, len(y))  # x축 범위 설정
        plt.run()

        image_path = "temp_waveform.png"
        plt.write(image_path)
        pixmap = QPixmap(image_path)
        os.remove(image_path)

        self.waveform_scene.clear()
        self.waveform_scene.addPixmap(pixmap)

    def convert_audio(self):
        # Implement audio conversion logic here
        input_audio_path = self.input_line_edit.text()

        if not input_audio_path:
            QMessageBox.critical(self, "Error", "Please select an input audio file.")
            return

        # 분석된 피아노 코드를 저장할 리스트
        piano_notes = []

        # 음악 분석 및 피아노 코드 할당
        y, sr = librosa.load(input_audio_path)
        pitches, magnitudes = librosa.core.pitch.piptrack(y=y, sr=sr)
        pitches = pitches[magnitudes > 0.5]
        estimated_pitches = []
        for frame in pitches.T:
            non_zero_frames = frame[frame > 0]
            if len(non_zero_frames) > 0:
                estimated_pitch = non_zero_frames[0]
                estimated_pitches.append(estimated_pitch)

        for pitch in estimated_pitches:
            # 피아노 코드로 변환
            midi_note = librosa.hz_to_midi(pitch)
            piano_note = music21.note.Note()
            piano_note.pitch.ps = midi_note
            piano_notes.append(piano_note)

        # 악보에 피아노 코드 추가
        self.score = music21.stream.Score()
        part = music21.stream.Part()
        part.append(piano_notes)
        self.score.append(part)

    def save_result(self):
        # Implement saving logic here
        if not self.score:
            QMessageBox.warning(self, "Warning", "Please convert audio first.")
            return

        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix("png")
        file_dialog.setNameFilter("Image Files (*.png)")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        if file_dialog.exec_():
            save_path = file_dialog.selectedFiles()[0]
            if not save_path.endswith(".png"):
                save_path += ".png"

            # 악보를 이미지로 저장
            image = self.score.write(
                "musicxml", fp="temp_score.xml", format="musicxml.png"
            )
            image.write(save_path)
            os.remove("temp_score.xml")

            QMessageBox.information(self, "Success", f"Score saved at: {save_path}")


if __name__ == "__main__":
    app = QApplication([])
    window = AudioConverterApp()
    window.show()
    app.exec()
