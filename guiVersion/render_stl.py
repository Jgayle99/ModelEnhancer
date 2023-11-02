import subprocess
import threading
import os

def generate_blender_script(file, output_image_path):
    safe_stlpath = file.replace('\\', '\\\\')
    safe_imagepath = output_image_path.replace('\\', '\\\\')

    blender_script = f"""
import bpy
from mathutils import Vector

def set_camera_and_light(obj):
    # Set camera
    cam_data = bpy.data.cameras.new(name='Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Fit camera to object
    bpy.context.view_layer.objects.active = cam
    cam.select_set(True)
    obj.select_set(True)
    bpy.ops.view3d.camera_to_view_selected()
    cam.select_set(False)
    obj.select_set(False)

    # Set light
    light_data = bpy.data.lights.new(name="Light", type='SUN')
    light = bpy.data.objects.new(name="Light", object_data=light_data)
    bpy.context.collection.objects.link(light)
    light.location = (5, -5, 5)
    light_data.energy = 2  # Increase light intensity


stl_file_path = r"{safe_stlpath}"
output_image_path = r"{safe_imagepath}"

# Clear existing data
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import STL
bpy.ops.import_mesh.stl(filepath=stl_file_path)
imported_obj = bpy.context.selected_objects[0]

# Center object at origin and print dimensions
imported_obj.location = Vector((0.0, 0.0, 0.0))
print("Imported object dimensions:", imported_obj.dimensions)

# Create a new material
mat = bpy.data.materials.new(name="Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
assert bsdf is not None
# Set the material color (can be adjusted)
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)  # Light grey
bsdf.inputs['Roughness'].default_value = 0.5  # Adjust for different surface characteristics
bsdf.inputs['Specular'].default_value = 0.5  # Adjust for specular highlights
# Enable backface culling
mat.use_backface_culling = True
# Append material to the object
imported_obj.data.materials.append(mat)


# Setup camera and light
set_camera_and_light(imported_obj)

# Render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.eevee.use_gtao = True  # Enable Ambient Occlusion
bpy.context.scene.eevee.gtao_factor = 1.5  # Adjust AO factor for more pronounced effect
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = output_image_path
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.ops.render.render(write_still=True)
"""
    return blender_script



def run_render_script(file, update_status_callback):
    # Extract the directory, filename without extension, and then construct the new path
    directory, filename = os.path.split(file)
    filename_without_ext = os.path.splitext(filename)[0]
    output_image_path = os.path.join(directory, filename_without_ext + ".png")


    blender_script = generate_blender_script(file, output_image_path)

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
                    update_status_callback(filename, "Error")
                break
            if output:
                print(output.strip())
                # Use callback for UI updates instead of direct interaction

    thread = threading.Thread(target=run_script)
    thread.start()
