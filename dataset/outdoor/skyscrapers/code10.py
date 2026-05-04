import bpy
import bmesh
import math

# Pulisci tutto
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def add_realistic_details(obj):
    """Aggiungi dettagli realistici"""
    
    # Bevel per bordi realistici
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.02
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    
    # Subdivision accurata
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    subsurf.quality = 3
    
    # Wireframe sottile per grid
    wire = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.03
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_modern_glass_material(name, base_color, is_dark=False):
    """Materiale vetro fotorealistico"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Glass BSDF
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.location = (0, 100)
    glass.inputs['Color'].default_value = base_color
    glass.inputs['Roughness'].default_value = 0.02 if not is_dark else 0.05
    glass.inputs['IOR'].default_value = 1.45
    
    # Glossy BSDF per riflessioni
    glossy = nodes.new('ShaderNodeBsdfGlossy')
    glossy.location = (0, -100)
    glossy.inputs['Color'].default_value = base_color
    glossy.inputs['Roughness'].default_value = 0.08 if not is_dark else 0.15
    
    # Layer Weight per fresnel realistico
    layer = nodes.new('ShaderNodeLayerWeight')
    layer.location = (-200, 0)
    layer.inputs['Blend'].default_value = 0.3
    
    # Mix Shader
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (200, 0)
    
    # Collegamenti
    links.new(layer.outputs['Facing'], mix.inputs['Fac'])
    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(glossy.outputs['BSDF'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    return mat

def create_metal_frame_material(name):
    """Materiale cornici metalliche"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.18
    
    return mat

def create_hexagon_points(center_x, center_y, width):
    """Crea punti esagonali"""
    points = []
    for i in range(6):
        angle = i * math.pi / 3
        x = center_x + (width / 2) * math.cos(angle)
        y = center_y + (width / 2) * math.sin(angle)
        points.append((x, y))
    return points

def create_supertall_tower(x_pos, name, height, base_w, top_w):
    """Grattacielo supertall realistico con sezione esagonale"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Interpolazione larghezza con curve
        curve_factor = 1 - (0.3 * (math.sin(progress * math.pi)))
        width = (base_w * 1.2) - ((base_w * 1.2) - (top_w * 1.2)) * progress * curve_factor
        
        # Aggiungi leggera curvatura
        offset_x = math.sin(progress * math.pi * 0.5) * 0.3
        
        # Crea punti esagonali
        hex_points = create_hexagon_points(x_pos + offset_x, 0, width)
        
        floor_verts = []
        for px, py in hex_points:
            v = bm.verts.new((px, py, z))
            floor_verts.append(v)
        
        if floor > 0:
            prev_verts = bm.verts[-12:-6]
            curr_verts = bm.verts[-6:]
            
            for i in range(6):
                next_i = (i + 1) % 6
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    # Chiudi top e bottom
    bottom_verts = bm.verts[0:6]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-6:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_twisted_modern(x_pos, name, height, width):
    """Torre twisted moderna con sezione esagonale"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 70
    floor_height = height / floors
    max_rotation = math.radians(90)
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Rotazione con easing
        angle = max_rotation * progress * progress
        
        # Dimensione variabile aumentata del 20%
        scale = 1.0 - 0.25 * progress
        w = (width * 1.2) * scale
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Punti esagonali base
        hex_points = create_hexagon_points(0, 0, w)
        
        # Applica rotazione e traslazione
        floor_verts = []
        for px, py in hex_points:
            vx = x_pos + (px * cos_a - py * sin_a)
            vy = px * sin_a + py * cos_a
            v = bm.verts.new((vx, vy, z))
            floor_verts.append(v)
        
        if floor > 0:
            prev_verts = bm.verts[-12:-6]
            curr_verts = bm.verts[-6:]
            
            for i in range(6):
                next_i = (i + 1) % 6
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    bottom_verts = bm.verts[0:6]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-6:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_parametric_tower(x_pos, name, height):
    """Torre con geometria parametrica esagonale"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Forma che si espande e contrae, aumentata del 20%
        base = 12 * 1.2
        variation = 3 * math.sin(progress * math.pi * 3)
        width = base + variation
        
        # Crea punti esagonali
        hex_points = create_hexagon_points(x_pos, 0, width)
        
        floor_verts = []
        for px, py in hex_points:
            v = bm.verts.new((px, py, z))
            floor_verts.append(v)
        
        if floor > 0:
            prev_verts = bm.verts[-12:-6]
            curr_verts = bm.verts[-6:]
            
            for i in range(6):
                next_i = (i + 1) % 6
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    bottom_verts = bm.verts[0:6]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-6:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

# CREA TORRI con tonalità terra
tower1 = create_supertall_tower(-35, "SupertallAmber", 120, 18, 10)
glass1 = create_modern_glass_material("AmberGlass", (0.85, 0.65, 0.35, 1))
frame1 = create_metal_frame_material("Frame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_twisted_modern(0, "TwistedBronze", 105, 15)
glass2 = create_modern_glass_material("BronzeGlass", (0.75, 0.55, 0.35, 1))
frame2 = create_metal_frame_material("Frame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_parametric_tower(35, "ParametricCopper", 95)
glass3 = create_modern_glass_material("CopperGlass", (0.65, 0.45, 0.35, 1), is_dark=True)
frame3 = create_metal_frame_material("Frame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Piano terra realistico
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ground = bpy.context.active_object
ground.scale = (60, 50, 0.5)

ground_mat = bpy.data.materials.new(name="GroundMat")
ground_mat.use_nodes = True
g_bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
g_bsdf.inputs['Base Color'].default_value = (0.18, 0.19, 0.2, 1)
g_bsdf.inputs['Metallic'].default_value = 0.3
g_bsdf.inputs['Roughness'].default_value = 0.6
ground.data.materials.append(ground_mat)

# Camera cinematica
bpy.ops.object.camera_add(location=(85, -95, 40))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(68), 0, math.radians(42))
cam.data.lens = 38
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 90
cam.data.dof.aperture_fstop = 5.6
bpy.context.scene.camera = cam

# HDRI realistico
world = bpy.data.worlds['World']
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

output = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
sky = nodes.new('ShaderNodeTexSky')

sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(35)
sky.sun_rotation = math.radians(125)
sky.sun_intensity = 1.0
sky.sun_disc = True
sky.air_density = 1.0
sky.dust_density = 1.5

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 1.1

# Sole principale
bpy.ops.object.light_add(type='SUN', location=(80, -70, 100))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.data.angle = math.radians(1.5)
sun.rotation_euler = (math.radians(35), 0, math.radians(125))
sun.data.color = (1.0, 0.98, 0.95)

# Fill light ambientale
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 1200
fill.data.size = 80
fill.data.color = (0.7, 0.8, 1.0)

# Settings rendering fotorealistici
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 2048
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.adaptive_threshold = 0.01
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'High Contrast'
bpy.context.scene.view_settings.exposure = 0.3

# Light paths per realismo
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.transmission_bounces = 12
bpy.context.scene.cycles.transparent_max_bounces = 8

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 grattacieli fotorealistici esagonali:")
print("  - Supertall curvo (ambra)")
print("  - Twisted moderno (bronzo)")
print("  - Parametrico ondulato (rame)")
print("  - Sezioni esagonali e dimensioni aumentate del 20%")
print("  - 2048 samples per fotorealismo")

