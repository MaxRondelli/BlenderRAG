import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the candle body (cylinder) - more realistic size
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.15,
    depth=0.6,
    location=(0, 0, 0.3)
)
candle_body = bpy.context.active_object
candle_body.name = "Candle_Body"

# Create material for candle body
candle_mat = bpy.data.materials.new(name="Candle_Material")
candle_mat.use_nodes = True
candle_body.data.materials.append(candle_mat)

# Set up candle material (deep purple color)
bsdf = candle_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.8, 1.0)  # Deep purple color
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Metallic'].default_value = 0.1

# Create the wick (small cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.01,
    depth=0.1,
    location=(0, 0, 0.65)
)
wick = bpy.context.active_object
wick.name = "Wick"

# Create wick material (dark brown/black)
wick_mat = bpy.data.materials.new(name="Wick_Material")
wick_mat.use_nodes = True
wick.data.materials.append(wick_mat)

wick_bsdf = wick_mat.node_tree.nodes["Principled BSDF"]
wick_bsdf.inputs['Base Color'].default_value = (0.1, 0.10, 0.02, 1.0)
wick_bsdf.inputs['Roughness'].default_value = 0.8

# Create the flame (icosphere for glow effect)
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=3,
    radius=0.05,
    location=(0, 0, 0.69)
)
flame = bpy.context.active_object
flame.name = "Flame"

# Scale flame to be more teardrop shaped
flame.scale[2] = 1.5

# Create flame material with emission
flame_mat = bpy.data.materials.new(name="Flame_Material")
flame_mat.use_nodes = True
flame.data.materials.append(flame_mat)

# Set up emission shader for flame
flame_nodes = flame_mat.node_tree.nodes
flame_links = flame_mat.node_tree.links

# Clear default nodes
for node in flame_nodes:
    flame_nodes.remove(node)

# Add emission and output nodes
emission = flame_nodes.new(type='ShaderNodeEmission')
output = flame_nodes.new(type='ShaderNodeOutputMaterial')

emission.inputs['Color'].default_value = (1.0, 0.2, 0.3, 1.0)  # Red flame
emission.inputs['Strength'].default_value = 25.0

flame_links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Add a point light at the flame for additional lighting
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.75))
flame_light = bpy.context.active_object
flame_light.name = "Flame_Light"
flame_light.data.energy = 35
flame_light.data.color = (1.0, 0.4, 0.5)
flame_light.data.shadow_soft_size = 0.05

# Set up camera
bpy.ops.object.camera_add(location=(0.8, -0.8, 0.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# Add a plane as ground
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Ground"

# Create ground material
ground_mat = bpy.data.materials.new(name="Ground_Material")
ground_mat.use_nodes = True
plane.data.materials.append(ground_mat)

ground_bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
ground_bsdf.inputs['Base Color'].default_value = (0.15, 0.1, 0.25, 1.0)  # Dark purple tint
ground_bsdf.inputs['Roughness'].default_value = 0.7

# Set up world background (dark for nighttime feel)
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
bg_node = world_nodes['Background']
bg_node.inputs['Color'].default_value = (0.08, 0.05, 0.12, 1.0)  # Dark purple background
bg_node.inputs['Strength'].default_value = 0.4

# Add a key light for better overall lighting
bpy.ops.object.light_add(type='AREA', location=(0.6, -0.6, 1.2))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 25
key_light.data.color = (1.0, 0.8, 0.6)  # Warm golden light
key_light.data.size = 0.5
key_light.rotation_euler = (math.radians(45), 0, math.radians(45))

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = '/tmp/candle_render.png'

# Enable denoising for cleaner render
bpy.context.scene.cycles.use_denoising = True