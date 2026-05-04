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

mat_base = bpy.data.materials.new(name="BaseBlack")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.4
base.data.materials.append(mat_base)

# POLE - darker charcoal gray with increased metallic properties
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
pole = bpy.context.active_object

mat_pole = bpy.data.materials.new(name="PoleCharcoal")
mat_pole.use_nodes = True
bsdf_pole = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf_pole.inputs['Base Color'].default_value = (0.25, 0.25, 0.28, 1)
bsdf_pole.inputs['Metallic'].default_value = 0.9
bsdf_pole.inputs['Roughness'].default_value = 0.15
pole.data.materials.append(mat_pole)

# MAIN HOUSING - more robust rectangular with thicker dimensions
bpy.ops.mesh.primitive_cube_add(size=1., location=(0, 0, 2.9))
housing = bpy.context.active_object
housing.scale = (0.22, 0.18, 0.75)

# Add rounded corner edges using subdivision and bevel
bpy.context.view_layer.objects.active = housing
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bevel(offset=0.01, segments=3)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subdivision for smoother rounded edges
subsurf_mod = housing.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf_mod.levels = 1

mat_housing = bpy.data.materials.new(name="HousingBlack")
mat_housing.use_nodes = True
bsdf_housing = mat_housing.node_tree.nodes["Principled BSDF"]
bsdf_housing.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1)
bsdf_housing.inputs['Roughness'].default_value = 0.2
bsdf_housing.inputs['Metallic'].default_value = 0.1
housing.data.materials.append(mat_housing)

# LIGHTS WITH HOODS
lights_data = [
    ("Red", (1, 0, 0), 3.15),
    ("Yellow", (1, 0.6, 0), 2.9),
    ("Green", (0, 1, 0), 2.65)
]

for name, color, z_pos in lights_data:
    # HOOD above the light
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.08, location=(0, 0.09, z_pos + 0.08))
    hood = bpy.context.active_object
    hood.rotation_euler = (math.radians(90), 0, 0)
    hood.scale = (1, 0.6, 1)
    hood.data.materials.append(mat_housing)
    
    # Light (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0.02, z_pos))
    light = bpy.context.active_object
    
    # Warmer amber-tinted glass material
    mat_light = bpy.data.materials.new(name=f"Mat_{name}")
    mat_light.use_nodes = True
    nodes = mat_light.node_tree.nodes
    links = mat_light.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mix = nodes.new('ShaderNodeMixShader')
    emission = nodes.new('ShaderNodeEmission')
    glass = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Create amber-tinted version of each color
    amber_tint = (0.9, 0.7, 0.3)
    tinted_color = (
        color[0] * 0.7 + amber_tint[0] * 0.3,
        color[1] * 0.7 + amber_tint[1] * 0.3,
        color[2] * 0.7 + amber_tint[2] * 0.3
    )
    
    emission.inputs['Color'].default_value = (*tinted_color, 1)
    emission.inputs['Strength'].default_value = 8.0
    glass.inputs['Base Color'].default_value = (*tinted_color, 1)
    glass.inputs['Alpha'].default_value = 0.3
    glass.inputs['IOR'].default_value = 1.45
    glass.inputs['Roughness'].default_value = 0.0
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs[0].default_value = 0.8
    
    light.data.materials.append(mat_light)
    
    # Black ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.012, location=(0, 0.02, z_pos))
    ring = bpy.context.active_object
    ring.rotation_euler = (math.radians(90), 0, 0)
    ring.data.materials.append(mat_housing)

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

print("Enhanced stoplight with robust housing and amber-tinted lights created!")


