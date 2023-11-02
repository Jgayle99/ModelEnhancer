import subprocess
import threading

def generate_blender_script(
    filepath, directory_path, filename, 
    target_polygon_count, laplacian_smooth_lambda_factor, 
    subdivision_levels, smoothing_factor, smoothing_iterations, 
    crisp_edge_bevel_width 
):
    # Replace file paths for safety...
    safe_filepath = filepath.replace('\\', '\\\\')
    safe_directory_path = directory_path.replace('\\', '\\\\')
    # The script content for Blender...
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
# Write a '.done' file to indicate processing completion
done_file_path = os.path.join(r"{safe_directory_path}", "{filename}.done")
with open(done_file_path, 'w') as done_file:
    done_file.write('done')
   """
    return blender_script

def run_blender_script(
    filepath, directory_path, filename,
    target_polygon_count, laplacian_smooth_lambda_factor,
    subdivision_levels, smoothing_factor, smoothing_iterations,
    crisp_edge_bevel_width, update_status_callback
):
    blender_script = generate_blender_script(
        filepath, directory_path, filename, 
        target_polygon_count, laplacian_smooth_lambda_factor, 
        subdivision_levels, smoothing_factor, smoothing_iterations, 
        crisp_edge_bevel_width
    )

    def run_script():
        command = ['blender', '--background', '--python-expr', blender_script]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                if process.returncode == 0:
                    update_status_callback(filename, "Complete")
                else:
                    update_status_callback(filename, "Error", "red")
                break
            if output:
                print(output.strip())
                # Use callback for UI updates instead of direct interaction

    thread = threading.Thread(target=run_script)
    thread.start()
