import os
import sys
import json
import bpy

#Tellong Blender where the custom library is
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
import mars_lib

#Catch the JSON file passed from the AI Pipeline

argv = sys.argv
if "--" not in argv:
    print("❌ [ORCHESTRATOR ERROR]: No JSON payload provided!")
    print("Usage: blender -b -P orchestrator.py -- /path/to/payload.json")
    sys.exit(1)

#Get the filepath immediately after the '--'
json_filepath = argv[argv.index("--") + 1]

if not os.path.exists(json_filepath):
    print(f"❌ [ORCHESTRATOR ERROR]: Cannot find JSON file at {json_filepath}")
    sys.exit(1)


print(f"\n [ORCHESTRATOR] Reading AI payload from: {json_filepath}")
with open(json_filepath, 'r') as f:
    dynamic_payload = json.load(f)

#Clear the Blender Scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


print(" [ORCHESTRATOR] Firing MARS_LIB Engine...")
my_object = mars_lib.build_from_recipe(dynamic_payload)

bpy.context.view_layer.update()

#Export Logic
output_dir = "/content/drive/MyDrive/MARS/output/"
os.makedirs(output_dir, exist_ok=True)  

# Dynamically name 3D file based onJSON file name

base_name = os.path.basename(json_filepath).replace('.json', '')
output_path = os.path.join(output_dir, f"{base_name}.glb")

# Export the scene as a GLB
bpy.ops.export_scene.gltf(filepath=output_path)
print(f"\n✅ --- SUCCESS: 3D MODEL GENERATED AND SAVED TO {output_path} ---")