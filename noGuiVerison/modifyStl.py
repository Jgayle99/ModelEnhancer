import bpy
import os
import time
# C:\Program Files\Blender Foundation\Blender 3.6
#  ./blender --background --python modifyStl.py
# Set the directory path
directory_path = "E:/scans/scripts/todo"

# Get a list of all files in directory
all_files = os.listdir(directory_path)

# Filter out all .stl files
stl_files = [f for f in all_files if f.endswith(".stl")]

for stl in stl_files:
    # Clear all mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    print("Processing file: ", stl, flush=True)

    # Import STL file
    start_time = time.time()
    bpy.ops.import_mesh.stl(filepath=os.path.join(directory_path, stl))
    print("Time to import: ", time.time() - start_time, "seconds", flush=True)

    # Get the current object
    obj = bpy.context.active_object

    print("Applying final decimation...", flush=True)
    start_time = time.time() 
    # Decimate the model to 50k polygons
    final_decimate_ratio = 250000 / len(obj.data.polygons)
    bpy.ops.object.modifier_add(type='DECIMATE')
    obj.modifiers["Decimate"].ratio = final_decimate_ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print("Time for final decimation: ", time.time() - start_time, "seconds", flush=True)

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

    print("Cleaning up the mesh...", flush=True)
    start_time = time.time()
    # Clean up the mesh
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.fill_holes()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    print("Time for cleaning up the mesh: ", time.time() - start_time, "seconds", flush=True)

    # print("Remeshing...", flush=True)
    # start_time = time.time()
    # Remeshing
    # bpy.ops.object.modifier_add(type='REMESH')
    # obj.modifiers["Remesh"].octree_depth = 5
    # obj.modifiers["Remesh"].use_smooth_shade = True
    # bpy.ops.object.modifier_apply(modifier="Remesh")
    # print("Time for remeshing: ", time.time() - start_time, "seconds", flush=True)

    print("Applying final decimation...", flush=True)
    start_time = time.time() 
    # Decimate the model to 50k polygons
    final_decimate_ratio = 250000 / len(obj.data.polygons)
    bpy.ops.object.modifier_add(type='DECIMATE')
    obj.modifiers["Decimate"].ratio = final_decimate_ratio
    bpy.ops.object.modifier_apply(modifier="Decimate")
    print("Time for final decimation: ", time.time() - start_time, "seconds", flush=True)

    # print("Adding Edge Split modifier...", flush=True)
    # start_time = time.time()
    # # Add Edge Split modifier
    # bpy.ops.object.modifier_add(type='EDGE_SPLIT')
    # obj.modifiers["EdgeSplit"].split_angle = 0.785398 # 45 degrees
    # bpy.ops.object.modifier_apply(modifier="EdgeSplit")
    # print("Time for Edge Split: ", time.time() - start_time, "seconds", flush=True)

    print("Exporting the processed STL...", flush=True)
    start_time = time.time()
    # Export the processed STL
    bpy.ops.export_mesh.stl(filepath=os.path.join(directory_path, "processed_" + stl))
    print("Time for exporting: ", time.time() - start_time, "seconds", flush=True)

    print("Done processing ", stl, "\n", flush=True)
