
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
def spawn_support(part, w, d, h, parent, main_shape="square", main_surface_z=1.0, main_surface_thick=0.05, armrest_z=None):
    """Spawns table legs, chair legs, or bed frame pillars."""
    
    count = part.get("count", 4)
    shape = clean_string(part.get("shape", "box"))
    thick = part.get("thickness_m", 0.05)
    
    y_pos_mod = clean_string(part.get("y_position", "center"))
    x_pos_mod = clean_string(part.get("x_position", "center"))
    
    # 🚨 THE STRUCTURAL HEURISTIC
    # Target height is armrest_z if it exists; otherwise, it's the seat (main_surface_z).
    target_z = armrest_z if armrest_z is not None else main_surface_z
    
    z_ratio = part.get("z_position_ratio", 1.0)
    if z_ratio <= 0.01:
        z_ratio = target_z
    
    if z_ratio <= target_z:
        # ALL 4 LEGS reach the highest structural point (Armrest or Seat)
        z_ratio = target_z
    else:
        # Trust AI for taller bedposts/decorative pillars
        pass

    # Calculate raw top height
    z_top = h * z_ratio 

    # 🚨 THE UNDERSIDE CUT
    # Chop height so it rests UNDER the object it supports rather than clipping through.
    if armrest_z is not None and abs(z_ratio - armrest_z) < 0.02:
        z_top -= 0.05 # Standard Armrest Thickness
    elif abs(z_ratio - main_surface_z) < 0.02:
        z_top -= main_surface_thick

    # --- X/Y Geometry Math ---
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
    
    # 1. Clean Data
    shape = clean_string(part.get("shape", "disc"))
    thick = 0.04  # Bases are generally thin plates
    
    # 🚨 SELF-HEALING AUTO-CLAMP: 
    # If the AI forgets scale_w, default it to 0.5 (50% of table width).
    # Even if the AI asks for a massive base, clamp it at 0.65 so it never tips over but never looks like a UFO pad.
    raw_scale = part.get("scale_w", 0.5)
    base_scale = min(raw_scale, 0.65) 
    
    # 🚨 FIX 1: Symmetry Lock + Safe Scale. 
    # Floor bases (discs/stars) must be perfectly symmetrical so they don't tip over.
    # We lock the overall size to the smallest dimension, then apply our safe scale.
    diameter = min(w, d) * base_scale

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


def spawn_backrest(part, w, d, h, parent, seat_z):
    """
    Spawns a vertical backrest that sits flush on top of the seat surface
    and aligns perfectly with the rear edge of the bounding box.
    """
    
    # 1. Base Dimensions
    # A standard wooden/padded backrest is about 5cm thick.
    thick = part.get("thickness_m", 0.05) 
    
    # We allow the AI to scale the width (e.g., if it wants a narrow backrest), 
    # but it defaults to the full width of the chair.
    scale_w = w * part.get("scale_w", 1.0) 
    
    # 2. The Architectural Math
    # The backrest doesn't start at the floor; it starts on top of the seat.
    # So, its total height is the bounding box height minus the seat height.
    back_height = h - seat_z 

    # 3. Geometry Generation
    back = butil.spawn_cube(size=1)
    back.name = "MARS_Backrest"
    
    # Scale X (Width), Y (Thickness), Z (Height)
    back.scale = (scale_w, thick, back_height)
    
    # 4. Y-Axis Positioning (The "Flush Back" Math)
    # The absolute back of the bounding box is at (d / 2).
    # Since the origin point of the cube is perfectly in its center, 
    # placing it at (d / 2) would leave exactly half of it hanging off the edge in thin air.
    # We pull it inward by half its own thickness so the back face sits flush.
    y_off = (d / 2) - (thick / 2)
    
    # 5. Z-Axis Positioning (The "Stacking" Math)
    # The bottom of the backrest needs to touch 'seat_z'.
    # Because the origin point is in the center, we start at 'seat_z' 
    # and shift UP by exactly half the height of the backrest.
    z_off = seat_z + (back_height / 2)
    
    # Apply locations (X is 0 so it stays perfectly centered left-to-right)
    back.location = (0, y_off, z_off)
    back.parent = parent
    
    # 6. Universal Polish
    butil.modify_mesh(back, type='BEVEL', width=0.01, segments=3)

def spawn_armrest(part, w, d, h, parent, seat_z):
    """
    Spawns two horizontal armrests spanning the depth of the chair,
    anchored to the extreme left/right edges and sitting halfway up the backrest.
    """
    
    # 1. Base Dimensions
    # We look for a thickness, defaulting to 5cm for standard armrests.
    thick = part.get("thickness_m", 0.05)
    
    # We need the backrest thickness to ensure the armrests don't clip through it.
    # We use our standard 5cm here to perfectly match the spawn_backrest logic.
    backrest_thick = 0.05 
    
    # 2. Z-Axis Positioning (The "Height" Math)
    # The armrest needs to sit halfway between the seat and the very top of the chair.
    backrest_height = h - seat_z
    arm_z = seat_z + (backrest_height * 0.5)
    
    # 3. Y-Axis Positioning & Length (The "Depth" Math)
    # The armrest spans the whole depth of the chair, MINUS the backrest.
    # If we didn't subtract the backrest thickness, the arm would poke out the back!
    arm_length = d - backrest_thick
    
    # Because we chopped off the backrest thickness, we have to shift the armrest 
    # slightly forward so it perfectly touches the backrest without clipping inside it.
    y_off = -(backrest_thick / 2)
    
    # 4. Spawning the Left and Right Arms
    for side, x_mult in [("Left", -1), ("Right", 1)]:
        arm = butil.spawn_cube(size=1)
        arm.name = f"MARS_Armrest_{side}"
        
        # Scale: Width (X), Depth/Length (Y), Thickness (Z)
        arm.scale = (thick, arm_length, thick) 
        
        # 5. X-Axis Positioning (The "Edge" Math)
        # Push to the boundary (w / 2), then pull it back inward by half its own 
        # thickness so the outer edge sits perfectly flush with the bounding box.
        x_off = ((w / 2) - (thick / 2)) * x_mult
        
        arm.location = (x_off, y_off, arm_z)
        arm.parent = parent
        
        # Universal Polish
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

    # 🚨 PRE-SCAN: Find shape, seat height, AND calculate armrest height
    recipe = payload.get("component_recipe", [])
    main_shape = "square" 
    main_surface_z = 1.0 
    main_surface_thick = 0.05
    has_armrest = False

    for part in recipe:
        ptype = clean_string(part.get("type", ""))
        if ptype == "surface":
            main_shape = clean_string(part.get("shape", "square"))
            main_surface_z = part.get("z_position_ratio", 1.0) 
            # Capture thickness for support cutting
            main_surface_thick = h * part.get("thickness_ratio", 0.05)
        elif ptype == "armrest":
            has_armrest = True

    # Calculate armrest height (halfway between seat and top)
    armrest_z = None
    if has_armrest:
        armrest_z = main_surface_z + ((1.0 - main_surface_z) * 0.5)

    # THE LOOP
    for part in recipe:
        ptype = clean_string(part.get("type", "unknown"))
        
        if ptype == "surface":
            print(f"    Spawning Surface (Z: {part.get('z_position_ratio')})")
            spawn_surface(part, w, d, h, master_parent)
            
        elif ptype == "support":
            print(f"    Spawning Support ({part.get('count')} {part.get('shape')}s)")
            # 🚨 PASSING armrest_z so legs reach the armrest height
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

