import bpy
import bmesh
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BRONZE/COPPER MATERIAL
mat_bronze = bpy.data.materials.new(name="Bronze")
mat_bronze.use_nodes = True
nodes = mat_bronze.node_tree.nodes
links = mat_bronze.node_tree.links

# Remove default node
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

# Configure noise for patina texture
noise1.inputs['Scale'].default_value = 5.0
noise1.inputs['Detail'].default_value = 12.0
noise2.inputs['Scale'].default_value = 25.0
voronoi.inputs['Scale'].default_value = 30.0

# Configure color ramp for bronze colors
color_ramp.color_ramp.elements[0].color = (0.35, 0.25, 0.15, 1.0)
color_ramp.color_ramp.elements[1].color = (0.55, 0.35, 0.20, 1.0)

# Links
links.new(texture_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Configure BSDF for bronze
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.4

# TURQUOISE WATER MATERIAL
mat_water = bpy.data.materials.new(name="Water")
mat_water.use_nodes = True
bsdf_water = mat_water.node_tree.nodes["Principled BSDF"]
bsdf_water.inputs['Base Color'].default_value = (0.15, 0.45, 0.55, 1.0)
bsdf_water.inputs['Metallic'].default_value = 0.9
bsdf_water.inputs['Roughness'].default_value = 0.05
bsdf_water.inputs['Alpha'].default_value = 0.85

# BOTTOM BASE
bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.25, location=(0, 0, 0.125))
base_bottom = bpy.context.active_object
base_bottom.name = "Base_Bottom"
base_bottom.data.materials.append(mat_bronze)

# MID RING
bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=0.15, location=(0, 0, 0.325))
mid_ring = bpy.context.active_object
mid_ring.name = "Mid_Ring"
mid_ring.data.materials.append(mat_bronze)

# CENTRAL PEDESTAL
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=1.4, location=(0, 0, 1.1))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat_bronze)

# BOWL BASE - more rounded
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, location=(0, 0, 1.85))
bowl_base = bpy.context.active_object
bowl_base.name = "Bowl_Base"
bowl_base.scale[2] = 0.2
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bm = bmesh.from_edit_mesh(bowl_base.data)
for vert in bm.verts:
    if vert.co.z < 0:
        vert.co.z = 0
bmesh.update_edit_mesh(bowl_base.data)
bpy.ops.object.mode_set(mode='OBJECT')
bowl_base.data.materials.append(mat_bronze)

# MAIN BOWL - more curved and rounded
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, location=(0, 0, 2.0))
bowl = bpy.context.active_object
bowl.name = "Bowl"
bowl.scale[2] = 0.4
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bm = bmesh.from_edit_mesh(bowl.data)
for vert in bm.verts:
    if vert.co.z < -0.3:
        bm.verts.remove(vert)
    elif vert.co.z > 0.2:
        bm.verts.remove(vert)
bmesh.update_edit_mesh(bowl.data)
bpy.ops.object.mode_set(mode='OBJECT')
modifier = bowl.modifiers.new(name="Subsurf", type="SUBSURF")
modifier.levels = 2
bowl.data.materials.append(mat_bronze)

# WATER in bowl
bpy.ops.mesh.primitive_cylinder_add(radius=1.65, depth=0.08, location=(0, 0, 1.92))
water_pool = bpy.context.active_object
water_pool.name = "Water_Pool"
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bm = bmesh.from_edit_mesh(water_pool.data)
for vert in bm.verts:
    distance = math.sqrt(vert.co.x**2 + vert.co.y**2)
    if distance > 1.4:
        vert.co.z += (distance - 1.4) * 0.3
bmesh.update_edit_mesh(water_pool.data)
bpy.ops.object.mode_set(mode='OBJECT')
modifier = water_pool.modifiers.new(name="Subsurf", type="SUBSURF")
modifier.levels = 2
water_pool.data.materials.append(mat_water)

# CAMERA
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Bronze fountain with curved bowl and turquoise water created!")

