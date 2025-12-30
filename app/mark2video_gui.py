import os
import sys

# 确保导入本地开发版本的 povideo 模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from povideo.api.video import mark2video


# 全局样式表 - 科技感深色主题
DARK_STYLE = """
QMainWindow {
    background-color: #0a0a0f;
}

QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* 分组框样式 */
QFrame.group-frame {
    background-color: rgba(20, 20, 30, 0.85);
    border: 1px solid rgba(100, 100, 255, 0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 8px;
}

QFrame.group-frame:hover {
    border: 1px solid rgba(100, 200, 255, 0.5);
}

/* 标题标签 */
QLabel.group-title {
    color: #00d4ff;
    font-size: 16px;
    font-weight: bold;
    padding-bottom: 12px;
    min-height: 24px;
}

QLabel.field-label {
    color: #c0c0d0;
    font-size: 14px;
    min-width: 80px;
    padding-right: 10px;
}

/* 输入框样式 */
QLineEdit {
    background-color: rgba(30, 30, 45, 0.9);
    border: 2px solid rgba(80, 80, 120, 0.5);
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffffff;
    font-size: 14px;
    min-height: 20px;
    selection-background-color: #6366f1;
}

QLineEdit:focus {
    border: 2px solid #00d4ff;
    background-color: rgba(40, 40, 60, 0.95);
}

QLineEdit:hover {
    border: 2px solid rgba(100, 200, 255, 0.6);
}

/* 数字输入框 */
QSpinBox {
    background-color: rgba(30, 30, 45, 0.9);
    border: 2px solid rgba(80, 80, 120, 0.5);
    border-radius: 8px;
    padding: 10px 14px;
    color: #ffffff;
    font-size: 14px;
    min-width: 120px;
    min-height: 20px;
}

QSpinBox:focus {
    border: 2px solid #00d4ff;
}

QSpinBox:hover {
    border: 2px solid rgba(100, 200, 255, 0.6);
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: rgba(100, 100, 255, 0.3);
    border: none;
    border-radius: 4px;
    width: 24px;
    margin: 2px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: rgba(100, 200, 255, 0.5);
}

/* 普通按钮样式 */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(60, 60, 100, 0.9),
        stop:1 rgba(40, 40, 80, 0.9));
    border: 1px solid rgba(100, 100, 200, 0.4);
    border-radius: 8px;
    padding: 12px 24px;
    color: #d0d0e0;
    font-size: 14px;
    font-weight: 500;
    min-width: 90px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(80, 80, 140, 0.95),
        stop:1 rgba(60, 60, 120, 0.95));
    border: 1px solid rgba(100, 200, 255, 0.6);
    color: #ffffff;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(50, 50, 100, 0.95),
        stop:1 rgba(30, 30, 70, 0.95));
}

/* 主操作按钮样式 */
QPushButton.primary-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1,
        stop:0.5 #8b5cf6,
        stop:1 #a855f7);
    border: none;
    border-radius: 10px;
    padding: 16px 48px;
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
    min-height: 24px;
}

QPushButton.primary-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #818cf8,
        stop:0.5 #a78bfa,
        stop:1 #c084fc);
}

QPushButton.primary-btn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f46e5,
        stop:0.5 #7c3aed,
        stop:1 #9333ea);
}

QPushButton.primary-btn:disabled {
    background: rgba(80, 80, 100, 0.5);
    color: rgba(200, 200, 200, 0.5);
}

/* 进度条样式 */
QProgressBar {
    background-color: rgba(30, 30, 50, 0.8);
    border: none;
    border-radius: 12px;
    height: 24px;
    text-align: center;
    color: #ffffff;
    font-size: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #06b6d4,
        stop:0.3 #8b5cf6,
        stop:0.6 #ec4899,
        stop:1 #f59e0b);
    border-radius: 12px;
}

/* 状态标签 */
QLabel.status-label {
    color: #00d4ff;
    font-size: 15px;
    padding: 12px;
    min-height: 20px;
}

/* 颜色预览框 */
QLabel.color-preview {
    border: 2px solid rgba(100, 200, 255, 0.5);
    border-radius: 6px;
}

/* 消息框样式 */
QMessageBox {
    background-color: #1a1a2e;
}

QMessageBox QLabel {
    color: #e0e0e0;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 100px;
}
"""


class GlowEffect(QGraphicsDropShadowEffect):
    """发光效果"""
    def __init__(self, color="#00d4ff", blur=20, parent=None):
        super().__init__(parent)
        self.setBlurRadius(blur)
        self.setColor(QColor(color))
        self.setOffset(0, 0)


class VideoProcessThread(QThread):
    """视频处理线程"""
    finished = Signal(bool, str)
    
    def __init__(self, video_path, output_path, output_name, watermark_content, font_size, font_type, font_color):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.output_name = output_name
        self.watermark_content = watermark_content
        self.font_size = font_size
        self.font_type = font_type
        self.font_color = font_color
    
    def run(self):
        try:
            mark2video(
                video_path=self.video_path,
                output_path=self.output_path,
                output_name=self.output_name,
                watermark_content=self.watermark_content,
                font_size=self.font_size,
                font_type=self.font_type,
                font_color=self.font_color
            )
            self.finished.emit(True, "视频水印添加成功！")
        except Exception as e:
            self.finished.emit(False, f"处理失败：{str(e)}")


class Mark2VideoApp(QMainWindow):
    """视频水印工具主窗口 - 科技感界面"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ 视频水印工具 - povideo")
        self.setMinimumSize(850, 720)
        self.resize(900, 750)
        self.font_color = "black"
        self.init_ui()
        self.apply_effects()
    
    def create_group_frame(self, title):
        """创建带标题的分组框"""
        frame = QFrame()
        frame.setProperty("class", "group-frame")
        frame.setGraphicsEffect(GlowEffect(color="#6366f1", blur=15))
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 20, 24, 24)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "group-title")
        title_label.setFixedHeight(28)
        layout.addWidget(title_label)
        
        return frame, layout
    
    def create_field_row(self, label_text, widget, button=None):
        """创建表单行 - 使用容器Widget避免重叠"""
        container = QWidget()
        container.setFixedHeight(50)
        
        row = QHBoxLayout(container)
        row.setSpacing(15)
        row.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text)
        label.setProperty("class", "field-label")
        label.setFixedWidth(90)
        label.setFixedHeight(40)
        row.addWidget(label)
        
        widget.setFixedHeight(44)
        row.addWidget(widget, 1)
        
        if button:
            button.setFixedHeight(44)
            row.addWidget(button)
        
        return container
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 顶部标题
        header = QLabel("🎬 视频水印工具")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, stop:0.5 #a855f7, stop:1 #f472b6);
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # 输入设置组
        input_frame, input_layout = self.create_group_frame("📁 输入设置")
        
        self.video_path_edit = QLineEdit()
        self.video_path_edit.setPlaceholderText("请选择视频文件...")
        video_btn = QPushButton("📂 浏览")
        video_btn.clicked.connect(self.select_video)
        input_layout.addWidget(self.create_field_row("视频文件", self.video_path_edit, video_btn))
        
        self.watermark_edit = QLineEdit("www.python-office.com")
        input_layout.addWidget(self.create_field_row("水印文字", self.watermark_edit))
        
        main_layout.addWidget(input_frame)
        
        # 输出设置组
        output_frame, output_layout = self.create_group_frame("💾 输出设置")
        
        self.output_path_edit = QLineEdit("./")
        output_path_btn = QPushButton("📂 浏览")
        output_path_btn.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.create_field_row("输出路径", self.output_path_edit, output_path_btn))
        
        self.output_name_edit = QLineEdit("mark2video.mp4")
        output_layout.addWidget(self.create_field_row("文件名", self.output_name_edit))
        
        main_layout.addWidget(output_frame)
        
        # 字体设置组
        font_frame, font_layout = self.create_group_frame("🎨 字体设置")
        
        # 字体大小和颜色放一行
        size_color_container = QWidget()
        size_color_container.setFixedHeight(50)
        size_color_row = QHBoxLayout(size_color_container)
        size_color_row.setSpacing(40)
        size_color_row.setContentsMargins(0, 0, 0, 0)
        
        # 字体大小
        size_sub = QHBoxLayout()
        size_label = QLabel("字体大小")
        size_label.setProperty("class", "field-label")
        size_label.setMinimumWidth(70)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(28)
        size_sub.addWidget(size_label)
        size_sub.addWidget(self.font_size_spin)
        size_color_row.addLayout(size_sub)
        
        # 字体颜色
        color_sub = QHBoxLayout()
        color_label = QLabel("字体颜色")
        color_label.setProperty("class", "field-label")
        color_label.setMinimumWidth(70)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(100, 36)
        self.color_preview.setProperty("class", "color-preview")
        self.color_preview.setStyleSheet("""
            background-color: black;
            border: 2px solid rgba(100, 200, 255, 0.5);
            border-radius: 6px;
        """)
        color_btn = QPushButton("🎨 选择")
        color_btn.clicked.connect(self.select_color)
        color_sub.addWidget(color_label)
        color_sub.addWidget(self.color_preview)
        color_sub.addWidget(color_btn)
        size_color_row.addLayout(color_sub)
        
        size_color_row.addStretch()
        font_layout.addWidget(size_color_container)
        
        # 字体文件
        self.font_type_edit = QLineEdit(r"C:\Windows\Fonts\arial.ttf")
        font_type_btn = QPushButton("📂 浏览")
        font_type_btn.clicked.connect(self.select_font)
        font_layout.addWidget(self.create_field_row("字体文件", self.font_type_edit, font_type_btn))
        
        main_layout.addWidget(font_frame)
        
        # 处理区域
        process_frame, process_layout = self.create_group_frame("⚡ 处理")
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.hide()
        process_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("✅ 就绪，等待处理...")
        self.status_label.setProperty("class", "status-label")
        self.status_label.setAlignment(Qt.AlignCenter)
        process_layout.addWidget(self.status_label)
        
        # 开始按钮
        self.start_btn = QPushButton("🚀 开始处理")
        self.start_btn.setProperty("class", "primary-btn")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_process)
        self.start_btn.setGraphicsEffect(GlowEffect(color="#8b5cf6", blur=25))
        process_layout.addWidget(self.start_btn)
        
        main_layout.addWidget(process_frame)
        
        # 底部版权
        footer = QLabel("Powered by povideo • Python Office")
        footer.setStyleSheet("color: rgba(150, 150, 180, 0.6); font-size: 11px; padding: 5px;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def apply_effects(self):
        """应用视觉效果"""
        self.setStyleSheet(DARK_STYLE)
    
    def select_video(self):
        """选择视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv);;所有文件 (*)"
        )
        if file_path:
            self.video_path_edit.setText(file_path)
    
    def select_output_path(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_path_edit.setText(dir_path)
    
    def select_font(self):
        """选择字体文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择字体文件", "C:/Windows/Fonts", "字体文件 (*.ttf *.otf);;所有文件 (*)"
        )
        if file_path:
            self.font_type_edit.setText(file_path)
    
    def select_color(self):
        """选择字体颜色"""
        color = QColorDialog.getColor(QColor(self.font_color), self, "选择字体颜色")
        if color.isValid():
            self.font_color = color.name()
            self.color_preview.setStyleSheet(f"""
                background-color: {self.font_color};
                border: 2px solid rgba(100, 200, 255, 0.5);
                border-radius: 6px;
            """)
    
    def validate_inputs(self):
        """验证输入参数"""
        video_path = self.video_path_edit.text().strip()
        if not video_path:
            QMessageBox.warning(self, "⚠️ 警告", "请选择视频文件！")
            return False
        if not os.path.exists(video_path):
            QMessageBox.warning(self, "⚠️ 警告", "视频文件不存在！")
            return False
        
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "⚠️ 警告", "请设置输出路径！")
            return False
        
        output_name = self.output_name_edit.text().strip()
        if not output_name:
            QMessageBox.warning(self, "⚠️ 警告", "请设置输出文件名！")
            return False
        if not output_name.endswith('.mp4'):
            QMessageBox.warning(self, "⚠️ 警告", "输出文件名需以 .mp4 结尾！")
            return False
        
        watermark = self.watermark_edit.text().strip()
        if not watermark:
            QMessageBox.warning(self, "⚠️ 警告", "请输入水印文字！")
            return False
        
        font_type = self.font_type_edit.text().strip()
        if not os.path.exists(font_type):
            QMessageBox.warning(self, "⚠️ 警告", "字体文件不存在！")
            return False
        
        return True
    
    def start_process(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        output_path = self.output_path_edit.text().strip()
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        self.start_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("⏳ 正在处理，请稍候...")
        self.status_label.setStyleSheet("color: #f59e0b;")
        
        self.thread = VideoProcessThread(
            video_path=self.video_path_edit.text().strip(),
            output_path=output_path,
            output_name=self.output_name_edit.text().strip(),
            watermark_content=self.watermark_edit.text().strip(),
            font_size=self.font_size_spin.value(),
            font_type=self.font_type_edit.text().strip(),
            font_color=self.font_color
        )
        self.thread.finished.connect(self.on_process_finished)
        self.thread.start()
    
    def on_process_finished(self, success, message):
        """处理完成回调"""
        self.progress_bar.hide()
        self.start_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("✅ 处理完成！")
            self.status_label.setStyleSheet("color: #10b981;")
            QMessageBox.information(self, "🎉 成功", message)
        else:
            self.status_label.setText("❌ 处理失败")
            self.status_label.setStyleSheet("color: #ef4444;")
            QMessageBox.critical(self, "❌ 错误", message)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Mark2VideoApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
