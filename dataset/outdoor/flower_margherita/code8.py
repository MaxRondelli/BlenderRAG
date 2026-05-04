import bpy
import math
import random

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scale_factor = 0.5  # Riduzione dimensione

# Centro arancione-marrone più scuro
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4*scale_factor, location=(0, 0, 0), segments=64, ring_count=32)
center = bpy.context.active_object
center.scale[2] = 0.3

mat_center = bpy.data.materials.new("Centro")
mat_center.use_nodes = True
nodes = mat_center.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.05, 1)  # Arancione-marrone più scuro
bsdf.inputs['Roughness'].default_value = 0.8

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 1.2
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 80
noise.inputs['Detail'].default_value = 8

output = nodes.new('ShaderNodeOutputMaterial')
mat_center.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
mat_center.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

center.data.materials.append(mat_center)

mod = center.modifiers.new('Subsurf', 'SUBSURF')
mod.levels = 2

# Petali viola scuro
mat_petalo = bpy.data.materials.new("Petalo")
mat_petalo.use_nodes = True
nodes = mat_petalo.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.6, 1)  # Viola scuro
bsdf.inputs['Roughness'].default_value = 0.4
bsdf.inputs['Metallic'].default_value = 0.1

output = nodes.new('ShaderNodeOutputMaterial')
mat_petalo.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

num_petali = 21
for i in range(num_petali):
    angle = (2 * math.pi / num_petali) * i + random.uniform(-0.05, 0.05)
    dist = 0.42 * scale_factor + random.uniform(-0.02, 0.02) * scale_factor
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    
    bpy.ops.mesh.primitive_plane_add(size=1*scale_factor, location=(x, y, 0))
    petalo = bpy.context.active_object
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=5)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    petalo.scale = (0.15, 0.6, 1)
    petalo.rotation_euler[2] = angle
    petalo.rotation_euler[0] = random.uniform(-0.15, 0.15)
    
    mod = petalo.modifiers.new('Subsurf', 'SUBSURF')
    mod.levels = 2
    
    mod_simple = petalo.modifiers.new('SimpleDeform', 'SIMPLE_DEFORM')
    mod_simple.deform_method = 'BEND'
    mod_simple.angle = random.uniform(0.3, 0.5)
    mod_simple.deform_axis = 'Y'
    
    petalo.data.materials.append(mat_petalo)

# Stelo più robusto e scanalato
bpy.ops.mesh.primitive_cylinder_add(radius=0.1*scale_factor, depth=2.5*scale_factor, location=(0, 0, -1.25*scale_factor), vertices=16)
stelo = bpy.context.active_object

# Aggiungi scanalature allo stelo
bpy.context.view_layer.objects.active = stelo
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=8)
bpy.ops.object.mode_set(mode='OBJECT')

mat_stelo = bpy.data.materials.new("Stelo")
mat_stelo.use_nodes = True
nodes = mat_stelo.node_tree.nodes
nodes.clear()

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.08, 0.25, 0.05, 1)  # Verde più scuro
bsdf.inputs['Roughness'].default_value = 0.7

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 1.5
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 35
noise.inputs['Detail'].default_value = 6

# Aggiungi texture per le scanalature
wave = nodes.new('ShaderNodeTexWave')
wave.wave_profile = 'SIN'
wave.inputs['Scale'].default_value = 15
wave.inputs['Distortion'].default_value = 0.5

mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MULTIPLY'


output = nodes.new('ShaderNodeOutputMaterial')

mat_stelo.node_tree.links.new(wave.outputs['Color'], mix.inputs['Color2'])
mat_stelo.node_tree.links.new(mix.outputs['Color'], bump.inputs['Height'])
mat_stelo.node_tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
mat_stelo.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

stelo.data.materials.append(mat_stelo)

# Aggiungi modificatore per le scanalature
mod_disp = stelo.modifiers.new('Displacement', 'DISPLACE')
mod_disp.strength = 0.02

# Illuminazione
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_nodes.clear()
bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.5, 0.7, 1, 1)
bg.inputs['Strength'].default_value = 0.8
world_output = world_nodes.new('ShaderNodeOutputWorld')
bpy.context.scene.world.node_tree.links.new(bg.outputs['Background'], world_output.inputs['Surface'])

bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
sun = bpy.context.active_object
sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
fill = bpy.context.active_object
fill.data.energy = 150
fill.data.size = 2

# Camera
bpy.ops.object.camera_add(location=(2, -2.5, 1.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(80), 0, math.radians(40))
camera.data.lens = 85
bpy.context.scene.camera = camera

# Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
