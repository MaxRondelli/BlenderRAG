import bpy
import math

# Pulisci tutto
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_light_oak_material():
    mat = bpy.data.materials.new("LightOak")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.75, 0.55, 1)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

def create_black_metal_material():
    mat = bpy.data.materials.new("BlackMetal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.15
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

light_oak_mat = create_light_oak_material()
black_metal_mat = create_black_metal_material()

# SEDUTA - 5 listelli più spessi
seat_width = 2.4
seat_depth = 0.6
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -seat_depth/2 + 0.1 + i*0.14, 0.5)
    )
    slat = bpy.context.active_object
    slat.scale = (seat_width/2, 0.06, 0.04)
    slat.data.materials.append(light_oak_mat)
    slat.modifiers.new(name="Bevel", type="BEVEL")
    slat.modifiers["Bevel"].width = 0.008
    slat.modifiers["Bevel"].segments = 4

# SCHIENALE - top rail più spesso
bpy.ops.mesh.primitive_cube_add(location=(0, 0.4, 1.1))
top_rail = bpy.context.active_object
top_rail.scale = (seat_width/2, 0.05, 0.055)
top_rail.data.materials.append(light_oak_mat)
top_rail.modifiers.new(name="Bevel", type="BEVEL")
top_rail.modifiers["Bevel"].width = 0.008
top_rail.modifiers["Bevel"].segments = 4

# SCHIENALE - listelli più spessi
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.35, 0.65 + i*0.13)
    )
    back_slat = bpy.context.active_object
    back_slat.scale = (seat_width/2, 0.035, 0.05)
    back_slat.data.materials.append(light_oak_mat)
    back_slat.modifiers.new(name="Bevel", type="BEVEL")
    back_slat.modifiers["Bevel"].width = 0.008
    back_slat.modifiers["Bevel"].segments = 4

# GAMBE - anteriori nere
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -0.2, 0.25))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.25)
    leg.data.materials.append(black_metal_mat)

# GAMBE - posteriori nere
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.35, 0.55))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.55)
    leg.data.materials.append(black_metal_mat)

# BRACCIOLI - neri minimalisti
for x_sign in [-1, 1]:
    x_pos = x_sign * (seat_width/2 + 0.05)
    
    bpy.ops.curve.primitive_bezier_curve_add(location=(x_pos, 0, 0))
    curve = bpy.context.active_object
    curve.data.dimensions = '3D'
    curve.data.bevel_depth = 0.02
    curve.data.bevel_resolution = 6
    
    spline = curve.data.splines[0]
    spline.bezier_points.add(2)
    
    spline.bezier_points[0].co = (0, -0.25, 0.5)
    spline.bezier_points[0].handle_right_type = 'FREE'
    spline.bezier_points[0].handle_right = (0, -0.1, 0.55)
    spline.bezier_points[0].handle_left_type = 'FREE'
    spline.bezier_points[0].handle_left = (0, -0.3, 0.48)
    
    spline.bezier_points[1].co = (0, 0, 0.75)
    spline.bezier_points[1].handle_left_type = 'FREE'
    spline.bezier_points[1].handle_left = (0, -0.05, 0.65)
    spline.bezier_points[1].handle_right_type = 'FREE'
    spline.bezier_points[1].handle_right = (0, 0.1, 0.85)
    
    spline.bezier_points[2].co = (0, 0.3, 1.0)
    spline.bezier_points[2].handle_left_type = 'FREE'
    spline.bezier_points[2].handle_left = (0, 0.2, 0.95)
    spline.bezier_points[2].handle_right_type = 'FREE'
    spline.bezier_points[2].handle_right = (0, 0.35, 1.05)
    
    spline.bezier_points[3].co = (0, 0.37, 1.1)
    spline.bezier_points[3].handle_left_type = 'FREE'
    spline.bezier_points[3].handle_left = (0, 0.36, 1.08)
    spline.bezier_points[3].handle_right_type = 'FREE'
    spline.bezier_points[3].handle_right = (0, 0.38, 1.12)
    
    bpy.ops.object.convert(target='MESH')
    curve.data.materials.append(black_metal_mat)

# DECORAZIONI SCHIENALE - placche rettangolari metalliche
for i in range(6):
    x_pos = -0.5 + i * 0.2
    for j in range(3):
        z_pos = 0.72 + j * 0.12
        
        bpy.ops.mesh.primitive_cube_add(
            location=(x_pos, 0.38, z_pos)
        )
        plate = bpy.context.active_object
        plate.scale = (0.025, 0.003, 0.035)
        plate.data.materials.append(black_metal_mat)
        plate.modifiers.new(name="Bevel", type="BEVEL")
        plate.modifiers["Bevel"].width = 0.002
        plate.modifiers["Bevel"].segments = 2

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

print("✓ Panca minimalista moderna creata!")