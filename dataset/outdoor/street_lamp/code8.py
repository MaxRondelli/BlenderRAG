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
    principled.inputs['Metallic'].default_value = 0.8
    principled.inputs['Roughness'].default_value = 0.6
    
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_glass_material():
    mat = bpy.data.materials.new(name="GlassMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    glass = nodes.new('ShaderNodeBsdfGlass')
    glass.inputs['Color'].default_value = (0.95, 0.92, 0.88, 1.0)
    glass.inputs['Roughness'].default_value = 0.05
    glass.inputs['IOR'].default_value = 1.45
    
    mat.node_tree.links.new(glass.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
aged_bronze = create_bronze_material("AgedBronze", (0.52, 0.35, 0.25, 1.0))
glass_mat = create_glass_material()

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

# Palo principale fluted (conico con scanalature verticali)
bpy.ops.mesh.primitive_cone_add(radius1=0.065, radius2=0.055, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "MainPole"

# Convert to edit mode to add fluting
bpy.context.view_layer.objects.active = pole
bpy.ops.object.mode_set(mode='EDIT')

# Get bmesh representation
bm = bmesh.from_edit_mesh(pole.data)

# Add loop cuts for fluting detail
bmesh.ops.subdivide_edges(
    bm,
    edges=[e for e in bm.edges if e.is_boundary or any(abs(f.normal.z) < 0.1 for f in e.link_faces)],
    cuts=16,
    use_grid_fill=True
)

# Create vertical ridges by moving vertices
for vert in bm.verts:
    if vert.co.z > 0.2 and vert.co.z < 2.6:
        angle = math.atan2(vert.co.y, vert.co.x)
        ridge_factor = math.cos(angle * 8) * 0.008
        direction = vert.co.xy.normalized()
        vert.co.xy += direction * ridge_factor

bmesh.update_edit_mesh(pole.data)
bpy.ops.object.mode_set(mode='OBJECT')
pole.data.materials.append(aged_bronze)

# Sezioni decorative palo con dettagli ornamentali
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.08, location=(0, 0, z))
    section = bpy.context.object
    
    # Add ornate details with torus elements
    for i in range(3):
        offset = (i - 1) * 0.02
        bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.008, location=(0, 0, z + offset))
        detail = bpy.context.object
        detail.data.materials.append(aged_bronze)
    
    section.data.materials.append(aged_bronze)



# Braccio decorativo ornato con elementi vittoriani
curve = bpy.data.curves.new('ArmCurve', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.03
polyline = curve.splines.new('BEZIER')
polyline.bezier_points.add(4)

# Punti che formano la curva più elaborata
points = [
    (0.06, 0, 2.6),
    (0.15, 0, 2.75),
    (0.3, 0, 2.82),
    (0.42, 0, 2.72),
    (0.5, 0, 2.6)
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

arm_obj = bpy.data.objects.new('DecorativeArm', curve)
bpy.context.collection.objects.link(arm_obj)
arm_obj.data.materials.append(aged_bronze)

# Volute decorative elaborate in stile vittoriano
for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
    x_pos = 0.08 * math.cos(angle)
    y_pos = 0.08 * math.sin(angle)
    
    # Spirale principale
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.05,
        minor_radius=0.012,
        location=(x_pos, y_pos, 2.78)
    )
    volute = bpy.context.object
    volute.rotation_euler = (math.pi/3, angle * 0.5, angle)
    volute.data.materials.append(aged_bronze)
    
    # Spirale secondaria
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.03,
        minor_radius=0.008,
        location=(x_pos * 1.2, y_pos * 1.2, 2.8)
    )
    small_volute = bpy.context.object
    small_volute.rotation_euler = (math.pi/4, angle * -0.3, angle + math.pi/4)
    small_volute.data.materials.append(aged_bronze)

# Connettore ornato al globo
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.15, location=(0.5, 0, 2.52))
connector = bpy.context.object
connector.data.materials.append(aged_bronze)

# Supporto superiore elaborato
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.5, 0, 2.65))
support_top = bpy.context.object
support_top.scale = (1, 1, 0.4)
support_top.data.materials.append(aged_bronze)

# Cappello decorativo vittoriano
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.05, location=(0.5, 0, 2.7))
cap = bpy.context.object
cap.data.materials.append(aged_bronze)

# Corona decorativa
for i in range(6):
    angle = i * math.pi / 3
    x_offset = 0.035 * math.cos(angle)
    y_offset = 0.035 * math.sin(angle)
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.008,
        radius2=0.002,
        depth=0.03,
        location=(0.5 + x_offset, y_offset, 2.72)
    )
    crown_spike = bpy.context.object
    crown_spike.data.materials.append(aged_bronze)

# Globo lanterna allungata
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.5, 0, 2.35))
globe = bpy.context.object
globe.name = "LanternGlobe"
globe.scale = (1, 1, 1.3)
globe.data.materials.append(glass_mat)

# Supporto inferiore del globo
bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.02, location=(0.5, 0, 2.1))
globe_base = bpy.context.object
globe_base.data.materials.append(aged_bronze)

# Dettagli ornamentali sul supporto del globo
for i in range(8):
    angle = i * math.pi / 4
    x_offset = 0.2 * math.cos(angle)
    y_offset = 0.2 * math.sin(angle)
    bpy.ops.mesh.primitive_cube_add(
        size=0.02,
        location=(0.5 + x_offset, y_offset, 2.11)
    )
    ornament = bpy.context.object
    ornament.rotation_euler = (0, 0, angle)
    ornament.data.materials.append(aged_bronze)

# Luce interna più calda
bpy.ops.object.light_add(type='POINT', location=(0.5, 0, 2.35))
light = bpy.context.object
light.data.energy = 180
light.data.color = (1.0, 0.85, 0.65)

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Victorian street lamp with bronze materials and fluted column generated successfully!")

