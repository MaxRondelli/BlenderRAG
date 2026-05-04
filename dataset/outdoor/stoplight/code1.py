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

mat_base = bpy.data.materials.new(name="BaseCharcoal")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.17, 1)
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['Metallic'].default_value = 0.1
base.data.materials.append(mat_base)

# CHROME POLE
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
palo = bpy.context.active_object

mat_chrome = bpy.data.materials.new(name="Chrome")
mat_chrome.use_nodes = True
bsdf_chrome = mat_chrome.node_tree.nodes["Principled BSDF"]
bsdf_chrome.inputs['Base Color'].default_value = (0.9, 0.9, 0.95, 1)
bsdf_chrome.inputs['Metallic'].default_value = 1.0
bsdf_chrome.inputs['Roughness'].default_value = 0.05
palo.data.materials.append(mat_chrome)

# HEXAGONAL MAIN BODY
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.2, depth=1.4, location=(0, 0, 2.9))
corpo = bpy.context.active_object

mat_corpo = bpy.data.materials.new(name="CharcoalBody")
mat_corpo.use_nodes = True
bsdf_corpo = mat_corpo.node_tree.nodes["Principled BSDF"]
bsdf_corpo.inputs['Base Color'].default_value = (0.1, 0.1, 0.12, 1)
bsdf_corpo.inputs['Roughness'].default_value = 0.15
bsdf_corpo.inputs['Metallic'].default_value = 0.2
corpo.data.materials.append(mat_corpo)

# LIGHTS WITH THIN METALLIC RINGS
luci_data = [
    ("Red", (1, 0.1, 0.05), 3.25),
    ("Yellow", (1, 0.8, 0.05), 2.9),
    ("Green", (0.05, 1, 0.1), 2.55)
]

for nome, colore, z_pos in luci_data:
    # Thin metallic ring around light
    bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.008, location=(0, 0.12, z_pos))
    ring = bpy.context.active_object
    ring.data.materials.append(mat_chrome)
    
    # Light sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, 0.1, z_pos))
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
    emission.inputs['Strength'].default_value = 12.0
    glass.inputs['Color'].default_value = (*colore, 1)
    glass.inputs['IOR'].default_value = 1.5
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs[0].default_value = 0.75
    
    luce.data.materials.append(mat_luce)

# CHROME TOP CAP
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.15, depth=0.1, location=(0, 0, 3.65))
top_cap = bpy.context.active_object
top_cap.data.materials.append(mat_chrome)

# CHROME BASE RING
bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.015, location=(0, 0, 2.2))
base_ring = bpy.context.active_object
base_ring.data.materials.append(mat_chrome)

# CAMERA
bpy.ops.object.camera_add(location=(1.8, -2.2, 2.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(35))
bpy.context.scene.camera = camera

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 2.5

bpy.ops.object.light_add(type='AREA', location=(-3, -2, 4))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 2

bpy.ops.object.light_add(type='SPOT', location=(2, 1, 3))
spot = bpy.context.active_object
spot.data.energy = 100
spot.rotation_euler = (math.radians(45), 0, math.radians(-30))

# WORLD SETUP
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.4

# RENDER SETTINGS
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

print("Modern hexagonal stoplight created!")


