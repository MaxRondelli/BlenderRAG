import bpy
import bmesh
import math

# Clear everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def add_realistic_details(obj):
    """Add realistic details"""
    
    # Bevel for realistic edges
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 1
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(60)
    
    # Subdivision
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2
    subsurf.quality = 2
    
    # Wireframe for concrete panel grid
    wire = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.08
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_brutalist_glass_material(name, base_color, tint_darkness=0.3):
    """Dark tinted glass material with concrete frame feeling"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    # Main glass shader - darker and more reflective
    glass = nodes.new('ShaderNodeBsdfPrincipled')
    glass.location = (200, 100)
    
    # Darken the base color significantly
    darkened_color = [c * (1 - tint_darkness) for c in base_color[:3]] + [0.7]
    glass.inputs['Base Color'].default_value = darkened_color
    glass.inputs['Metallic'].default_value = 0.0
    glass.inputs['Roughness'].default_value = 0.15
    glass.inputs['Alpha'].default_value = 0.7
    glass.inputs['IOR'].default_value = 1.52
    
    # Mix with emission for slight glow from interior lighting
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, -100)
    emission.inputs['Color'].default_value = (0.2, 0.25, 0.3, 1.0)
    emission.inputs['Strength'].default_value = 0.8
    
    # Fresnel for realistic glass behavior
    fresnel = nodes.new('ShaderNodeFresnel')
    fresnel.location = (-200, 0)
    fresnel.inputs['IOR'].default_value = 1.52
    
    # Mix the shaders
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (400, 0)
    
    # Connect nodes
    links.new(glass.outputs['BSDF'], mix.inputs[1])
    links.new(emission.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    mat.blend_method = 'BLEND'
    
    return mat

def create_concrete_frame_material(name):
    """Brutalist concrete material with steel accents"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    # Concrete base
    bsdf.inputs['Base Color'].default_value = (0.12, 0.13, 0.14, 1)
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Roughness'].default_value = 0.8
    
    # Add noise for concrete texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Color ramp for concrete variation
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.08, 0.09, 0.1, 1)
    ramp.color_ramp.elements[1].color = (0.16, 0.17, 0.18, 1)
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    return mat

def create_stepped_brutalist_tower(x_pos, name, height, base_w, segments):
    """Angular stepped brutalist tower"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    segment_height = height / segments
    
    for segment in range(segments + 1):
        z = segment * segment_height
        progress = segment / segments
        
        # Step down width in angular chunks
        step_factor = 1.0 - (progress * 0.6)
        if segment % 8 == 0 and segment > 0:
            step_factor *= 0.85  # Create dramatic steps
            
        width = base_w * step_factor
        depth = width * 1.2
        
        # Create rectangular profile
        v1 = bm.verts.new((x_pos - width/2, -depth/2, z))
        v2 = bm.verts.new((x_pos + width/2, -depth/2, z))
        v3 = bm.verts.new((x_pos + width/2, depth/2, z))
        v4 = bm.verts.new((x_pos - width/2, depth/2, z))
        
        if segment > 0:
            prev_verts = bm.verts[-8:-4]
            curr_verts = bm.verts[-4:]
            
            for i in range(4):
                next_i = (i + 1) % 4
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    # Close top and bottom
    bottom_verts = bm.verts[0:4]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-4:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_angular_fortress_tower(x_pos, name, height, width):
    """Fortress-like angular tower"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 60
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Create angular profile with setbacks
        scale = 1.0
        if progress > 0.3:
            scale = 1.0 - (progress - 0.3) * 0.7
        if progress > 0.7:
            scale *= 0.8
            
        # Octagonal shape for more brutalist feel
        w = width * scale
        d = w * 0.9
        
        # Create chamfered corners
        corner_cut = w * 0.15
        
        vertices = [
            (x_pos - w/2 + corner_cut, -d/2, z),
            (x_pos + w/2 - corner_cut, -d/2, z),
            (x_pos + w/2, -d/2 + corner_cut, z),
            (x_pos + w/2, d/2 - corner_cut, z),
            (x_pos + w/2 - corner_cut, d/2, z),
            (x_pos - w/2 + corner_cut, d/2, z),
            (x_pos - w/2, d/2 - corner_cut, z),
            (x_pos - w/2, -d/2 + corner_cut, z)
        ]
        
        for vx, vy, vz in vertices:
            bm.verts.new((vx, vy, vz))
        
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

def create_geometric_monolith(x_pos, name, height):
    """Geometric monolithic tower with dramatic angles"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 70
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Create dramatic geometric changes
        base = 14
        if progress < 0.4:
            width = base
            depth = base * 0.7
        elif progress < 0.6:
            width = base * 0.8
            depth = base * 1.1
        else:
            width = base * 0.6
            depth = base * 0.6
        
        # Add angular offset for dramatic effect
        offset = 0
        if progress > 0.4:
            offset = (progress - 0.4) * 8
            
        v1 = bm.verts.new((x_pos + offset - width/2, -depth/2, z))
        v2 = bm.verts.new((x_pos + offset + width/2, -depth/2, z))
        v3 = bm.verts.new((x_pos + offset + width/2, depth/2, z))
        v4 = bm.verts.new((x_pos + offset - width/2, depth/2, z))
        
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

# CREATE BRUTALIST TOWERS
tower1 = create_stepped_brutalist_tower(-35, "BrutalistGray", 120, 20, 80)
glass1 = create_brutalist_glass_material("DarkGrayGlass", (0.25, 0.28, 0.32, 1), 0.5)
frame1 = create_concrete_frame_material("ConcreteFrame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_angular_fortress_tower(0, "FortressBlue", 110, 17)
glass2 = create_brutalist_glass_material("DeepBlueGlass", (0.15, 0.2, 0.35, 1), 0.6)
frame2 = create_concrete_frame_material("ConcreteFrame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_geometric_monolith(35, "GeometricMonolith", 100)
glass3 = create_brutalist_glass_material("CharcoalGlass", (0.12, 0.14, 0.16, 1), 0.7)
frame3 = create_concrete_frame_material("ConcreteFrame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Concrete plaza
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ground = bpy.context.active_object
ground.scale = (70, 60, 0.5)

ground_mat = bpy.data.materials.new(name="ConcretePlaza")
ground_mat.use_nodes = True
nodes = ground_mat.node_tree.nodes
links = ground_mat.node_tree.links
g_bsdf = nodes.get("Principled BSDF")

# Add concrete texture to ground
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 8.0

ramp = nodes.new('ShaderNodeValToRGB')
ramp.location = (-200, 0)
ramp.color_ramp.elements[0].color = (0.1, 0.11, 0.12, 1)
ramp.color_ramp.elements[1].color = (0.15, 0.16, 0.17, 1)

links.new(ramp.outputs['Color'], g_bsdf.inputs['Base Color'])

g_bsdf.inputs['Metallic'].default_value = 0.0
g_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

# Dramatic camera angle
bpy.ops.object.camera_add(location=(90, -100, 25))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(78), 0, math.radians(48))
cam.data.lens = 28
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 95
cam.data.dof.aperture_fstop = 8.0
bpy.context.scene.camera = cam

# Overcast brutalist sky
world = bpy.data.worlds['World']
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

output = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
sky = nodes.new('ShaderNodeTexSky')

sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(15)
sky.sun_rotation = math.radians(180)
sky.sun_intensity = 0.8
sky.sun_disc = False
sky.air_density = 2.0
sky.dust_density = 3.0

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 0.7

# Harsh directional light
bpy.ops.object.light_add(type='SUN', location=(60, -80, 80))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.data.angle = math.radians(5.0)
sun.rotation_euler = (math.radians(60), 0, math.radians(160))
sun.data.color = (0.95, 0.96, 1.0)

# Cold fill light
bpy.ops.object.light_add(type='AREA', location=(-40, 60, 40))
fill = bpy.context.active_object
fill.data.energy = 800
fill.data.size = 100
fill.data.color = (0.6, 0.65, 0.8)

# Rendering settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 1536
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.adaptive_threshold = 0.02
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = -0.2

# Light paths
bpy.context.scene.cycles.max_bounces = 8
bpy.context.scene.cycles.diffuse_bounces = 3
bpy.context.scene.cycles.glossy_bounces = 4
bpy.context.scene.cycles.transmission_bounces = 8
bpy.context.scene.cycles.transparent_max_bounces = 6

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 Brutalist Concrete Towers:")
print("  - Stepped angular monolith (dark gray)")
print("  - Fortress-like octagonal (deep blue)")
print("  - Geometric offset tower (charcoal)")
print("  - Heavy concrete aesthetic with dark tinted glass")


