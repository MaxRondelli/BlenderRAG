import bpy
import random
from math import radians

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# === GROUND ===
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

mat_ground = bpy.data.materials.new("GroundMat")
mat_ground.use_nodes = True
nodes = mat_ground.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.08, 0.12, 0.04, 1)
bsdf.inputs['Roughness'].default_value = 0.95
output = nodes.new('ShaderNodeOutputMaterial')
mat_ground.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
ground.data.materials.append(mat_ground)

# === REALISTIC GRASS BLADE (BENT PLANE) ===
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
grass_blade = bpy.context.active_object
grass_blade.name = "GrassBlade"
grass_blade.scale = (0.035, 0.4, 1)

# Model the grass blade
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=3)

# Bend the tip
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Move vertices for curvature
for i, vert in enumerate(grass_blade.data.vertices):
    if vert.co.z > 0.2:
        vert.co.x += 0.05 * vert.co.z
        vert.co.z *= 0.9

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')

# Autumn/Winter dormant grass material with golden-brown and amber gradient
mat_grass = bpy.data.materials.new("GrassMat")
mat_grass.use_nodes = True
nodes = mat_grass.node_tree.nodes
nodes.clear()

coord = nodes.new('ShaderNodeTexCoord')
separate = nodes.new('ShaderNodeSeparateXYZ')
ramp = nodes.new('ShaderNodeValToRGB')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
output = nodes.new('ShaderNodeOutputMaterial')

ramp.color_ramp.elements[0].color = (0.45, 0.28, 0.12, 1)
ramp.color_ramp.elements[1].color = (0.85, 0.58, 0.25, 1)

mat_grass.node_tree.links.new(coord.outputs['Object'], separate.inputs[0])
mat_grass.node_tree.links.new(separate.outputs['Z'], ramp.inputs[0])
mat_grass.node_tree.links.new(ramp.outputs[0], bsdf.inputs['Base Color'])
mat_grass.node_tree.links.new(bsdf.outputs[0], output.inputs[0])

bsdf.inputs['Roughness'].default_value = 0.5
grass_blade.data.materials.append(mat_grass)

# === PARTICLES ===
ground.select_set(True)
bpy.context.view_layer.objects.active = ground
bpy.ops.object.particle_system_add()

ps = ground.particle_systems[0]
pset = ps.settings
pset.type = 'HAIR'
pset.render_type = 'OBJECT'
pset.instance_object = grass_blade
pset.use_advanced_hair = True

pset.count = 55000
pset.hair_length = 1.5
pset.use_rotations = True
pset.rotation_mode = 'NOR'
pset.phase_factor_random = 2
pset.particle_size = 1.2
pset.size_random = 0.65
pset.length_random = 0.5

# Children
pset.child_type = 'SIMPLE'
pset.rendered_child_count = 10
pset.child_radius = 0.4
pset.child_length = 0.85
pset.child_size_random = 0.5

pset.clump_factor = 0.2
pset.roughness_1 = 0.6

# Viewport display
pset.display_method = 'RENDER'
pset.display_percentage = 50

# === LIGHTS ===
bpy.ops.object.light_add(type='SUN', location=(15, -10, 20))
sun = bpy.context.active_object
sun.data.energy = 5
sun.rotation_euler = (1.0, 0.3, 0.8)

# === CAMERA ===
bpy.ops.object.camera_add(location=(8, -8, 4))
cam = bpy.context.active_object
cam.rotation_euler = (1.2, 0, 0.785)
bpy.context.scene.camera = cam

# === ENVIRONMENT ===
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1)
    bg.inputs['Strength'].default_value = 1.0

# Viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("✓ Autumn/winter prairie grass with golden-brown coloration!")
