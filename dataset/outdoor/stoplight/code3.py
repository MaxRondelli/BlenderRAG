import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BASE
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.1))
base = bpy.context.active_object
base.scale = (0.5, 0.3, 0.05)

mat_base = bpy.data.materials.new(name="BaseGunmetal")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.17, 1)
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.2
base.data.materials.append(mat_base)

# POLE
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
pole = bpy.context.active_object

mat_pole = bpy.data.materials.new(name="PoleGunmetal")
mat_pole.use_nodes = True
bsdf_pole = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf_pole.inputs['Base Color'].default_value = (0.2, 0.2, 0.22, 1)
bsdf_pole.inputs['Metallic'].default_value = 0.9
bsdf_pole.inputs['Roughness'].default_value = 0.15
pole.data.materials.append(mat_pole)

# MAIN BODY - Modern rectangular shape
bpy.ops.mesh.primitive_cube_add(size=1., location=(0, 0, 2.9))
body = bpy.context.active_object
body.scale = (0.2, 0.12, 0.75)

# Add subdivision for smoother look
subsurf_modifier = body.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf_modifier.levels = 2

mat_body = bpy.data.materials.new(name="BodyGunmetal")
mat_body.use_nodes = True
bsdf_body = mat_body.node_tree.nodes["Principled BSDF"]
bsdf_body.inputs['Base Color'].default_value = (0.1, 0.1, 0.12, 1)
bsdf_body.inputs['Metallic'].default_value = 0.85
bsdf_body.inputs['Roughness'].default_value = 0.1
body.data.materials.append(mat_body)

# LED LIGHTS
light_data = [
    ("Red", (0.9, 0.05, 0.05), 3.2),
    ("Amber", (1.0, 0.5, 0.0), 2.9),
    ("Green", (0.05, 0.8, 0.1), 2.6)
]

for name, color, z_pos in light_data:
    # LED Light (sphere) - embedded in the body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0, 0.05, z_pos))
    light = bpy.context.active_object
    
    # LED emissive material
    mat_light = bpy.data.materials.new(name=f"LED_{name}")
    mat_light.use_nodes = True
    nodes = mat_light.node_tree.nodes
    links = mat_light.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mix = nodes.new('ShaderNodeMixShader')
    emission = nodes.new('ShaderNodeEmission')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Bright LED emission
    emission.inputs['Color'].default_value = (*color, 1)
    emission.inputs['Strength'].default_value = 15.0
    
    # Glass-like properties
    principled.inputs['Base Color'].default_value = (*color, 1)
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.05
    principled.inputs['IOR'].default_value = 1.45
    principled.inputs['Alpha'].default_value = 0.8
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(principled.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs["Fac"].default_value = 0.85
    
    # Enable transparency
    mat_light.blend_method = 'BLEND'
    
    light.data.materials.append(mat_light)
    
    # Black ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.012, location=(0, 0.05, z_pos))
    ring = bpy.context.active_object
    ring.rotation_euler = (math.radians(90), 0, 0)
    ring.data.materials.append(mat_body)

# CAMERA
bpy.ops.object.camera_add(location=(1.5, -1.8, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(40))
bpy.context.scene.camera = camera

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 4.0

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 2.0

# WORLD HDRI
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.2

# RENDER SETTINGS
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'

print("Modern traffic light created!")
