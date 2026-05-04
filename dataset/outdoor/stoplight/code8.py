import bpy
import bmesh
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BASE
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.1))
base = bpy.context.active_object
base.scale = (0.5, 0.3, 0.05)

# Add subdivision and smooth base
modifier = base.modifiers.new(name="Subsurf", type="SUBSURF")
modifier.levels = 2
bpy.context.view_layer.objects.active = base
bpy.ops.object.shade_smooth()

mat_base = bpy.data.materials.new(name="BaseBlack")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.4
base.data.materials.append(mat_base)

# POLE
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
palo = bpy.context.active_object

mat_palo = bpy.data.materials.new(name="PaloGrigio")
mat_palo.use_nodes = True
bsdf_palo = mat_palo.node_tree.nodes["Principled BSDF"]
bsdf_palo.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1)
bsdf_palo.inputs['Metallic'].default_value = 0.7
bsdf_palo.inputs['Roughness'].default_value = 0.3
palo.data.materials.append(mat_palo)

# MAIN BODY - Modern rounded rectangular housing
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.9))
corpo = bpy.context.active_object
corpo.scale = (0.18, 0.14, 0.7)

# Add subdivision for rounded edges
modifier = corpo.modifiers.new(name="Subsurf", type="SUBSURF")
modifier.levels = 3
bpy.context.view_layer.objects.active = corpo
bpy.ops.object.shade_smooth()

# Brushed metallic silver material for main body
mat_corpo = bpy.data.materials.new(name="CorpoBrushedSilver")
mat_corpo.use_nodes = True
nodes = mat_corpo.node_tree.nodes
links = mat_corpo.node_tree.links

bsdf_corpo = nodes["Principled BSDF"]
bsdf_corpo.inputs['Base Color'].default_value = (0.8, 0.82, 0.85, 1)
bsdf_corpo.inputs['Metallic'].default_value = 0.9
bsdf_corpo.inputs['Roughness'].default_value = 0.15

# Add noise texture for brushed metal effect
noise_tex = nodes.new('ShaderNodeTexNoise')
noise_tex.inputs['Scale'].default_value = 150
noise_tex.inputs['Detail'].default_value = 16

color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1)
color_ramp.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1)

links.new(color_ramp.outputs['Color'], bsdf_corpo.inputs['Roughness'])

corpo.data.materials.append(mat_corpo)

# HEXAGONAL LIGHTS WITH HOODS
luci_data = [
    ("Rosso", (1, 0, 0), 3.15),
    ("Giallo", (1, 0.6, 0), 2.9),
    ("Verde", (0, 1, 0), 2.65)
]

for nome, colore, z_pos in luci_data:
    # HOOD above the light
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.08, location=(0, 0.08, z_pos + 0.08))
    visiera = bpy.context.active_object
    visiera.rotation_euler = (math.radians(90), 0, 0)
    visiera.scale = (1, 0.6, 1)
    
    # Add subdivision for smooth hood
    modifier = visiera.modifiers.new(name="Subsurf", type="SUBSURF")
    modifier.levels = 2
    bpy.context.view_layer.objects.active = visiera
    bpy.ops.object.shade_smooth()
    
    visiera.data.materials.append(mat_corpo)
    
    # Hexagonal light panel
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.08, depth=0.02, location=(0, 0.02, z_pos))
    luce = bpy.context.active_object
    
    # Emissive glass material
    mat_luce = bpy.data.materials.new(name=f"Mat_{nome}")
    mat_luce.use_nodes = True
    nodes = mat_luce.node_tree.nodes
    links = mat_luce.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mix = nodes.new('ShaderNodeMixShader')
    emission = nodes.new('ShaderNodeEmission')
    glass = nodes.new('ShaderNodeBsdfGlass')
    
    emission.inputs['Color'].default_value = (*colore, 1)
    emission.inputs['Strength'].default_value = 10.0
    glass.inputs['Color'].default_value = (*colore, 1)
    glass.inputs['IOR'].default_value = 1.45
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs['Fac'].default_value = 0.8
    
    luce.data.materials.append(mat_luce)
    
    # Black ring around hexagonal light
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.015, location=(0, 0.025, z_pos))
    anello = bpy.context.active_object
    anello.rotation_euler = (math.radians(90), 0, 0)
    
    # Create dark metallic ring material
    mat_ring = bpy.data.materials.new(name=f"Ring_{nome}")
    mat_ring.use_nodes = True
    bsdf_ring = mat_ring.node_tree.nodes["Principled BSDF"]
    bsdf_ring.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    bsdf_ring.inputs['Metallic'].default_value = 0.3
    bsdf_ring.inputs['Roughness'].default_value = 0.1
    
    anello.data.materials.append(mat_ring)

# CAMERA
bpy.ops.object.camera_add(location=(1.5, -1.8, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(40))
bpy.context.scene.camera = camera

# LIGHTS
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
area = bpy.context.active_object
area.data.energy = 150

# WORLD HDRI
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.3

# RENDER SETTINGS
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'

print("Modern hexagonal stoplight with brushed silver housing created!")

