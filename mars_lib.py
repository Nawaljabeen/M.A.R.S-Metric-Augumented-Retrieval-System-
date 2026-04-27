import bpy
# Assuming your infinigen folder is in the same directory
from infinigen import butil 

def build_table(payload):
    """
    Constructs a low-fidelity procedural table proxy using RAG metrics and Vision heuristics.
    """
    print("\n🔨 [MARS_LIB] Initializing Table Construction...")

    # 1. EXTRACT RAG METRICS (The Absolute Boundaries)
    bbox = payload["overall_bounding_box"]
    w = bbox["width_m"]
    d = bbox["depth_m"]
    h = bbox["height_m"]

    # 2. EXTRACT VISION HEURISTICS
    heuristics = payload["vision_heuristics"]
    weight = heuristics.get("build_weight", "standard")
    leg_shape = heuristics.get("leg_shape", "square")

    # 3. APPLY HEURISTIC MATH (The Safety Net)
    # We define exactly what "thin", "standard", and "chunky" mean in meters.
    weight_map = {
        "thin": {"top_thickness": 0.02, "leg_thickness": 0.03},
        "standard": {"top_thickness": 0.04, "leg_thickness": 0.05},
        "chunky": {"top_thickness": 0.08, "leg_thickness": 0.10}
    }
    
    # Safely grab the math, default to "standard" if the AI hallucinated a weird word
    math_profile = weight_map.get(weight, weight_map["standard"])
    top_thick = math_profile["top_thickness"]
    leg_thick = math_profile["leg_thickness"]

    # Calculate leg height perfectly so they touch the floor and the bottom of the table
    leg_height = h - top_thick

    # 4. CONSTRUCT GEOMETRY WITH BUTIL
    print(f"   📐 Spawning Top: {w}x{d}x{top_thick}m")
    
    # --- TABLETOP ---
    top = butil.spawn_cube(size=1)
    top.name = "MARS_TableTop"
    top.scale = (w, d, top_thick)
    # Move up so the top face rests perfectly at height 'h'
    top.location = (0, 0, h - (top_thick / 2))

    # --- LEGS ---
    print(f"   🦵 Spawning 4 {leg_shape} legs (Height: {leg_height}m, Thick: {leg_thick}m)")
    
    # Calculate where the corners are, inset slightly so legs don't clip outside the top
    x_offset = (w / 2) - (leg_thick / 2) - 0.01 
    y_offset = (d / 2) - (leg_thick / 2) - 0.01
    leg_z = leg_height / 2

    corners = [
        (x_offset, y_offset, leg_z),
        (-x_offset, y_offset, leg_z),
        (x_offset, -y_offset, leg_z),
        (-x_offset, -y_offset, leg_z)
    ]

    for i, loc in enumerate(corners):
        if leg_shape == "cylinder" or leg_shape == "tapered":
            # For low-fi, a cylinder works perfectly as a proxy for tapered
            leg = butil.spawn_cylinder(radius=leg_thick/2, depth=leg_height)
        else: 
            # Default to square block legs
            leg = butil.spawn_cube(size=1)
            leg.scale = (leg_thick, leg_thick, leg_height)
        
        leg.name = f"MARS_Leg_{i+1}"
        leg.location = loc
        
        # Parent the legs to the tabletop so if you move the table, the legs follow!
        butil.parent_to(leg, top)

    print("✅ [MARS_LIB] Table construction complete!")
    return top