import os
import sys
import bpy
# 1. Tell Blender where the custom library is
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
import mars_lib

# 2. The Data Payload
test_payload = {
    "category": "Tables & desks",
    "overall_bounding_box": {
        "width_m": 1.0,
        "depth_m": 0.75,
        "height_m": 0.48
    },
    "vision_heuristics": {
        "style_aesthetic": "industrial",
        "leg_shape": "square",
        "build_weight": "chunky",
        "backrest_style": "none",
        "has_armrests": False
    }
}

# 3. Trigger Execution
my_table = mars_lib.build_table(test_payload)


output_dir = "/content/drive/MyDrive/MARS/output/"
os.makedirs(output_dir, exist_ok=True)  # Safety net: creates the folder if it's missing

output_path = os.path.join(output_dir, "mars_test_table.glb")

# Export the scene as a GLB
bpy.ops.export_scene.gltf(filepath=output_path)
print(f"\n✅ --- SUCCESS: 3D TABLE GENERATED AND SAVED TO {output_path} ---")