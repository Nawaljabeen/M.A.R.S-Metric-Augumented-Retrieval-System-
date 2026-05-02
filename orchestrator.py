import os
import sys
import bpy


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    
import mars_lib



test_payload = {
    "overall_bounding_box": {
        "width_m": 1.6,
        "depth_m": 2.0,
        "height_m": 0.99
    },
    "component_recipe": [
        {
            "type": "surface",
            "shape": "square",
            "is_cushion": False,
            "z_position_ratio": 0.2,
            "scale_w": 1.0,
            "scale_d": 1.0,
            "thickness_ratio": 0.4
        },
        {
            "type": "surface",
            "shape": "square",
            "is_cushion": True,
            "z_position_ratio": 0.5,
            "scale_w": 0.9,
            "scale_d": 0.85,
            "thickness_ratio": 0.2
        },
        {
            "type": "backrest",
            "is_cushion": False,
            "z_position_ratio": 0.7,
            "thickness_m": 0.05,
            "scale_w": 1.0,
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

output_path = os.path.join(output_dir, "mars_brimnesbed2.glb")

# Export the scene as a GLB
bpy.ops.export_scene.gltf(filepath=output_path)
print(f"\n✅ --- SUCCESS: 3D TABLE GENERATED AND SAVED TO {output_path} ---")