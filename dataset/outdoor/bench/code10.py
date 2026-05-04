import bpy
import math

# Clear everything
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_wood_material():
    mat = bpy.data.materials.new("Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.65, 0.4, 0.15, 1)
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
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.1
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

wood_mat = create_wood_material()
black_metal_mat = create_black_metal_material()

# SEAT - 4 thicker slats with more spacing
seat_width = 2.4
seat_depth = 0.6
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -seat_depth/2 + 0.08 + i*0.16, 0.5)
    )
    slat = bpy.context.active_object
    slat.scale = (seat_width/2, 0.07, 0.045)
    slat.data.materials.append(wood_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    slat.modifiers["Bevel"].width = 0.015
    slat.modifiers["Bevel"].segments = 4

# BACKREST - top rail
bpy.ops.mesh.primitive_cube_add(location=(0, 0.4, 1.1))
top_rail = bpy.context.active_object
top_rail.scale = (seat_width/2, 0.04, 0.045)
top_rail.data.materials.append(wood_mat)
bpy.ops.object.modifier_add(type='BEVEL')
top_rail.modifiers["Bevel"].width = 0.01
top_rail.modifiers["Bevel"].segments = 3

# BACKREST - slats
for i in range(3):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.35, 0.7 + i*0.15)
    )
    back_slat = bpy.context.active_object
    back_slat.scale = (seat_width/2, 0.025, 0.04)
    back_slat.data.materials.append(wood_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    back_slat.modifiers["Bevel"].width = 0.008
    back_slat.modifiers["Bevel"].segments = 3

# LEGS - front
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -0.2, 0.25))
    leg = bpy.context.active_object
    leg.scale = (0.04, 0.04, 0.25)
    leg.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    leg.modifiers["Bevel"].width = 0.003
    leg.modifiers["Bevel"].segments = 2

# LEGS - back
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.35, 0.55))
    leg = bpy.context.active_object
    leg.scale = (0.04, 0.04, 0.55)
    leg.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    leg.modifiers["Bevel"].width = 0.003
    leg.modifiers["Bevel"].segments = 2

# HORIZONTAL FRAME CONNECTIONS
# Front horizontal support
bpy.ops.mesh.primitive_cube_add(location=(0, -0.2, 0.15))
front_support = bpy.context.active_object
front_support.scale = (seat_width/2 - 0.14, 0.025, 0.025)
front_support.data.materials.append(black_metal_mat)

# Back horizontal support
bpy.ops.mesh.primitive_cube_add(location=(0, 0.35, 0.15))
back_support = bpy.context.active_object
back_support.scale = (seat_width/2 - 0.14, 0.025, 0.025)
back_support.data.materials.append(black_metal_mat)

# Side horizontal supports
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.075, 0.15))
    side_support = bpy.context.active_object
    side_support.scale = (0.025, 0.275, 0.025)
    side_support.data.materials.append(black_metal_mat)

# ARMRESTS - sleek metal with curves
for x_sign in [-1, 1]:
    x_pos = x_sign * (seat_width/2 + 0.04)
    
    bpy.ops.curve.primitive_bezier_curve_add(location=(x_pos, 0, 0))
    curve = bpy.context.active_object
    curve.data.dimensions = '3D'
    curve.data.bevel_depth = 0.02
    curve.data.bevel_resolution = 6
    
    spline = curve.data.splines[0]
    spline.bezier_points.add(1)
    
    # Point 0: front connection
    spline.bezier_points[0].co = (0, -0.2, 0.5)
    spline.bezier_points[0].handle_right_type = 'FREE'
    spline.bezier_points[0].handle_right = (0, -0.05, 0.6)
    spline.bezier_points[0].handle_left_type = 'FREE'
    spline.bezier_points[0].handle_left = (0, -0.25, 0.48)
    
    # Point 1: curve up
    spline.bezier_points[1].co = (0, 0.1, 0.75)
    spline.bezier_points[1].handle_left_type = 'FREE'
    spline.bezier_points[1].handle_left = (0, 0, 0.65)
    spline.bezier_points[1].handle_right_type = 'FREE'
    spline.bezier_points[1].handle_right = (0, 0.25, 0.8)
    
    # Point 2: back connection
    spline.bezier_points[2].co = (0, 0.35, 0.8)
    spline.bezier_points[2].handle_left_type = 'FREE'
    spline.bezier_points[2].handle_left = (0, 0.3, 0.78)
    spline.bezier_points[2].handle_right_type = 'FREE'
    spline.bezier_points[2].handle_right = (0, 0.37, 0.82)
    
    bpy.ops.object.convert(target='MESH')
    curve.data.materials.append(black_metal_mat)

# GEOMETRIC BACKREST DECORATION - horizontal metal strips
for i in range(5):
    z_pos = 0.72 + i * 0.08
    
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.38, z_pos)
    )
    strip = bpy.context.active_object
    strip.scale = (0.8, 0.015, 0.008)
    strip.data.materials.append(black_metal_mat)
    
    # Add slight bevel for clean edges
    bpy.ops.object.modifier_add(type='BEVEL')
    strip.modifiers["Bevel"].width = 0.002
    strip.modifiers["Bevel"].segments = 2

# LIGHTING
bpy.ops.object.light_add(type='SUN', location=(8, -8, 12))
sun = bpy.context.active_object
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), 0, math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-5, 3, 5))
area = bpy.context.active_object
area.data.energy = 120
area.data.size = 4

# Additional rim light for metal highlights
bpy.ops.object.light_add(type='AREA', location=(3, 2, 3))
rim_light = bpy.context.active_object
rim_light.data.energy = 80
rim_light.data.size = 2

# CAMERA
bpy.ops.object.camera_add(location=(4.5, -3.5, 2.2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(72), 0, math.radians(55))
bpy.context.scene.camera = camera

# RENDER SETTINGS
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.render.film_transparent = True

print("✓ Modern minimalist bench created!")