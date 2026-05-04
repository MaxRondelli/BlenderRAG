import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear existing materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Trash can dimensions
width = 0.25           # 25cm width
depth = 0.20           # 20cm depth
height = 0.40          # 40cm height
wall_thickness = 0.003 # 3mm wall thickness
lid_height = 0.025     # 2.5cm lid height

# Create outer cube (main body)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, height/2)
)
outer_body = bpy.context.active_object
outer_body.scale = (width, depth, height)
outer_body.name = "Outer_Body"

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add bevel modifier for rounded corners
bevel_mod = outer_body.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 4

# Create inner cube (to hollow it out)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, height/2 + 0.005)
)
inner_body = bpy.context.active_object
inner_body.scale = (width - wall_thickness*2, depth - wall_thickness*2, height - 0.01)
inner_body.name = "Inner_Body"

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Boolean to make it hollow
outer_body.select_set(True)
bpy.context.view_layer.objects.active = outer_body
bool_mod = outer_body.modifiers.new(name="Boolean", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = inner_body
bool_mod.solver = 'FAST'
bpy.ops.object.modifier_apply(modifier="Boolean")
bpy.ops.object.modifier_apply(modifier="Bevel")
bpy.data.objects.remove(inner_body, do_unlink=True)

trash_can_body = outer_body
trash_can_body.name = "Trash_Can_Body"

# Create lid
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, height + lid_height/2)
)
lid = bpy.context.active_object
lid.scale = (width + 0.02, depth + 0.02, lid_height)
lid.name = "Lid"

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add bevel to lid
lid_bevel = lid.modifiers.new(name="Bevel", type='BEVEL')
lid_bevel.width = 0.015
lid_bevel.segments = 3
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create lid handle/knob
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.012,
    depth=0.035,
    location=(0, depth * 0.3, height + lid_height + 0.012)
)
handle = bpy.context.active_object
handle.rotation_euler = (math.radians(90), 0, 0)
handle.name = "Handle"

# Join lid and handle
bpy.ops.object.select_all(action='DESELECT')
lid.select_set(True)
handle.select_set(True)
bpy.context.view_layer.objects.active = lid
bpy.ops.object.join()

# Create foot pedal base
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, depth/2 + 0.035, 0.018)
)
pedal_base = bpy.context.active_object
pedal_base.scale = (0.09, 0.045, 0.035)
pedal_base.name = "Pedal_Base"

# Create foot pedal
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, depth/2 + 0.055, 0.045)
)
pedal = bpy.context.active_object
pedal.scale = (0.11, 0.085, 0.012)
pedal.rotation_euler = (math.radians(-12), 0, 0)
pedal.name = "Pedal"

# Join pedal parts
bpy.ops.object.select_all(action='DESELECT')
pedal_base.select_set(True)
pedal.select_set(True)
bpy.context.view_layer.objects.active = pedal_base
bpy.ops.object.join()
pedal_assembly = bpy.context.active_object
pedal_assembly.name = "Pedal_Assembly"

# Smooth shading
trash_can_body.select_set(True)
bpy.context.view_layer.objects.active = trash_can_body
bpy.ops.object.shade_smooth()

lid.select_set(True)
bpy.context.view_layer.objects.active = lid
bpy.ops.object.shade_smooth()

# Create brushed copper material for body
copper_mat = bpy.data.materials.new(name="Brushed_Copper")
copper_mat.use_nodes = True
nodes = copper_mat.node_tree.nodes
links = copper_mat.node_tree.links
nodes.clear()

# Principled BSDF for copper
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (300, 0)
bsdf.inputs['Base Color'].default_value = (0.95, 0.64, 0.54, 1.0)  # Copper color
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.35  # Brushed finish
bsdf.inputs['IOR'].default_value = 1.5

# Add noise texture for brushed effect
noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.location = (0, 0)
noise_tex.inputs['Scale'].default_value = 15.0
noise_tex.inputs['Detail'].default_value = 2.0
noise_tex.inputs['Roughness'].default_value = 0.5

# ColorRamp for roughness variation
ramp = nodes.new(type='ShaderNodeValToRGB')
ramp.location = (150, 0)
ramp.color_ramp.elements[0].color = (0.3, 0.3, 0.3, 1.0)
ramp.color_ramp.elements[1].color = (0.4, 0.4, 0.4, 1.0)

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (500, 0)

# Connect nodes
links.new(noise_tex.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to body and lid
trash_can_body.data.materials.append(copper_mat)
lid.data.materials.append(copper_mat)

# Create dark plastic material for pedal
plastic_mat = bpy.data.materials.new(name="Dark_Plastic")
plastic_mat.use_nodes = True
plastic_nodes = plastic_mat.node_tree.nodes
plastic_nodes.clear()

plastic_bsdf = plastic_nodes.new(type='ShaderNodeBsdfPrincipled')
plastic_bsdf.location = (0, 0)
plastic_bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)  # Dark gray
plastic_bsdf.inputs['Roughness'].default_value = 0.45

plastic_output = plastic_nodes.new(type='ShaderNodeOutputMaterial')
plastic_output.location = (200, 0)
plastic_mat.node_tree.links.new(plastic_bsdf.outputs['BSDF'], plastic_output.inputs['Surface'])

pedal_assembly.data.materials.append(plastic_mat)

# Setup camera
bpy.ops.object.camera_add(location=(0.7, -0.8, 0.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(40))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 2.5

bpy.ops.object.light_add(type='AREA', location=(-2, -3, 3))
area = bpy.context.active_object
area.data.energy = 80
area.data.size = 2.5

# World lighting
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
bg_node = world_nodes.get('Background')
if bg_node:
    bg_node.inputs['Strength'].default_value = 0.4

print("=" * 60)
print("MODERN RECTANGULAR TRASH CAN GENERATED SUCCESSFULLY!")
print("=" * 60)
print(f"\nDimensions:")
print(f"  • Width: {width * 100:.1f} cm")
print(f"  • Depth: {depth * 100:.1f} cm")
print(f"  • Height: {height * 100:.1f} cm")
print(f"  • Wall thickness: {wall_thickness * 1000:.1f} mm")
print(f"\nFeatures:")
print(f"  • Rectangular body with rounded corners")
print(f"  • Lid with handle")
print(f"  • Foot pedal mechanism")
print(f"  • Brushed copper finish")
print("=" * 60)