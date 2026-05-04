import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Clear existing materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

# Create the metal base stand
def create_metal_base():
    # Create a cone for the metal stand
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=0.55,
        radius2=0.45,
        depth=0.18,
        location=(0, 0, 0.09)
    )
    base = bpy.context.active_object
    base.name = "Metal_Base"
    
    # Add subdivision for smooth appearance
    subsurf = base.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    
    # Create black metal material
    mat_base = bpy.data.materials.new(name="Black_Metal")
    mat_base.use_nodes = True
    base.data.materials.append(mat_base)
    
    nodes = mat_base.node_tree.nodes
    nodes.clear()
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Matte black metal color
    node_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 0.8
    node_bsdf.inputs['Roughness'].default_value = 0.25
    
    links = mat_base.node_tree.links
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    node_bsdf.location = (0, 0)
    node_output.location = (200, 0)
    
    return base

# Create the bulbous glass base with amber tint
def create_glass_bulb():
    # Create UV sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64,
        ring_count=32,
        radius=1,
        location=(0, 0, 0.65)
    )
    bulb = bpy.context.active_object
    bulb.name = "Glass_Bulb"
    
    # Enter edit mode to reshape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Modify vertices to create more angular bulbous shape
    mesh = bulb.data
    for vert in mesh.vertices:
        z = vert.co.z
        radius = math.sqrt(vert.co.x**2 + vert.co.y**2)
        
        # Create more angular geometric shape
        if z > 0.4:  # Upper portion - sharper taper
            scale_factor = 0.3 + (1.0 - z) * 0.5
        elif z > -0.1:  # Middle - more defined widest part
            scale_factor = 1.15 + math.sin((z + 0.1) * 4) * 0.05
        else:  # Bottom - more angular base
            scale_factor = 0.8 + (z + 0.1) * 0.4
        
        scale_factor = max(0.25, min(1.25, scale_factor))
        vert.co.x *= scale_factor
        vert.co.y *= scale_factor
        
        # More defined bottom
        if z < -0.75:
            vert.co.z = max(vert.co.z, -0.8)
    
    # Scale the bulb
    bulb.scale = (0.7, 0.7, 0.85)
    
    # Add subdivision surface
    subsurf = bulb.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    
    # Create amber glass material
    mat_glass = bpy.data.materials.new(name="Amber_Glass")
    mat_glass.use_nodes = True
    bulb.data.materials.append(mat_glass)
    
    nodes = mat_glass.node_tree.nodes
    nodes.clear()
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_mix = nodes.new(type='ShaderNodeMixShader')
    
    # Amber glass appearance
    node_bsdf.inputs['Base Color'].default_value = (0.9, 0.65, 0.3, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 0.0
    node_bsdf.inputs['Roughness'].default_value = 0.05
    
    # Warm amber glow
    node_emission.inputs['Color'].default_value = (1.0, 0.7, 0.4, 1.0)
    
    links = mat_glass.node_tree.links
    links.new(node_bsdf.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_emission.outputs['Emission'], node_mix.inputs[2])
    node_mix.inputs[0].default_value = 0.4  # Mix factor
    links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])
    
    node_bsdf.location = (-200, 100)
    node_emission.location = (-200, -100)
    node_mix.location = (0, 0)
    node_output.location = (200, 0)
    
    return bulb

# Create the neck/stem between bulb and shade
def create_neck():
    # Create cylinder for neck - slightly thicker
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=0.25,
        depth=0.45,
        location=(0, 0, 1.4)
    )
    neck = bpy.context.active_object
    neck.name = "Glass_Neck"
    
    # Add subdivision
    subsurf = neck.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    
    # Use same amber glass material
    mat_glass = bpy.data.materials.get("Amber_Glass")
    if mat_glass:
        neck.data.materials.append(mat_glass)
    
    return neck

# Create the lampshade with more angular profile
def create_lampshade():
    # Create truncated cone for shade
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=0.8,
        radius2=1.4,
        depth=1.2,
        location=(0, 0, 2.25)
    )
    shade = bpy.context.active_object
    shade.name = "Glass_Shade"
    
    # Modify the shade to have more angular geometric profile
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = shade.data
    for vert in mesh.vertices:
        z = vert.co.z
        radius = math.sqrt(vert.co.x**2 + vert.co.y**2)
        
        # Create more angular geometric shade profile
        if z > 0:
            # Upper portion - straight flare outward
            curve_factor = 1.0 + (z / 0.6) * 0.2
        else:
            # Lower portion - minimal curve, more angular
            curve_factor = 1.0 - abs(z / 0.6) * 0.05
        
        vert.co.x *= curve_factor
        vert.co.y *= curve_factor
    
    # Add subdivision for smooth curves
    subsurf = shade.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 4
    
    # Add solidify modifier for thickness - slightly thicker
    solidify = shade.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 0.04
    solidify.offset = 0
    
    # Use amber glass material
    mat_glass = bpy.data.materials.get("Amber_Glass")
    if mat_glass:
        shade.data.materials.append(mat_glass)
    
    return shade

# Add key lighting to illuminate the lamp
def create_lighting():
    # Main key light
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 280
    key_light.data.size = 2.0
    key_light.data.color = (1.0, 0.9, 0.8)
    
    # Rim light to highlight glass edges
    bpy.ops.object.light_add(type='AREA', location=(-2, 2, 3))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim_Light"
    rim_light.data.energy = 140
    rim_light.data.size = 1.5
    rim_light.data.color = (0.9, 0.85, 1.0)
    
    # Soft fill light from below
    bpy.ops.object.light_add(type='AREA', location=(0, 0, -1))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 45
    fill_light.data.size = 3.0
    fill_light.rotation_euler = (0, 0, 0)

print("Creating modern lamp with amber glass and black metal base...")

# Create all components
base = create_metal_base()
bulb = create_glass_bulb()
neck = create_neck()
shade = create_lampshade()

# Add lighting
create_lighting()

# Set up camera
bpy.ops.object.camera_add(location=(4.5, -4.5, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(78), 0, math.radians(45))
bpy.context.scene.camera = camera

# Set up world (normal gray background)
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)  # Medium gray
bg_node.inputs[1].default_value = 1.0

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.view_settings.exposure = 0.3

# Enable better rendering
bpy.context.scene.render.film_transparent = False

# Set viewport shading to Material Preview to see colors
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.shading.use_scene_lights = True
                space.shading.use_scene_world = True
                break

print("Modern lamp created!")
print("- Metal base: Matte black finish")
print("- Glass shade and bulb: Amber-tinted with warm glow")
print("- More angular, geometric proportions")
print("Switch to 'Rendered' viewport (Z key -> Rendered) to see the full effect.")