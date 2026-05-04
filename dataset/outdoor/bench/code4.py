import bpy
import math

# Pulisci tutto
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_wood_material():
    mat = bpy.data.materials.new("Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.2, 0.15, 0.08, 1)
    bsdf.inputs['Roughness'].default_value = 0.8
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

def create_metal_material():
    mat = bpy.data.materials.new("Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.7, 0.4, 0.2, 1)
    bsdf.inputs['Metallic'].default_value = 0.6
    bsdf.inputs['Roughness'].default_value = 0.35
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

wood_mat = create_wood_material()
metal_mat = create_metal_material()

# SEDUTA - 5 listelli
seat_width = 2.4
seat_depth = 0.6
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -seat_depth/2 + 0.1 + i*0.14, 0.5)
    )
    slat = bpy.context.active_object
    slat.scale = (seat_width/2, 0.06, 0.036)
    slat.data.materials.append(wood_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    slat.modifiers["Bevel"].width = 0.005
    slat.modifiers["Bevel"].segments = 3

# SCHIENALE - top rail
bpy.ops.mesh.primitive_cube_add(location=(0, 0.4, 1.1))
top_rail = bpy.context.active_object
top_rail.scale = (seat_width/2, 0.048, 0.054)
top_rail.data.materials.append(wood_mat)

# SCHIENALE - listelli
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.35, 0.65 + i*0.13)
    )
    back_slat = bpy.context.active_object
    back_slat.scale = (seat_width/2, 0.03, 0.048)
    back_slat.data.materials.append(wood_mat)

# GAMBE - anteriori
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -0.2, 0.25))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.25)
    leg.data.materials.append(metal_mat)

# GAMBE - posteriori
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.35, 0.55))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.55)
    leg.data.materials.append(metal_mat)

# BRACCIOLI - collegati allo schienale
for x_sign in [-1, 1]:
    x_pos = x_sign * (seat_width/2 + 0.05)
    
    bpy.ops.curve.primitive_bezier_curve_add(location=(x_pos, 0, 0))
    curve = bpy.context.active_object
    curve.data.dimensions = '3D'
    curve.data.bevel_depth = 0.025
    curve.data.bevel_resolution = 8
    
    # La curva parte con 2 punti, ne aggiungo altri 2
    spline = curve.data.splines[0]
    spline.bezier_points.add(2)  # Ora ho 4 punti totali
    
    # Punto 0: base anteriore
    spline.bezier_points[0].co = (0, -0.25, 0.5)
    spline.bezier_points[0].handle_right_type = 'FREE'
    spline.bezier_points[0].handle_right = (0, -0.1, 0.55)
    spline.bezier_points[0].handle_left_type = 'FREE'
    spline.bezier_points[0].handle_left = (0, -0.3, 0.48)
    
    # Punto 1: parte centrale curvata
    spline.bezier_points[1].co = (0, 0, 0.75)
    spline.bezier_points[1].handle_left_type = 'FREE'
    spline.bezier_points[1].handle_left = (0, -0.05, 0.65)
    spline.bezier_points[1].handle_right_type = 'FREE'
    spline.bezier_points[1].handle_right = (0, 0.1, 0.85)
    
    # Punto 2: arrivo verso schienale
    spline.bezier_points[2].co = (0, 0.3, 1.0)
    spline.bezier_points[2].handle_left_type = 'FREE'
    spline.bezier_points[2].handle_left = (0, 0.2, 0.95)
    spline.bezier_points[2].handle_right_type = 'FREE'
    spline.bezier_points[2].handle_right = (0, 0.35, 1.05)
    
    # Punto 3: attacco finale allo schienale
    spline.bezier_points[3].co = (0, 0.37, 1.1)
    spline.bezier_points[3].handle_left_type = 'FREE'
    spline.bezier_points[3].handle_left = (0, 0.36, 1.08)
    spline.bezier_points[3].handle_right_type = 'FREE'
    spline.bezier_points[3].handle_right = (0, 0.38, 1.12)
    
    bpy.ops.object.convert(target='MESH')
    curve.data.materials.append(metal_mat)

# DECORAZIONI SCHIENALE
for i in range(7):
    x_pos = -0.6 + i * 0.2
    for j in range(3):
        z_pos = 0.7 + j * 0.15
        
        bpy.ops.mesh.primitive_torus_add(
            location=(x_pos, 0.37, z_pos),
            rotation=(0, math.pi/2, 0),
            major_radius=0.04,
            minor_radius=0.006
        )
        dec = bpy.context.active_object
        dec.data.materials.append(metal_mat)

# ILLUMINAZIONE
bpy.ops.object.light_add(type='SUN', location=(8, -8, 12))
sun = bpy.context.active_object
sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-5, 3, 5))
area = bpy.context.active_object
area.data.energy = 150
area.data.size = 5

# CAMERA
bpy.ops.object.camera_add(location=(4, -4, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(50))
bpy.context.scene.camera = camera

# RENDER
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.render.film_transparent = True

print("✓ Industrial dark walnut bench with copper accents!")