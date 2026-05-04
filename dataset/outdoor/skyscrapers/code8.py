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
    bevel.width = 0.02
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    
    # Accurate subdivision
    subsurf = obj.modifiers.new(name="Subdivision", type="SUBSURF")
    subsurf.levels = 2
    subsurf.render_levels = 3
    
    # Thin wireframe for grid
    wire = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.03
    wire.use_replace = False
    wire.use_boundary = True
    wire.material_offset = 1

def create_modern_glass_material(name, base_color, is_dark=False):
    """Photorealistic glass material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF for glass-like material
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.02 if not is_dark else 0.05
    principled.inputs['Alpha'].default_value = 0.15
    principled.inputs['IOR'].default_value = 1.45
    
    # Layer Weight for realistic fresnel
    layer = nodes.new('ShaderNodeLayerWeight')
    layer.location = (-200, 100)
    layer.inputs['Blend'].default_value = 0.3
    
    # Connect nodes
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Set blend mode for transparency
    mat.blend_method = 'BLEND'
    
    return mat

def create_metal_frame_material(name):
    """Metal frame material"""
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.18
    
    return mat

def create_angular_supertall_tower(x_pos, name, height, base_w, top_w):
    """Angular crystalline supertall skyscraper"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 80
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Sharp angular interpolation
        angular_factor = 1 - (0.4 * progress * progress)
        width = base_w - (base_w - top_w) * progress * angular_factor
        depth = width * 0.85
        
        # Add crystalline faceting
        facet_offset = 0.5 * math.sin(progress * math.pi * 4)
        
        # Create octagonal cross-section for more angular look
        angle_step = math.pi / 4
        verts = []
        for i in range(8):
            angle = i * angle_step
            radius_x = width / 2 + facet_offset * (0.1 if i % 2 == 0 else -0.1)
            radius_y = depth / 2 + facet_offset * (0.1 if i % 2 == 1 else -0.1)
            x = x_pos + radius_x * math.cos(angle)
            y = radius_y * math.sin(angle)
            verts.append(bm.verts.new((x, y, z)))
        
        if floor > 0:
            prev_verts = bm.verts[-16:-8]
            curr_verts = bm.verts[-8:]
            
            for i in range(8):
                next_i = (i + 1) % 8
                bm.faces.new([prev_verts[i], prev_verts[next_i], 
                             curr_verts[next_i], curr_verts[i]])
    
    # Close bottom and top
    bottom_verts = bm.verts[0:8]
    bm.faces.new(bottom_verts)
    top_verts = bm.verts[-8:]
    bm.faces.new(reversed(top_verts))
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj

def create_crystalline_twisted_tower(x_pos, name, height, width):
    """Crystalline twisted tower"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 70
    floor_height = height / floors
    max_rotation = math.radians(120)
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Sharp rotation with angular steps
        angle = max_rotation * progress * progress * progress
        
        # Variable size with angular cuts
        scale = 1.0 - 0.3 * progress
        w = width * scale
        d = w * 0.9
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Hexagonal cross-section for sharper edges
        points = []
        for i in range(6):
            hex_angle = i * math.pi / 3
            px = (w/2) * math.cos(hex_angle)
            py = (d/2) * math.sin(hex_angle)
            points.append((px, py))
        
        for px, py in points:
            vx = x_pos + (px * cos_a - py * sin_a)
            vy = px * sin_a + py * cos_a
            bm.verts.new((vx, vy, z))
        
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

def create_faceted_parametric_tower(x_pos, name, height):
    """Tower with sharp parametric geometry"""
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    floors = 75
    floor_height = height / floors
    
    for floor in range(floors + 1):
        z = floor * floor_height
        progress = floor / floors
        
        # Sharp expanding and contracting form
        base = 12
        variation = 4 * math.sin(progress * math.pi * 2.5)
        width = base + variation
        depth = base - variation * 0.3
        
        # Add sharp corner cuts
        corner_cut = 2 * abs(math.sin(progress * math.pi * 6))
        
        # Create diamond-like cross section
        v1 = bm.verts.new((x_pos, -depth/2 - corner_cut, z))
        v2 = bm.verts.new((x_pos + width/2 + corner_cut, 0, z))
        v3 = bm.verts.new((x_pos, depth/2 + corner_cut, z))
        v4 = bm.verts.new((x_pos - width/2 - corner_cut, 0, z))
        
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

# CREATE TOWERS WITH WARM BRONZE PALETTE
tower1 = create_angular_supertall_tower(-35, "AngularAmber", 120, 18, 10)
glass1 = create_modern_glass_material("AmberGlass", (0.85, 0.55, 0.25, 1))
frame1 = create_metal_frame_material("Frame1")
tower1.data.materials.append(glass1)
tower1.data.materials.append(frame1)
add_realistic_details(tower1)

tower2 = create_crystalline_twisted_tower(0, "CrystallineCopper", 105, 15)
glass2 = create_modern_glass_material("CopperGlass", (0.75, 0.35, 0.25, 1))
frame2 = create_metal_frame_material("Frame2")
tower2.data.materials.append(glass2)
tower2.data.materials.append(frame2)
add_realistic_details(tower2)

tower3 = create_faceted_parametric_tower(35, "FacetedBurgundy", 95)
glass3 = create_modern_glass_material("BurgundyGlass", (0.45, 0.15, 0.15, 1), is_dark=True)
frame3 = create_metal_frame_material("Frame3")
tower3.data.materials.append(glass3)
tower3.data.materials.append(frame3)
add_realistic_details(tower3)

# Realistic ground plane
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
sky.sun_rotation = math.radians(135)
sky.sun_intensity = 1.2
sky.sun_disc = True
sky.air_density = 1.0
sky.dust_density = 2.0

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 1.3

# Main sun light
bpy.ops.object.light_add(type='SUN', location=(80, -70, 100))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.data.angle = math.radians(1.5)
sun.rotation_euler = (math.radians(25), 0, math.radians(135))
sun.data.color = (1.0, 0.9, 0.8)

# Warm fill light
bpy.ops.object.light_add(type='AREA', location=(-50, 50, 60))
fill = bpy.context.active_object
fill.data.energy = 1500
fill.data.size = 80
fill.data.color = (0.9, 0.7, 0.5)

# Photorealistic rendering settings
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
bpy.context.scene.view_settings.exposure = 0.4

# Light paths for realism
bpy.context.scene.cycles.max_bounces = 12
bpy.context.scene.cycles.diffuse_bounces = 4
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.transmission_bounces = 12
bpy.context.scene.cycles.transparent_max_bounces = 8

# Caustics
bpy.context.scene.cycles.caustics_reflective = True
bpy.context.scene.cycles.caustics_refractive = True

print("✓ 3 crystalline skyscrapers with warm bronze palette:")
print("  - Angular supertall (amber)")
print("  - Crystalline twisted (copper)")
print("  - Faceted parametric (burgundy)")
print("  - 2048 samples for photorealism")

