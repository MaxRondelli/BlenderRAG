import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BASE
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.1))
base = bpy.context.active_object
base.scale = (0.5, 0.3, 0.05)

mat_base = bpy.data.materials.new(name="BaseBlack")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.4
base.data.materials.append(mat_base)

# POLE - Chrome material
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
palo = bpy.context.active_object

mat_palo = bpy.data.materials.new(name="ChromePole")
mat_palo.use_nodes = True
bsdf_palo = mat_palo.node_tree.nodes["Principled BSDF"]
bsdf_palo.inputs['Base Color'].default_value = (0.9, 0.9, 0.95, 1)
bsdf_palo.inputs['Metallic'].default_value = 1.0
bsdf_palo.inputs['Roughness'].default_value = 0.05
palo.data.materials.append(mat_palo)

# MAIN BODY - Sleeker rectangular design
bpy.ops.mesh.primitive_cube_add(size=1., location=(0, 0, 2.9))
corpo = bpy.context.active_object
corpo.scale = (0.15, 0.12, 0.75)

# Add subdivision for smoother appearance
subsurf_mod = corpo.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf_mod.levels = 2

mat_corpo = bpy.data.materials.new(name="ChromeHousing")
mat_corpo.use_nodes = True
bsdf_corpo = mat_corpo.node_tree.nodes["Principled BSDF"]
bsdf_corpo.inputs['Base Color'].default_value = (0.85, 0.85, 0.9, 1)
bsdf_corpo.inputs['Roughness'].default_value = 0.08
bsdf_corpo.inputs['Metallic'].default_value = 0.95
corpo.data.materials.append(mat_corpo)

# LIGHTS WITH VISORS - Larger and more pronounced
luci_data = [
    ("Rosso", (1, 0, 0), 3.2),
    ("Giallo", (1, 0.6, 0), 2.9),
    ("Verde", (0, 1, 0), 2.6)
]

for nome, colore, z_pos in luci_data:
    # VISOR above light - more pronounced
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.1, location=(0, 0.09, z_pos + 0.1))
    visiera = bpy.context.active_object
    visiera.rotation_euler = (math.radians(90), 0, 0)
    visiera.scale = (1, 0.7, 1)
    visiera.data.materials.append(mat_corpo)
    
    # Light (sphere) - larger
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, location=(0, 0.025, z_pos))
    luce = bpy.context.active_object
    
    # Add subdivision for smoother light
    light_subsurf = luce.modifiers.new(name="LightSubsurf", type="SUBSURF")
    light_subsurf.levels = 2
    
    # Emissive glass material with brighter emission
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
    emission.inputs['Strength'].default_value = 12.0
    glass.inputs['Color'].default_value = (*colore, 1)
    glass.inputs['IOR'].default_value = 1.45
    glass.inputs['Roughness'].default_value = 0.0
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs['Fac'].default_value = 0.85
    
    luce.data.materials.append(mat_luce)
    
    # Black ring - slightly larger
    bpy.ops.mesh.primitive_torus_add(major_radius=0.105, minor_radius=0.014, location=(0, 0.025, z_pos))
    anello = bpy.context.active_object
    anello.rotation_euler = (math.radians(90), 0, 0)
    
    # Chrome ring material instead of black
    mat_anello = bpy.data.materials.new(name=f"Ring_{nome}")
    mat_anello.use_nodes = True
    bsdf_anello = mat_anello.node_tree.nodes["Principled BSDF"]
    bsdf_anello.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1)
    bsdf_anello.inputs['Metallic'].default_value = 0.9
    bsdf_anello.inputs['Roughness'].default_value = 0.1
    anello.data.materials.append(mat_anello)

# CAMERA
bpy.ops.object.camera_add(location=(1.5, -1.8, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(40))
bpy.context.scene.camera = camera

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.5

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
area = bpy.context.active_object
area.data.energy = 200

# Additional rim light for chrome reflections
bpy.ops.object.light_add(type='AREA', location=(2, 1, 4))
rim_light = bpy.context.active_object
rim_light.data.energy = 100
rim_light.data.color = (0.9, 0.95, 1.0)

# WORLD HDRI
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.5

# RENDER SETTINGS
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

print("Modern minimalist stoplight created!")

