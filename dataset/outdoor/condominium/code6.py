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
# MATERIALI MODERNI
# ============================================================

def safe_set(inputs, name, value):
    if name in inputs:
        inputs[name].default_value = value

# CEMENTO CON TEXTURE
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
    
    bump_noise = nodes.new('ShaderNodeTexNoise')
    bump_noise.inputs['Scale'].default_value = 25.0
    bump_noise.inputs['Detail'].default_value = 10.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.05
    

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.7)
    safe_set(bsdf.inputs, 'Metallic', 0.0)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# ACCIAIO NERO STRUTTURALE
def mat_black_steel():
    m = bpy.data.materials.new("BlackSteel")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 100.0
    noise.inputs['Detail'].default_value = 5.0
    
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.08, 0.08, 0.08, 1)
    mix.inputs[7].default_value = (0.12, 0.12, 0.12, 1)
    
    links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Metallic', 0.95)
    safe_set(bsdf.inputs, 'Roughness', 0.25)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# VETRO OSCURATO MODERNO
def mat_dark_glass():
    m = bpy.data.materials.new("DarkGlass")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.15, 0.15, 0.18, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.02)
    safe_set(bsdf.inputs, 'IOR', 1.45)
    safe_set(bsdf.inputs, 'Alpha', 0.4)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    if hasattr(m, 'use_screen_refraction'):
        m.use_screen_refraction = True
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# VETRO TRASPARENTE
def mat_clear_glass():
    m = bpy.data.materials.new("ClearGlass")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.92, 0.96, 0.98, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.01)
    safe_set(bsdf.inputs, 'IOR', 1.45)
    safe_set(bsdf.inputs, 'Alpha', 0.2)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    if hasattr(m, 'use_screen_refraction'):
        m.use_screen_refraction = True
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# LEGNO
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
    
    bump_noise = nodes.new('ShaderNodeTexNoise')
    bump_noise.inputs['Scale'].default_value = 15.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.2
    
    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.4)
    safe_set(bsdf.inputs, 'Metallic', 0.0)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

M_CONC = mat_concrete()
M_BLACK_STEEL = mat_black_steel()
M_DARK_GLASS = mat_dark_glass()
M_CLEAR_GLASS = mat_clear_glass()
M_WOOD = mat_wood()

# ============================================================
# PARAMETRI
# ============================================================
P = {
    "floors": 5,
    "floor_h": 3.0,
    "width": 22.0,
    "depth": 13.0,
    "slab_h": 0.25,
    "balcony_depth": 1.8,
    "balcony_w": 5.0,
    "pilaster_w": 1.2,
    "pilaster_d": 1.2,
    "window_w": 1.6,
    "window_h": 2.2,
    "window_frame": 0.08,
    "railing_h": 1.0,
    "rail_post_r": 0.025,
}

col_struct = new_collection("Structure")
col_facade = new_collection("Facade")
col_balconies = new_collection("Balconies")
col_env = new_collection("Environment")

# ============================================================
# STRUTTURA
# ============================================================

foundation = box("Foundation", (P["width"]+3, P["depth"]+3, 0.8), (0,0,0.4), col_struct)
foundation.data.materials.append(M_CONC)

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
    pil.data.materials.append(M_BLACK_STEEL)

for floor in range(P["floors"] + 1):
    z = 0.8 + floor * P["floor_h"]
    slab = box(f"Slab_{floor}", 
              (P["width"], P["depth"], P["slab_h"]),
              (0, 0, z), col_struct)
    slab.data.materials.append(M_CONC)

# ============================================================
# PANNELLI VETRO LATERALI
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    panel_h = P["floor_h"] - P["slab_h"]
    
    left_panel = box(f"LeftGlass_F{floor}",
                    (0.12, P["depth"] - 2*P["pilaster_d"], panel_h),
                    (-P["width"]/2 + 0.06, 0, z_base + panel_h/2 + P["slab_h"]),
                    col_facade)
    left_panel.data.materials.append(M_DARK_GLASS)
    
    right_panel = box(f"RightGlass_F{floor}",
                     (0.12, P["depth"] - 2*P["pilaster_d"], panel_h),
                     (P["width"]/2 - 0.06, 0, z_base + panel_h/2 + P["slab_h"]),
                     col_facade)
    right_panel.data.materials.append(M_DARK_GLASS)

# ============================================================
# FACCIATA FRONTALE CON VETRO
# ============================================================

front_window_x = [-7.0, -0.5, 6.0]

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    z_window = z_base + P["floor_h"]/2
    panel_h = P["floor_h"] - P["slab_h"]
    front_y = P["depth"]/2
    
    # Pannello unico di vetro oscurato
    main_glass = box(f"FrontMainGlass_F{floor}",
                    (P["width"] - 2*P["pilaster_w"] - 0.2, 0.12, panel_h),
                    (0, front_y + 0.06, z_base + panel_h/2 + P["slab_h"]),
                    col_facade)
    main_glass.data.materials.append(M_DARK_GLASS)
    
    # Cornici nere per le finestre trasparenti
    for i, x in enumerate(front_window_x):
        frame = box(f"WinFrame_F{floor}_F{i}",
                   (P["window_w"] + P["window_frame"]*2, 
                    P["window_frame"],
                    P["window_h"] + P["window_frame"]*2),
                   (x, front_y + 0.14, z_window),
                   col_facade)
        frame.data.materials.append(M_BLACK_STEEL)
        
        glass = box(f"Window_F{floor}_F{i}",
                   (P["window_w"], 0.02, P["window_h"]),
                   (x, front_y + 0.12, z_window),
                   col_facade)
        glass.data.materials.append(M_CLEAR_GLASS)

# ============================================================
# FACCIATA POSTERIORE CON VETRO
# ============================================================

back_window_x = [-7.5, -2.5, 2.5, 7.5]

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    z_window = z_base + P["floor_h"]/2
    panel_h = P["floor_h"] - P["slab_h"]
    back_y = -P["depth"]/2
    
    # Pannello unico di vetro oscurato
    main_glass = box(f"BackMainGlass_F{floor}",
                    (P["width"] - 2*P["pilaster_w"] - 0.2, 0.12, panel_h),
                    (0, back_y - 0.06, z_base + panel_h/2 + P["slab_h"]),
                    col_facade)
    main_glass.data.materials.append(M_DARK_GLASS)
    
    # Cornici nere per le finestre trasparenti
    for i, x in enumerate(back_window_x):
        frame = box(f"WinFrame_F{floor}_B{i}",
                   (P["window_w"] + P["window_frame"]*2, 
                    P["window_frame"],
                    P["window_h"] + P["window_frame"]*2),
                   (x, back_y - 0.14, z_window),
                   col_facade)
        frame.data.materials.append(M_BLACK_STEEL)
        
        glass = box(f"Window_F{floor}_B{i}",
                   (P["window_w"], 0.02, P["window_h"]),
                   (x, back_y - 0.12, z_window),
                   col_facade)
        glass.data.materials.append(M_CLEAR_GLASS)

# ============================================================
# BALCONI CON RINGHIERE DI VETRO
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.8 + floor * P["floor_h"]
    
    for side, x_sign in [("L", -1), ("R", 1)]:
        x_pos = x_sign * (P["width"]/2 - P["balcony_w"]/2 - P["pilaster_w"])
        y_pos = P["depth"]/2 + P["balcony_depth"]/2
        
        balcony = box(f"Balcony_{side}_F{floor}",
                     (P["balcony_w"], P["balcony_depth"], 0.2),
                     (x_pos, y_pos, z_base + 0.1),
                     col_balconies)
        balcony.data.materials.append(M_CONC)
        
        under = box(f"BalconyUnder_{side}_F{floor}",
                   (P["balcony_w"] - 0.2, P["balcony_depth"] - 0.2, 0.15),
                   (x_pos, y_pos, z_base - 0.075),
                   col_balconies)
        under.data.materials.append(M_CONC)
        
        # Ringhiera di vetro continua frontale
        glass_railing_front = box(f"GlassRail_{side}_F{floor}_Front",
                                 (P["balcony_w"] - 0.2, 0.04, P["railing_h"]),
                                 (x_pos, y_pos + P["balcony_depth"]/2 - 0.1,
                                  z_base + 0.2 + P["railing_h"]/2),
                                 col_balconies)
        glass_railing_front.data.materials.append(M_CLEAR_GLASS)
        
        # Cornice superiore frontale
        handrail_front = box(f"Handrail_{side}_F{floor}_Front",
                           (P["balcony_w"] - 0.1, 0.08, 0.06),
                           (x_pos, y_pos + P["balcony_depth"]/2 - 0.1,
                            z_base + 0.2 + P["railing_h"] + 0.03),
                           col_balconies)
        handrail_front.data.materials.append(M_BLACK_STEEL)
        
        # Ringhiera di vetro laterale sinistra
        glass_railing_left = box(f"GlassRail_{side}_F{floor}_Left",
                               (0.04, P["balcony_depth"] - 0.2, P["railing_h"]),
                               (x_pos - P["balcony_w"]/2 + 0.1, y_pos,
                                z_base + 0.2 + P["railing_h"]/2),
                               col_balconies)
        glass_railing_left.data.materials.append(M_CLEAR_GLASS)
        
        # Cornice superiore sinistra
        handrail_left = box(f"Handrail_{side}_F{floor}_Left",
                          (0.08, P["balcony_depth"] - 0.1, 0.06),
                          (x_pos - P["balcony_w"]/2 + 0.1, y_pos,
                           z_base + 0.2 + P["railing_h"] + 0.03),
                          col_balconies)
        handrail_left.data.materials.append(M_BLACK_STEEL)
        
        # Ringhiera di vetro laterale destra
        glass_railing_right = box(f"GlassRail_{side}_F{floor}_Right",
                                (0.04, P["balcony_depth"] - 0.2, P["railing_h"]),
                                (x_pos + P["balcony_w"]/2 - 0.1, y_pos,
                                 z_base + 0.2 + P["railing_h"]/2),
                                col_balconies)
        glass_railing_right.data.materials.append(M_CLEAR_GLASS)
        
        # Cornice superiore destra
        handrail_right = box(f"Handrail_{side}_F{floor}_Right",
                           (0.08, P["balcony_depth"] - 0.1, 0.06),
                           (x_pos + P["balcony_w"]/2 - 0.1, y_pos,
                            z_base + 0.2 + P["railing_h"] + 0.03),
                           col_balconies)
        handrail_right.data.materials.append(M_BLACK_STEEL)

# ============================================================
# PENTHOUSE
# ============================================================

col_pent = new_collection("Penthouse")
ph_z = 0.8 + P["floors"] * P["floor_h"]

ph_base = box("PH_Base", (14.0, 11.0, 2.8), (0, 0, ph_z + 1.4), col_pent)
ph_base.data.materials.append(M_BLACK_STEEL)

ph_back = box("PH_Back", (14.0, 0.25, 2.8), (0, -5.5, ph_z + 1.4), col_pent)
ph_back.data.materials.append(M_BLACK_STEEL)

ph_left = box("PH_Left", (0.25, 11.0, 2.8), (-7.0, 0, ph_z + 1.4), col_pent)
ph_left.data.materials.append(M_BLACK_STEEL)

ph_right = box("PH_Right", (0.25, 11.0, 2.8), (7.0, 0, ph_z + 1.4), col_pent)
ph_right.data.materials.append(M_BLACK_STEEL)

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
    frame.data.materials.append(M_BLACK_STEEL)
    
    if i % 2 == 1:
        glass = box(f"PH_Glass_{i}",
                   (0.85, 0.03, 2.2),
                   (x, y_offset + 0.1, ph_z + 1.6),
                   col_pent)
        glass.rotation_euler.z = rotation
        glass.data.materials.append(M_CLEAR_GLASS)

roof = box("Roof", (15.0, 12.0, 0.25), (0, 0, ph_z + 3.0), col_pent)
roof.data.materials.append(M_BLACK_STEEL)

# ============================================================
# AMBIENTE
# ============================================================




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

print("✅ Condominio moderno in vetro - F12 per render")

