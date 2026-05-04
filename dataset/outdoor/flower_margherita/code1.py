import bpy
import math
import random

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scale_factor = 0.5  # Riduzione dimensione

# Centro marrone scuro (sunflower center)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4*scale_factor, location=(0, 0, 0), segments=64, ring_count=32)
center = bpy.context.active_object
center.scale[2] = 0.3

mat_center = bpy.data.materials.new("Centro")
mat_center.use_nodes = True
nodes = mat_center.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.2, 0.1, 0.05, 1)  # Rich dark brown
bsdf.inputs['Roughness'].default_value = 0.9

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 1.2  # Deeper texture
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 80  # More detailed texture

voronoi = nodes.new('ShaderNodeTexVoronoi')
voronoi.inputs['Scale'].default_value = 120
voronoi.feature = 'F1'  # or 'DISTANCE_TO_EDGE'

mix = nodes.new('ShaderNodeMix')
mix.data_type = 'FLOAT'

output = nodes.new('ShaderNodeOutputMaterial')
mat_center.node_tree.links.new(voronoi.outputs['Distance'], mix.inputs['B'])
mat_center.node_tree.links.new(mix.outputs['Result'], bump.inputs['Height'])
mat_center.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
mat_center.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

center.data.materials.append(mat_center)

mod = center.modifiers.new('Subsurf', type='SUBSURF')
mod.levels = 2

# Petali giallo dorato (sunflower petals)
mat_petalo = bpy.data.materials.new("Petalo")
mat_petalo.use_nodes = True
nodes = mat_petalo.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.95, 0.75, 0.1, 1)  # Golden yellow
bsdf.inputs['Roughness'].default_value = 0.4

gradient = nodes.new('ShaderNodeTexGradient')
gradient.gradient_type = 'RADIAL'
colorramp = nodes.new('ShaderNodeValToRGB')
colorramp.color_ramp.elements[0].color = (0.9, 0.65, 0.05, 1)
colorramp.color_ramp.elements[1].color = (1.0, 0.85, 0.3, 1)

output = nodes.new('ShaderNodeOutputMaterial')
mat_petalo.node_tree.links.new(colorramp.outputs['Color'], bsdf.inputs['Base Color'])
mat_petalo.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

num_petali = 29  # More petals for sunflower
for i in range(num_petali):
    angle = (2 * math.pi / num_petali) * i + random.uniform(-0.03, 0.03)
    dist = 0.42 * scale_factor + random.uniform(-0.015, 0.015) * scale_factor
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    
    bpy.ops.mesh.primitive_plane_add(size=1*scale_factor, location=(x, y, 0))
    petalo = bpy.context.active_object
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=6)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Wider petals with more rounded tips
    petalo.scale = (0.2, 0.75, 1)  # Wider and longer
    petalo.rotation_euler[2] = angle
    petalo.rotation_euler[0] = random.uniform(-0.1, 0.1)
    
    mod = petalo.modifiers.new('Subsurf', type='SUBSURF')
    mod.levels = 3  # More subdivision for rounder tips
    
    mod_simple = petalo.modifiers.new('SimpleDeform', type='SIMPLE_DEFORM')
    mod_simple.deform_method = 'BEND'
    mod_simple.angle = random.uniform(0.2, 0.4)  # Less bend for straighter petals
    mod_simple.deform_axis = 'Y'
    
    petalo.data.materials.append(mat_petalo)

# Stelo
bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale_factor, depth=2.5*scale_factor, location=(0, 0, -1.25*scale_factor), vertices=32)
stelo = bpy.context.active_object

mat_stelo = bpy.data.materials.new("Stelo")
mat_stelo.use_nodes = True
nodes = mat_stelo.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.05, 1)  # Darker green
bsdf.inputs['Roughness'].default_value = 0.7

bump = nodes.new('ShaderNodeBump')
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 25
output = nodes.new('ShaderNodeOutputMaterial')

mat_stelo.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
mat_stelo.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

stelo.data.materials.append(mat_stelo)

# Illuminazione
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_nodes.clear()
bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.6, 0.8, 1, 1)
bg.inputs['Strength'].default_value = 0.9
world_output = world_nodes.new('ShaderNodeOutputWorld')
bpy.context.scene.world.node_tree.links.new(bg.outputs['Background'], world_output.inputs['Surface'])

bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
sun = bpy.context.active_object
sun.data.energy = 4
sun.rotation_euler = (math.radians(45), 0, math.radians(35))

bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
fill = bpy.context.active_object
fill.data.energy = 180
fill.data.size = 2.5

# Camera
bpy.ops.object.camera_add(location=(2.2, -2.8, 1.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(38))
camera.data.lens = 90
bpy.context.scene.camera = camera

# Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
