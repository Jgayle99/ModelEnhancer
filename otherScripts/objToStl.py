import os
import trimesh

def convert_obj_to_stl(input_folder, output_folder):
    # Ensure output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through all files in the input directory
    for file in os.listdir(input_folder):
        if file.lower().endswith('.obj'):
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.stl')

            # Load STL file
            try:
                mesh = trimesh.load(input_file)
                # Export as OBJ
                mesh.export(output_file, file_type='stl')
                print(f"Converted '{input_file}' to '{output_file}'")
            except Exception as e:
                print(f"Error converting {input_file}: {e}")

# Set your folder paths here
input_folder = 'E:/scans/scripts/todo'
output_folder = 'E:/scans/scripts/todo'

convert_obj_to_stl(input_folder, output_folder)