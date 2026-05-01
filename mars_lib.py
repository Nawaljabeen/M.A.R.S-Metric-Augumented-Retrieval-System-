


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

    #GEOMETRY GENERATION (Cylinder Implementation)
    if shape in ["circular", "oval"]:
        # Spawn cylinder with reduced vertices (24 instead of 32 for optimal low-poly)
        # We set 'depth=thick' immediately so it's the correct height right out of the box.
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        surf = bpy.context.active_object
        
        # Scale X and Y. (Z is 1 because we already set depth=thick)
        surf.scale = (scale_w / 2, scale_d / 2, 1) 
    else:
        # Standard Infinigen Proxy Box
        surf = butil.spawn_cube(size=1)
        surf.scale = (scale_w, scale_d, thick)

    surf.name = f"MARS_Surface_{z_pos}"
    
    # Y-AXIS ALIGNMENT (Front, Back, Center)
    y_off = 0
    y_pos_mod = clean_string(part.get("y_position", "center"))
    if y_pos_mod == "front":
        y_off = -(d / 2) + (thick / 2)
    elif y_pos_mod == "back":
        y_off = (d / 2) - (thick / 2)

    surf.location = (0, y_off, z_pos - (thick / 2))
    surf.parent = parent

    # ROTATION (Pitch Angle for Backrests/Headboards)
    angle = part.get("pitch_angle", 0)
    if angle != 0:
        surf.rotation_euler = (math.radians(angle), 0, 0)

    #INFINIGEN BEVEL
    # Applies a clean, subtle edge bevel to both Cubes AND Cylinders.
    butil.modify_mesh(surf, type='BEVEL', width=0.01, segments=3)

# 🚨 FIX: Added main_surface_z parameter
def spawn_support(part, w, d, h, parent, main_shape="square", main_surface_z=1.0, main_surface_thick=0.05):
    """Spawns table legs, chair legs, or bed frame pillars."""
    
    count = part.get("count", 4)
    shape = clean_string(part.get("shape", "box"))
    thick = part.get("thickness_m", 0.05)
    
    # 🚨 GET BOTH X AND Y MODIFIERS!
    y_pos_mod = clean_string(part.get("y_position", "center"))
    x_pos_mod = clean_string(part.get("x_position", "center"))
    
    # UNDERSIDE CUT FIX
    # 🚨 SMART HEIGHT FIX
    z_ratio = part.get("z_position_ratio", 1.0)
    
    # Catch Pancake Legs (0.0) and snap them to the main surface
    if z_ratio <= 0.01:
        z_ratio = main_surface_z
        
    z_top = h * z_ratio
    
    # Only apply the "Underside Cut" if this specific support is 
    # intended to hold up the main surface!
    if z_ratio == main_surface_z:
        z_top -= main_surface_thick
    if main_shape in ["circular", "oval", "round"]:
        diameter = min(w, d)
        x_off = ((diameter / 2) * 0.707) - (thick / 2) - 0.01
        y_off = ((diameter / 2) * 0.707) - (thick / 2) - 0.01
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
        # 🚨 THE NEW DESK FIX IS HERE!
        if x_pos_mod == "right":
            locations = [(x_off, y_off, z_top/2), (x_off, -y_off, z_top/2)] # Both on right (front/back)
        elif x_pos_mod == "left":
            locations = [(-x_off, y_off, z_top/2), (-x_off, -y_off, z_top/2)] # Both on left (front/back)
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
    
    # 1. Clean & Extract Data
    shape = clean_string(part.get("shape", "box"))
    thick = h * part.get("thickness_ratio", 0.5) 
    z_pos = h * part.get("z_position_ratio", 0.0) # Default to floor level if missing
    
    scale_w = w * part.get("scale_w", 1.0)
    scale_d = d * part.get("scale_d", 1.0)

    # FIX 1: X-Axis Asymmetry (Left, Right, Center) with Clean String
    x_off = 0
    x_pos_mod = clean_string(part.get("x_position", "center"))
    if x_pos_mod == "left":
        x_off = -(w / 2) + (scale_w / 2)
    elif x_pos_mod == "right":
        x_off = (w / 2) - (scale_w / 2)

    # FIX 2: Y-Axis Asymmetry (Front, Back, Center)
    y_off = 0
    y_pos_mod = clean_string(part.get("y_position", "center"))
    if y_pos_mod == "front":
        y_off = -(d / 2) + (scale_d / 2)
    elif y_pos_mod == "back":
        y_off = (d / 2) - (scale_d / 2)

    #FIX 3: Geometry Generation (In case of a round laundry basket or cylindrical pedestal)
    if shape in ["cylinder", "circular", "oval"]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        box = bpy.context.active_object
        box.scale = (scale_w / 2, scale_d / 2, 1)
    else:
        box = butil.spawn_cube(size=1)
        box.scale = (scale_w, scale_d, thick)

    box.name = f"MARS_Storage_{z_pos}"
    
    # FIX 4: Z-Axis Clipping math
    # Assuming z_pos is the resting surface (like the floor), we shift UP by half thickness
    box.location = (x_off, y_off, z_pos + (thick / 2)) 
    box.parent = parent

    # fiX 5: Universal Infinigen Bevel
    butil.modify_mesh(box, type='BEVEL', width=0.005, segments=3)

def spawn_base(part, w, d, h, parent):
    """Spawns floor mounts like flat discs or crossed stars."""
    
    # 1. Clean Data & Proportion Lock
    shape = clean_string(part.get("shape", "disc"))
    thick = 0.04  # Bases are generally thin plates
    
    # 🚨 FIX 1: Symmetry Lock. 
    # Floor bases (discs/stars) must be perfectly symmetrical so they don't tip over.
    # We lock the overall size to the smallest dimension of the bounding box.
    diameter = min(w, d)

    # 2. Create an invisible anchor point on the floor
    base_anchor = butil.spawn_cube(size=0.001) 
    base_anchor.name = "MARS_Base_Anchor"
    base_anchor.location = (0, 0, thick / 2) # Prevents Z-axis floor clipping
    base_anchor.parent = parent

    # 3. Geometry Generation
    if shape in ["disc", "circular", "circle"]:
        # 🚨 FIX 2: Native optimized 24-vertex cylinder
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=thick)
        disc = bpy.context.active_object
        disc.name = "MARS_Base_Disc"
        
        # Scale X/Y to the locked radius. Z is 1 because depth is already set to 'thick'
        disc.scale = (diameter / 2, diameter / 2, 1) 
        disc.parent = base_anchor
        
        # 🚨 FIX 3: Universal Infinigen Bevel instead of manual shading loops
        butil.modify_mesh(disc, type='BEVEL', width=0.005, segments=3)
        
    elif shape in ["star", "cross"]:
        # A 4-pronged cross base (like an office chair)
        for i, rot in enumerate([0, 90]):
            leg = butil.spawn_cube(size=1)
            leg.name = f"MARS_Base_Prong_{i+1}"
            
            # 🚨 FIX 4: Use 'diameter' so both crossing prongs are the exact same length
            leg.scale = (diameter, 0.06, thick)
            leg.rotation_euler = (0, 0, math.radians(rot))
            leg.parent = base_anchor
            
            # 🚨 FIX 3: Universal Infinigen Bevel for the metal prongs
            butil.modify_mesh(leg, type='BEVEL', width=0.005, segments=3)

def build_from_recipe(payload):
    print("\n [MARS_LIB] Initializing Universal Assembly...")
    
    bbox = payload.get("overall_bounding_box", {})
    w = bbox.get("width_m", 1.0)
    d = bbox.get("depth_m", 1.0)
    h = bbox.get("height_m", 1.0)

    master_parent = butil.spawn_cube(size=0.001)
    master_parent.name = "MARS_Root"
    master_parent.location = (0, 0, 0) 

    # 🚨 FIX 1: Scan for both shape AND tabletop height!
    recipe = payload.get("component_recipe", [])
    main_shape = "square" 
    main_surface_z = 1.0 # Default
    for part in recipe:
        if clean_string(part.get("type", "")) == "surface":
            main_shape = clean_string(part.get("shape", "square"))
            # Grab the exact height the tabletop is sitting at
            main_surface_z = part.get("z_position_ratio", 1.0) 
            break 

    # THE LOOP
    for part in recipe:
        ptype = clean_string(part.get("type", "unknown"))
        
        if ptype == "surface":
            print(f"    Spawning Surface (Z: {part.get('z_position_ratio')})")
            spawn_surface(part, w, d, h, master_parent)
            
        elif ptype == "support":
            print(f"    Spawning Support ({part.get('count')} {part.get('shape')}s)")
            # 🚨 FIX: Pass BOTH the shape and the height down to the legs
            spawn_support(part, w, d, h, master_parent, main_shape, main_surface_z)
            
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


