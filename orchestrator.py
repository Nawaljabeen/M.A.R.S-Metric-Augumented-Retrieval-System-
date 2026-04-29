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
test_payload = {
    # --- FROM THE RAG DATABASE ---
    "overall_bounding_box": {
        "width_m": 1.0,   # (Flipped W and D so it matches the image's orientation)
        "depth_m": 0.75,  
        "height_m": 0.48
    },
    # --- FROM THE VISION AI ---
    "component_recipe": [
        # The Main Tabletop
        {
            "type": "surface", 
            "shape": "square", 
            "is_cushion": False, 
            "z_position_ratio": 1.0
        },
        # The Lower Shelf (Scaled down by 15% to fit between the legs)
        {
            "type": "surface", 
            "shape": "square", 
            "is_cushion": False, 
            "z_position_ratio": 0.3, 
            "scale_w": 0.85, 
            "scale_d": 0.85
        },
        # The 4 Chunky Legs
        {
            "type": "support", 
            "count": 4, 
            "shape": "box"
        }
    ]
}
my_object = mars_lib.build_from_recipe(test_payload)

bpy.context.view_layer.update()
# 1. Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
output_dir = "/content/drive/MyDrive/MARS/output/"
os.makedirs(output_dir, exist_ok=True)  # Safety net: creates the folder if it's missing

output_path = os.path.join(output_dir, "mars_test_table.glb")

# Export the scene as a GLB
bpy.ops.export_scene.gltf(filepath=output_path)
print(f"\n✅ --- SUCCESS: 3D TABLE GENERATED AND SAVED TO {output_path} ---")