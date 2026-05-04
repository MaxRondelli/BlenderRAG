import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BASE
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.1))
base = bpy.context.active_object
base.scale = (0.6, 0.4, 0.05)

mat_base = bpy.data.materials.new(name="BaseBlack")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.4
base.data.materials.append(mat_base)

# POLE - Thicker with brushed metal
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.5, location=(0, 0, 1.35))
palo = bpy.context.active_object

mat_palo = bpy.data.materials.new(name="BrushedMetal")
mat_palo.use_nodes = True
nodes_palo = mat_palo.node_tree.nodes
links_palo = mat_palo.node_tree.links

bsdf_palo = nodes_palo["Principled BSDF"]
bsdf_palo.inputs['Base Color'].default_value = (0.7, 0.7, 0.75, 1)
bsdf_palo.inputs['Metallic'].default_value = 0.9
bsdf_palo.inputs['Roughness'].default_value = 0.15

# Add brushed texture
noise_tex = nodes_palo.new('ShaderNodeTexNoise')
noise_tex.inputs['Scale'].default_value = 50.0
noise_tex.inputs['Detail'].default_value = 15.0
noise_tex.inputs['Roughness'].default_value = 0.8

colorramp = nodes_palo.new('ShaderNodeValToRGB')
colorramp.color_ramp.elements[0].position = 0.4
colorramp.color_ramp.elements[1].position = 0.6

links_palo.new(noise_tex.outputs['Fac'], colorramp.inputs['Fac'])
links_palo.new(colorramp.outputs['Color'], bsdf_palo.inputs['Roughness'])

palo.data.materials.append(mat_palo)

# MAIN HOUSING - Modern rectangular design
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.9))
corpo = bpy.context.active_object
corpo.scale = (0.35, 0.25, 0.9)

# Add bevel for modern look
bevel_modifier = corpo.modifiers.new(name="Bevel", type="BEVEL")
bevel_modifier.width = 0.02
bevel_modifier.segments = 3

mat_corpo = bpy.data.materials.new(name="ModernHousing")
mat_corpo.use_nodes = True
bsdf_corpo = mat_corpo.node_tree.nodes["Principled BSDF"]
bsdf_corpo.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1)
bsdf_corpo.inputs['Roughness'].default_value = 0.3
bsdf_corpo.inputs['Metallic'].default_value = 0.2
corpo.data.materials.append(mat_corpo)

# LIGHTS WITH VISORS - Blue, Orange, White
luci_data = [
    ("Blue", (0.2, 0.5, 1.0), 3.25),
    ("Orange", (1.0, 0.5, 0.1), 2.9),
    ("White", (1.0, 1.0, 0.95), 2.55)
]

for nome, colore, z_pos in luci_data:
    # VISOR above light - rectangular style
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.12, z_pos + 0.08))
    visiera = bpy.context.active_object
    visiera.scale = (0.22, 0.08, 0.04)
    visiera.rotation_euler = (math.radians(15), 0, 0)
    visiera.data.materials.append(mat_corpo)
    
    # Light (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0.03, z_pos))
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
    glass.inputs['Roughness'].default_value = 0.0
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs[0].default_value = 0.7
    
    luce.data.materials.append(mat_luce)
    
    # Black ring - rectangular frame
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.03, z_pos))
    anello = bpy.context.active_object
    anello.scale = (0.18, 0.02, 0.18)
    anello.data.materials.append(mat_corpo)
    
    # Inner cutout for light
    bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.1, location=(0, 0.03, z_pos))
    cutout = bpy.context.active_object
    
    # Boolean modifier to cut hole
    bool_modifier = anello.modifiers.new(name="Boolean", type="BOOLEAN")
    bool_modifier.operation = 'DIFFERENCE'
    bool_modifier.object = cutout
    
    # Hide cutout object
    cutout.hide_set(True)

# CAMERA
bpy.ops.object.camera_add(location=(1.8, -2.2, 2.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(35))
bpy.context.scene.camera = camera

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.data.angle = math.radians(5)

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 2.0

# Fill light
bpy.ops.object.light_add(type='AREA', location=(2, 1, 2))
fill = bpy.context.active_object
fill.data.energy = 80
fill.data.size = 1.5

# WORLD HDRI
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.2

# RENDER SETTINGS
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

print("Modern rectangular stoplight with blue, orange, and white lights created!")

