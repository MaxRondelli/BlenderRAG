import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear existing materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Trash can dimensions - wider base variation
radius_top = 0.15      # 15cm radius at top
radius_bottom = 0.18   # 18cm radius at bottom (wider)
height = 0.35          # 35cm height
wall_thickness = 0.003 # 3mm wall thickness
lid_height = 0.025     # 2.5cm lid height

# Create outer cone (main body) - tapered design
bpy.ops.mesh.primitive_cone_add(
    vertices=64,
    radius1=radius_bottom,  # Bottom radius (wider)
    radius2=radius_top,      # Top radius (narrower)
    depth=height,
    location=(0, 0, height/2)
)
outer_body = bpy.context.active_object
outer_body.name = "Outer_Body"

# Create inner cone (to hollow it out)
bpy.ops.mesh.primitive_cone_add(
    vertices=64,
    radius1=radius_bottom - wall_thickness,
    radius2=radius_top - wall_thickness,
    depth=height - 0.01,
    location=(0, 0, height/2 + 0.005)
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

# Create lid
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=radius_top + 0.01,
    depth=lid_height,
    location=(0, 0, height + lid_height/2)
)
lid = bpy.context.active_object
lid.name = "Lid"

# Create lid handle/knob - copper colored
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.018,
    depth=0.035,
    location=(0, radius_top * 0.6, height + lid_height + 0.018)
)
handle = bpy.context.active_object
handle.rotation_euler = (math.radians(90), 0, 0)
handle.name = "Handle"

# PEDAL ASSEMBLY - ATTACHED TO TRASH CAN BODY
# Position pedal very close to the trash can bottom edge
bracket_x = 0
bracket_y = radius_bottom + 0.003  # Almost touching the trash can body at bottom
bracket_z = 0.04

# Create mounting bracket at base of trash can
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, bracket_y, bracket_z)
)
mounting_bracket = bpy.context.active_object
mounting_bracket.scale = (0.04, 0.012, 0.05)
mounting_bracket.name = "Mounting_Bracket"

# Create hinge/pivot cylinder - very close to body
hinge_y = bracket_y + 0.015
hinge_z = 0.035

bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.007,
    depth=0.045,
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
pedal_base.scale = (0.09, 0.04, 0.028)
pedal_base.name = "Pedal_Base"

# Create pedal pad - positioned right at the trash can base
pedal_y = pedal_base_y + 0.035
pedal_z = 0.03

bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(bracket_x, pedal_y, pedal_z)
)
pedal = bpy.context.active_object
pedal.scale = (0.11, 0.08, 0.012)
pedal.rotation_euler = (math.radians(-22), 0, 0)
pedal.name = "Pedal"

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

# Smooth shading
trash_can_body.select_set(True)
bpy.context.view_layer.objects.active = trash_can_body
bpy.ops.object.shade_smooth()

lid.select_set(True)
bpy.context.view_layer.objects.active = lid
bpy.ops.object.shade_smooth()

pedal_assembly.select_set(True)
bpy.context.view_layer.objects.active = pedal_assembly
bpy.ops.object.shade_smooth()

# Create matte black material for body
black_mat = bpy.data.materials.new(name="Matte_Black")
black_mat.use_nodes = True
nodes = black_mat.node_tree.nodes
links = black_mat.node_tree.links
nodes.clear()

# Principled BSDF for matte black
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Deep matte black
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.8  # Very matte finish

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (200, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign black material to body and lid
trash_can_body.data.materials.append(black_mat)
lid.data.materials.append(black_mat)

# Create copper material for handle
copper_mat = bpy.data.materials.new(name="Copper")
copper_mat.use_nodes = True
copper_nodes = copper_mat.node_tree.nodes
copper_links = copper_mat.node_tree.links
copper_nodes.clear()

copper_bsdf = copper_nodes.new(type='ShaderNodeBsdfPrincipled')
copper_bsdf.location = (0, 0)
copper_bsdf.inputs['Base Color'].default_value = (0.95, 0.64, 0.54, 1.0)  # Copper color
copper_bsdf.inputs['Metallic'].default_value = 1.0
copper_bsdf.inputs['Roughness'].default_value = 0.3

copper_output = copper_nodes.new(type='ShaderNodeOutputMaterial')
copper_output.location = (200, 0)
copper_links.new(copper_bsdf.outputs['BSDF'], copper_output.inputs['Surface'])

handle.data.materials.append(copper_mat)

# Create dark plastic material for pedal
plastic_mat = bpy.data.materials.new(name="Dark_Plastic")
plastic_mat.use_nodes = True
plastic_nodes = plastic_mat.node_tree.nodes
plastic_nodes.clear()

plastic_bsdf = plastic_nodes.new(type='ShaderNodeBsdfPrincipled')
plastic_bsdf.location = (0, 0)
plastic_bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1.0)  # Dark gray
plastic_bsdf.inputs['Roughness'].default_value = 0.5

plastic_output = plastic_nodes.new(type='ShaderNodeOutputMaterial')
plastic_output.location = (200, 0)
plastic_mat.node_tree.links.new(plastic_bsdf.outputs['BSDF'], plastic_output.inputs['Surface'])

pedal_assembly.data.materials.append(plastic_mat)

# Setup camera
bpy.ops.object.camera_add(location=(0.7, -0.7, 0.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting setup
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.light_add(type='AREA', location=(-3, -3, 4))
area = bpy.context.active_object
area.data.energy = 120
area.data.size = 3

# World lighting
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
bg_node = world_nodes.get('Background')
if bg_node:
    bg_node.inputs['Strength'].default_value = 0.6

print("=" * 60)
print("MATTE BLACK TRASH CAN WITH COPPER ACCENTS GENERATED!")
print("=" * 60)
print(f"\nDimensions:")
print(f"  • Top diameter: {radius_top * 2 * 100:.1f} cm")
print(f"  • Bottom diameter: {radius_bottom * 2 * 100:.1f} cm (wider base)")
print(f"  • Height: {height * 100:.1f} cm")
print(f"  • Wall thickness: {wall_thickness * 1000:.1f} mm")
print(f"\nFeatures:")
print(f"  • Tapered cylindrical body (wider at base)")
print(f"  • Matte black finish")
print(f"  • Copper handle accent")
print(f"  • Foot pedal mechanism attached to body")
print(f"  • Mounting bracket and hinge system")
print("=" * 60)