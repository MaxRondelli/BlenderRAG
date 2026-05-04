import bpy
import bmesh
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Camera
cam = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam)
bpy.context.scene.collection.objects.link(cam_obj)
cam_obj.location = (0, -3, 2.6)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = cam_obj

# Light
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 2
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.location = (3, -3, 5)
sun_obj.rotation_euler = (math.radians(45), 0, math.radians(30))

# Base (wider, gray metallic)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.1, depth=0.12, location=(0, 0, 0.06))
base = bpy.context.active_object
mat_grigio = bpy.data.materials.new("GrigioMetallo")
mat_grigio.use_nodes = True
bsdf_grigio = mat_grigio.node_tree.nodes["Principled BSDF"]
bsdf_grigio.inputs["Base Color"].default_value = (0.25, 0.25, 0.25, 1)
bsdf_grigio.inputs["Metallic"].default_value = 0.9
bsdf_grigio.inputs["Roughness"].default_value = 0.3
base.data.materials.append(mat_grigio)

# Main hexagonal tapered pole
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object

# Apply taper using bmesh
bpy.context.view_layer.objects.active = palo
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(palo.data)

# Taper the top vertices
for vert in bm.verts:
    if vert.co.z > 0:
        vert.co.x *= 0.7
        vert.co.y *= 0.7

bmesh.update_edit_mesh(palo.data)
bpy.ops.object.mode_set(mode='OBJECT')

mat_palo = bpy.data.materials.new("PaloMetallo")
mat_palo.use_nodes = True
bsdf_palo = mat_palo.node_tree.nodes["Principled BSDF"]
bsdf_palo.inputs["Base Color"].default_value = (0.35, 0.35, 0.4, 1)
bsdf_palo.inputs["Metallic"].default_value = 0.8
bsdf_palo.inputs["Roughness"].default_value = 0.25
palo.data.materials.append(mat_palo)

# Curved angular support brackets
for i, z_pos in enumerate([2.25, 2.55]):
    # Create curved bracket using bezier curve
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0.035, z_pos))
    curve_obj = bpy.context.active_object
    
    # Modify curve points for angular bracket shape
    curve_obj.data.splines[0].bezier_points[0].co = (-0.15, 0, 0)
    curve_obj.data.splines[0].bezier_points[1].co = (0.15, 0, 0)
    curve_obj.data.splines[0].bezier_points[0].handle_right = (-0.1, 0.05, 0)
    curve_obj.data.splines[0].bezier_points[1].handle_left = (0.1, 0.05, 0)
    
    # Add bevel for thickness
    curve_obj.data.bevel_depth = 0.02
    curve_obj.data.bevel_resolution = 3
    
    # Convert to mesh
    bpy.ops.object.convert(target='MESH')
    curve_obj.data.materials.append(mat_grigio)

# White border backing
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
bordo = bpy.context.active_object
bordo.rotation_euler = (math.radians(90), 0, 0)
mat_bianco = bpy.data.materials.new("Bianco")
mat_bianco.use_nodes = True
bsdf_bianco = mat_bianco.node_tree.nodes["Principled BSDF"]
bsdf_bianco.inputs["Base Color"].default_value = (1, 1, 1, 1)
bsdf_bianco.inputs["Roughness"].default_value = 0.1
bordo.data.materials.append(mat_bianco)

# Modern STOP sign with deep crimson and metallic finish
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.04, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)

# Add subtle bevel modifier for modern edge
bevel_mod = stop_sign.modifiers.new(name="Bevel", type="BEVEL")
bevel_mod.width = 0.01
bevel_mod.segments = 2

mat_crimson = bpy.data.materials.new("CrimsonStop")
mat_crimson.use_nodes = True
bsdf_crimson = mat_crimson.node_tree.nodes["Principled BSDF"]
bsdf_crimson.inputs["Base Color"].default_value = (0.7, 0.0, 0.05, 1)
bsdf_crimson.inputs["Metallic"].default_value = 0.4
bsdf_crimson.inputs["Roughness"].default_value = 0.15
stop_sign.data.materials.append(mat_crimson)

# STOP text with modern styling
bpy.ops.object.text_add(location=(0, -0.04, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.32
text_obj.data.extrude = 0.02
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'

# Bevel the text for modern look
text_bevel = text_obj.modifiers.new(name="TextBevel", type="BEVEL")
text_bevel.width = 0.005
text_bevel.segments = 1

text_obj.data.materials.append(mat_bianco)

# Background
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
bg.inputs["Strength"].default_value = 1

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True

