import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
    QFileDialog,
)
import matplotlib.pyplot as plt
import librosa
import music21

from ui_templet import UiTemplet

class AudioConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()  # QMainWindow 초기화

        self.ui_templet = UiTemplet()
        self.ui_templet.setup_ui(self)

        # 결과 악보를 저장할 변수
        self.score = None

        # Connect button signals to slots
        self.ui_templet.browse_button.clicked.connect(self.browse_file)
        self.ui_templet.convert_button.clicked.connect(self.convert_audio)
        self.ui_templet.save_button.clicked.connect(self.save_result)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio Files (*.m4a *.mp3 *.wav *.ogg *.flac *.aac)")
        file_dialog.exec_()
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            self.ui_templet.input_line_edit.setText(file_paths[0])

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

        self.ui_templet.waveform_scene.clear()
        self.ui_templet.waveform_scene.addPixmap(pixmap)

    def convert_audio(self):
        # Implement audio conversion logic here
        input_audio_path = self.ui_templet.input_line_edit.text()

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
