import bpy
import bmesh
import math

# Clear everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def add_realistic_details(obj):
    """Add realistic details with thicker frames"""
    
    # Thicker bevel for industrial look
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.05
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    
    # Subdivision for smoothing
    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Much thicker wireframe for bold grid pattern
    wire = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.12
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_industrial_glass_material(name, base_color, is_dark=False):
    """Dark industrial glass material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    # Principled BSDF for industrial glass
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    
    # Darken the glass colors significantly
    dark_color = (base_color[0] * 0.3, base_color[1] * 0.3, base_color[2] * 0.3, 0.4)
    principled.inputs['Base Color'].default_value = dark_color
    principled.inputs['Metallic'].default_value = 0.1
    principled.inputs['Roughness'].default_value = 0.15 if not is_dark else 0.25
    principled.inputs['Alpha'].default_value = 0.4
    principled.inputs['IOR'].default_value = 1.45
    
    # Add noise for subtle variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-200, 0)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # ColorRamp for contrast
    colorramp = nodes.new('ShaderNodeValToRGB')
    colorramp.location = (0, -200)
    colorramp.color_ramp.elements[0].position = 0.4
    colorramp.color_ramp.elements[1].position = 0.6
    
    # Mix with base color
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MULTIPLY'
    
    
    # Connect nodes
    links.new(noise.outputs['Fac'], colorramp.inputs['Fac'])
    links.new(colorramp.outputs['Color'], mix.inputs['Color2'])
    mix.inputs['Color1'].default_value = dark_color
    links.new(mix.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Enable blend mode for transparency
    mat.blend_method = 'BLEND'
    
    return mat

def create_heavy_metal_frame_material(name):
    """Heavy industrial metal frame material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    # Dark bronze/charcoal metal
    bsdf.inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.35
    
    return mat

def create_supertall_tower(x_pos, name, height, base_w, top_w):
    """Supertall tower with industrial proportions"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Interpolation with industrial curve
        curve_factor = 1 - (0.3 * (math.sin(progress * math.pi)))
        width = base_w - (base_w - top_w) * progress * curve_factor
        depth = width * 0.85
        
        # Slight curvature
        offset_x = math.sin(progress * math.pi * 0.5) * 0.2
        
        v1 = bm.verts.new((x_pos + offset_x - width/2, -depth/2, z))
        v2 = bm.verts.new((x_pos + offset_x + width/2, -depth/2, z))
        v3 = bm.verts.new((x_pos + offset_x + width/2, depth/2, z))
        v4 = bm.verts.new((x_pos + offset_x - width/2, depth/2, z))
        
        if floor > 0:
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

def create_twisted_modern(x_pos, name, height, width):
    """Industrial twisted tower"""
    
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
        
        # Rotation with easing
        angle = max_rotation * progress * progress
        
        # Size variation for industrial look
        scale = 1.0 - 0.2 * progress
        w = width * scale
        d = w
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Rotated vertices
        points = [
            (-w/2, -d/2),
            (w/2, -d/2),
            (w/2, d/2),
            (-w/2, d/2)
        ]
        
        for px, py in points:
            vx = x_pos + (px * cos_a - py * sin_a)
            vy = px * sin_a + py * cos_a
            bm.verts.new((vx, vy, z))
        
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

def create_parametric_tower(x_pos, name, height):
    """Industrial parametric tower"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # More pronounced industrial form
        base = 12
        variation = 2.5 * math.sin(progress * math.pi * 3)
        width = base + variation
        depth = base - variation * 0.4
        
        v1 = bm.verts.new((x_pos - width/2, -depth/2, z))
        v2 = bm.verts.new((x_pos + width/2, -depth/2, z))
        v3 = bm.verts.new((x_pos + width/2, depth/2, z))
        v4 = bm.verts.new((x_pos - width/2, depth/2, z))
        
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

# CREATE TOWERS WITH INDUSTRIAL MATERIALS
tower1 = create_supertall_tower(-35, "IndustrialBlue", 120, 18, 10)
glass1 = create_industrial_glass_material("DarkBlueGlass", (0.2, 0.3, 0.4, 1))
frame1 = create_heavy_metal_frame_material("HeavyFrame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_twisted_modern(0, "IndustrialBronze", 105, 15)
glass2 = create_industrial_glass_material("DarkBronzeGlass", (0.3, 0.25, 0.15, 1))
frame2 = create_heavy_metal_frame_material("HeavyFrame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_parametric_tower(35, "IndustrialCharcoal", 95)
glass3 = create_industrial_glass_material("DarkCharcoalGlass", (0.15, 0.2, 0.18, 1), is_dark=True)
frame3 = create_heavy_metal_frame_material("HeavyFrame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Industrial ground plane
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ground = bpy.context.active_object
ground.scale = (60, 50, 0.5)

ground_mat = bpy.data.materials.new(name="IndustrialGround")
ground_mat.use_nodes = True
g_bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
g_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1)
g_bsdf.inputs['Metallic'].default_value = 0.1
g_bsdf.inputs['Roughness'].default_value = 0.8
ground.data.materials.append(ground_mat)

# Camera setup
bpy.ops.object.camera_add(location=(85, -95, 40))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(68), 0, math.radians(42))
cam.data.lens = 38
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 90
cam.data.dof.aperture_fstop = 5.6
bpy.context.scene.camera = cam

# Darker, more industrial HDRI setup
world = bpy.data.worlds['World']
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

output = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
sky = nodes.new('ShaderNodeTexSky')

sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(25)
sky.sun_rotation = math.radians(135)
sky.sun_intensity = 0.8
sky.sun_disc = True
sky.air_density = 2.0
sky.dust_density = 3.0

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 0.7

# Dimmer main sun for industrial mood
bpy.ops.object.light_add(type='SUN', location=(80, -70, 100))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.data.angle = math.radians(2.0)
sun.rotation_euler = (math.radians(25), 0, math.radians(135))
sun.data.color = (0.95, 0.92, 0.88)

# Cooler fill light
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 800
fill.data.size = 80
fill.data.color = (0.6, 0.7, 0.9)

# Rendering settings for industrial look
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 2048
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'
bpy.context.scene.cycles.use_adaptive_sampling = True
bpy.context.scene.cycles.adaptive_threshold = 0.01
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Very High Contrast'
bpy.context.scene.view_settings.exposure = -0.2

# Light paths
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.transmission_bounces = 12
bpy.context.scene.cycles.transparent_max_bounces = 8

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 Industrial Skyscrapers Created:")
print("  - Dark blue supertall with heavy frames")
print("  - Bronze twisted tower with thick grid")
print("  - Charcoal parametric with bold structure")
print("  - Industrial materials and lighting")


