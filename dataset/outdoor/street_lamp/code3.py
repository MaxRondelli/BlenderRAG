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
    principled.inputs['Metallic'].default_value = 0.9
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
bronze_metal = create_bronze_material("BronzeMetal", (0.25, 0.15, 0.08, 1.0))
glass_mat = create_glass_material()

# Base (cilindrica con anelli decorativi più elaborati)
bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.35, location=(0, 0, 0.175))
base = bpy.context.object
base.name = "Base"
base.data.materials.append(bronze_metal)

# Anelli decorativi base più elaborati
for z in [0.06, 0.28]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.025, location=(0, 0, z))
    ring = bpy.context.object
    ring.data.materials.append(bronze_metal)
    
    # Piccoli ornamenti sui ring principali
    for angle in [0, math.pi/3, 2*math.pi/3, math.pi, 4*math.pi/3, 5*math.pi/3]:
        x_pos = 0.175 * math.cos(angle)
        y_pos = 0.175 * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.04, location=(x_pos, y_pos, z))
        ornament = bpy.context.object
        ornament.data.materials.append(bronze_metal)

# Palo principale fluted (cilindrico con scanalature verticali)
bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=2.8, location=(0, 0, 1.7))
pole = bpy.context.object
pole.name = "FlutedPole"
pole.data.materials.append(bronze_metal)

# Creare scanalature verticali usando bmesh
bpy.context.view_layer.objects.active = pole
bpy.ops.object.mode_set(mode='EDIT')

bm = bmesh.from_edit_mesh(pole.data)
bmesh.ops.subdivide_edges(bm, 
                         edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.1],
                         cuts=16,
                         use_grid_fill=True)

# Creare le scanalature
for vert in bm.verts:
    if abs(vert.co.x) > 0.001 or abs(vert.co.y) > 0.001:
        angle = math.atan2(vert.co.y, vert.co.x)
        flute_depth = 0.008 * math.sin(angle * 12)
        radius_factor = 1.0 + flute_depth
        vert.co.x *= radius_factor
        vert.co.y *= radius_factor

bmesh.update_edit_mesh(pole.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Sezioni decorative palo più ornate
for z in [0.8, 1.5, 2.4]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.12, location=(0, 0, z))
    section = bpy.context.object
    section.data.materials.append(bronze_metal)
    
    # Piccoli ornamenti intorno alle sezioni
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        x_pos = 0.1 * math.cos(angle)
        y_pos = 0.1 * math.sin(angle)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x_pos, y_pos, z))
        ornament = bpy.context.object
        ornament.data.materials.append(bronze_metal)



# Braccio decorativo più ornato
curve = bpy.data.curves.new('VictorianArmCurve', 'CURVE')
curve.dimensions = '3D'
curve.bevel_depth = 0.03
polyline = curve.splines.new('BEZIER')
polyline.bezier_points.add(5)

# Punti che formano una curva più elaborata
points = [
    (0.06, 0, 2.6),
    (0.15, 0, 2.75),
    (0.28, 0, 2.82),
    (0.42, 0, 2.75),
    (0.52, 0, 2.65),
    (0.55, 0, 2.55)
]

for i, point in enumerate(points):
    polyline.bezier_points[i].co = point
    polyline.bezier_points[i].handle_left_type = 'AUTO'
    polyline.bezier_points[i].handle_right_type = 'AUTO'

arm_obj = bpy.data.objects.new('VictorianArm', curve)
bpy.context.collection.objects.link(arm_obj)
arm_obj.data.materials.append(bronze_metal)

# Volute decorative superiori più elaborate
for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
    # Volute principali
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.08, 
        minor_radius=0.018, 
        location=(0.08 + 0.06 * math.cos(angle), 0.06 * math.sin(angle), 2.78)
    )
    volute = bpy.context.object
    volute.rotation_euler = (math.pi/2.2, angle * 0.4, angle)
    volute.data.materials.append(bronze_metal)
    
    # Spirali ornamentali più piccole
    for i in range(3):
        radius_offset = 0.04 + i * 0.02
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.025, 
            minor_radius=0.008, 
            location=(0.08 + radius_offset * math.cos(angle), radius_offset * math.sin(angle), 2.72 + i * 0.04)
        )
        small_spiral = bpy.context.object
        small_spiral.rotation_euler = (math.pi/3, angle * 0.6 + i * 0.5, angle + i * 0.3)
        small_spiral.data.materials.append(bronze_metal)

# Connettore più ornato
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.15, location=(0.55, 0, 2.5))
connector = bpy.context.object
connector.rotation_euler = (0, 0, 0)
connector.data.materials.append(bronze_metal)

# Dettagli sul connettore
for z_offset in [-0.05, 0, 0.05]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.008, location=(0.55, 0, 2.5 + z_offset))
    detail = bpy.context.object
    detail.data.materials.append(bronze_metal)

# Supporto superiore globo più elaborato
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(0.55, 0, 2.62))
support_top = bpy.context.object
support_top.scale = (1, 1, 0.6)
support_top.data.materials.append(bronze_metal)

# Corona decorativa intorno al supporto
for angle in [i * math.pi/4 for i in range(8)]:
    x_pos = 0.55 + 0.065 * math.cos(angle)
    y_pos = 0.065 * math.sin(angle)
    bpy.ops.mesh.primitive_cone_add(radius1=0.008, radius2=0.003, depth=0.025, location=(x_pos, y_pos, 2.62))
    crown_spike = bpy.context.object
    crown_spike.data.materials.append(bronze_metal)

# Elemento decorativo sulla cima più ornato
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.05, location=(0.55, 0, 2.67))
cap = bpy.context.object
cap.data.materials.append(bronze_metal)

# Globo in vetro
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.55, 0, 2.3))
globe = bpy.context.object
globe.name = "GlassGlobe"
globe.data.materials.append(glass_mat)

# Supporto inferiore del globo
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.08, location=(0.55, 0, 2.12))
support_bottom = bpy.context.object
support_bottom.data.materials.append(bronze_metal)

# Catene decorative attorno al globo
for chain_angle in [0, 2*math.pi/3, 4*math.pi/3]:
    for link in range(8):
        link_angle = chain_angle + link * 0.3
        radius = 0.19 + 0.01 * math.sin(link * 2)
        x_pos = 0.55 + radius * math.cos(link_angle)
        y_pos = radius * math.sin(link_angle)
        z_pos = 2.15 + link * 0.04
        
        bpy.ops.mesh.primitive_torus_add(major_radius=0.012, minor_radius=0.004, location=(x_pos, y_pos, z_pos))
        chain_link = bpy.context.object
        chain_link.rotation_euler = (math.pi/2, 0, link_angle)
        chain_link.data.materials.append(bronze_metal)

# Luce interna
bpy.ops.object.light_add(type='POINT', location=(0.55, 0, 2.3))
light = bpy.context.object
light.data.energy = 150
light.data.color = (1.0, 0.95, 0.85)

# Camera
bpy.ops.object.camera_add(location=(3.5, -3.5, 2.5))
camera = bpy.context.object
camera.rotation_euler = (math.radians(70), 0, math.radians(50))
bpy.context.scene.camera = camera

print("Victorian street lamp with ornate cast iron detailing generated successfully!")

