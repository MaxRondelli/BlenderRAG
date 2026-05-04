import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BRONZE/COPPER MATERIAL
mat_bronze = bpy.data.materials.new(name="Bronze")
mat_bronze.use_nodes = True
nodes = mat_bronze.node_tree.nodes
links = mat_bronze.node_tree.links

# Remove default nodes
nodes.clear()

# Create nodes for bronze texture
texture_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
noise1 = nodes.new(type='ShaderNodeTexNoise')
noise2 = nodes.new(type='ShaderNodeTexNoise')
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
color_ramp = nodes.new(type='ShaderNodeValToRGB')
mix_rgb = nodes.new(type='ShaderNodeMixRGB')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Position nodes
texture_coord.location = (-800, 0)
mapping.location = (-600, 0)
noise1.location = (-400, 200)
noise2.location = (-400, -100)
voronoi.location = (-400, -400)
color_ramp.location = (-200, 0)
mix_rgb.location = (0, 0)
bsdf.location = (300, 0)
output.location = (500, 0)

# Configure noise for bronze patina
noise1.inputs['Scale'].default_value = 4.0
noise1.inputs['Detail'].default_value = 10.0
noise2.inputs['Scale'].default_value = 18.0
voronoi.inputs['Scale'].default_value = 25.0

# Configure color ramp for bronze colors
color_ramp.color_ramp.elements[0].color = (0.4, 0.25, 0.15, 1.0)
color_ramp.color_ramp.elements[1].color = (0.6, 0.4, 0.2, 1.0)

# Links
links.new(texture_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Configure BSDF for bronze
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.4

# DEEP BLUE-GREEN WATER MATERIAL
mat_water = bpy.data.materials.new(name="Water")
mat_water.use_nodes = True
bsdf_water = mat_water.node_tree.nodes["Principled BSDF"]
bsdf_water.inputs['Base Color'].default_value = (0.1, 0.4, 0.5, 1.0)
bsdf_water.inputs['Metallic'].default_value = 0.95
bsdf_water.inputs['Roughness'].default_value = 0.05
bsdf_water.inputs['Alpha'].default_value = 0.8

# BASE INFERIOR - slightly taller
bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.35, location=(0, 0, 0.175))
base_bottom = bpy.context.active_object
base_bottom.name = "Base_Bottom"
base_bottom.data.materials.append(mat_bronze)

# INTERMEDIATE RING - taller
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.25, location=(0, 0, 0.475))
mid_ring = bpy.context.active_object
mid_ring.name = "Mid_Ring"
mid_ring.data.materials.append(mat_bronze)

# CENTRAL PEDESTAL - taller and more tapered
bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.8, location=(0, 0, 1.35))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat_bronze)

# Enter edit mode to taper the pedestal
bpy.context.view_layer.objects.active = pedestal
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Use bmesh to select top vertices
import bmesh
bm = bmesh.new()
bm.from_mesh(pedestal.data)

for vert in bm.verts:
    if vert.co.z > 0.8:
        vert.co.x *= 0.7
        vert.co.y *= 0.7

bm.to_mesh(pedestal.data)
bm.free()

# MAIN BOWL - base, taller
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.3, location=(0, 0, 2.35))
bowl_base = bpy.context.active_object
bowl_base.name = "Bowl_Base"
bowl_base.data.materials.append(mat_bronze)

# MAIN BOWL - rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.4, location=(0, 0, 2.55))
bowl = bpy.context.active_object
bowl.name = "Bowl"
bowl.scale[2] = 0.6
bowl.data.materials.append(mat_bronze)

# WATER in bowl
bpy.ops.mesh.primitive_cylinder_add(radius=1.7, depth=0.05, location=(0, 0, 2.48))
water_pool = bpy.context.active_object
water_pool.name = "Water_Pool"
water_pool.data.materials.append(mat_water)

# CAMERA
bpy.ops.object.camera_add(location=(6, -6, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Bronze fountain with reflective water created!")

