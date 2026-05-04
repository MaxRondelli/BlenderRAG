import bpy
import math

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# MATERIALE BRONZO/RAME
mat_bronze = bpy.data.materials.new(name="Bronze")
mat_bronze.use_nodes = True
nodes = mat_bronze.node_tree.nodes
links = mat_bronze.node_tree.links

# Rimuovi nodo default
nodes.clear()

# Crea nodi per texture bronzo
texture_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
noise1 = nodes.new(type='ShaderNodeTexNoise')
noise2 = nodes.new(type='ShaderNodeTexNoise')
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
color_ramp = nodes.new(type='ShaderNodeValToRGB')
mix_rgb = nodes.new(type='ShaderNodeMixRGB')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Posiziona nodi
texture_coord.location = (-800, 0)
mapping.location = (-600, 0)
noise1.location = (-400, 200)
noise2.location = (-400, -100)
voronoi.location = (-400, -400)
color_ramp.location = (-200, 0)
mix_rgb.location = (0, 0)
bsdf.location = (300, 0)
output.location = (500, 0)

# Configura noise per texture bronzo
noise1.inputs['Scale'].default_value = 5.0
noise1.inputs['Detail'].default_value = 10.0
noise2.inputs['Scale'].default_value = 25.0
voronoi.inputs['Scale'].default_value = 30.0

# Configura color ramp per colori bronzo/rame scuro
color_ramp.color_ramp.elements[0].color = (0.35, 0.18, 0.08, 1.0)
color_ramp.color_ramp.elements[1].color = (0.52, 0.28, 0.12, 1.0)

# Collegamenti
links.new(texture_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Configura BSDF per bronzo
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.4

# MATERIALE ACQUA VERDE SMERALDO
mat_water = bpy.data.materials.new(name="EmeraldWater")
mat_water.use_nodes = True
bsdf_water = mat_water.node_tree.nodes["Principled BSDF"]
bsdf_water.inputs['Base Color'].default_value = (0.1, 0.4, 0.2, 1.0)
bsdf_water.inputs['Metallic'].default_value = 0.95
bsdf_water.inputs['Roughness'].default_value = 0.05
bsdf_water.inputs['Alpha'].default_value = 0.8

# BASE INFERIORE - più spessa e arrotondata
bpy.ops.mesh.primitive_cylinder_add(radius=2.4, depth=0.35, location=(0, 0, 0.175))
base_bottom = bpy.context.active_object
base_bottom.name = "Base_Bottom"
base_bottom.data.materials.append(mat_bronze)

# Aggiungi modifica per arrotondare
modifier = base_bottom.modifiers.new(name="Bevel", type="BEVEL")
modifier.width = 0.08
modifier.segments = 3

# ANELLO INTERMEDIO - più spesso
bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.25, location=(0, 0, 0.475))
mid_ring = bpy.context.active_object
mid_ring.name = "Mid_Ring"
mid_ring.data.materials.append(mat_bronze)

# Aggiungi modifica per arrotondare
modifier = mid_ring.modifiers.new(name="Bevel", type="BEVEL")
modifier.width = 0.06
modifier.segments = 3

# PIEDISTALLO CENTRALE - più spesso
bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.4, location=(0, 0, 1.3))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat_bronze)

# Aggiungi modifica per arrotondare
modifier = pedestal.modifiers.new(name="Bevel", type="BEVEL")
modifier.width = 0.05
modifier.segments = 3

# VASCA PRINCIPALE - base più spessa
bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=0.3, location=(0, 0, 2.15))
bowl_base = bpy.context.active_object
bowl_base.name = "Bowl_Base"
bowl_base.data.materials.append(mat_bronze)

# Aggiungi modifica per arrotondare
modifier = bowl_base.modifiers.new(name="Bevel", type="BEVEL")
modifier.width = 0.07
modifier.segments = 3

# VASCA PRINCIPALE - bordo più arrotondato
bpy.ops.mesh.primitive_torus_add(major_radius=1.9, minor_radius=0.45, location=(0, 0, 2.35))
bowl = bpy.context.active_object
bowl.name = "Bowl"
bowl.scale[2] = 0.7
bowl.data.materials.append(mat_bronze)

# ACQUA nella vasca - verde smeraldo
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.08, location=(0, 0, 2.29))
water_pool = bpy.context.active_object
water_pool.name = "Water_Pool"
water_pool.data.materials.append(mat_water)

# CAMERA
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Fontana in bronzo con acqua verde smeraldo creata!")

import mathutils
import os

# Get all objects except lights
all_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

# Automatic method - calculates distance based on sunflower dimensions
def frame_flower(camera, objects):
    if not objects:
        return
    
    # Get bounding box corners for all objects
    bbox_corners = []
    for obj in objects:
        bbox_corners.extend([obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box])
    
    # Calculate center and bounding sphere radius
    center = sum(bbox_corners, mathutils.Vector()) / len(bbox_corners)
    radius = max((corner - center).length for corner in bbox_corners)
    
    # Camera distance (multiplier to ensure everything is visible)
    distance = radius * 5
    
    # Position camera at artistic angle for flower photography
    angle = math.radians(30)
    camera.location.x = center.x + distance * math.cos(angle)
    camera.location.y = center.y - distance * math.sin(angle)
    camera.location.z = center.z + distance * 0.5
    
    # Point toward center (slightly above center for better composition)
    target = center + mathutils.Vector((0, 0, -0.2))
    direction = target - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Adjust camera settings for macro photography feel
    camera.data.lens = 85
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = distance
    camera.data.dof.aperture_fstop = 2.8

# Create new camera for automatic framing
cam_data = bpy.data.cameras.new("AutoCamera")
auto_camera = bpy.data.objects.new("AutoCamera", cam_data)
bpy.context.scene.collection.objects.link(auto_camera)

# Frame the sunflower
frame_flower(auto_camera, all_objects)

# Set as active camera
bpy.context.scene.camera = auto_camera



bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render and save
bpy.ops.render.render(animation=False, write_still=True)

print(f"✅ Image saved: {bpy.context.scene.render.filepath}")

