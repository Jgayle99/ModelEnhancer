import os
import time
import sys
import subprocess
from tkinter import messagebox
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QCheckBox, QGridLayout, QLineEdit, QLabel, QTextEdit, QListWidgetItem, QAbstractItemView
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QEventLoop
from PyQt5.QtCore import QSemaphore
from blender_script_utils import run_blender_script
from render_stl import run_render_script

def check_processing_complete_flag(filepath):
    """
    Check if the .done file exists for the given filepath.
    """
    # Assuming the status file is named as '[filename].done'
    status_file = f"{filepath}.done"
    return os.path.exists(status_file)

class RunBlenderScriptThread(QThread):
    output = pyqtSignal(str)
    # Add a flag to control the execution
    _is_running = True

    def stop(self):  # Method to signal the thread to stop
        self._is_running = False

    def __init__(self, filepath, value_fields, update_status, parent=None):
        super(RunBlenderScriptThread, self).__init__(parent)
        self.filepath = filepath
        self.value_fields = value_fields
        self.update_status = update_status

    def run(self):
        file_name = os.path.basename(self.filepath)
        start_time = time.time()  # Capture start time
        self.output.emit(f'Processing file {file_name}')
        # Extract values from the UI
        directory = self.value_fields['directory_entry'].text()
        smoothing_factor = float(self.value_fields['smoothing_factor_entry'].text())
        smoothing_iterations = int(self.value_fields['smoothing_iterations_entry'].text())
        crisp_edge_bevel_width = float(self.value_fields['crisp_edge_bevel_width_entry'].text())
        target_polygon_count = int(self.value_fields['target_polygon_count_entry'].text())
        subdivision_levels = int(self.value_fields['subdivision_levels_entry'].text())
        laplacian_smooth_lambda_factor = float(self.value_fields['laplacian_smooth_lambda_factor_entry'].text())
        # Call the function with all required arguments
        run_blender_script(
            filepath=self.filepath,
            directory_path=directory,
            filename=os.path.basename(self.filepath),
            target_polygon_count = target_polygon_count,
            laplacian_smooth_lambda_factor = laplacian_smooth_lambda_factor,
            subdivision_levels = subdivision_levels,
            smoothing_factor=smoothing_factor,
            smoothing_iterations=smoothing_iterations,
            crisp_edge_bevel_width=crisp_edge_bevel_width,
            update_status_callback=self.update_status
        )
                    # Wait until the processing of the file is complete
        while not check_processing_complete_flag(self.filepath):
            time.sleep(1)  # Wait a bit before re-checking
        # Remove the .done files or they will interfere with the next batch
        os.remove(f"{self.filepath}.done")

        end_time = time.time()  # Capture end time
        runtime_seconds = end_time - start_time
        minutes, seconds = divmod(runtime_seconds, 60)
        self.output.emit(f"{file_name} completed in {int(minutes)} minutes and {int(seconds)} seconds.")

class RenderScriptThread(QThread):
    output = pyqtSignal(str)
    # Add a flag to control the execution
    _is_running = True

    def stop(self):  # Method to signal the thread to stop
        self._is_running = False

    def callRenderScript(self):
        run_render_script(file=self.file, update_status_callback=self.update_status)
        self.output.emit(f'Render completed successfully. File {self.file_name}')

    def __init__(self, file, update_status, parent=None):
        super(RenderScriptThread, self).__init__(parent)
        self.file = file
        self.file_name = os.path.basename(self.file)
        self.update_status = update_status

    def run(self):
        self.callRenderScript()



class MeshProcessorApp(QWidget):
    allThreadsFinished = pyqtSignal()  # Signal to indicate all threads in the batch have finished

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mesh Processor')
        self.create_widgets()
        self.set_dark_theme()
        self.concurrent_processing_count = 1  # Initialize the variable
        self.value_fields = {
            'directory_entry': self.directory_entry,
            'target_polygon_count_entry': self.target_polygon_count_entry,
            'laplacian_smooth_lambda_factor_entry': self.laplacian_smooth_lambda_factor_entry,
            'subdivision_levels_entry': self.subdivision_levels_entry,
            'smoothing_factor_entry': self.smoothing_factor_entry,
            'smoothing_iterations_entry': self.smoothing_iterations_entry,
            'crisp_edge_bevel_width_entry': self.crisp_edge_bevel_width_entry
        }
        self.thread_list = []  # Initialize a list to keep threads
        self.semaphore = QSemaphore(self.concurrent_processing_count)  # Set the limit for concurrent threads
        self.allThreadsFinished.connect(self.on_all_threads_finished)
        self.active_thread_count = 0
        self.batch_event_loop = QEventLoop()

    def create_widgets(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_directory)
        self.directory_label = QLabel('Directory: ')
        self.directory_entry = QLineEdit()
        self.file_list = QListWidget()

        self.apply_button = QPushButton('Process Selected')
        self.apply_button.clicked.connect(self.apply)
        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(self.close)

        self.select_all_button = QPushButton("Select all", self)
        self.select_all_button.clicked.connect(self.select_all)


        self.deselect_all_button = QPushButton("Deselect all", self)
        self.deselect_all_button.clicked.connect(self.deselect_all)
        # Clear list button
        self.clear_list_button = QPushButton('Clear List')
        self.clear_list_button.clicked.connect(self.clear_file_list)
        # Remove selected button
        self.remove_selected_button = QPushButton('Remove Selected')
        self.remove_selected_button.clicked.connect(self.remove_selected_files)

        self.target_polygon_count_entry = QLineEdit("250000")
        self.laplacian_smooth_lambda_factor_entry = QLineEdit("1.0")
        self.subdivision_levels_entry = QLineEdit("1")
        self.smoothing_factor_entry = QLineEdit("1.0")
        self.smoothing_iterations_entry = QLineEdit("2")
        self.crisp_edge_bevel_width_entry = QLineEdit("0.1")
        self.concurrent_processing_entry = QLineEdit("1")

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

        self.render_button = QPushButton('Render STL')
        self.render_button.clicked.connect(self.render_stl)
        # Labels for showing rendered images
        self.original_render_label = QLabel()
        self.processed_render_label = QLabel()

        grid_layout.addWidget(self.render_button, 9, 0)
        grid_layout.addWidget(self.original_render_label, 10, 0, 1, 2)
        grid_layout.addWidget(self.processed_render_label, 10, 2, 1, 2)

        grid_layout.addWidget(self.directory_label, 0, 0)
        grid_layout.addWidget(self.directory_entry, 0, 1)
        grid_layout.addWidget(self.browse_button, 0, 2)
        grid_layout.addWidget(QLabel('target_polygon_count:'), 1, 0)
        grid_layout.addWidget(self.target_polygon_count_entry, 1, 1)
        grid_layout.addWidget(QLabel('laplacian_smooth_lambda_factor:'), 2, 0)
        grid_layout.addWidget(self.laplacian_smooth_lambda_factor_entry, 2, 1)
        grid_layout.addWidget(QLabel('subdivision_levels:'), 3, 0)
        grid_layout.addWidget(self.subdivision_levels_entry, 3, 1)
        grid_layout.addWidget(QLabel('smoothing_factor:'), 4, 0)
        grid_layout.addWidget(self.smoothing_factor_entry, 4, 1)
        grid_layout.addWidget(QLabel('smoothing_iterations:'), 5, 0)
        grid_layout.addWidget(self.smoothing_iterations_entry, 5, 1)
        grid_layout.addWidget(QLabel('crisp_edge_bevel_width:'), 6, 0)
        grid_layout.addWidget(self.crisp_edge_bevel_width_entry, 6, 1)
        grid_layout.addWidget(QLabel('concurrent_processing:'), 1, 2)
        grid_layout.addWidget(self.concurrent_processing_entry, 1, 3)
        grid_layout.addWidget(self.crisp_edge_bevel_width_entry, 6, 1)
        grid_layout.addWidget(self.apply_button, 7, 0)
        grid_layout.addWidget(self.quit_button, 7, 1)
        grid_layout.addWidget(self.deselect_all_button, 8, 0)
        grid_layout.addWidget(self.select_all_button, 8, 1)
        grid_layout.addWidget(self.clear_list_button, 8, 2)
        grid_layout.addWidget(self.remove_selected_button, 8, 3)
        layout.addLayout(grid_layout)
        layout.addWidget(self.file_list)
        layout.addWidget(self.console_output)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setLayout(layout)

    def render_stl(self):
        # This function will be triggered when the render button is clicked
        # For now, let's just display some placeholder text
        self.original_render_label.setText("Original Rendered Image Here")
        self.processed_render_label.setText("Processed Rendered Image Here")

    def render_stl(self, filename):
        return


    def load_and_display_image(self, image_path, label):
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap)

    def render_stl(self):
        # Assuming you have a function to render STL and return the image paths
        original_image, processed_image = self.render_stl_images()
        self.load_and_display_image(original_image, self.original_render_label)
        self.load_and_display_image(processed_image, self.processed_render_label)

        self.concurrent_processing_count = int(self.concurrent_processing_entry.text())
        selected_files = [self.directory_entry.text() + '/' + self.file_list.item(index).text()
                          for index in range(self.file_list.count())
                          if self.file_list.item(index).checkState() == Qt.Checked]
        for file in selected_files:
            file_name = os.path.basename(file)
            self.update_status(file_name, "Pending")

        self.file_batches = list(self.chunk_file_list(selected_files,  self.concurrent_processing_count))

        for file_batch in self.file_batches:
            self.active_thread_count = len(file_batch)
            for file in file_batch:
                file_name = os.path.basename(file)
                self.update_status(file_name, "Processing")
                thread = RenderScriptThread(file, self.update_status)
                thread.finished.connect(thread.deleteLater)
                thread.finished.connect(lambda: self.thread_finished())
                thread.output.connect(self.console_output.append)
                self.thread_list.append(thread)
                thread.start()
            self.batch_event_loop.exec_()

    def render_stl_images(self):
        # Here, call your Blender script or any other rendering process
        # Then return the paths of the rendered images
        return "path/to/original_render.png", "path/to/processed_render.png"

    def update_status(self, filename, status):
        # Search for the item in the QListWidget using the stored filename
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.data(Qt.UserRole) == filename:  # Compare with the stored filename
                # Updating the item text with the new status
                item.setText(f"{filename} - {status}")
                break

    # Function to clear the file list
    def clear_file_list(self):
        self.file_list.clear()

    # Function to remove selected files from the list
    def remove_selected_files(self):
        # Go through the list backwards so you can remove items without affecting the indices of subsequent items
        for index in reversed(range(self.file_list.count())):
            item = self.file_list.item(index)
            # Check if the item's checkbox is checked
            if item.checkState() == Qt.Checked:
                self.file_list.takeItem(index)

    def chunk_file_list(self, files, size=3):
        """Yield successive size-sized chunks from files."""
        for i in range(0, len(files), size):
            yield files[i:i + size]

    def apply(self):
        self.concurrent_processing_count = int(self.concurrent_processing_entry.text())
        selected_files = [self.directory_entry.text() + '/' + self.file_list.item(index).text()
                          for index in range(self.file_list.count())
                          if self.file_list.item(index).checkState() == Qt.Checked]
        for file in selected_files:
            file_name = os.path.basename(file)
            self.update_status(file_name, "Pending")

        self.file_batches = list(self.chunk_file_list(selected_files,  self.concurrent_processing_count))

        for file_batch in self.file_batches:
            self.active_thread_count = len(file_batch)
            for file in file_batch:
                file_name = os.path.basename(file)
                self.update_status(file_name, "Processing")
                thread = RunBlenderScriptThread(file, self.value_fields, self.update_status)
                thread.finished.connect(thread.deleteLater)
                thread.finished.connect(lambda: self.thread_finished())
                thread.output.connect(self.console_output.append)
                self.thread_list.append(thread)
                thread.start()
            self.batch_event_loop.exec_()

    def thread_finished(self):
        self.active_thread_count -= 1
        if self.active_thread_count == 0:
            self.allThreadsFinished.emit()

    def on_all_threads_finished(self):
        self.batch_event_loop.exit()

    def remove_thread(self, thread):
        self.thread_list.remove(thread)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select a directory', os.getenv('HOME'))
        if directory:
            self.directory_entry.setText(directory)
            self.file_list.clear()
            stl_files = [f for f in os.listdir(directory) if f.endswith('.stl')]
            for file in stl_files:
                item = QListWidgetItem(file)
                filename=os.path.basename(file)
                item.setData(Qt.UserRole, filename)  # Store the original filename
                self.file_list.addItem(item)
                item.setCheckState(Qt.Checked)
                self.file_list.addItem(item)
            self.apply_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)


    def run(self):
        self.window.mainloop()

    def select_all(self):
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            item.setCheckState(Qt.Checked)

    def deselect_all(self):
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            item.setCheckState(Qt.Unchecked)

    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyleSheet("""
            QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
            QListWidget { color: #ffffff; }
            QPushButton { background-color: #353535; color: #ffffff; }
            QLineEdit { background-color: #353535; color: #ffffff; }
        """)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MeshProcessorApp()
    window.show()
    sys.exit(app.exec_())