import bpy
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
    principled.inputs['Metallic'].default_value = 0.8
    principled.inputs['Roughness'].default_value = 0.7
    
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
    principled.inputs['Roughness'].default_value = 0.1
    principled.inputs['Alpha'].default_value = 0.7
    principled.inputs['IOR'].default_value = 1.45
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    mat.blend_method = 'BLEND'
    return mat

# Create materials
aged_bronze = create_bronze_material("AgedBronze", (0.55, 0.42, 0.25, 1.0))
amber_glass_mat = create_amber_glass_material()

# Base (cilindrica con anelli decorativi)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(0, 0, 0.15))
base = bpy.context.object
base.name = "Base"
base.data.materials.append(aged_bronze)

# Anelli decorativi base
for z in [0.05, 0.25]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.02, location=(0, 0, z))
    ring = bpy.context.object
    ring.data.materials.append(aged_bronze)

# Palo principale (conico leggermente)
bpy.ops.mesh.primitive_cone_add(radius1=0.065, radius2=0.055, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "MainPole"
pole.data.materials.append(aged_bronze)

# Sezioni decorative palo
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.08, location=(0, 0, z))
    section = bpy.context.object
    section.data.materials.append(aged_bronze)

# Punta superiore


# Angular geometric bracket arm - replacing the curved arm with straight segments
# Horizontal segment from pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.25, location=(0.125, 0, 2.6))
arm_horizontal = bpy.context.object
arm_horizontal.rotation_euler = (0, math.pi/2, 0)
arm_horizontal.data.materials.append(aged_bronze)

# Vertical down segment
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.15, location=(0.25, 0, 2.525))
arm_vertical_down = bpy.context.object
arm_vertical_down.data.materials.append(aged_bronze)

# Second horizontal segment
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.2, location=(0.35, 0, 2.45))
arm_horizontal2 = bpy.context.object
arm_horizontal2.rotation_euler = (0, math.pi/2, 0)
arm_horizontal2.data.materials.append(aged_bronze)

# Final upward segment to globe
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.1, location=(0.45, 0, 2.5))
arm_vertical_up = bpy.context.object
arm_vertical_up.data.materials.append(aged_bronze)

# Joint connectors at the angles
joint_positions = [(0.25, 0, 2.6), (0.25, 0, 2.45), (0.45, 0, 2.45)]
for pos in joint_positions:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=pos)
    joint = bpy.context.object
    joint.data.materials.append(aged_bronze)

# Decorative brackets at joints
for i, pos in enumerate(joint_positions):
    bpy.ops.mesh.primitive_cube_add(size=0.04, location=(pos[0], pos[1], pos[2] + 0.02))
    bracket = bpy.context.object
    bracket.scale = (1.2, 0.8, 0.6)
    bracket.data.materials.append(aged_bronze)

# Volute decorative superiori (spirali ornamentali) - made more angular
for angle in [math.pi * 0.3, math.pi * 1.7]:
    # Replace torus with angular decorative elements
    bpy.ops.mesh.primitive_cube_add(
        size=0.08,
        location=(0.06 + 0.05 * math.cos(angle), 0.05 * math.sin(angle), 2.75)
    )
    volute = bpy.context.object
    volute.rotation_euler = (math.pi/6, angle * 0.3, angle)
    volute.scale = (1.5, 0.3, 0.3)
    volute.data.materials.append(aged_bronze)

# Connettore bracket al globo
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.08, location=(0.5, 0, 2.48))
connector = bpy.context.object
connector.data.materials.append(aged_bronze)

# Supporto superiore globo (cappello decorativo)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0.5, 0, 2.56))
support_top = bpy.context.object
support_top.scale = (1, 1, 0.5)
support_top.data.materials.append(aged_bronze)

# Elemento decorativo sulla cima del supporto
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04, location=(0.5, 0, 2.61))
cap = bpy.context.object
cap.data.materials.append(aged_bronze)

# Globo in vetro ambrato
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.5, 0, 2.3))
globe = bpy.context.object
globe.name = "AmberGlassGlobe"
globe.data.materials.append(amber_glass_mat)

# Luce interna con tonalità più calda
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.3))
light = bpy.context.object
light.data.energy = 120
light.data.color = (1.0, 0.8, 0.5)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Victorian-era street lamp with bronze finish and angular bracket generated successfully!")


