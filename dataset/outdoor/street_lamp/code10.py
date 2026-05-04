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
    principled.inputs['Metallic'].default_value = 0.85
    principled.inputs['Roughness'].default_value = 0.2
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_amber_glass_material():
    mat = bpy.data.materials.new(name="AmberGlassMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.95, 0.85, 0.65, 1.0)
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.02
    principled.inputs['Alpha'].default_value = 0.15
    principled.inputs['IOR'].default_value = 1.45
    
    mat.blend_method = 'BLEND'
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
bronze_metal = create_bronze_material("BronzeMetal", (0.72, 0.52, 0.35, 1.0))
amber_glass_mat = create_amber_glass_material()

# Base (wider cylindrical with decorative rings)
bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.3, location=(0, 0, 0.15))
base = bpy.context.object
base.name = "Base"
base.data.materials.append(bronze_metal)

# Thicker decorative rings for base
for z in [0.05, 0.25]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.025, location=(0, 0, z))
    ring = bpy.context.object
    ring.data.materials.append(bronze_metal)

# Main pole (slightly conical)
bpy.ops.mesh.primitive_cone_add(radius1=0.065, radius2=0.055, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "MainPole"
pole.data.materials.append(bronze_metal)

# Thicker decorative pole sections
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.1, location=(0, 0, z))
    section = bpy.context.object
    section.data.materials.append(bronze_metal)



# Decorative arm (main curve from pole to globe)
curve = bpy.data.curves.new('ArmCurve', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.03
polyline = curve.splines.new('BEZIER')
polyline.bezier_points.add(4)

# Points forming the characteristic S curve from pole outward
points = [
    (0.06, 0, 2.6),      # Attachment to pole
    (0.12, 0, 2.72),     # First curve upward
    (0.25, 0, 2.78),     # Maximum height
    (0.38, 0, 2.68),     # Curve downward
    (0.5, 0, 2.55)       # Globe attachment point
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

arm_obj = bpy.data.objects.new('DecorativeArm', curve)
bpy.context.collection.objects.link(arm_obj)
arm_obj.data.materials.append(bronze_metal)

# Upper decorative volutes (ornamental spirals)
for angle in [math.pi * 0.3, math.pi * 1.7]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.06, 
        minor_radius=0.018, 
        location=(0.06 + 0.05 * math.cos(angle), 0.05 * math.sin(angle), 2.75)
    )
    volute = bpy.context.object
    volute.rotation_euler = (math.pi/2.5, angle * 0.3, angle)
    volute.data.materials.append(bronze_metal)

# Curve to globe connector
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.12, location=(0.5, 0, 2.5))
connector = bpy.context.object
connector.rotation_euler = (0, 0, 0)
connector.data.materials.append(bronze_metal)

# Globe upper support (decorative cap)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(0.5, 0, 2.58))
support_top = bpy.context.object
support_top.scale = (1, 1, 0.5)
support_top.data.materials.append(bronze_metal)

# Decorative element on support top
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.04, location=(0.5, 0, 2.63))
cap = bpy.context.object
cap.data.materials.append(bronze_metal)

# Amber glass globe
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.5, 0, 2.3))
globe = bpy.context.object
globe.name = "AmberGlassGlobe"
globe.data.materials.append(amber_glass_mat)

# Internal light
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.3))
light = bpy.context.object
light.data.energy = 150
light.data.color = (1.0, 0.9, 0.7)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Bronze street lamp with amber glass generated successfully!")

