import bpy
import bmesh
import math

# Clear everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def add_realistic_details(obj):
    """Add realistic details with thicker wireframe"""
    
    # Bevel for realistic edges
    bevel = obj.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.02
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    
    # Accurate subdivision
    subsurf = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Thicker wireframe for pronounced grid
    wire = obj.modifiers.new(name="Wireframe", type="WIREFRAME")
    wire.thickness = 0.05
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_industrial_glass_material(name, base_tint):
    """Dark charcoal-tinted glass material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF for dark glass
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    # Dark charcoal base with tint
    dark_color = (base_tint[0] * 0.15, base_tint[1] * 0.15, base_tint[2] * 0.15, 0.3)
    principled.inputs['Base Color'].default_value = dark_color
    principled.inputs['Metallic'].default_value = 0.1
    principled.inputs['Roughness'].default_value = 0.15
    principled.inputs['Alpha'].default_value = 0.3
    principled.inputs['IOR'].default_value = 1.45
    
    # Connect to output
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Enable blend mode
    mat.blend_method = 'BLEND'
    
    return mat

def create_industrial_frame_material(name):
    """Industrial metal frame with increased roughness"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.03, 0.03, 0.04, 1)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.45
    
    return mat

def create_supertall_tower(x_pos, name, height, base_w, top_w):
    """Supertall realistic skyscraper"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Width interpolation with curves
        curve_factor = 1 - (0.3 * (math.sin(progress * math.pi)))
        width = base_w - (base_w - top_w) * progress * curve_factor
        depth = width * 0.9
        
        # Add slight curvature
        offset_x = math.sin(progress * math.pi * 0.5) * 0.3
        
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
    """Twisted modern tower"""
    
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
        
        # Variable size
        scale = 1.0 - 0.25 * progress
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
    """Tower with parametric geometry"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Shape that expands and contracts
        base = 12
        variation = 3 * math.sin(progress * math.pi * 3)
        width = base + variation
        depth = base - variation * 0.5
        
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

# CREATE TOWERS WITH INDUSTRIAL AESTHETIC
tower1 = create_supertall_tower(-35, "IndustrialBlue", 120, 18, 10)
glass1 = create_industrial_glass_material("CharcoalBlue", (0.5, 0.65, 0.85))
frame1 = create_industrial_frame_material("IndustrialFrame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_twisted_modern(0, "IndustrialGold", 105, 15)
glass2 = create_industrial_glass_material("CharcoalGold", (0.85, 0.65, 0.35))
frame2 = create_industrial_frame_material("IndustrialFrame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_parametric_tower(35, "IndustrialGreen", 95)
glass3 = create_industrial_glass_material("CharcoalGreen", (0.3, 0.55, 0.45))
frame3 = create_industrial_frame_material("IndustrialFrame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Realistic ground plane
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
ground = bpy.context.active_object
ground.scale = (60, 50, 0.5)

ground_mat = bpy.data.materials.new(name="IndustrialGround")
ground_mat.use_nodes = True
g_bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
g_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1)
g_bsdf.inputs['Metallic'].default_value = 0.6
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

# Realistic HDRI
world = bpy.data.worlds['World']
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()

output = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
sky = nodes.new('ShaderNodeTexSky')

sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(25)
sky.sun_rotation = math.radians(125)
sky.sun_intensity = 0.8
sky.sun_disc = True
sky.air_density = 1.2
sky.dust_density = 2.0

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 0.8

# Main sun light
bpy.ops.object.light_add(type='SUN', location=(80, -70, 100))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.data.angle = math.radians(1.5)
sun.rotation_euler = (math.radians(25), 0, math.radians(125))
sun.data.color = (0.95, 0.93, 0.90)

# Ambient fill light
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 800
fill.data.size = 80
fill.data.color = (0.6, 0.7, 0.9)

# Photorealistic render settings
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
bpy.context.scene.view_settings.exposure = 0.1

# Light paths for realism
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.transmission_bounces = 12
bpy.context.scene.cycles.transparent_max_bounces = 8

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 industrial skyscrapers created:")
print("  - Charcoal-tinted glass materials")
print("  - Increased metallic roughness")
print("  - Thicker wireframe grid patterns")
print("  - 2048 samples for photorealism")



