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

def create_curved_balcony(name, center, floor, col=None):
    bm = bmesh.new()
    
    # Create curved balcony mesh
    segments = 16
    inner_r = 2.5
    outer_r = 4.0
    angle_range = pi * 0.7  # 126 degrees
    
    inner_verts = []
    outer_verts = []
    
    for i in range(segments + 1):
        angle = -angle_range/2 + (i * angle_range / segments)
        
        inner_x = inner_r * cos(angle)
        inner_y = inner_r * sin(angle)
        outer_x = outer_r * cos(angle)
        outer_y = outer_r * sin(angle)
        
        inner_bot = bm.verts.new((inner_x, inner_y, 0))
        inner_top = bm.verts.new((inner_x, inner_y, 0.2))
        outer_bot = bm.verts.new((outer_x, outer_y, 0))
        outer_top = bm.verts.new((outer_x, outer_y, 0.2))
        
        inner_verts.append((inner_bot, inner_top))
        outer_verts.append((outer_bot, outer_top))
    
    # Create faces for the curved balcony
    for i in range(segments):
        # Top surface
        bm.faces.new([inner_verts[i][1], outer_verts[i][1], 
                     outer_verts[i+1][1], inner_verts[i+1][1]])
        # Bottom surface  
        bm.faces.new([inner_verts[i][0], inner_verts[i+1][0],
                     outer_verts[i+1][0], outer_verts[i][0]])
        # Outer edge
        bm.faces.new([outer_verts[i][0], outer_verts[i][1],
                     outer_verts[i+1][1], outer_verts[i+1][0]])
        # Inner edge
        bm.faces.new([inner_verts[i][0], inner_verts[i+1][0],
                     inner_verts[i+1][1], inner_verts[i][1]])
    
    # End caps
    bm.faces.new([inner_verts[0][0], inner_verts[0][1], 
                 outer_verts[0][1], outer_verts[0][0]])
    bm.faces.new([outer_verts[-1][0], outer_verts[-1][1],
                 inner_verts[-1][1], inner_verts[-1][0]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(center)
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

# BRIGHT WHITE CONCRETE
def mat_white_concrete():
    m = bpy.data.materials.new("WhiteConcrete")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.5
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.95, 0.95, 0.95, 1)
    ramp.color_ramp.elements[1].color = (0.98, 0.98, 0.98, 1)
    
    bump_noise = nodes.new('ShaderNodeTexNoise')
    bump_noise.inputs['Scale'].default_value = 30.0
    bump_noise.inputs['Detail'].default_value = 12.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.2
    bump.inputs['Distance'].default_value = 0.03
    
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.4)
    safe_set(bsdf.inputs, 'Metallic', 0.0)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# BLACK STEEL STRUCTURE
def mat_black_steel():
    m = bpy.data.materials.new("BlackSteel")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 80.0
    noise.inputs['Detail'].default_value = 15.0
    
    mix = nodes.new('ShaderNodeMixRGB')
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Metallic', 0.95)
    safe_set(bsdf.inputs, 'Roughness', 0.1)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# HIGH-TECH GLASS
def mat_modern_glass():
    m = bpy.data.materials.new("ModernGlass")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.88, 0.92, 0.98, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.0)
    safe_set(bsdf.inputs, 'IOR', 1.52)
    safe_set(bsdf.inputs, 'Alpha', 0.2)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    if hasattr(m, 'use_screen_refraction'):
        m.use_screen_refraction = True
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# SLEEK METAL RAILS
def mat_sleek_metal():
    m = bpy.data.materials.new("SleekMetal")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.9, 0.9, 0.9, 1))
    safe_set(bsdf.inputs, 'Metallic', 0.98)
    safe_set(bsdf.inputs, 'Roughness', 0.05)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# DARK FOUNDATION
def mat_dark_concrete():
    m = bpy.data.materials.new("DarkConcrete")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.3, 0.3, 0.3, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.8)
    safe_set(bsdf.inputs, 'Metallic', 0.0)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

M_WHITE = mat_white_concrete()
M_BLACK_STEEL = mat_black_steel()
M_GLASS = mat_modern_glass()
M_METAL = mat_sleek_metal()
M_DARK = mat_dark_concrete()

# ============================================================
# PARAMETERS
# ============================================================
P = {
    "floors": 5,
    "floor_h": 3.2,
    "width": 22.0,
    "depth": 13.0,
    "slab_h": 0.3,
    "pilaster_w": 0.8,
    "pilaster_d": 0.8,
    "window_w": 2.4,
    "window_h": 2.6,
    "window_frame": 0.1,
    "railing_h": 1.1,
    "rail_post_r": 0.02,
}

col_struct = new_collection("Structure")
col_facade = new_collection("Facade")
col_balconies = new_collection("Balconies")
col_env = new_collection("Environment")

# ============================================================
# STEEL STRUCTURE
# ============================================================

foundation = box("Foundation", (P["width"]+3, P["depth"]+3, 0.8), (0,0,0.4), col_struct)
foundation.data.materials.append(M_DARK)

# Steel pillar locations at corners
pilaster_locs = [
    (-P["width"]/2 + P["pilaster_w"]/2, -P["depth"]/2 + P["pilaster_d"]/2),
    (P["width"]/2 - P["pilaster_w"]/2, -P["depth"]/2 + P["pilaster_d"]/2),
    (-P["width"]/2 + P["pilaster_w"]/2, P["depth"]/2 - P["pilaster_d"]/2),
    (P["width"]/2 - P["pilaster_w"]/2, P["depth"]/2 - P["pilaster_d"]/2),
]

total_h = P["floors"] * P["floor_h"]
for i, (px, py) in enumerate(pilaster_locs):
    pil = box(f"SteelColumn_{i}", 
             (P["pilaster_w"], P["pilaster_d"], total_h),
             (px, py, total_h/2 + 0.8), col_struct)
    pil.data.materials.append(M_BLACK_STEEL)

# Floor slabs
for floor in range(P["floors"] + 1):
    z = 0.8 + floor * P["floor_h"]
    slab = box(f"Slab_{floor}", 
              (P["width"], P["depth"], P["slab_h"]),
              (0, 0, z), col_struct)
    slab.data.materials.append(M_WHITE)

# ============================================================
# WHITE CONCRETE WALLS
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    wall_h = P["floor_h"] - P["slab_h"]
    
    # Side walls - bright white
    left_wall = box(f"LeftWall_F{floor}",
                   (0.2, P["depth"] - 2*P["pilaster_d"], wall_h),
                   (-P["width"]/2 + 0.1, 0, z_base + wall_h/2 + P["slab_h"]),
                   col_facade)
    left_wall.data.materials.append(M_WHITE)
    
    right_wall = box(f"RightWall_F{floor}",
                    (0.2, P["depth"] - 2*P["pilaster_d"], wall_h),
                    (P["width"]/2 - 0.1, 0, z_base + wall_h/2 + P["slab_h"]),
                    col_facade)
    right_wall.data.materials.append(M_WHITE)

# ============================================================
# FRONT FACADE - GLASS AND STEEL
# ============================================================

front_window_x = [-8.0, -2.0, 4.0]

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    z_window = z_base + P["floor_h"]/2
    wall_h = P["floor_h"] - P["slab_h"]
    front_y = P["depth"]/2
    
    # Steel frame segments between windows
    seg1_w = front_window_x[0] - P["window_w"]/2 - P["window_frame"] - (-P["width"]/2 + P["pilaster_w"])
    seg1_x = -P["width"]/2 + P["pilaster_w"] + seg1_w/2
    seg1 = box(f"SteelFrame_F{floor}_Seg1",
              (seg1_w, 0.15, wall_h),
              (seg1_x, front_y + 0.075, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg1.data.materials.append(M_BLACK_STEEL)
    
    seg2_w = front_window_x[1] - P["window_w"]/2 - P["window_frame"] - (front_window_x[0] + P["window_w"]/2 + P["window_frame"])
    seg2_x = (front_window_x[0] + P["window_w"]/2 + P["window_frame"]) + seg2_w/2
    seg2 = box(f"SteelFrame_F{floor}_Seg2",
              (seg2_w, 0.15, wall_h),
              (seg2_x, front_y + 0.075, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg2.data.materials.append(M_BLACK_STEEL)
    
    seg3_w = front_window_x[2] - P["window_w"]/2 - P["window_frame"] - (front_window_x[1] + P["window_w"]/2 + P["window_frame"])
    seg3_x = (front_window_x[1] + P["window_w"]/2 + P["window_frame"]) + seg3_w/2
    seg3 = box(f"SteelFrame_F{floor}_Seg3",
              (seg3_w, 0.15, wall_h),
              (seg3_x, front_y + 0.075, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg3.data.materials.append(M_BLACK_STEEL)
    
    seg4_w = (P["width"]/2 - P["pilaster_w"]) - (front_window_x[2] + P["window_w"]/2 + P["window_frame"])
    seg4_x = (front_window_x[2] + P["window_w"]/2 + P["window_frame"]) + seg4_w/2
    seg4 = box(f"SteelFrame_F{floor}_Seg4",
              (seg4_w, 0.15, wall_h),
              (seg4_x, front_y + 0.075, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg4.data.materials.append(M_BLACK_STEEL)
    
    # Large glass windows
    for i, x in enumerate(front_window_x):
        # Steel window frame
        frame = box(f"WindowFrame_F{floor}_F{i}",
                   (P["window_w"] + P["window_frame"]*2, 
                    P["window_frame"],
                    P["window_h"] + P["window_frame"]*2),
                   (x, front_y + 0.04, z_window),
                   col_facade)
        frame.data.materials.append(M_BLACK_STEEL)
        
        # Modern glass panel
        glass = box(f"Glass_F{floor}_F{i}",
                   (P["window_w"], 0.015, P["window_h"]),
                   (x, front_y, z_window),
                   col_facade)
        glass.data.materials.append(M_GLASS)

# ============================================================
# BACK FACADE - WHITE CONCRETE WITH GLASS
# ============================================================

back_window_x = [-7.5, -2.5, 2.5, 7.5]

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    z_window = z_base + P["floor_h"]/2
    wall_h = P["floor_h"] - P["slab_h"]
    back_y = -P["depth"]/2
    
    # White concrete wall segments
    seg1_w = back_window_x[0] - P["window_w"]/2 - P["window_frame"] - (-P["width"]/2 + P["pilaster_w"])
    seg1_x = -P["width"]/2 + P["pilaster_w"] + seg1_w/2
    seg1 = box(f"BackWall_F{floor}_Seg1",
              (seg1_w, 0.2, wall_h),
              (seg1_x, back_y - 0.1, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg1.data.materials.append(M_WHITE)
    
    for j in range(3):
        seg_w = back_window_x[j+1] - P["window_w"]/2 - P["window_frame"] - (back_window_x[j] + P["window_w"]/2 + P["window_frame"])
        seg_x = (back_window_x[j] + P["window_w"]/2 + P["window_frame"]) + seg_w/2
        seg = box(f"BackWall_F{floor}_Seg{j+2}",
                 (seg_w, 0.2, wall_h),
                 (seg_x, back_y - 0.1, z_base + wall_h/2 + P["slab_h"]),
                 col_facade)
        seg.data.materials.append(M_WHITE)
    
    seg5_w = (P["width"]/2 - P["pilaster_w"]) - (back_window_x[3] + P["window_w"]/2 + P["window_frame"])
    seg5_x = (back_window_x[3] + P["window_w"]/2 + P["window_frame"]) + seg5_w/2
    seg5 = box(f"BackWall_F{floor}_Seg5",
              (seg5_w, 0.2, wall_h),
              (seg5_x, back_y - 0.1, z_base + wall_h/2 + P["slab_h"]),
              col_facade)
    seg5.data.materials.append(M_WHITE)
    
    # Glass windows with steel frames
    for i, x in enumerate(back_window_x):
        frame = box(f"BackFrame_F{floor}_B{i}",
                   (P["window_w"] + P["window_frame"]*2, 
                    P["window_frame"],
                    P["window_h"] + P["window_frame"]*2),
                   (x, back_y - 0.04, z_window),
                   col_facade)
        frame.data.materials.append(M_BLACK_STEEL)
        
        glass = box(f"BackGlass_F{floor}_B{i}",
                   (P["window_w"], 0.015, P["window_h"]),
                   (x, back_y, z_window),
                   col_facade)
        glass.data.materials.append(M_GLASS)

# ============================================================
# CURVED CORNER BALCONIES
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    
    # Left corner curved balcony
    left_balcony = create_curved_balcony(f"CurvedBalcony_L_F{floor}", 
                                       (-P["width"]/2, P["depth"]/2, z_base + 0.1), 
                                       floor, col_balconies)
    left_balcony.data.materials.append(M_WHITE)
    
    # Right corner curved balcony  
    right_balcony = create_curved_balcony(f"CurvedBalcony_R_F{floor}",
                                        (P["width"]/2, P["depth"]/2, z_base + 0.1),
                                        floor, col_balconies)
    right_balcony.rotation_euler.z = pi  # Rotate 180 degrees
    right_balcony.data.materials.append(M_WHITE)
    
    # Glass railings for curved balconies
    for side, x_pos in [("L", -P["width"]/2), ("R", P["width"]/2)]:
        # Curved glass railing
        segments = 12
        for i in range(segments):
            angle = -pi*0.35 + (i * pi*0.7 / (segments-1))
            if side == "R":
                angle = pi - angle
            
            r = 3.2
            rail_x = x_pos + r * cos(angle)
            rail_y = P["depth"]/2 + r * sin(angle)
            
            rail_glass = box(f"RailGlass_{side}_F{floor}_{i}",
                           (0.02, 0.3, P["railing_h"]),
                           (rail_x, rail_y, z_base + 0.2 + P["railing_h"]/2),
                           col_balconies)
            rail_glass.rotation_euler.z = angle + pi/2
            rail_glass.data.materials.append(M_GLASS)
            
            # Steel posts
            post = cylinder(f"RailPost_{side}_F{floor}_{i}",
                          P["rail_post_r"], P["railing_h"],
                          (rail_x, rail_y, z_base + 0.2),
                          col_balconies, v=8)
            post.data.materials.append(M_BLACK_STEEL)

# ============================================================
# MODERN PENTHOUSE
# ============================================================

col_pent = new_collection("Penthouse")
ph_z = 0.8 + P["floors"] * P["floor_h"]

# Glass penthouse structure
ph_base = box("PH_Base", (16.0, 12.0, 3.2), (0, 0, ph_z + 1.6), col_pent)
ph_base.data.materials.append(M_WHITE)

# Glass walls
ph_front = box("PH_Front_Glass", (16.0, 0.02, 2.8), (0, 6.0, ph_z + 1.4), col_pent)
ph_front.data.materials.append(M_GLASS)

ph_back = box("PH_Back_Glass", (16.0, 0.02, 2.8), (0, -6.0, ph_z + 1.4), col_pent)
ph_back.data.materials.append(M_GLASS)

ph_left = box("PH_Left_Glass", (0.02, 12.0, 2.8), (-8.0, 0, ph_z + 1.4), col_pent)
ph_left.data.materials.append(M_GLASS)

ph_right = box("PH_Right_Glass", (0.02, 12.0, 2.8), (8.0, 0, ph_z + 1.4), col_pent)
ph_right.data.materials.append(M_GLASS)

# Steel frame elements
for x in [-7.5, -2.5, 2.5, 7.5]:
    frame = box(f"PH_SteelFrame_{x}",
               (0.1, 12.0, 0.1),
               (x, 0, ph_z + 2.6),
               col_pent)
    frame.data.materials.append(M_BLACK_STEEL)

# Modern roof
roof = box("ModernRoof", (17.0, 13.0, 0.2), (0, 0, ph_z + 3.3), col_pent)
roof.data.materials.append(M_BLACK_STEEL)

# ============================================================
# ENVIRONMENT
# ============================================================



# Lighting setup for modern look
sun = bpy.data.lights.new("Sun", 'SUN')
sun_obj = bpy.data.objects.new("Sun", sun)
sun_obj.location = (50, -40, 60)
sun_obj.rotation_euler = Euler((radians(50), 0, radians(130)), 'XYZ')
sun.energy = 4.0
sun.angle = radians(0.3)
col_env.objects.link(sun_obj)

# Area light for glass reflections
area = bpy.data.lights.new("AreaKey", 'AREA')
area_obj = bpy.data.objects.new("AreaKey", area)
area_obj.location = (-30, 40, 35)
area_obj.rotation_euler = Euler((radians(45), 0, radians(-45)), 'XYZ')
area.energy = 500
area.size = 20
col_env.objects.link(area_obj)

# Camera for dramatic angle
cam = bpy.data.cameras.new("Camera")
cam.lens = 28
cam.dof.use_dof = True
cam.dof.focus_distance = 50
cam.dof.aperture_fstop = 4.0
cam_obj = bpy.data.objects.new("Camera", cam)
cam_obj.location = (45, -38, 22)
cam_obj.rotation_euler = Euler((radians(75), 0, radians(45)), 'XYZ')
col_env.objects.link(cam_obj)
s.camera = cam_obj

print("✅ Modern glass-and-steel condominium with curved balconies - F12 for render")

