import bpy
import math
from infinigen import butil


def spawn_surface(part, w, d, h, parent):
    """Spawns flat boards, shelves, or soft cushions."""
    thick = h * part.get("thickness_ratio", 0.05)
    z_pos = h * part.get("z_position_ratio", 1.0)
    
    # AI can scale things down (e.g., a shelf that fits inside table legs)
    scale_w = w * part.get("scale_w", 1.0)
    scale_d = d * part.get("scale_d", 1.0)

    # 1. Spawn the base proxy
    surf = butil.spawn_cube(size=1)
    surf.name = f"MARS_Surface_{z_pos}"
    surf.scale = (scale_w, scale_d, thick)
    surf.location = (0, 0, z_pos - (thick / 2))
    surf.parent = parent

    # 2. ROTATION (Pitch Angle)
    angle = part.get("pitch_angle", 0)
    if angle != 0:
        surf.rotation_euler = (math.radians(angle), 0, 0)

    # 3. THE FINESSE: Is it a hard board or a soft cushion?
    if part.get("is_cushion", False):
        # Puff it up into a seat!
        subsurf = surf.modifiers.new(name="Smooth", type='SUBSURF')
        subsurf.levels = 3 
        
        cast = surf.modifiers.new(name="Puff", type='CAST')
        cast.cast_type = 'SPHERE'
        cast.factor = 0.6  # 0.0 is flat, 1.0 is a ball. 0.6 is a nice cushion.
        
        # Shade smooth for export
        for poly in surf.data.polygons:
            poly.use_smooth = True
            
    else:
        # It's a hard board: Add a subtle Bevel so the edges catch light
        bevel = surf.modifiers.new(name="Edge_Bevel", type='BEVEL')
        bevel.width = 0.01 # 1cm rounded edge
        bevel.segments = 3

def spawn_support(part, w, d, h, parent):
    """Spawns vertical or horizontal pillars (legs, stretchers)."""
    # If AI doesn't specify, default to 4 square legs
    count = part.get("count", 4)
    shape = part.get("shape", "box")
    
    thick = part.get("thickness_m", 0.05)
    z_top = h * part.get("z_position_ratio", 1.0) 

    # Math to push legs to the corners
    x_off = (w / 2) - (thick / 2) - 0.01
    y_off = (d / 2) - (thick / 2) - 0.01

    # Decide where to place them based on count and asymmetry
    locations = []
    x_pos_mod = part.get("x_position", "center") # left, right, or center

    if count == 4:
        locations = [
            (x_off, y_off, z_top / 2), (-x_off, y_off, z_top / 2),
            (x_off, -y_off, z_top / 2), (-x_off, -y_off, z_top / 2)
        ]
    elif count == 2 and x_pos_mod == "left":
        locations = [(-x_off, y_off, z_top / 2), (-x_off, -y_off, z_top / 2)]
    elif count == 2 and x_pos_mod == "right":
        locations = [(x_off, y_off, z_top / 2), (x_off, -y_off, z_top / 2)]
    elif count == 1:
        locations = [(0, 0, z_top / 2)] # Dead center (like a barstool)

    # Spawn them!
    for i, loc in enumerate(locations):
        if shape == "cylinder":
            leg = butil.spawn_cylinder(radius=thick/2, depth=z_top)
            # Make cylinders smooth
            for poly in leg.data.polygons:
                poly.use_smooth = True
        else:
            leg = butil.spawn_cube(size=1)
            leg.scale = (thick, thick, z_top)
            # Add finesse to box legs
            bevel = leg.modifiers.new(name="Edge_Bevel", type='BEVEL')
            bevel.width = 0.005
            bevel.segments = 2
            
        leg.name = f"MARS_Support_{i+1}"
        leg.location = loc
        leg.parent = parent


def spawn_storage_box(part, w, d, h, parent):
    """Spawns a solid geometric volume for cabinets, dressers, or desk pedestals."""
    # Storage is usually thick, so default to 50% of the total height
    thick = h * part.get("thickness_ratio", 0.5) 
    z_pos = h * part.get("z_position_ratio", 0.5)

    # Cabinets on desks usually don't take up the whole width
    scale_w = w * part.get("scale_w", 1.0)
    scale_d = d * part.get("scale_d", 1.0)

    # X-Axis Asymmetry (Left, Right, Center)
    x_off = 0
    x_pos_mod = part.get("x_position", "center")
    if x_pos_mod == "left":
        x_off = -(w / 2) + (scale_w / 2)
    elif x_pos_mod == "right":
        x_off = (w / 2) - (scale_w / 2)

    box = butil.spawn_cube(size=1)
    box.name = f"MARS_Storage_{z_pos}"
    box.scale = (scale_w, scale_d, thick)
    box.location = (x_off, 0, z_pos) # Shift left/right, and up
    box.parent = parent

    # Finesse: Give it a nice, manufactured edge
    bevel = box.modifiers.new(name="Edge_Bevel", type='BEVEL')
    bevel.width = 0.005
    bevel.segments = 3


def spawn_base(part, w, d, h, parent):
    """Spawns floor mounts like flat discs or crossed stars."""
    shape = part.get("shape", "disc")
    thick = 0.04 # Bases are generally thin plates
    
    # Create an invisible anchor point on the floor
    base_anchor = butil.spawn_cube(size=0.001) 
    base_anchor.name = "MARS_Base_Anchor"
    base_anchor.location = (0, 0, thick / 2)
    base_anchor.parent = parent

    if shape == "disc":
        # A heavy, flat circular plate
        disc = butil.spawn_cylinder(radius=w/2, depth=thick)
        disc.name = "MARS_Base_Disc"
        disc.parent = base_anchor
        # Shade smooth!
        for poly in disc.data.polygons: 
            poly.use_smooth = True
            
    elif shape == "star":
        # A 4-pronged cross base (like an office chair)
        for rot in [0, 90]:
            leg = butil.spawn_cube(size=1)
            leg.scale = (w, 0.06, thick)
            leg.rotation_euler = (0, 0, math.radians(rot))
            leg.parent = base_anchor


def build_from_recipe(payload):
    print("\n [MARS_LIB] Initializing Universal Assembly...")
    
    bbox = payload["overall_bounding_box"]
    w, d, h = bbox["width_m"], bbox["depth_m"], bbox["height_m"]

    # The Master Anchor (Everything glues to this)
    master_parent = butil.spawn_cube(size=0.001)
    master_parent.name = "MARS_Root"

    # THE LOOP
    for part in payload.get("component_recipe", []):
        ptype = part.get("type")
        
        if ptype == "surface":
            print(f"    Spawning Surface (Z: {part.get('z_position_ratio')})")
            spawn_surface(part, w, d, h, master_parent)
            
        elif ptype == "support":
            print(f"    Spawning Support ({part.get('count')} {part.get('shape')}s)")
            spawn_support(part, w, d, h, master_parent)
            
        elif ptype == "storage_box":
            print(f"    Spawning Storage ({part.get('x_position')})")
            spawn_storage_box(part, w, d, h, master_parent)
            
        elif ptype == "base":
            print(f"    Spawning Base ({part.get('shape')})")
            spawn_base(part, w, d, h, master_parent)
            
        else:
            print(f"   ⚠️ WARNING: AI hallucinated unknown component: {ptype}")

    print("✅ [MARS_LIB] Assembly complete!")
    return master_parent