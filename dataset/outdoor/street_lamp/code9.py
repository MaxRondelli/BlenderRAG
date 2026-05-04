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
    principled.inputs['Metallic'].default_value = 0.9
    principled.inputs['Roughness'].default_value = 0.4
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_amber_glass_material():
    mat = bpy.data.materials.new(name="AmberGlassMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.inputs['Color'].default_value = (1.0, 0.8, 0.6, 1.0)
    glass.inputs['Roughness'].default_value = 0.05
    glass.inputs['IOR'].default_value = 1.45
    
    mat.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
bronze_metal = create_bronze_material("BronzeMetal", (0.6, 0.4, 0.2, 1.0))
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



# Braccio decorativo (curva semplice e gentile)
curve = bpy.data.curves.new('ArmCurve', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.025
polyline = curve.splines.new('BEZIER')
polyline.bezier_points.add(2)

# Punti che formano una curva semplice e gentile dal palo verso l'esterno
points = [
    (0.06, 0, 2.6),      # Attacco al palo
    (0.3, 0, 2.65),      # Punto intermedio con leggera salita
    (0.5, 0, 2.55)       # Punto di attacco al globo
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

arm_obj = bpy.data.objects.new('DecorativeArm', curve)
bpy.context.collection.objects.link(arm_obj)
arm_obj.data.materials.append(bronze_metal)

# Connettore curva al globo
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.12, location=(0.5, 0, 2.5))
connector = bpy.context.object
connector.rotation_euler = (0, 0, 0)
connector.data.materials.append(bronze_metal)

# Supporto superiore globo (cappello decorativo)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0.5, 0, 2.58))
support_top = bpy.context.object
support_top.scale = (1, 1, 0.5)
support_top.data.materials.append(bronze_metal)

# Elemento decorativo sulla cima del supporto
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04, location=(0.5, 0, 2.63))
cap = bpy.context.object
cap.data.materials.append(bronze_metal)

# Globo in vetro ambrato
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.5, 0, 2.3))
globe = bpy.context.object
globe.name = "AmberGlassGlobe"
globe.data.materials.append(amber_glass_mat)

# Luce interna
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.3))
light = bpy.context.object
light.data.energy = 150
light.data.color = (1.0, 0.85, 0.6)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Bronze street lamp with amber glass generated successfully!")

