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
    principled.inputs['Roughness'].default_value = 0.6
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_amber_glass_material():
    mat = bpy.data.materials.new(name="AmberGlassMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.inputs['Color'].default_value = (1.0, 0.85, 0.6, 1.0)
    glass.inputs['Roughness'].default_value = 0.05
    glass.inputs['IOR'].default_value = 1.45
    
    mat.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
bronze_metal = create_bronze_material("BronzeMetal", (0.7, 0.5, 0.3, 1.0))
amber_glass = create_amber_glass_material()

# Base (cilindrica con anelli decorativi)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(0, 0, 0.15))
base = bpy.context.object
base.name = "Base"
base.data.materials.append(bronze_metal)

# Elaborate scrollwork elements instead of simple rings
for z in [0.05, 0.25]:
    # Main decorative torus
    bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.025, location=(0, 0, z))
    main_ring = bpy.context.object
    main_ring.data.materials.append(bronze_metal)
    
    # Ornate scrollwork around the main ring
    for angle in range(0, 360, 45):
        rad_angle = math.radians(angle)
        x = 0.13 * math.cos(rad_angle)
        y = 0.13 * math.sin(rad_angle)
        
        # Small decorative scroll
        bpy.ops.mesh.primitive_torus_add(major_radius=0.03, minor_radius=0.008, location=(x, y, z))
        scroll = bpy.context.object
        scroll.rotation_euler = (math.pi/2, 0, rad_angle)
        scroll.scale = (1.2, 0.8, 1.5)
        scroll.data.materials.append(bronze_metal)
        
        # Tiny ornamental detail
        bpy.ops.mesh.primitive_torus_add(major_radius=0.015, minor_radius=0.004, location=(x * 1.1, y * 1.1, z + 0.01))
        detail = bpy.context.object
        detail.rotation_euler = (0, math.pi/3, rad_angle + math.pi/4)
        detail.data.materials.append(bronze_metal)

# Palo principale (conico leggermente)
bpy.ops.mesh.primitive_cone_add(radius1=0.065, radius2=0.055, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "MainPole"
pole.data.materials.append(bronze_metal)

# Sezioni decorative palo con scrollwork
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.08, location=(0, 0, z))
    section = bpy.context.object
    section.data.materials.append(bronze_metal)
    
    # Ornate details on each section
    for angle in range(0, 360, 90):
        rad_angle = math.radians(angle)
        x = 0.08 * math.cos(rad_angle)
        y = 0.08 * math.sin(rad_angle)
        
        bpy.ops.mesh.primitive_torus_add(major_radius=0.02, minor_radius=0.005, location=(x, y, z))
        ornament = bpy.context.object
        ornament.rotation_euler = (math.pi/2, 0, rad_angle)
        ornament.scale = (1.5, 1.0, 0.8)
        ornament.data.materials.append(bronze_metal)



# Braccio decorativo (curva principale dal palo al globo)
curve = bpy.data.curves.new('ArmCurve', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.025
polyline = curve.splines.new('BEZIER')
polyline.bezier_points.add(4)

# Punti che formano la curva caratteristica a S dal palo verso l'esterno
points = [
    (0.06, 0, 2.6),
    (0.12, 0, 2.72),
    (0.25, 0, 2.78),
    (0.38, 0, 2.68),
    (0.5, 0, 2.55)
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

arm_obj = bpy.data.objects.new('DecorativeArm', curve)
bpy.context.collection.objects.link(arm_obj)
arm_obj.data.materials.append(bronze_metal)

# Enhanced Victorian scrollwork (more elaborate spiral ornaments)
for angle in [math.pi * 0.3, math.pi * 1.7]:
    base_x = 0.06 + 0.05 * math.cos(angle)
    base_y = 0.05 * math.sin(angle)
    
    # Main volute
    bpy.ops.mesh.primitive_torus_add(major_radius=0.06, minor_radius=0.015, location=(base_x, base_y, 2.75))
    volute = bpy.context.object
    volute.rotation_euler = (math.pi/2.5, angle * 0.3, angle)
    volute.data.materials.append(bronze_metal)
    
    # Secondary scrolls
    for sub_angle in [angle + math.pi/3, angle - math.pi/3]:
        x = base_x + 0.03 * math.cos(sub_angle)
        y = base_y + 0.03 * math.sin(sub_angle)
        
        bpy.ops.mesh.primitive_torus_add(major_radius=0.025, minor_radius=0.008, location=(x, y, 2.77))
        sub_scroll = bpy.context.object
        sub_scroll.rotation_euler = (math.pi/3, sub_angle * 0.5, sub_angle)
        sub_scroll.scale = (1.3, 0.7, 1.2)
        sub_scroll.data.materials.append(bronze_metal)

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

# Victorian crown details on support
for angle in range(0, 360, 60):
    rad_angle = math.radians(angle)
    x = 0.5 + 0.05 * math.cos(rad_angle)
    y = 0.05 * math.sin(rad_angle)
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.008, radius2=0.003, depth=0.02, location=(x, y, 2.61))
    crown_detail = bpy.context.object
    crown_detail.data.materials.append(bronze_metal)

# Elemento decorativo sulla cima del supporto
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.04, location=(0.5, 0, 2.63))
cap = bpy.context.object
cap.data.materials.append(bronze_metal)

# Globo in vetro ambrato
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.5, 0, 2.3))
globe = bpy.context.object
globe.name = "AmberGlassGlobe"
globe.data.materials.append(amber_glass)

# Luce interna più calda per l'ambra
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.3))
light = bpy.context.object
light.data.energy = 150
light.data.color = (1.0, 0.8, 0.6)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Victorian bronze street lamp with ornate scrollwork generated successfully!")
