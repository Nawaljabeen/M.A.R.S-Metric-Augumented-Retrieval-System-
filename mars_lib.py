
import bpy
import math
from infinigen import butil


import math
import bpy
from infinigen import butil

def clean_string(s):
    """Safety rail to fix messy AI strings."""
    return str(s).lower().strip()

def spawn_surface(part, w, d, h, parent):
    """Spawns flat structural boards, shelves, or hard seats."""
    
    #Clean & Extract Math
    shape = clean_string(part.get("shape", "square"))
    thick = h * part.get("thickness_ratio", 0.05)
    z_pos = h * part.get("z_position_ratio", 1.0)
    
    scale_w = w * part.get("scale_w", 1.0)
    scale_d = d * part.get("scale_d", 1.0)

    #PROPORTION LOCK (for circles)
    if shape == "circular":
        diameter = min(scale_w, scale_d)
        scale_w = diameter
        scale_d = diameter

    
    if shape in ["circular", "oval"]:
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        surf = bpy.context.active_object
        
        
        surf.scale = (scale_w / 2, scale_d / 2, 1) 
    else:
        
        surf = butil.spawn_cube(size=1)
        surf.scale = (scale_w, scale_d, thick)

    surf.name = f"MARS_Surface_{z_pos}"
    
   
    y_off = 0
    y_pos_mod = clean_string(part.get("y_position", "center"))
    if y_pos_mod == "front":
        y_off = -(d / 2) + (thick / 2)
    elif y_pos_mod == "back":
        y_off = (d / 2) - (thick / 2)

    surf.location = (0, y_off, z_pos + (thick / 2))
    surf.parent = parent

   
    angle = part.get("pitch_angle", 0)
    if angle != 0:
        surf.rotation_euler = (math.radians(angle), 0, 0)

    #INFINIGEN BEVEL
   
    butil.modify_mesh(surf, type='BEVEL', width=0.01, segments=3)

def spawn_support(part, w, d, h, parent, main_shape="square", main_surface_z=1.0, main_surface_thick=0.05, armrest_z=None):
    """Spawns table legs, chair legs, or bed frame pillars."""
    
    count = part.get("count", 4)
    shape = clean_string(part.get("shape", "box"))
    thick = part.get("thickness_m", 0.05)
    
    y_pos_mod = clean_string(part.get("y_position", "center"))
    x_pos_mod = clean_string(part.get("x_position", "center"))
    
    
    target_z = armrest_z if armrest_z is not None else main_surface_z
    
    
    z_ratio = part.get("z_position_ratio", 0.0)
    
    if z_ratio <= 0.01:
        z_ratio = target_z
    
    if z_ratio <= target_z:
      
        z_ratio = target_z
    else:
      
        pass

    
    z_top = h * z_ratio 

    if armrest_z is not None and abs(z_ratio - armrest_z) < 0.02:
        
        z_top -= 0.025 
    
 

   
    if main_shape in ["circular", "oval", "round"]:

        x_off = ((w / 2) * 0.707) - (thick / 2) - 0.01
        y_off = ((d / 2) * 0.707) - (thick / 2) - 0.01
    else:
        x_off = (w / 2) - (thick / 2) - 0.01
        y_off = (d / 2) - (thick / 2) - 0.01

    locations = []
    if count == 4:
        locations = [
            (x_off, y_off, z_top/2), 
            (-x_off, y_off, z_top/2), 
            (x_off, -y_off, z_top/2), 
            (-x_off, -y_off, z_top/2)
        ]
    elif count == 2:
        if x_pos_mod == "right":
            locations = [(x_off, y_off, z_top/2), (x_off, -y_off, z_top/2)] 
        elif x_pos_mod == "left":
            locations = [(-x_off, y_off, z_top/2), (-x_off, -y_off, z_top/2)] 
        elif y_pos_mod == "back":
            locations = [(x_off, y_off, z_top/2), (-x_off, y_off, z_top/2)]
        elif y_pos_mod == "front":
            locations = [(x_off, -y_off, z_top/2), (-x_off, -y_off, z_top/2)]
        else:
            locations = [(x_off, 0, z_top/2), (-x_off, 0, z_top/2)] 
    elif count == 3:
        locations = [(x_off, y_off, z_top/2), (-x_off, y_off, z_top/2), (0, -y_off, z_top/2)]
    else:
        locations = [(0, 0, z_top/2)] 

    for i, loc in enumerate(locations):
        if shape in ["cylinder", "circular", "round"]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=thick/2, depth=z_top)
            leg = bpy.context.active_object
        else:
            leg = butil.spawn_cube(size=1)
            leg.scale = (thick, thick, z_top)

        leg.name = f"MARS_Support_{i+1}"
        leg.location = loc
        leg.parent = parent
        butil.modify_mesh(leg, type='BEVEL', width=0.005, segments=2)

def spawn_storage_box(part, w, d, h, parent):
    """Spawns a solid geometric volume for cabinets, dressers, or desk pedestals."""
    
    #Clean & Extract Data
    shape = clean_string(part.get("shape", "box"))
    thick = h * part.get("thickness_ratio", 0.5) 
    z_pos = h * part.get("z_position_ratio", 0.0) 
    
    scale_w = w * part.get("scale_w", 1.0)
    scale_d = d * part.get("scale_d", 1.0)


    x_off = 0
    x_pos_mod = clean_string(part.get("x_position", "center"))
    if x_pos_mod == "left":
        x_off = -(w / 2) + (scale_w / 2)
    elif x_pos_mod == "right":
        x_off = (w / 2) - (scale_w / 2)


    y_off = 0
    y_pos_mod = clean_string(part.get("y_position", "center"))
    if y_pos_mod == "front":
        y_off = -(d / 2) + (scale_d / 2)
    elif y_pos_mod == "back":
        y_off = (d / 2) - (scale_d / 2)

    
    if shape in ["cylinder", "circular", "oval"]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        box = bpy.context.active_object
        box.scale = (scale_w / 2, scale_d / 2, 1)
    else:
        box = butil.spawn_cube(size=1)
        box.scale = (scale_w, scale_d, thick)

    box.name = f"MARS_Storage_{z_pos}"
    
    
    box.location = (x_off, y_off, z_pos + (thick / 2)) 
    box.parent = parent

   
    butil.modify_mesh(box, type='BEVEL', width=0.005, segments=3)

def spawn_base(part, w, d, h, parent):
    """Spawns floor mounts like flat discs or crossed stars."""
    
    # 1. Clean Data
    shape = clean_string(part.get("shape", "disc"))
    thick = 0.04  
  
    raw_scale = part.get("scale_w", 0.5)
    base_scale = min(raw_scale, 0.65) 
    
    
    diameter = min(w, d) * base_scale

   
    base_anchor = butil.spawn_cube(size=0.001) 
    base_anchor.name = "MARS_Base_Anchor"
    base_anchor.location = (0, 0, thick / 2) 
    base_anchor.parent = parent

   
    if shape in ["disc", "circular", "circle"]:
      
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        disc = bpy.context.active_object
        disc.name = "MARS_Base_Disc"
        
        
        disc.scale = (diameter / 2, diameter / 2, 1) 
        disc.parent = base_anchor
        
        
        butil.modify_mesh(disc, type='BEVEL', width=0.005, segments=3)
        
    elif shape in ["star", "cross"]:
        
        for i, rot in enumerate([0, 90]):
            leg = butil.spawn_cube(size=1)
            leg.name = f"MARS_Base_Prong_{i+1}"
            
            
            leg.scale = (diameter, 0.06, thick)
            leg.rotation_euler = (0, 0, math.radians(rot))
            leg.parent = base_anchor
            
            
            butil.modify_mesh(leg, type='BEVEL', width=0.005, segments=3)

def spawn_backrest(part, w, d, h, parent, seat_z):
    """
    Spawns a vertical backrest that sits flush on top of the seat surface
    and aligns perfectly with the rear edge of the bounding box.
    """
    
  
    thick = part.get("thickness_m", 0.05) 
    scale_w = w * part.get("scale_w", 1.0) 
    
 
    seat_z_m = h * seat_z
    
   
    back_height = h - seat_z_m 

  
    back = butil.spawn_cube(size=1)
    back.name = "MARS_Backrest"
    
 
    back.scale = (scale_w, thick, back_height)
    
   
    y_off = (d / 2) - (thick / 2)
    
   
    z_off = seat_z_m + (back_height / 2)
    
   
    back.location = (0, y_off, z_off)
    back.parent = parent
    
   
    butil.modify_mesh(back, type='BEVEL', width=0.01, segments=3)

def spawn_armrest(part, w, d, h, parent, seat_z):
    """
    Spawns two horizontal armrests spanning the depth of the chair,
    anchored to the extreme left/right edges and sitting halfway up the backrest.
    """
    
    thick = part.get("thickness_m", 0.05)
    backrest_thick = 0.05 
   
    seat_z_m = h * seat_z
 
    backrest_height = h - seat_z_m
    arm_z = seat_z_m + (backrest_height * 0.5)
    
   
    arm_length = d - backrest_thick
    y_off = -(backrest_thick / 2)
    
   
    for side, x_mult in [("Left", -1), ("Right", 1)]:
        arm = butil.spawn_cube(size=1)
        arm.name = f"MARS_Armrest_{side}"
        
      
        arm.scale = (thick, arm_length, thick) 
        
      
        x_off = ((w / 2) - (thick / 2)) * x_mult
        
        arm.location = (x_off, y_off, arm_z)
        arm.parent = parent
        
       
        butil.modify_mesh(arm, type='BEVEL', width=0.01, segments=3)

def build_from_recipe(payload):
    print("\n [MARS_LIB] Initializing Universal Assembly...")
    
    bbox = payload.get("overall_bounding_box", {})
    w = bbox.get("width_m", 1.0)
    d = bbox.get("depth_m", 1.0)
    h = bbox.get("height_m", 1.0)

    master_parent = butil.spawn_cube(size=0.001)
    master_parent.name = "MARS_Root"
    master_parent.location = (0, 0, 0) 

   
    recipe = payload.get("component_recipe", [])
    main_shape = "square" 
    main_surface_z = 0.0 
    main_surface_thick = 0.05
    has_armrest = False

    for part in recipe:
        ptype = clean_string(part.get("type", ""))
        
        if ptype == "surface":
            current_z = part.get("z_position_ratio", 1.0)
            
           
            if current_z >= main_surface_z:
                main_surface_z = current_z
                main_shape = clean_string(part.get("shape", "square"))
               
                main_surface_thick = h * part.get("thickness_ratio", 0.05)
                
        elif ptype == "armrest":
            has_armrest = True

   
    armrest_z = None
    if has_armrest:
        armrest_z = main_surface_z + ((1.0 - main_surface_z) * 0.5)

   
    for part in recipe:
        ptype = clean_string(part.get("type", "unknown"))
        
        if ptype == "surface":
            print(f"    Spawning Surface (Z: {part.get('z_position_ratio')})")
            spawn_surface(part, w, d, h, master_parent)
            
        elif ptype == "support":
            print(f"    Spawning Support ({part.get('count')} {part.get('shape')}s)")
           
            spawn_support(part, w, d, h, master_parent, main_shape, main_surface_z, main_surface_thick, armrest_z)
            
        elif ptype == "backrest":
            print(f"    Spawning Backrest")
            spawn_backrest(part, w, d, h, master_parent, main_surface_z)

        elif ptype == "armrest":
            print(f"    Spawning Armrests")
            spawn_armrest(part, w, d, h, master_parent, main_surface_z)

        elif ptype == "storage_box":
            print(f"    Spawning Storage ({part.get('x_position')})")
            spawn_storage_box(part, w, d, h, master_parent)
            
        elif ptype == "base":
            print(f"    Spawning Base ({part.get('shape')})")
            spawn_base(part, w, d, h, master_parent)
            
        else:
            print(f" ⚠️ WARNING: AI hallucinated unknown component: {ptype}")

    print("[MARS_LIB] Assembly complete!")
    return master_parent