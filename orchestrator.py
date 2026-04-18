# testing if this works :D(PLEASE WORK)
# if i appear on github i hv been linked

import bpy

def create_mars_test():
    # 1. Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # 2. Add cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    
    # 3. Export (Ensure this folder exists in your Drive!)
    output_path = "/content/drive/MyDrive/MARS/output/mars_test_cube.glb"
    bpy.ops.export_scene.gltf(filepath=output_path)
    print("--- SUCCESS: 3D CUBE GENERATED ---")

if __name__ == "__main__":
    create_mars_test()

#I ONLY PUSH CHANGES TO ORCHETRATOR.PY