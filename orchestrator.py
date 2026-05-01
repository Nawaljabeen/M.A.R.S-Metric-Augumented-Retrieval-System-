import os
import sys
import bpy

# 1. Tell Blender where the custom library is
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
import mars_lib


# 3. Trigger Execution
test_payload = {
    "overall_bounding_box": {
        "width_m": 0.45,
        "depth_m": 0.32,
        "height_m": 0.65
    },
    "component_recipe": [
        {
            "type": "surface",
            "shape": "oval",
            "is_cushion": False,
            "z_position_ratio": 0.45,
            "thickness_ratio": 0.03
        },
        {
            "type": "support",
            "count": 4,
            "shape": "cylinder",
            "pitch_angle": 7,
            "thickness_m": 0.04
        },
        {
            "type": "backrest",
            "is_cushion": False,
            "pitch_angle": 5,
            "z_position_ratio": 0.7,
            "thickness_m": 0.03,
            "scale_w": 0.8,
            "y_position": "back"
        }
    ]
}

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

my_object = mars_lib.build_from_recipe(test_payload)

bpy.context.view_layer.update()
# 1. Clear scene

output_dir = "/content/drive/MyDrive/MARS/output/"
os.makedirs(output_dir, exist_ok=True)  # Safety net: creates the folder if it's missing

output_path = os.path.join(output_dir, "mars_woodchair.glb")

# Export the scene as a GLB
bpy.ops.export_scene.gltf(filepath=output_path)
print(f"\n✅ --- SUCCESS: 3D TABLE GENERATED AND SAVED TO {output_path} ---")