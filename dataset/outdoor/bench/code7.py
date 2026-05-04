import bpy
import math

# Clear all
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_white_material():
    mat = bpy.data.materials.new("WhiteWood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1)
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
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.6
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

white_mat = create_white_material()
black_metal_mat = create_black_metal_material()

# SEAT - 5 slats with white material
seat_width = 2.4
seat_depth = 0.6
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -seat_depth/2 + 0.1 + i*0.14, 0.5)
    )
    slat = bpy.context.active_object
    slat.scale = (seat_width/2, 0.05, 0.03)
    slat.data.materials.append(white_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    slat.modifiers["Bevel"].width = 0.005
    slat.modifiers["Bevel"].segments = 3

# BACKREST - top rail with white material
bpy.ops.mesh.primitive_cube_add(location=(0, 0.4, 1.1))
top_rail = bpy.context.active_object
top_rail.scale = (seat_width/2, 0.04, 0.045)
top_rail.data.materials.append(white_mat)

# BACKREST - slats with white material
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.35, 0.65 + i*0.13)
    )
    back_slat = bpy.context.active_object
    back_slat.scale = (seat_width/2, 0.025, 0.04)
    back_slat.data.materials.append(white_mat)

# LEGS - front with black metal
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -0.2, 0.25))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.25)
    leg.data.materials.append(black_metal_mat)

# LEGS - back with black metal
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.35, 0.55))
    leg = bpy.context.active_object
    leg.scale = (0.035, 0.035, 0.55)
    leg.data.materials.append(black_metal_mat)

# ARMRESTS - thicker with softer curves and black metal
for x_sign in [-1, 1]:
    x_pos = x_sign * (seat_width/2 + 0.05)
    
    bpy.ops.curve.primitive_bezier_curve_add(location=(x_pos, 0, 0))
    curve = bpy.context.active_object
    curve.data.dimensions = '3D'
    curve.data.bevel_depth = 0.035
    curve.data.bevel_resolution = 12
    
    spline = curve.data.splines[0]
    spline.bezier_points.add(2)
    
    # Point 0: front base with softer curve
    spline.bezier_points[0].co = (0, -0.25, 0.5)
    spline.bezier_points[0].handle_right_type = 'FREE'
    spline.bezier_points[0].handle_right = (0, -0.15, 0.6)
    spline.bezier_points[0].handle_left_type = 'FREE'
    spline.bezier_points[0].handle_left = (0, -0.3, 0.45)
    
    # Point 1: curved middle section with gentler transition
    spline.bezier_points[1].co = (0, 0, 0.8)
    spline.bezier_points[1].handle_left_type = 'FREE'
    spline.bezier_points[1].handle_left = (0, -0.1, 0.7)
    spline.bezier_points[1].handle_right_type = 'FREE'
    spline.bezier_points[1].handle_right = (0, 0.15, 0.9)
    
    # Point 2: approach to backrest with smooth curve
    spline.bezier_points[2].co = (0, 0.3, 1.05)
    spline.bezier_points[2].handle_left_type = 'FREE'
    spline.bezier_points[2].handle_left = (0, 0.15, 1.0)
    spline.bezier_points[2].handle_right_type = 'FREE'
    spline.bezier_points[2].handle_right = (0, 0.35, 1.08)
    
    # Point 3: final attachment with rounded end
    spline.bezier_points[3].co = (0, 0.37, 1.1)
    spline.bezier_points[3].handle_left_type = 'FREE'
    spline.bezier_points[3].handle_left = (0, 0.36, 1.09)
    spline.bezier_points[3].handle_right_type = 'FREE'
    spline.bezier_points[3].handle_right = (0, 0.38, 1.11)
    
    bpy.ops.object.convert(target='MESH')
    curve.data.materials.append(black_metal_mat)

# BACKREST DECORATIONS - minimalist circular elements in black metal
for i in range(5):
    x_pos = -0.4 + i * 0.2
    for j in range(2):
        z_pos = 0.8 + j * 0.2
        
        bpy.ops.mesh.primitive_torus_add(
            location=(x_pos, 0.37, z_pos),
            rotation=(0, math.pi/2, 0),
            major_radius=0.03,
            minor_radius=0.005
        )
        dec = bpy.context.active_object
        dec.data.materials.append(black_metal_mat)

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(8, -8, 12))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-5, 3, 5))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 6

# CAMERA
bpy.ops.object.camera_add(location=(4, -4, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(50))
bpy.context.scene.camera = camera

# RENDER SETTINGS
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.render.film_transparent = True

print("✓ Modern minimalist bench with black metal frame and white slats created!")