import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear existing materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Trash can dimensions
radius = 0.15          # 15cm radius (30cm diameter)
height = 0.40          # 40cm height
wall_thickness = 0.003 # 3mm wall thickness
lid_height = 0.04      # 4cm lid height

# Create outer cylinder (main body)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=radius,
    depth=height,
    location=(0, 0, height/2)
)
outer_body = bpy.context.active_object
outer_body.name = "Outer_Body"

# Create inner cylinder (to hollow it out)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=radius - wall_thickness,
    depth=height - 0.02,
    location=(0, 0, height/2 + 0.01)
)
inner_body = bpy.context.active_object
inner_body.name = "Inner_Body"

# Boolean to make it hollow
outer_body.select_set(True)
bpy.context.view_layer.objects.active = outer_body
bool_mod = outer_body.modifiers.new(name="Boolean", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = inner_body
bool_mod.solver = 'FAST'
bpy.ops.object.modifier_apply(modifier="Boolean")
bpy.data.objects.remove(inner_body, do_unlink=True)

trash_can_body = outer_body
trash_can_body.name = "Trash_Can_Body"

# Create circular lid
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=radius + 0.015,
    depth=lid_height,
    location=(0, 0, height + lid_height/2)
)
lid = bpy.context.active_object
lid.name = "Lid"

# Add subtle bevel to lid edge
lid_bevel = lid.modifiers.new(name="Bevel", type='BEVEL')
lid_bevel.width = 0.005
lid_bevel.segments = 3
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create lid handle/slot (rectangular opening on lid)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, 0, height + lid_height/2)
)
handle_slot = bpy.context.active_object
handle_slot.scale = (0.05, 0.025, 0.05)
handle_slot.name = "Handle_Slot"

# Boolean to create slot in lid
lid.select_set(True)
bpy.context.view_layer.objects.active = lid
bool_mod_lid = lid.modifiers.new(name="Boolean", type='BOOLEAN')
bool_mod_lid.operation = 'DIFFERENCE'
bool_mod_lid.object = handle_slot
bool_mod_lid.solver = 'FAST'
bpy.ops.object.modifier_apply(modifier="Boolean")
bpy.data.objects.remove(handle_slot, do_unlink=True)

# PEDAL ASSEMBLY - ATTACHED TO TRASH CAN BODY
# Position pedal very close to the trash can
bracket_x = 0
bracket_y = radius + 0.002  # Almost touching the trash can body
bracket_z = 0.04

# Create mounting bracket at base of trash can
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, bracket_y, bracket_z)
)
mounting_bracket = bpy.context.active_object
mounting_bracket.scale = (0.035, 0.012, 0.05)
mounting_bracket.name = "Mounting_Bracket"

# Create hinge/pivot cylinder - very close to body
hinge_y = bracket_y + 0.015
hinge_z = 0.035

bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.007,
    depth=0.04,
    location=(bracket_x, hinge_y, hinge_z)
)
hinge = bpy.context.active_object
hinge.rotation_euler = (0, math.radians(90), 0)
hinge.name = "Hinge"

# Create connecting arm - short and close to can
arm_length = 0.055
arm_y = hinge_y + 0.032
arm_z = hinge_z - 0.015

bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, arm_y, arm_z)
)
arm = bpy.context.active_object
arm.scale = (0.018, arm_length, 0.009)
arm.rotation_euler = (math.radians(-20), 0, 0)
arm.name = "Connecting_Arm"

# Create pedal base - very close to trash can
pedal_base_y = hinge_y + 0.06
pedal_base_z = 0.015

bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, pedal_base_y, pedal_base_z)
)
pedal_base = bpy.context.active_object
pedal_base.scale = (0.08, 0.035, 0.025)
pedal_base.name = "Pedal_Base"

# Create pedal pad - positioned right at the trash can base
pedal_y = pedal_base_y + 0.032
pedal_z = 0.028

bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, pedal_y, pedal_z)
)
pedal = bpy.context.active_object
pedal.scale = (0.10, 0.07, 0.012)
pedal.rotation_euler = (math.radians(-22), 0, 0)
pedal.name = "Pedal_Pad"

# Add bevel to pedal for rounded edges
pedal_bevel = pedal.modifiers.new(name="Bevel", type='BEVEL')
pedal_bevel.width = 0.004
pedal_bevel.segments = 2
bpy.ops.object.modifier_apply(modifier="Bevel")

# Join all pedal parts
bpy.ops.object.select_all(action='DESELECT')
mounting_bracket.select_set(True)
hinge.select_set(True)
arm.select_set(True)
pedal_base.select_set(True)
pedal.select_set(True)
bpy.context.view_layer.objects.active = mounting_bracket
bpy.ops.object.join()
pedal_assembly = bpy.context.active_object
pedal_assembly.name = "Pedal_Assembly"

# Apply smooth shading
for obj in [trash_can_body, lid, pedal_assembly]:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    obj.select_set(False)

# Create dark metal material for body and lid
metal_mat = bpy.data.materials.new(name="Dark_Metal")
metal_mat.use_nodes = True
nodes = metal_mat.node_tree.nodes
links = metal_mat.node_tree.links
nodes.clear()

# Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.25, 0.25, 0.28, 1.0)  # Dark gray
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.2

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (200, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign to body and lid
trash_can_body.data.materials.append(metal_mat)
lid.data.materials.append(metal_mat)

# Create darker material for pedal mechanism
pedal_mat = bpy.data.materials.new(name="Pedal_Material")
pedal_mat.use_nodes = True
pedal_nodes = pedal_mat.node_tree.nodes
pedal_nodes.clear()

pedal_bsdf = pedal_nodes.new(type='ShaderNodeBsdfPrincipled')
pedal_bsdf.location = (0, 0)
pedal_bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)  # Darker gray
pedal_bsdf.inputs['Metallic'].default_value = 0.8
pedal_bsdf.inputs['Roughness'].default_value = 0.3

pedal_output = pedal_nodes.new(type='ShaderNodeOutputMaterial')
pedal_output.location = (200, 0)
pedal_mat.node_tree.links.new(pedal_bsdf.outputs['BSDF'], pedal_output.inputs['Surface'])

pedal_assembly.data.materials.append(pedal_mat)

# Setup camera
bpy.ops.object.camera_add(location=(0.7, -0.7, 0.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting setup
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.light_add(type='AREA', location=(-3, -3, 4))
area = bpy.context.active_object
area.data.energy = 100
area.data.size = 3.0

# World lighting
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
bg_node = world_nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
    bg_node.inputs['Strength'].default_value = 0.3

# Set render settings for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 60)
print("CYLINDRICAL TRASH CAN WITH PEDAL - GENERATED!")
print("=" * 60)
print(f"\nDimensions:")
print(f"  • Diameter: {radius * 2 * 100:.1f} cm")
print(f"  • Height: {height * 100:.1f} cm")
print(f"  • Wall thickness: {wall_thickness * 1000:.1f} mm")
print(f"\nFeatures:")
print(f"  • Cylindrical body with smooth finish")
print(f"  • Hollow interior")
print(f"  • Circular lid with handle slot")
print(f"  • Foot pedal mechanism attached to body")
print(f"  • Mounting bracket and hinge")
print(f"  • Connecting arm and pedal pad")
print(f"  • Dark metallic finish")
print("=" * 60)