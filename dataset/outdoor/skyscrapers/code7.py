import bpy
import bmesh
import math

# Clear everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def add_realistic_details(obj):
    """Add realistic details with enhanced industrial features"""
    
    # Bevel for realistic edges with sharper corners
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.015
    bevel.segments = 1
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(45)
    
    # Subdivision
    subsurf = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    subsurf.levels = 1
    subsurf.render_levels = 2
    subsurf.quality = 3
    
    # Wireframe for structural grid
    wire = obj.modifiers.new(name="Wireframe", type="WIREFRAME")
    wire.thickness = 0.04
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_dark_glass_material(name):
    """Dark charcoal glass material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF for dark glass
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.15, 1)
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Alpha'].default_value = 0.4
    bsdf.inputs['IOR'].default_value = 1.45
    
    # Add some noise for variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 5.0
    
    # ColorRamp for controlling noise
    colorramp = nodes.new('ShaderNodeValToRGB')
    colorramp.location = (-150, 0)
    colorramp.color_ramp.elements[0].position = 0.45
    colorramp.color_ramp.elements[1].position = 0.55
    colorramp.color_ramp.elements[0].color = (0.08, 0.08, 0.12, 1)
    colorramp.color_ramp.elements[1].color = (0.16, 0.16, 0.18, 1)
    
    # Mix for subtle variation
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-150, -150)
    
    mix.inputs['Color1'].default_value = (0.12, 0.12, 0.15, 1)
    
    # Links
    
    links.new(colorramp.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Set blend mode for transparency
    mat.blend_method = 'BLEND'
    
    return mat

def create_bronze_frame_material(name):
    """Bronze-tinted metal frame material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.15, 0.12, 0.08, 1)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.25
    bsdf.inputs['IOR'].default_value = 2.8
    
    return mat

def create_supertall_tower(x_pos, name, height, base_w, top_w):
    """Enhanced supertall tower with thicker structure"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 85
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Enhanced thickness variation
        curve_factor = 1 - (0.4 * (math.sin(progress * math.pi)))
        width = (base_w * 1.1) - ((base_w * 1.1) - (top_w * 1.1)) * progress * curve_factor
        depth = width * 0.85
        
        # Slight angular offset for industrial look
        offset_x = math.sin(progress * math.pi * 0.3) * 0.5
        
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
    """Enhanced twisted tower with sharper edges"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    max_rotation = math.radians(120)
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Enhanced rotation with sharper transitions
        angle = max_rotation * progress * progress * 1.2
        
        # Thicker base dimensions
        scale = 1.0 - 0.2 * progress
        w = (width * 1.15) * scale
        d = w * 0.9
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Vertices with enhanced angular geometry
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
    """Enhanced parametric tower with more pronounced angles"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Enhanced parametric variation
        base = 14
        variation = 4 * math.sin(progress * math.pi * 2.5)
        width = base + variation
        depth = base - variation * 0.4
        
        # Add angular cutting for industrial look
        cut_factor = 0.8 + 0.2 * math.cos(progress * math.pi * 4)
        width *= cut_factor
        depth *= cut_factor
        
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

# CREATE TOWERS WITH MONOCHROMATIC DARK THEME
tower1 = create_supertall_tower(-35, "SupertallDark", 120, 18, 10)
glass1 = create_dark_glass_material("DarkGlass1")
frame1 = create_bronze_frame_material("BronzeFrame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_twisted_modern(0, "TwistedDark", 105, 15)
glass2 = create_dark_glass_material("DarkGlass2")
frame2 = create_bronze_frame_material("BronzeFrame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_parametric_tower(35, "ParametricDark", 95)
glass3 = create_dark_glass_material("DarkGlass3")
frame3 = create_bronze_frame_material("BronzeFrame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Dark ground plane
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ground = bpy.context.active_object
ground.scale = (60, 50, 0.5)

ground_mat = bpy.data.materials.new(name="DarkGroundMat")
ground_mat.use_nodes = True
g_bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
g_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1)
g_bsdf.inputs['Metallic'].default_value = 0.2
g_bsdf.inputs['Roughness'].default_value = 0.8
ground.data.materials.append(ground_mat)

# Cinematic camera
bpy.ops.object.camera_add(location=(85, -95, 40))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(68), 0, math.radians(42))
cam.data.lens = 38
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 90
cam.data.dof.aperture_fstop = 5.6
bpy.context.scene.camera = cam

# Darker HDRI atmosphere
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

# Dramatic main light
bpy.ops.object.light_add(type='SUN', location=(80, -70, 100))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.data.angle = math.radians(2.0)
sun.rotation_euler = (math.radians(25), 0, math.radians(135))
sun.data.color = (0.9, 0.85, 0.8)

# Subtle fill light
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 800
fill.data.size = 100
fill.data.color = (0.5, 0.6, 0.7)

# Moody rendering settings
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

# Enhanced light paths for dark materials
bpy.context.scene.cycles.max_bounces = 14
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 8
bpy.context.scene.cycles.transmission_bounces = 14
bpy.context.scene.cycles.transparent_max_bounces = 10

# Caustics for glass interaction
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 monochromatic dark industrial towers:")
print("  - Enhanced supertall (dark charcoal)")
print("  - Sharp twisted modern (dark charcoal)")
print("  - Angular parametric (dark charcoal)")
print("  - Bronze-tinted frames")
print("  - Industrial aesthetic with sharper edges")


