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
    
    # Wireframe più spesso per look industriale
    wire = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.08
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_modern_glass_material(name, base_color, is_dark=False):
    """Materiale vetro fotorealistico con toni sunset"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF per vetro
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Metallic'].default_value = 0.1
    principled.inputs['Roughness'].default_value = 0.02 if not is_dark else 0.05
    principled.inputs['Alpha'].default_value = 0.3
    principled.inputs['IOR'].default_value = 1.45
    
    # Layer Weight per fresnel realistico
    layer = nodes.new('ShaderNodeLayerWeight')
    layer.location = (-200, 0)
    layer.inputs['Blend'].default_value = 0.3
    
    # ColorRamp per controllo trasparenza
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 0)
    color_ramp.color_ramp.elements[0].position = 0.2
    color_ramp.color_ramp.elements[1].position = 0.8
    
    # Collegamenti
    links.new(layer.outputs['Facing'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Alpha'], principled.inputs['Alpha'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_metal_frame_material(name):
    """Materiale cornici metalliche industriali più spesse"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.04, 1)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['IOR'].default_value = 0.8
    
    return mat

def create_angular_tower(x_pos, name, height, base_w, top_w):
    """Grattacielo angolare con forme faceted"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Interpolazione angolare a gradini
        step_factor = math.floor(progress * 8) / 8
        width = base_w - (base_w - top_w) * step_factor
        depth = width * 0.8
        
        # Forma angolare esagonale
        angle_offset = step_factor * math.radians(45)
        
        # Vertici per forma angolare
        vertices = []
        for i in range(6):
            angle = i * math.pi / 3 + angle_offset
            vx = x_pos + (width/2) * math.cos(angle)
            vy = (depth/2) * math.sin(angle)
            vertices.append(bm.verts.new((vx, vy, z)))
        
        if floor > 0:
            prev_verts = bm.verts[-12:-6]
            curr_verts = bm.verts[-6:]
            
            for i in range(6):
                next_i = (i + 1) % 6
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    # Chiudi bottom e top
    bottom_verts = bm.verts[0:6]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-6:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_faceted_modern(x_pos, name, height, width):
    """Torre con superficie faceted geometrica"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 70
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Dimensioni che cambiano a blocchi
        block = math.floor(progress * 6)
        scale = 1.0 - 0.15 * (block / 6)
        w = width * scale
        d = w * 0.7
        
        # Forma ottagonale per look più industriale
        vertices = []
        for i in range(8):
            angle = i * math.pi / 4
            if i % 2 == 0:
                radius = w/2
            else:
                radius = w/2.5
            
            vx = x_pos + radius * math.cos(angle)
            vy = radius * math.sin(angle)
            vertices.append(bm.verts.new((vx, vy, z)))
        
        if floor > 0:
            prev_verts = bm.verts[-16:-8]
            curr_verts = bm.verts[-8:]
            
            for i in range(8):
                next_i = (i + 1) % 8
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    bottom_verts = bm.verts[0:8]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-8:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_geometric_tower(x_pos, name, height):
    """Torre con geometria sharp e angoli definiti"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Forma che alterna tra quadrata e diamante
        base = 12
        if math.floor(progress * 10) % 2 == 0:
            # Quadrato
            w = base * (1 - progress * 0.3)
            v1 = bm.verts.new((x_pos - w/2, -w/2, z))
            v2 = bm.verts.new((x_pos + w/2, -w/2, z))
            v3 = bm.verts.new((x_pos + w/2, w/2, z))
            v4 = bm.verts.new((x_pos - w/2, w/2, z))
        else:
            # Diamante ruotato
            w = base * (1 - progress * 0.3)
            v1 = bm.verts.new((x_pos, -w/1.4, z))
            v2 = bm.verts.new((x_pos + w/1.4, 0, z))
            v3 = bm.verts.new((x_pos, w/1.4, z))
            v4 = bm.verts.new((x_pos - w/1.4, 0, z))
        
        if floor > 0:
            prev_verts = bm.verts[-8:-4]
            curr_verts = bm.verts[-4:]
            
            for i in range(4):
                next_i = (i + 1) % 4
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    bottom_verts = bm.verts[0:4]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-4:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

# CREA TORRI CON TONI SUNSET
tower1 = create_angular_tower(-35, "AngularAmber", 120, 18, 10)
glass1 = create_modern_glass_material("AmberGlass", (0.9, 0.55, 0.15, 1))
frame1 = create_metal_frame_material("Frame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_faceted_modern(0, "FacetedRose", 105, 15)
glass2 = create_modern_glass_material("RoseGoldGlass", (0.95, 0.65, 0.55, 1))
frame2 = create_metal_frame_material("Frame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_geometric_tower(35, "GeometricBronze", 95)
glass3 = create_modern_glass_material("BronzeGlass", (0.75, 0.45, 0.25, 1), is_dark=True)
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

# HDRI sunset realistico
world = bpy.data.worlds['World']
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

output = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
sky = nodes.new('ShaderNodeTexSky')

sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(15)
sky.sun_rotation = math.radians(240)
sky.sun_intensity = 1.5
sky.sun_disc = True
sky.air_density = 2.0
sky.dust_density = 3.0

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 1.3

# Sole sunset
bpy.ops.object.light_add(type='SUN', location=(80, -70, 30))
sun = bpy.context.active_object
sun.data.energy = 6.0
sun.data.angle = math.radians(2.0)
sun.rotation_euler = (math.radians(15), 0, math.radians(240))
sun.data.color = (1.0, 0.7, 0.4)

# Fill light caldo
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 1500
fill.data.size = 80
fill.data.color = (1.0, 0.8, 0.6)

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
bpy.context.scene.view_settings.exposure = 0.5

# Light paths per realismo
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.transmission_bounces = 12
bpy.context.scene.cycles.transparent_max_bounces = 8

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 grattacieli sunset fotorealistici:")
print("  - Angular tower (deep amber)")
print("  - Faceted modern (rose gold)")
print("  - Geometric alternating (bronze)")
print("  - Cornici metalliche industriali spesse")
print("  - 2048 samples per fotorealismo")


