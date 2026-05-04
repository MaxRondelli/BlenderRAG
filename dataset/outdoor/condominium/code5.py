import bpy
import bmesh
import math
from math import radians, sin, cos, pi
from mathutils import Vector, Euler

# ============================================================
# UTILITY
# ============================================================
def new_collection(name):
    c = bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c

def box(name, size, loc, col=None):
    sx, sy, sz = size
    x0, y0, z0 = -sx/2, -sy/2, -sz/2
    x1, y1, z1 = sx/2, sy/2, sz/2
    verts = [
        (x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
        (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)
    ]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    (col or bpy.context.scene.collection).objects.link(obj)
    return obj

def cylinder(name, r, h, loc, col=None, v=16):
    bm = bmesh.new()
    bot = [bm.verts.new((r*cos(2*pi*i/v), r*sin(2*pi*i/v), 0)) for i in range(v)]
    bm.faces.new(bot)
    top = [bm.verts.new((b.co.x, b.co.y, h)) for b in bot]
    bm.faces.new(reversed(top))
    for i in range(v):
        bm.faces.new((bot[i], bot[(i+1)%v], top[(i+1)%v], top[i]))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    (col or bpy.context.scene.collection).objects.link(obj)
    return obj

def create_curve_balcony(name, width, depth, height, loc, col=None):
    bm = bmesh.new()
    segments = 20
    for i in range(segments + 1):
        t = i / segments
        angle = t * pi
        x = (width / 2) * cos(angle)
        y = depth * sin(angle) / 2
        bm.verts.new((x, y, 0))
    
    for i in range(segments):
        t = i / segments
        angle = t * pi
        x = (width / 2) * cos(angle)
        y = depth * sin(angle) / 2
        bm.verts.new((x, y - 0.1, height))
    

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    (col or bpy.context.scene.collection).objects.link(obj)
    return obj

# ============================================================
# SCENE
# ============================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
if not s.world:
    s.world = bpy.data.worlds.new("World")

s.render.engine = 'CYCLES'
s.cycles.samples = 512
s.cycles.use_denoising = True
s.render.resolution_x = 1920
s.render.resolution_y = 1080

s.world.use_nodes = True
wn = s.world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
out = wn.nodes.new('ShaderNodeOutputWorld')
sky = wn.nodes.new('ShaderNodeTexSky')
sky.sun_elevation = radians(45)
sky.sun_rotation = radians(135)
sky.air_density = 2.0
sky.dust_density = 1.0
wn.links.new(sky.outputs['Color'], out.inputs['Surface'])

# ============================================================
# MODERN MATERIALS
# ============================================================

def safe_set(inputs, name, value):
    if name in inputs:
        inputs[name].default_value = value

# METALLIC SILVER CLADDING
def mat_silver_cladding():
    m = bpy.data.materials.new("SilverCladding")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 100.0
    noise.inputs['Detail'].default_value = 15.0
    noise.inputs['Roughness'].default_value = 0.4
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.88, 0.90, 0.92, 1)
    ramp.color_ramp.elements[1].color = (0.95, 0.97, 0.98, 1)
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Metallic', 0.98)
    safe_set(bsdf.inputs, 'Roughness', 0.05)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# DARK STEEL STRUCTURE
def mat_dark_steel():
    m = bpy.data.materials.new("DarkSteel")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.15, 0.18, 0.20, 1))
    safe_set(bsdf.inputs, 'Metallic', 1.0)
    safe_set(bsdf.inputs, 'Roughness', 0.08)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# ULTRA CLEAR GLASS
def mat_ultra_glass():
    m = bpy.data.materials.new("UltraClearGlass")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.98, 0.99, 1.0, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.0)
    safe_set(bsdf.inputs, 'IOR', 1.52)
    safe_set(bsdf.inputs, 'Alpha', 0.1)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    if hasattr(m, 'use_screen_refraction'):
        m.use_screen_refraction = True
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# MODERN GLASS RAILING
def mat_glass_railing():
    m = bpy.data.materials.new("GlassRailing")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.95, 0.97, 0.98, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.02)
    safe_set(bsdf.inputs, 'IOR', 1.5)
    safe_set(bsdf.inputs, 'Alpha', 0.2)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# BLACK METAL FRAME
def mat_black_frame():
    m = bpy.data.materials.new("BlackFrame")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.05, 0.05, 0.05, 1))
    safe_set(bsdf.inputs, 'Metallic', 1.0)
    safe_set(bsdf.inputs, 'Roughness', 0.12)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# CONCRETE FOUNDATION
def mat_concrete():
    m = bpy.data.materials.new("Concrete")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.75, 0.73, 0.70, 1)
    ramp.color_ramp.elements[1].color = (0.85, 0.83, 0.80, 1)
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.7)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# WOOD ACCENTS
def mat_wood():
    m = bpy.data.materials.new("Wood")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (2, 2, 20)
    
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 2.5
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.25, 0.15, 0.08, 1)
    ramp.color_ramp.elements[1].color = (0.45, 0.28, 0.15, 1)
    
    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.4)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

M_SILVER = mat_silver_cladding()
M_DARK_STEEL = mat_dark_steel()
M_ULTRA_GLASS = mat_ultra_glass()
M_GLASS_RAIL = mat_glass_railing()
M_BLACK_FRAME = mat_black_frame()
M_CONCRETE = mat_concrete()
M_WOOD = mat_wood()

# ============================================================
# PARAMETERS
# ============================================================
P = {
    "floors": 5,
    "floor_h": 3.0,
    "width": 22.0,
    "depth": 13.0,
    "slab_h": 0.25,
    "balcony_depth": 2.2,
    "balcony_w": 6.0,
    "pilaster_w": 1.2,
    "pilaster_d": 1.2,
    "window_w": 4.0,
    "window_h": 2.8,
    "window_frame": 0.05,
    "railing_h": 1.1,
    "rail_post_r": 0.03,
}

col_struct = new_collection("Structure")
col_facade = new_collection("Facade")
col_balconies = new_collection("Balconies")
col_env = new_collection("Environment")

# ============================================================
# STRUCTURE
# ============================================================

foundation = box("Foundation", (P["width"]+3, P["depth"]+3, 0.8), (0,0,0.4), col_struct)
foundation.data.materials.append(M_CONCRETE)

pilaster_locs = [
    (-P["width"]/2 + P["pilaster_w"]/2, -P["depth"]/2 + P["pilaster_d"]/2),
    (P["width"]/2 - P["pilaster_w"]/2, -P["depth"]/2 + P["pilaster_d"]/2),
    (-P["width"]/2 + P["pilaster_w"]/2, P["depth"]/2 - P["pilaster_d"]/2),
    (P["width"]/2 - P["pilaster_w"]/2, P["depth"]/2 - P["pilaster_d"]/2),
]

total_h = P["floors"] * P["floor_h"]
for i, (px, py) in enumerate(pilaster_locs):
    pil = box(f"Pillar_{i}", 
             (P["pilaster_w"], P["pilaster_d"], total_h),
             (px, py, total_h/2 + 0.8), col_struct)
    pil.data.materials.append(M_DARK_STEEL)

for floor in range(P["floors"] + 1):
    z = 0.8 + floor * P["floor_h"]
    slab = box(f"Slab_{floor}", 
              (P["width"], P["depth"], P["slab_h"]),
              (0, 0, z), col_struct)
    slab.data.materials.append(M_SILVER)

# ============================================================
# SIDE CLADDING
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    wall_h = P["floor_h"] - P["slab_h"]
    
    left_wall = box(f"LeftCladding_F{floor}",
                   (0.15, P["depth"] - 2*P["pilaster_d"], wall_h),
                   (-P["width"]/2 + 0.075, 0, z_base + wall_h/2 + P["slab_h"]),
                   col_facade)
    left_wall.data.materials.append(M_SILVER)
    
    right_wall = box(f"RightCladding_F{floor}",
                    (0.15, P["depth"] - 2*P["pilaster_d"], wall_h),
                    (P["width"]/2 - 0.075, 0, z_base + wall_h/2 + P["slab_h"]),
                    col_facade)
    right_wall.data.materials.append(M_SILVER)

# ============================================================
# CURTAIN WALL FACADE - FRONT
# ============================================================

front_glass_panels = 6

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    wall_h = P["floor_h"] - P["slab_h"]
    front_y = P["depth"]/2
    
    # Horizontal frame elements
    top_frame = box(f"FrontFrame_F{floor}_Top",
                   (P["width"] - 2*P["pilaster_w"], 0.08, 0.12),
                   (0, front_y + 0.04, z_base + P["slab_h"] + wall_h - 0.06),
                   col_facade)
    top_frame.data.materials.append(M_BLACK_FRAME)
    
    bot_frame = box(f"FrontFrame_F{floor}_Bot",
                   (P["width"] - 2*P["pilaster_w"], 0.08, 0.12),
                   (0, front_y + 0.04, z_base + P["slab_h"] + 0.06),
                   col_facade)
    bot_frame.data.materials.append(M_BLACK_FRAME)
    
    # Floor-to-ceiling glass panels
    panel_width = (P["width"] - 2*P["pilaster_w"] - (front_glass_panels-1)*0.08) / front_glass_panels
    
    for i in range(front_glass_panels):
        panel_x = -P["width"]/2 + P["pilaster_w"] + panel_width/2 + i*(panel_width + 0.08)
        
        # Vertical mullion (except for last panel)
        if i < front_glass_panels - 1:
            mullion = box(f"FrontMullion_F{floor}_{i}",
                         (0.08, 0.08, wall_h - 0.24),
                         (panel_x + panel_width/2 + 0.04, front_y + 0.04, z_base + wall_h/2 + P["slab_h"]),
                         col_facade)
            mullion.data.materials.append(M_BLACK_FRAME)
        
        # Glass panel
        glass_panel = box(f"FrontGlass_F{floor}_{i}",
                         (panel_width, 0.02, wall_h - 0.24),
                         (panel_x, front_y, z_base + wall_h/2 + P["slab_h"]),
                         col_facade)
        glass_panel.data.materials.append(M_ULTRA_GLASS)

# ============================================================
# CURTAIN WALL FACADE - BACK
# ============================================================

back_glass_panels = 8

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    wall_h = P["floor_h"] - P["slab_h"]
    back_y = -P["depth"]/2
    
    # Horizontal frame elements
    top_frame = box(f"BackFrame_F{floor}_Top",
                   (P["width"] - 2*P["pilaster_w"], 0.08, 0.12),
                   (0, back_y - 0.04, z_base + P["slab_h"] + wall_h - 0.06),
                   col_facade)
    top_frame.data.materials.append(M_BLACK_FRAME)
    
    bot_frame = box(f"BackFrame_F{floor}_Bot",
                   (P["width"] - 2*P["pilaster_w"], 0.08, 0.12),
                   (0, back_y - 0.04, z_base + P["slab_h"] + 0.06),
                   col_facade)
    bot_frame.data.materials.append(M_BLACK_FRAME)
    
    # Floor-to-ceiling glass panels
    panel_width = (P["width"] - 2*P["pilaster_w"] - (back_glass_panels-1)*0.08) / back_glass_panels
    
    for i in range(back_glass_panels):
        panel_x = -P["width"]/2 + P["pilaster_w"] + panel_width/2 + i*(panel_width + 0.08)
        
        # Vertical mullion (except for last panel)
        if i < back_glass_panels - 1:
            mullion = box(f"BackMullion_F{floor}_{i}",
                         (0.08, 0.08, wall_h - 0.24),
                         (panel_x + panel_width/2 + 0.04, back_y - 0.04, z_base + wall_h/2 + P["slab_h"]),
                         col_facade)
            mullion.data.materials.append(M_BLACK_FRAME)
        
        # Glass panel
        glass_panel = box(f"BackGlass_F{floor}_{i}",
                         (panel_width, 0.02, wall_h - 0.24),
                         (panel_x, back_y, z_base + wall_h/2 + P["slab_h"]),
                         col_facade)
        glass_panel.data.materials.append(M_ULTRA_GLASS)

# ============================================================
# CURVED CORNER BALCONIES
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    
    for side, x_sign in [("L", -1), ("R", 1)]:
        x_pos = x_sign * (P["width"]/2 - P["balcony_w"]/2 - P["pilaster_w"])
        y_pos = P["depth"]/2 + P["balcony_depth"]/2
        
        # Curved balcony platform
        balcony = create_curve_balcony(f"CurveBalcony_{side}_F{floor}",
                                     P["balcony_w"], P["balcony_depth"], 0.2,
                                     (x_pos, y_pos, z_base + 0.1),
                                     col_balconies)
        balcony.data.materials.append(M_SILVER)
        
        # Curved glass railing
        num_segments = 15
        for i in range(num_segments):
            t = i / (num_segments - 1)
            angle = t * pi
            rail_x = x_pos + (P["balcony_w"] / 2) * cos(angle)
            rail_y = y_pos + (P["balcony_depth"] * sin(angle) / 2) - 0.05
            
            glass_rail = box(f"GlassRail_{side}_F{floor}_{i}",
                           (0.02, 0.15, P["railing_h"]),
                           (rail_x, rail_y, z_base + 0.2 + P["railing_h"]/2),
                           col_balconies)
            glass_rail.data.materials.append(M_GLASS_RAIL)
            
            # Support posts
            if i % 3 == 0:
                post = cylinder(f"RailPost_{side}_F{floor}_{i}",
                              P["rail_post_r"], P["railing_h"],
                              (rail_x, rail_y, z_base + 0.2),
                              col_balconies, v=12)
                post.data.materials.append(M_BLACK_FRAME)
        
        # Top handrail
        handrail_segments = 12
        for i in range(handrail_segments):
            t = i / (handrail_segments - 1)
            angle = t * pi
            rail_x = x_pos + (P["balcony_w"] / 2) * cos(angle)
            rail_y = y_pos + (P["balcony_depth"] * sin(angle) / 2) - 0.05
            
            handrail = box(f"Handrail_{side}_F{floor}_{i}",
                          (0.08, 0.08, 0.05),
                          (rail_x, rail_y, z_base + 0.2 + P["railing_h"] + 0.025),
                          col_balconies)
            handrail.data.materials.append(M_BLACK_FRAME)

# ============================================================
# PENTHOUSE
# ============================================================

col_pent = new_collection("Penthouse")
ph_z = 0.8 + P["floors"] * P["floor_h"]

ph_base = box("PH_Base", (14.0, 11.0, 2.8), (0, 0, ph_z + 1.4), col_pent)
ph_base.data.materials.append(M_SILVER)

ph_back = box("PH_Back", (14.0, 0.25, 2.8), (0, -5.5, ph_z + 1.4), col_pent)
ph_back.data.materials.append(M_SILVER)

ph_left = box("PH_Left", (0.25, 11.0, 2.8), (-7.0, 0, ph_z + 1.4), col_pent)
ph_left.data.materials.append(M_SILVER)

ph_right = box("PH_Right", (0.25, 11.0, 2.8), (7.0, 0, ph_z + 1.4), col_pent)
ph_right.data.materials.append(M_SILVER)

num_segments = 15
for i in range(num_segments):
    x = -7.0 + i * 1.0
    curve_factor = 1.0 - (abs(i - 7) / 7.0) ** 1.5
    y_offset = 5.0 + curve_factor * 1.0
    rotation = (i - 7) * 0.07
    
    frame = box(f"PH_Frame_{i}",
               (0.10, 0.10, 2.4),
               (x, y_offset, ph_z + 1.6),
               col_pent)
    frame.rotation_euler.z = rotation
    frame.data.materials.append(M_BLACK_FRAME)
    
    if i % 2 == 1:
        glass = box(f"PH_Glass_{i}",
                   (0.85, 0.03, 2.2),
                   (x, y_offset + 0.1, ph_z + 1.6),
                   col_pent)
        glass.rotation_euler.z = rotation
        glass.data.materials.append(M_ULTRA_GLASS)

roof = box("Roof", (15.0, 12.0, 0.25), (0, 0, ph_z + 3.0), col_pent)
roof.data.materials.append(M_WOOD)

# ============================================================
# ENVIRONMENT
# ============================================================



sun = bpy.data.lights.new("Sun", 'SUN')
sun_obj = bpy.data.objects.new("Sun", sun)
sun_obj.location = (50, -40, 60)
sun_obj.rotation_euler = Euler((radians(50), 0, radians(130)), 'XYZ')
sun.energy = 3.5
sun.angle = radians(0.5)
col_env.objects.link(sun_obj)

fill = bpy.data.lights.new("Fill", 'AREA')
fill_obj = bpy.data.objects.new("Fill", fill)
fill_obj.location = (-25, 35, 30)
fill_obj.rotation_euler = Euler((radians(55), 0, radians(-50)), 'XYZ')
fill.energy = 300
fill.size = 15
col_env.objects.link(fill_obj)

cam = bpy.data.cameras.new("Camera")
cam.lens = 35
cam.dof.use_dof = True
cam.dof.focus_distance = 45
cam.dof.aperture_fstop = 5.6
cam_obj = bpy.data.objects.new("Camera", cam)
cam_obj.location = (42, -35, 20)
cam_obj.rotation_euler = Euler((radians(70), 0, radians(40)), 'XYZ')
col_env.objects.link(cam_obj)
s.camera = cam_obj

print("✅ Modern glass and steel building - F12 for render")


