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

def rounded_box(name, size, loc, col=None, corner_radius=0.1):
    import mathutils
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=corner_radius, segments=3)
    bm.transform(mathutils.Matrix.Scale(sx, 4, (1,0,0)))
    bm.transform(mathutils.Matrix.Scale(sy, 4, (0,1,0)))  
    bm.transform(mathutils.Matrix.Scale(sz, 4, (0,0,1)))
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
sky.air_density = 1.5
sky.dust_density = 0.8
wn.links.new(sky.outputs['Color'], out.inputs['Surface'])

# ============================================================
# MATERIALS - MODERN MINIMALIST
# ============================================================

def safe_set(inputs, name, value):
    if name in inputs:
        inputs[name].default_value = value

# BLACK METAL - STRUCTURAL
def mat_black_metal():
    m = bpy.data.materials.new("BlackMetal")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.05, 0.05, 0.05, 1))
    safe_set(bsdf.inputs, 'Metallic', 1.0)
    safe_set(bsdf.inputs, 'Roughness', 0.15)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# ULTRA CLEAR GLASS
def mat_clear_glass():
    m = bpy.data.materials.new("ClearGlass")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.95, 0.98, 1.0, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.005)
    safe_set(bsdf.inputs, 'IOR', 1.45)
    safe_set(bsdf.inputs, 'Transmission', 1.0)
    safe_set(bsdf.inputs, 'Alpha', 0.1)
    
    m.blend_method = 'BLEND'
    if hasattr(m, 'shadow_method'):
        m.shadow_method = 'HASHED'
    if hasattr(m, 'use_screen_refraction'):
        m.use_screen_refraction = True
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# WHITE CONCRETE - MINIMAL
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
    noise.inputs['Detail'].default_value = 4.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.92, 0.92, 0.92, 1)
    ramp.color_ramp.elements[1].color = (0.98, 0.98, 0.98, 1)
    
    bump_noise = nodes.new('ShaderNodeTexNoise')
    bump_noise.inputs['Scale'].default_value = 30.0
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.5)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# POLISHED DARK STONE - FOUNDATION
def mat_dark_stone():
    m = bpy.data.materials.new("DarkStone")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    safe_set(bsdf.inputs, 'Base Color', (0.15, 0.15, 0.18, 1))
    safe_set(bsdf.inputs, 'Roughness', 0.25)
    safe_set(bsdf.inputs, 'Specular', 0.6)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# GREEN VEGETATION - ROOFTOP GARDEN
def mat_vegetation():
    m = bpy.data.materials.new("Vegetation")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 6.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.15, 0.35, 0.12, 1)
    ramp.color_ramp.elements[1].color = (0.25, 0.50, 0.18, 1)
    
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.8)
    safe_set(bsdf.inputs, 'Subsurface', 0.1)
    safe_set(bsdf.inputs, 'Subsurface Color', (0.2, 0.4, 0.15, 1))
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# WOOD DECK
def mat_wood_deck():
    m = bpy.data.materials.new("WoodDeck")
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (3, 3, 15)
    
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = 4.0
    wave.inputs['Distortion'].default_value = 2.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.35, 0.25, 0.15, 1)
    ramp.color_ramp.elements[1].color = (0.50, 0.35, 0.20, 1)
    
    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    safe_set(bsdf.inputs, 'Roughness', 0.6)
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

M_BLACK_METAL = mat_black_metal()
M_GLASS = mat_clear_glass()
M_WHITE_CONC = mat_white_concrete()
M_DARK_STONE = mat_dark_stone()
M_VEGETATION = mat_vegetation()
M_WOOD_DECK = mat_wood_deck()

# ============================================================
# PARAMETERS
# ============================================================
P = {
    "floors": 5,
    "floor_h": 3.2,
    "width": 22.0,
    "depth": 13.0,
    "slab_h": 0.20,
    "balcony_depth": 2.0,
    "balcony_w": 5.5,
    "pilaster_w": 0.35,
    "pilaster_d": 0.35,
    "glass_frame": 0.05,
    "railing_h": 1.1,
    "rail_post_r": 0.02,
}

col_struct = new_collection("Structure")
col_facade = new_collection("Facade")
col_balconies = new_collection("Balconies")
col_rooftop = new_collection("RooftopGarden")
col_env = new_collection("Environment")

# ============================================================
# FOUNDATION - DARK POLISHED STONE
# ============================================================

foundation = box("Foundation", (P["width"]+3, P["depth"]+3, 0.6), (0,0,0.3), col_struct)
foundation.data.materials.append(M_DARK_STONE)

# ============================================================
# BLACK METAL PILLARS - SLEEK CORNERS
# ============================================================

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
             (px, py, total_h/2 + 0.6), col_struct)
    pil.data.materials.append(M_BLACK_METAL)

# ============================================================
# FLOOR SLABS - WHITE CONCRETE
# ============================================================

for floor in range(P["floors"] + 1):
    z = 0.6 + floor * P["floor_h"]
    slab = box(f"Slab_{floor}", 
              (P["width"], P["depth"], P["slab_h"]),
              (0, 0, z), col_struct)
    slab.data.materials.append(M_WHITE_CONC)

# ============================================================
# FLOOR-TO-CEILING GLASS FACADES
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.6 + floor * P["floor_h"]
    glass_h = P["floor_h"] - P["slab_h"] - 0.1
    z_center = z_base + P["slab_h"] + 0.05 + glass_h/2
    
    # FRONT FACADE - 3 GLASS PANELS
    front_y = P["depth"]/2
    panel_positions = [-7.0, 0.0, 7.0]
    panel_w = 6.5
    
    for i, x in enumerate(panel_positions):
        # Black metal frame
        frame_v = box(f"Frame_Front_F{floor}_P{i}_V",
                     (P["glass_frame"], P["glass_frame"], glass_h + 0.1),
                     (x - panel_w/2, front_y + 0.025, z_center),
                     col_facade)
        frame_v.data.materials.append(M_BLACK_METAL)
        
        frame_v2 = box(f"Frame_Front_F{floor}_P{i}_V2",
                      (P["glass_frame"], P["glass_frame"], glass_h + 0.1),
                      (x + panel_w/2, front_y + 0.025, z_center),
                      col_facade)
        frame_v2.data.materials.append(M_BLACK_METAL)
        
        frame_h_top = box(f"Frame_Front_F{floor}_P{i}_HT",
                         (panel_w, P["glass_frame"], P["glass_frame"]),
                         (x, front_y + 0.025, z_base + P["slab_h"] + 0.05 + glass_h),
                         col_facade)
        frame_h_top.data.materials.append(M_BLACK_METAL)
        
        frame_h_bot = box(f"Frame_Front_F{floor}_P{i}_HB",
                         (panel_w, P["glass_frame"], P["glass_frame"]),
                         (x, front_y + 0.025, z_base + P["slab_h"] + 0.05),
                         col_facade)
        frame_h_bot.data.materials.append(M_BLACK_METAL)
        
        # Glass panel
        glass = box(f"Glass_Front_F{floor}_P{i}",
                   (panel_w - 0.1, 0.02, glass_h - 0.1),
                   (x, front_y, z_center),
                   col_facade)
        glass.data.materials.append(M_GLASS)
    
    # BACK FACADE - 4 GLASS PANELS
    back_y = -P["depth"]/2
    back_positions = [-7.5, -2.5, 2.5, 7.5]
    back_panel_w = 4.5
    
    for i, x in enumerate(back_positions):
        frame_v = box(f"Frame_Back_F{floor}_P{i}_V",
                     (P["glass_frame"], P["glass_frame"], glass_h + 0.1),
                     (x - back_panel_w/2, back_y - 0.025, z_center),
                     col_facade)
        frame_v.data.materials.append(M_BLACK_METAL)
        
        frame_v2 = box(f"Frame_Back_F{floor}_P{i}_V2",
                      (P["glass_frame"], P["glass_frame"], glass_h + 0.1),
                      (x + back_panel_w/2, back_y - 0.025, z_center),
                      col_facade)
        frame_v2.data.materials.append(M_BLACK_METAL)
        
        frame_h_top = box(f"Frame_Back_F{floor}_P{i}_HT",
                         (back_panel_w, P["glass_frame"], P["glass_frame"]),
                         (x, back_y - 0.025, z_base + P["slab_h"] + 0.05 + glass_h),
                         col_facade)
        frame_h_top.data.materials.append(M_BLACK_METAL)
        
        frame_h_bot = box(f"Frame_Back_F{floor}_P{i}_HB",
                         (back_panel_w, P["glass_frame"], P["glass_frame"]),
                         (x, back_y - 0.025, z_base + P["slab_h"] + 0.05),
                         col_facade)
        frame_h_bot.data.materials.append(M_BLACK_METAL)
        
        glass = box(f"Glass_Back_F{floor}_P{i}",
                   (back_panel_w - 0.1, 0.02, glass_h - 0.1),
                   (x, back_y, z_center),
                   col_facade)
        glass.data.materials.append(M_GLASS)
    
    # SIDE WALLS - MINIMAL SOLID WITH GLASS STRIPS
    wall_h = P["floor_h"] - P["slab_h"] - 0.1
    
    for side_x, side_name in [(-P["width"]/2 + 0.125, "Left"), (P["width"]/2 - 0.125, "Right")]:
        wall = box(f"{side_name}Wall_F{floor}",
                  (0.25, P["depth"] - 2*P["pilaster_d"] - 2.0, wall_h * 0.4),
                  (side_x, 0, z_base + P["slab_h"] + 0.05 + wall_h * 0.2),
                  col_facade)
        wall.data.materials.append(M_WHITE_CONC)
        
        glass_strip = box(f"{side_name}Glass_F{floor}",
                         (0.02, P["depth"] - 2*P["pilaster_d"] - 3.0, wall_h * 0.5),
                         (side_x, 0, z_base + P["slab_h"] + 0.05 + wall_h * 0.75),
                         col_facade)
        glass_strip.data.materials.append(M_GLASS)

# ============================================================
# MODERN BALCONIES WITH GLASS RAILINGS
# ============================================================

for floor in range(P["floors"]):
    z_base = 0.6 + floor * P["floor_h"]
    
    for side, x_sign in [("L", -1), ("R", 1)]:
        x_pos = x_sign * (P["width"]/2 - P["balcony_w"]/2 - P["pilaster_w"])
        y_pos = P["depth"]/2 + P["balcony_depth"]/2
        
        # Sleek balcony slab
        balcony = box(f"Balcony_{side}_F{floor}",
                     (P["balcony_w"], P["balcony_depth"], 0.15),
                     (x_pos, y_pos, z_base + 0.075),
                     col_balconies)
        balcony.data.materials.append(M_WHITE_CONC)
        
        # Underside support
        under = box(f"BalconyUnder_{side}_F{floor}",
                   (P["balcony_w"] - 0.3, P["balcony_depth"] - 0.3, 0.08),
                   (x_pos, y_pos, z_base - 0.04),
                   col_balconies)
        under.data.materials.append(M_WHITE_CONC)
        
        # Glass railing panels
        glass_railing_h = P["railing_h"]
        
        # Front glass panel
        front_glass = box(f"RailingGlass_{side}_F{floor}_Front",
                         (P["balcony_w"] - 0.2, 0.012, glass_railing_h - 0.15),
                         (x_pos, y_pos + P["balcony_depth"]/2 - 0.05,
                          z_base + 0.15 + glass_railing_h/2),
                         col_balconies)
        front_glass.data.materials.append(M_GLASS)
        
        # Left glass panel
        left_glass = box(f"RailingGlass_{side}_F{floor}_Left",
                        (0.012, P["balcony_depth"] - 0.15, glass_railing_h - 0.15),
                        (x_pos - P["balcony_w"]/2 + 0.05, y_pos,
                         z_base + 0.15 + glass_railing_h/2),
                        col_balconies)
        left_glass.data.materials.append(M_GLASS)
        
        # Right glass panel
        right_glass = box(f"RailingGlass_{side}_F{floor}_Right",
                         (0.012, P["balcony_depth"] - 0.15, glass_railing_h - 0.15),
                         (x_pos + P["balcony_w"]/2 - 0.05, y_pos,
                          z_base + 0.15 + glass_railing_h/2),
                         col_balconies)
        right_glass.data.materials.append(M_GLASS)
        
        # Black metal handrail on top
        handrail_front = box(f"Handrail_{side}_F{floor}_Front",
                           (P["balcony_w"] - 0.2, 0.04, 0.04),
                           (x_pos, y_pos + P["balcony_depth"]/2 - 0.05,
                            z_base + 0.15 + glass_railing_h),
                           col_balconies)
        handrail_front.data.materials.append(M_BLACK_METAL)
        
        handrail_left = box(f"Handrail_{side}_F{floor}_Left",
                          (0.04, P["balcony_depth"] - 0.1, 0.04),
                          (x_pos - P["balcony_w"]/2 + 0.05, y_pos,
                           z_base + 0.15 + glass_railing_h),
                          col_balconies)
        handrail_left.data.materials.append(M_BLACK_METAL)
        
        handrail_right = box(f"Handrail_{side}_F{floor}_Right",
                           (0.04, P["balcony_depth"] - 0.1, 0.04),
                           (x_pos + P["balcony_w"]/2 - 0.05, y_pos,
                            z_base + 0.15 + glass_railing_h),
                           col_balconies)
        handrail_right.data.materials.append(M_BLACK_METAL)

# ============================================================
# ROOFTOP GARDEN TERRACE
# ============================================================

roof_z = 0.6 + P["floors"] * P["floor_h"]

# Main terrace deck
terrace_deck = box("TerraceDeck", (18.0, 11.0, 0.12), (0, 0, roof_z + 0.06), col_rooftop)
terrace_deck.data.materials.append(M_WOOD_DECK)

# Perimeter white concrete base
perimeter = box("TerracePerimeter", (19.0, 12.0, 0.3), (0, 0, roof_z - 0.15), col_rooftop)
perimeter.data.materials.append(M_WHITE_CONC)

# Glass railing around terrace
railing_h = 1.2

# Front glass railing
front_glass_rail = box("TerraceGlass_Front",
                      (18.0, 0.012, railing_h - 0.15),
                      (0, 6.0, roof_z + 0.12 + railing_h/2),
                      col_rooftop)
front_glass_rail.data.materials.append(M_GLASS)

# Back glass railing
back_glass_rail = box("TerraceGlass_Back",
                     (18.0, 0.012, railing_h - 0.15),
                     (0, -6.0, roof_z + 0.12 + railing_h/2),
                     col_rooftop)
back_glass_rail.data.materials.append(M_GLASS)

# Left glass railing
left_glass_rail = box("TerraceGlass_Left",
                     (0.012, 12.0, railing_h - 0.15),
                     (-9.5, 0, roof_z + 0.12 + railing_h/2),
                     col_rooftop)
left_glass_rail.data.materials.append(M_GLASS)

# Right glass railing
right_glass_rail = box("TerraceGlass_Right",
                      (0.012, 12.0, railing_h - 0.15),
                      (9.5, 0, roof_z + 0.12 + railing_h/2),
                      col_rooftop)
right_glass_rail.data.materials.append(M_GLASS)

# Black metal top rails
top_rail_front = box("TopRail_Front",
                    (18.2, 0.05, 0.05),
                    (0, 6.0, roof_z + 0.12 + railing_h),
                    col_rooftop)
top_rail_front.data.materials.append(M_BLACK_METAL)

top_rail_back = box("TopRail_Back",
                   (18.2, 0.05, 0.05),
                   (0, -6.0, roof_z + 0.12 + railing_h),
                   col_rooftop)
top_rail_back.data.materials.append(M_BLACK_METAL)

top_rail_left = box("TopRail_Left",
                   (0.05, 12.1, 0.05),
                   (-9.5, 0, roof_z + 0.12 + railing_h),
                   col_rooftop)
top_rail_left.data.materials.append(M_BLACK_METAL)

top_rail_right = box("TopRail_Right",
                    (0.05, 12.1, 0.05),
                    (9.5, 0, roof_z + 0.12 + railing_h),
                    col_rooftop)
top_rail_right.data.materials.append(M_BLACK_METAL)

# Garden planters
planter_positions = [
    (-6.0, 3.5), (-6.0, -3.5),
    (6.0, 3.5), (6.0, -3.5),
    (0, 4.5), (0, -4.5)
]

for i, (px, py) in enumerate(planter_positions):
    planter_box = rounded_box(f"Planter_{i}",
                             (2.0, 1.5, 0.6),
                             (px, py, roof_z + 0.42),
                             col_rooftop,
                             corner_radius=0.08)
    planter_box.data.materials.append(M_WHITE_CONC)
    
    # Vegetation inside
    veg = box(f"Vegetation_{i}",
             (1.8, 1.3, 0.4),
             (px, py, roof_z + 0.62),
             col_rooftop)
    veg.data.materials.append(M_VEGETATION)

# Central seating area
seating_deck = rounded_box("SeatingDeck",
                          (6.0, 6.0, 0.15),
                          (0, 0, roof_z + 0.195),
                          col_rooftop,
                          corner_radius=0.12)
seating_deck.data.materials.append(M_WOOD_DECK)

# Modern pergola structure
pergola_posts = [
    (-2.5, -2.5), (2.5, -2.5),
    (-2.5, 2.5), (2.5, 2.5)
]

for i, (px, py) in enumerate(pergola_posts):
    post = box(f"PergolaPost_{i}",
              (0.12, 0.12, 2.2),
              (px, py, roof_z + 0.27 + 1.1),
              col_rooftop)
    post.data.materials.append(M_BLACK_METAL)

# Pergola beams
for i in range(8):
    offset = -3.0 + i * 0.85
    beam = box(f"PergolaBeam_{i}",
              (5.2, 0.08, 0.08),
              (0, offset, roof_z + 0.27 + 2.2),
              col_rooftop)
    beam.data.materials.append(M_BLACK_METAL)

# ============================================================
# ENVIRONMENT
# ============================================================

sun = bpy.data.lights.new("Sun", 'SUN')
sun_obj = bpy.data.objects.new("Sun", sun)
sun_obj.location = (50, -40, 60)
sun_obj.rotation_euler = Euler((radians(50), 0, radians(130)), 'XYZ')
sun.energy = 4.0
sun.angle = radians(0.5)
col_env.objects.link(sun_obj)

fill = bpy.data.lights.new("Fill", 'AREA')
fill_obj = bpy.data.objects.new("Fill", fill)
fill_obj.location = (-30, 30, 25)
fill_obj.rotation_euler = Euler((radians(60), 0, radians(-45)), 'XYZ')
fill.energy = 350
fill.size = 18
col_env.objects.link(fill_obj)

cam = bpy.data.cameras.new("Camera")
cam.lens = 35
cam.dof.use_dof = True
cam.dof.focus_distance = 42
cam.dof.aperture_fstop = 4.5
cam_obj = bpy.data.objects.new("Camera", cam)
cam_obj.location = (38, -32, 22)
cam_obj.rotation_euler = Euler((radians(68), 0, radians(42)), 'XYZ')
col_env.objects.link(cam_obj)
s.camera = cam_obj

print("✅ Modern Glass Condominium with Rooftop Garden - F12 to render")