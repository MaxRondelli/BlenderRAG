import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear existing materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Trash can dimensions - slightly larger for premium look
radius = 0.18          # 18cm radius (increased from 15cm)
height = 0.40          # 40cm height (increased from 35cm)
wall_thickness = 0.003 # 3mm wall thickness (increased from 2mm)
lid_height = 0.035     # 3.5cm lid height (slightly increased)

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
    depth=height - 0.01,  # Leave bottom solid
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
    radius=radius + 0.01,
    depth=lid_height,
    location=(0, 0, height + lid_height/2)
)
lid = bpy.context.active_object
lid.name = "Lid"

# Create lid handle/knob
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.015,
    depth=0.04,
    location=(0, radius * 0.7, height + lid_height + 0.02)
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
    location=(0, radius + 0.03, 0.015)
)
pedal_base = bpy.context.active_object
pedal_base.scale = (0.08, 0.04, 0.03)
pedal_base.name = "Pedal_Base"

# Create foot pedal
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(0, radius + 0.05, 0.04)
)
pedal = bpy.context.active_object
pedal.scale = (0.1, 0.08, 0.01)
pedal.rotation_euler = (math.radians(-15), 0, 0)
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

# Create brushed bronze material for body
bronze_mat = bpy.data.materials.new(name="Brushed_Bronze")
bronze_mat.use_nodes = True
nodes = bronze_mat.node_tree.nodes
links = bronze_mat.node_tree.links
nodes.clear()

# Principled BSDF for bronze metal
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.72, 0.45, 0.20, 1.0)  # Bronze color
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.35  # More brushed texture

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (200, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to body and lid
trash_can_body.data.materials.append(bronze_mat)
lid.data.materials.append(bronze_mat)

# Create darker plastic material for pedal
dark_plastic_mat = bpy.data.materials.new(name="Darker_Plastic")
dark_plastic_mat.use_nodes = True
plastic_nodes = dark_plastic_mat.node_tree.nodes
plastic_nodes.clear()

plastic_bsdf = plastic_nodes.new(type='ShaderNodeBsdfPrincipled')
plastic_bsdf.location = (0, 0)
plastic_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Even darker gray
plastic_bsdf.inputs['Roughness'].default_value = 0.6  # More matte finish

plastic_output = plastic_nodes.new(type='ShaderNodeOutputMaterial')
plastic_output.location = (200, 0)
dark_plastic_mat.node_tree.links.new(plastic_bsdf.outputs['BSDF'], plastic_output.inputs['Surface'])

pedal_assembly.data.materials.append(dark_plastic_mat)

# Setup camera
bpy.ops.object.camera_add(location=(0.7, -0.7, 0.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(-3, -3, 4))
area = bpy.context.active_object
area.data.energy = 100
area.data.size = 3

# World lighting
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
bg_node = world_nodes.get('Background')
if bg_node:
    bg_node.inputs['Strength'].default_value = 0.5

print("=" * 60)
print("BRONZE TRASH CAN GENERATED SUCCESSFULLY!")
print("=" * 60)
print(f"\nDimensions:")
print(f"  • Diameter: {radius * 2 * 100:.1f} cm")
print(f"  • Height: {height * 100:.1f} cm")
print(f"  • Wall thickness: {wall_thickness * 1000:.1f} mm")
print(f"\nFeatures:")
print(f"  • Cylindrical body (hollow inside)")
print(f"  • Lid with handle")
print(f"  • Foot pedal mechanism")
print(f"  • Brushed bronze finish")
print("=" * 60)