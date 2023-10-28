import os
import subprocess
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QCheckBox, QGridLayout, QLineEdit, QLabel, QTextEdit, QListWidgetItem, QAbstractItemView
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class RunBlenderScriptThread(QThread):
    output = pyqtSignal(str)
    def run(self):
        # Placeholder for the real Blender script
        # This just emits output periodically to simulate a running Blender script
        for i in range(10):
            self.sleep(1)  # Replace with real processing
            self.output.emit(f'Processing... {i+1}0%')

class MeshProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mesh Processor')
        self.create_widgets()
        self.set_dark_theme()

    def create_widgets(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_directory)
        self.directory_label = QLabel('Directory: ')
        self.directory_entry = QLineEdit()

        self.file_list = QListWidget()

        self.apply_button = QPushButton('Apply')
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

        self.target_polygon_count_entry = QLineEdit("1.0")
        self.laplacian_smooth_lambda_factor_entry = QLineEdit("1.0")
        self.subdivision_levels_entry = QLineEdit("1.0")
        self.smoothing_factor_entry = QLineEdit("1.0")
        self.smoothing_iterations_entry = QLineEdit("1.0")
        self.crisp_edge_bevel_width_entry = QLineEdit("1.0")

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

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

        # self.setWindowTitle('Mesh Processor')
        # self.setGeometry(200, 200, 600, 400)

        # # Create main widget and set as central widget
        # self.main_widget = QWidget()
        # self.setCentralWidget(self.main_widget)

        # self.layout = QVBoxLayout(self.main_widget)

        # # Create and add widgets to layout
        # self.directory_label = QLabel('Directory:', self)
        # self.layout.addWidget(self.directory_label)

        # self.directory_entry = QLineEdit(self)
        # self.layout.addWidget(self.directory_entry)

        # self.directory_button = QPushButton('Browse', self)
        # self.directory_button.clicked.connect(self.browse_directory)
        # self.layout.addWidget(self.directory_button)

        # self.file_list = QListWidget(self)
        # self.layout.addWidget(self.file_list)

        # self.apply_button = QPushButton('Apply', self)
        # self.apply_button.clicked.connect(self.apply)
        # self.layout.addWidget(self.apply_button)

        # self.select_all_button = QPushButton("Select all", self)
        # self.select_all_button.clicked.connect(self.select_all)
        # self.layout.addWidget(self.select_all_button)

        # self.deselect_all_button = QPushButton("Deselect all", self)
        # self.deselect_all_button.clicked.connect(self.deselect_all)
        # self.layout.addWidget(self.deselect_all_button)

        # # Initially disable buttons
        # self.apply_button.setEnabled(False)
        # self.select_all_button.setEnabled(False)
        # self.deselect_all_button.setEnabled(False)

        # # Set Dark color theme
        # self.set_dark_theme()
    # def browse_directory(self):
    #     self.directory = QFileDialog.getExistingDirectory()
    #     self.directory_entry.setText(self.directory)
    
    # Function to clear the file list
    def clear_file_list(self):
        self.file_list.clear()
        # self.file_selection.clear()
        # self.file_status.clear()
   
    # Function to remove selected files from the list
    def remove_selected_files(self):
        for item in self.file_list.selectedItems():
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            # self.file_selection.pop(row)
            # self.file_status.pop(row)

    def apply(self):
        self.thread = RunBlenderScriptThread()
        self.thread.output.connect(self.console_output.append)
        self.thread.start()
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select a directory', os.getenv('HOME'))
        if directory:
            self.directory_entry.setText(directory)
            self.file_list.clear()
            stl_files = [f for f in os.listdir(directory) if f.endswith('.stl')]
            for file in stl_files:
                item = QListWidgetItem(file)
                item.setCheckState(Qt.Checked)  # Qt.Checked = 2
                self.file_list.addItem(item)
            self.apply_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)

    # def apply(self):
    #     for index in range(self.file_list.count()):
    #         item = self.file_list.item(index)
    #         if item.checkState() == Qt.Checked:  # Qt.Checked = 2
    #             filepath = os.path.join(self.directory_entry.text(), item.text())
    #             print(f"Processing file: {filepath}")
    #             thread = threading.Thread(target=self.run_blender_script(filepath, self.directory_entry.text(), item.text()))
    #             thread.start()

    def run_blender_script(self, filepath, directory_path, filename):
        # if self.cancelled:
        #     self.cancelled = False
        #     return
        target_polygon_count = self.target_polygon_count_entry.get()
        laplacian_smooth_lambda_factor = self.laplacian_smooth_lambda_factor_entry.get()
        subdivision_levels = self.subdivision_levels_entry.get()
        smoothing_factor = self.smoothing_factor_entry.get()
        smoothing_iterations = self.smoothing_iterations_entry.get()
        crisp_edge_bevel_width = self.crisp_edge_bevel_width_entry.get()

        safe_filepath = filepath.replace('\\', '\\\\')  # replace single backslashes with double backslashes
        safe_directory_path = directory_path.replace('\\', '\\\\')
        blender_script = f"""
import bpy
import sys
import os
import time

target_polygon_count = {target_polygon_count}
laplacian_smooth_lambda_factor = {laplacian_smooth_lambda_factor}
subdivision_levels = {subdivision_levels}
smoothing_factor = {smoothing_factor}
smoothing_iterations = {smoothing_iterations}
crisp_edge_bevel_width = {crisp_edge_bevel_width}
# Clear all mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()
print("Processing file: ", "{filename}", flush=True)
file_start_time = time.time()
# Import STL file
start_time = time.time()
bpy.ops.import_mesh.stl(filepath=r"{safe_filepath}")

print("Time to import: ", time.time() - start_time, "seconds", flush=True)
# Get the current object
obj = bpy.context.active_object
print("Applying initial decimation...", flush=True)
start_time = time.time() 
# Decimate the model to 50k polygons
final_decimate_ratio = 250000 / len(obj.data.polygons)
bpy.ops.object.modifier_add(type='DECIMATE')
obj.modifiers["Decimate"].ratio = final_decimate_ratio
bpy.ops.object.modifier_apply(modifier="Decimate")
print("Time for initial decimation: ", time.time() - start_time, "seconds", flush=True)
print("Denoising the surface - Laplacian Smooth...", flush=True)
start_time = time.time()
# Denoise the surface using Laplacian Smooth
bpy.ops.object.modifier_add(type='LAPLACIANSMOOTH')
obj.modifiers["LaplacianSmooth"].lambda_factor = 0.1
bpy.ops.object.modifier_apply(modifier="LaplacianSmooth")
print("Time for Laplacian Smooth denoising: ", time.time() - start_time, "seconds", flush=True)
print("Applying subdivision surface modifier...", flush=True)
start_time = time.time()
# Dynamic subdivision (Subdivision Surface)
bpy.ops.object.modifier_add(type='SUBSURF')
obj.modifiers["Subdivision"].levels = 1 # Increase as needed
bpy.ops.object.modifier_apply(modifier="Subdivision")
print("Time for subdivision: ", time.time() - start_time, "seconds", flush=True)
print("Denoising the surface - Smooth...", flush=True)
start_time = time.time()
# Denoise the surface using Smooth
bpy.ops.object.modifier_add(type='SMOOTH')
obj.modifiers["Smooth"].factor = .5
obj.modifiers["Smooth"].iterations = 2
bpy.ops.object.modifier_apply(modifier="Smooth")
print("Time for denoising - Smooth: ", time.time() - start_time, "seconds", flush=True)

print("Making edges crisp...", flush=True)
start_time = time.time()
# Make edges more crisp
bpy.ops.object.modifier_add(type='BEVEL')
obj.modifiers["Bevel"].width = 0.01
bpy.ops.object.modifier_apply(modifier="Bevel")
print("Time for making edges crisp: ", time.time() - start_time, "seconds", flush=True)
print("Removing doubles and filling holes...", flush=True)
start_time = time.time()
# Clean up the mesh
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.remove_doubles()
bpy.ops.mesh.fill_holes()
bpy.ops.object.mode_set(mode = 'OBJECT')
print("Time for cleaning up the mesh: ", time.time() - start_time, "seconds", flush=True)
print("Applying final decimation...", flush=True)
start_time = time.time() 
# Decimate the model to 50k polygons
final_decimate_ratio = 250000 / len(obj.data.polygons)
bpy.ops.object.modifier_add(type='DECIMATE')
obj.modifiers["Decimate"].ratio = final_decimate_ratio
bpy.ops.object.modifier_apply(modifier="Decimate")
print("Time for final decimation: ", time.time() - start_time, "seconds", flush=True)
print("Exporting the processed STL...", flush=True)
start_time = time.time()
# Export the processed STL
bpy.ops.export_mesh.stl(filepath=os.path.join("{safe_directory_path}", "processed_" + "{filename}"))
print("Time for exporting: ", time.time() - start_time, "seconds", flush=True)
print("Time for processing: ", time.time() - file_start_time, "seconds", flush=True)
print("Done processing ", "{filename}", "\\n", flush=True)
# Clear all mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()
        """
        with open('blender_script.py', 'w') as f:
            f.write(blender_script)

        def run_script():
            process = subprocess.Popen(["blender", "-b", "-P", "blender_script.py"], stdout=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    if process.returncode == 0:
                        self.status_labels[filename].config(text="Complete", foreground="green")
                    else:
                        self.status_labels[filename].config(text="Error", foreground="red")
                    break
                if output:
                    print(output.strip())
                    self.output_text.insert('end', output)

        thread = threading.Thread(target=run_script)
        thread.start()

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