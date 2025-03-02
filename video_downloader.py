import sys
import os
import yt_dlp
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

class VideoDownloader:
    def __init__(self):
        self.output_dir = os.getcwd()

    def progress_hook(self, d, callback):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                callback(percent)

    def download(self, url, is_audio=True, progress_callback=None):
        if is_audio:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'progress_hooks': [lambda d: self.progress_hook(d, progress_callback)] if progress_callback else [],
            }
        else:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'progress_hooks': [lambda d: self.progress_hook(d, progress_callback)] if progress_callback else [],
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

class DownloaderGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.downloader = VideoDownloader()
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                background-color: #363636;
                margin: 5px;
            }
            QPushButton {
                background-color: #0d6efd;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
            }
            QRadioButton {
                spacing: 8px;
                padding: 5px;
            }
            QGroupBox {
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        self.url_label = QtWidgets.QLabel("Enter Video URL:")
        self.url_label.setFont(QtGui.QFont('Arial', 10, QtGui.QFont.Bold))
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        
        self.format_group = QtWidgets.QGroupBox("Download Format")
        self.radio_audio = QtWidgets.QRadioButton("Audio (MP3)")
        self.radio_video = QtWidgets.QRadioButton("Video (MP4)")
        self.radio_audio.setChecked(True)
        
        format_layout = QtWidgets.QHBoxLayout()
        format_layout.addWidget(self.radio_audio)
        format_layout.addWidget(self.radio_video)
        self.format_group.setLayout(format_layout)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        
        self.download_button = QtWidgets.QPushButton("Download", self)
        self.download_button.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.status_text = QtWidgets.QLabel("")
        
        self.download_button.clicked.connect(self.start_download)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.format_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.download_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(500, 300)

    def update_progress(self, progress):
        self.progress_bar.show()
        self.progress_bar.setValue(int(progress))
        self.status_text.setText(f"Downloading... {progress:.1f}%")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_text.setText("Please enter a valid URL.")
            return
        
        self.status_text.setText("Starting download...")
        self.progress_bar.show()
        self.download_button.setEnabled(False)
        
        is_audio = self.radio_audio.isChecked()
        try:
            self.downloader.download(url, is_audio, self.update_progress)
            self.status_text.setText("Download successful!")
        except Exception as e:
            self.status_text.setText(f"Error: {str(e)}")
        finally:
            self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DownloaderGUI()
    window.show()
    sys.exit(app.exec_())