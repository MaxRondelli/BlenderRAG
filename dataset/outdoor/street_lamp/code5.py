import bpy
import bmesh
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def create_bronze_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = color
    principled.inputs['Metallic'].default_value = 0.85
    principled.inputs['Roughness'].default_value = 0.6
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_amber_glass_material():
    mat = bpy.data.materials.new(name="AmberGlassMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.95, 0.75, 0.45, 1.0)
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.4
    principled.inputs['Alpha'].default_value = 0.7
    principled.inputs['IOR'].default_value = 1.45
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
bronze_metal = create_bronze_material("BronzeMetal", (0.55, 0.35, 0.2, 1.0))
amber_glass_mat = create_amber_glass_material()

# Base (cilindrica con anelli decorativi)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(0, 0, 0.15))
base = bpy.context.object
base.name = "Base"
base.data.materials.append(bronze_metal)

# Anelli decorativi base
for z in [0.05, 0.25]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.02, location=(0, 0, z))
    ring = bpy.context.object
    ring.data.materials.append(bronze_metal)

# Palo principale (conico leggermente)
bpy.ops.mesh.primitive_cone_add(radius1=0.065, radius2=0.055, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "MainPole"
pole.data.materials.append(bronze_metal)

# Sezioni decorative palo
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.08, location=(0, 0, z))
    section = bpy.context.object
    section.data.materials.append(bronze_metal)



# Angular wrought-iron style bracket
# Main horizontal arm
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(0.25, 0, 2.65))
main_arm = bpy.context.object
main_arm.scale = (10, 1, 1)
main_arm.data.materials.append(bronze_metal)

# Vertical support arm
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(0.35, 0, 2.5))
vertical_arm = bpy.context.object
vertical_arm.scale = (1, 1, 6)
vertical_arm.data.materials.append(bronze_metal)

# Diagonal braces for geometric pattern
diagonal_positions = [
    (0.15, 0, 2.58, (0, 0, math.radians(20))),
    (0.2, 0, 2.62, (0, 0, math.radians(-20))),
    (0.3, 0, 2.58, (0, 0, math.radians(20))),
    (0.4, 0, 2.62, (0, 0, math.radians(-20)))
]

for pos_x, pos_y, pos_z, rot in diagonal_positions:
    bpy.ops.mesh.primitive_cube_add(size=0.03, location=(pos_x, pos_y, pos_z))
    brace = bpy.context.object
    brace.scale = (3, 1, 0.5)
    brace.rotation_euler = rot
    brace.data.materials.append(bronze_metal)

# Geometric decorative elements
for i, x_pos in enumerate([0.12, 0.18, 0.32, 0.38]):
    bpy.ops.mesh.primitive_cube_add(size=0.04, location=(x_pos, 0, 2.65))
    deco = bpy.context.object
    if i % 2 == 0:
        deco.rotation_euler = (0, 0, math.radians(45))
    deco.scale = (1, 1, 0.3)
    deco.data.materials.append(bronze_metal)

# Angular connection joints
joint_positions = [(0.06, 0, 2.65), (0.5, 0, 2.4)]
for pos in joint_positions:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=pos)
    joint = bpy.context.object
    joint.data.materials.append(bronze_metal)

# Decorative corner brackets
corner_positions = [
    (0.06, 0.02, 2.67),
    (0.06, -0.02, 2.67),
    (0.06, 0.02, 2.63),
    (0.06, -0.02, 2.63)
]

for pos in corner_positions:
    bpy.ops.mesh.primitive_cube_add(size=0.02, location=pos)
    corner = bpy.context.object
    corner.scale = (2, 1, 1)
    corner.data.materials.append(bronze_metal)

# Victorian ornamental scrollwork (angular version)
for angle in [0, math.pi]:
    x_offset = 0.08 * math.cos(angle)
    y_offset = 0.08 * math.sin(angle)
    
    bpy.ops.mesh.primitive_cube_add(size=0.025, location=(0.06 + x_offset, y_offset, 2.75))
    scroll_base = bpy.context.object
    scroll_base.rotation_euler = (0, 0, angle)
    scroll_base.scale = (3, 1, 1)
    scroll_base.data.materials.append(bronze_metal)
    
    bpy.ops.mesh.primitive_cube_add(size=0.02, location=(0.12 + x_offset, y_offset, 2.75))
    scroll_end = bpy.context.object
    scroll_end.rotation_euler = (0, 0, angle + math.radians(90))
    scroll_end.scale = (2, 1, 1)
    scroll_end.data.materials.append(bronze_metal)

# Lamp housing connection
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.08, location=(0.5, 0, 2.45))
housing_connect = bpy.context.object
housing_connect.data.materials.append(bronze_metal)

# Victorian lamp housing (angular design)
bpy.ops.mesh.primitive_cube_add(size=0.12, location=(0.5, 0, 2.58))
housing = bpy.context.object
housing.scale = (1, 1, 0.3)
housing.data.materials.append(bronze_metal)

# Housing corner posts
corner_offsets = [0.06, -0.06]
for x_off in corner_offsets:
    for y_off in corner_offsets:
        bpy.ops.mesh.primitive_cube_add(size=0.02, location=(0.5 + x_off, y_off, 2.58))
        post = bpy.context.object
        post.scale = (1, 1, 2)
        post.data.materials.append(bronze_metal)

# Housing top cap
bpy.ops.mesh.primitive_cube_add(size=0.15, location=(0.5, 0, 2.65))
cap = bpy.context.object
cap.scale = (1, 1, 0.2)
cap.data.materials.append(bronze_metal)

# Decorative finial
bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.02, depth=0.08, location=(0.5, 0, 2.72))
finial = bpy.context.object
finial.data.materials.append(bronze_metal)

# Amber frosted glass globe
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.5, 0, 2.3))
globe = bpy.context.object
globe.name = "AmberGlassGlobe"
globe.data.materials.append(amber_glass_mat)

# Luce interna con tonalità più calda
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.3))
light = bpy.context.object
light.data.energy = 120
light.data.color = (1.0, 0.8, 0.6)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Victorian street lamp with bronze finish and angular brackets generated successfully!")


