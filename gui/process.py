import sys

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import *
from qtpy import QtCore
from core.HSL import *
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QSize
# import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HSL-SOLVER")
        self.setGeometry(100, 100, 500, 700)

        self.input_text1 = QTextEdit()
        self.input_text1.setFixedHeight(1.5 * self.fontMetrics().height())

        self.input_text2 = QTextEdit()
        self.input_text2.setFixedHeight(1.5 * self.fontMetrics().height())

        self.input_text3 = QTextEdit()
        self.input_text3.setFixedHeight(1.5 * self.fontMetrics().height())

        self.output_text1 = QTextEdit()
        self.output_text2 = QTextEdit()

        self.file_label = QLabel()

        self.load_button = QPushButton("Load model")
        self.load_button.clicked.connect(self.load_file)

        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_input)
        self.process_button.setEnabled(False)  # 初始禁用 "处理输入" 按钮

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setText("Null")

        self.setup_ui()

        self.file_loaded = False  # 标记文件是否已加载

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        grid_layout = QGridLayout()

        label_input1 = QLabel("Logical formula:")
        label_input1.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_input1, 0, 0)
        grid_layout.addWidget(self.input_text1, 0, 1, 1, 4)
        grid_layout.addWidget(self.load_button, 0, 5)

        label_input2 = QLabel("Host agent:")
        label_input2.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_input2, 1, 0)
        grid_layout.addWidget(self.input_text2, 1, 1, 1, 2)

        label_input3 = QLabel("View range:")
        label_input3.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_input3, 1, 3)
        grid_layout.addWidget(self.input_text3, 1, 4)

        grid_layout.addWidget(self.process_button, 1, 5)

        label_file = QLabel("Loaded file:")
        label_file.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_file, 2, 0)
        grid_layout.addWidget(self.file_label, 2, 1, 1, 5)

        label_output1 = QLabel("Converted formula and Truth:")
        label_output1.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_output1, 3, 0, 1, 3)
        grid_layout.addWidget(self.output_text1, 4, 0, 1, 3)

        image_label_title = QLabel("Syntax tree:")
        image_label_title.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(image_label_title, 3, 3, 1, 3)
        grid_layout.addWidget(self.image_label, 4, 3, 1, 3)

        label_output2 = QLabel("Semantic interpretation of converted formula:")
        label_output2.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(label_output2, 5, 0, 1, 5)
        grid_layout.addWidget(self.output_text2, 6, 0, 1, 6)

        layout.addLayout(grid_layout)

    def load_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select file", "", "Text file (*.json)")
        if file_path:
            if file_path.strip() == "":
                QMessageBox.warning(self, "Tips", "Model does not exist!")
                return
            self.read_file(file_path)
            self.file_loaded = True
            self.process_button.setEnabled(True)

    def read_file(self, file_path):
        file_name = os.path.basename(file_path)
        self.file_label.setText(file_name)
        self.output_text2.clear()
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                print(line.strip())

    def process_input(self):
        self.output_text1.clear()
        self.output_text2.clear()
        input1 = self.input_text1.toPlainText()
        input2 = self.input_text2.toPlainText()
        input3 = self.input_text3.toPlainText()
        if input1.strip() == "" or input2.strip() == "" or input3.strip() == "":
            QMessageBox.warning(self, "Tips", "The input cannot be empty!")
            return
        print("Logical formula:", input1)
        print("Host agent:", input2)
        print("View range:", input3)
        res_truth, res_info, cal_time = hsl_sat(input1, input2, input3)
        self.output_text1.setPlainText("Formula: " + input1 + "\n \n" + "Truth Value: " + res_truth + "\n \n" + "Time: " + cal_time)
        self.output_text2.append(res_info)

        image_path = "/Users/wing/Workspaces/PycharmProjects/Z3-Test/gui/img/tree.svg"
        if image_path.strip() != "":
            renderer = QSvgRenderer(image_path)
            if not renderer.isValid():
                self.image_label.setText("Invalid SVG")
                return

            image_size = self.image_label.size() * self.devicePixelRatio()
            svg_image = QImage(image_size, QImage.Format_ARGB32)
            svg_image.fill(Qt.transparent)

            painter = QPainter(svg_image)
            renderer.render(painter)

            scaled_image = svg_image.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap = QPixmap.fromImage(scaled_image)

            self.image_label.setPixmap(pixmap)
            painter.end()
        else:
            self.image_label.setText("Null")

    # def scale_image(self, image, size):
    #     scaled_image = image.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #     return scaled_image


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
