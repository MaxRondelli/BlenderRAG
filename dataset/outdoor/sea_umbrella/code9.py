import bpy
import math
from mathutils import Vector

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materiali
def crea_materiale_legno():
    mat = bpy.data.materials.new(name="Legno")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1)
    color_ramp.color_ramp.elements[1].color = (0.28, 0.16, 0.08, 1)
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.8
    
    output = nodes.new('ShaderNodeOutputMaterial')
    
    links = mat.node_tree.links
    links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def crea_materiale_tessuto():
    mat = bpy.data.materials.new(name="Tessuto")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    wave = nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 12.0
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Y'
    
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].color = (0.05, 0.35, 0.85, 1)
    color_ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.98, 1)
    
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.9
    
    output = nodes.new('ShaderNodeOutputMaterial')
    
    links = mat.node_tree.links
    links.new(tex_coord.outputs['Generated'], wave.inputs['Vector'])
    links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def crea_materiale_metallo():
    mat = bpy.data.materials.new(name="Metallo")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.75, 1)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.2
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def crea_materiale_pavimento():
    mat = bpy.data.materials.new(name="Pavimento")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.25, 0.25, 0.25, 1)
    bsdf.inputs['Roughness'].default_value = 0.6
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

mat_legno = crea_materiale_legno()
mat_tessuto = crea_materiale_tessuto()
mat_metallo = crea_materiale_metallo()
mat_pavimento = crea_materiale_pavimento()

# Tavolo
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.75, depth=0.06, location=(0, 0, 0.3))
tavolo = bpy.context.active_object
tavolo.data.materials.append(mat_legno)
mod = tavolo.modifiers.new(name="Bevel", type='BEVEL')
mod.width = 0.01
mod.segments = 3
bpy.ops.object.shade_smooth()

# Palo ombrellone
centro_x, centro_y = 0, 0.05
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.028, depth=2.8, location=(centro_x, centro_y, 1.4))
palo = bpy.context.active_object
palo.data.materials.append(mat_metallo)
bpy.ops.object.shade_smooth()

# Hub centrale
altezza_hub = 2.8
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(centro_x, centro_y, altezza_hub))
hub = bpy.context.active_object
hub.data.materials.append(mat_metallo)

# Raggi
num_raggi = 8
raggio_esterno = 2.1
altezza_bordo = 2.05
offset_raggi = 0.03

# Telo ombrellone - mesh continua a ventaglio
mesh = bpy.data.meshes.new(name="Telo_Ombrellone")
obj = bpy.data.objects.new("Telo_Ombrellone", mesh)
bpy.context.collection.objects.link(obj)

verts = []
faces = []

# Centro
centro = Vector((centro_x, centro_y, altezza_hub))
verts.append(centro)

# Anelli radiali per densità
num_anelli = 5
for ring_idx in range(1, num_anelli + 1):
    t = ring_idx / num_anelli
    raggio_corrente = raggio_esterno * t
    
    # Altezza interpolata con curvatura più pronunciata
    z_corrente = altezza_hub - (altezza_hub - altezza_bordo) * t - 0.12 * t * (1 - t) * 4
    
    for i in range(num_raggi):
        angolo = (i / num_raggi) * 2 * math.pi
        x = centro_x + math.cos(angolo) * raggio_corrente
        y = centro_y + math.sin(angolo) * raggio_corrente
        verts.append(Vector((x, y, z_corrente)))

# Crea facce
# Triangoli dal centro al primo anello
for i in range(num_raggi):
    v1 = 0
    v2 = 1 + i
    v3 = 1 + (i + 1) % num_raggi
    faces.append((v1, v2, v3))

# Quad tra anelli
for ring_idx in range(num_anelli - 1):
    for i in range(num_raggi):
        base_ring = 1 + ring_idx * num_raggi
        next_ring = 1 + (ring_idx + 1) * num_raggi
        
        v1 = base_ring + i
        v2 = base_ring + (i + 1) % num_raggi
        v3 = next_ring + (i + 1) % num_raggi
        v4 = next_ring + i
        
        faces.append((v1, v2, v3, v4))

mesh.from_pydata(verts, [], faces)
mesh.update()

obj.data.materials.append(mat_tessuto)

# Subdivision per smoothness
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 2

bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()

# Camera
bpy.ops.object.camera_add(location=(5.5, -5, 2.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(72), 0, math.radians(48))
camera.data.lens = 35
bpy.context.scene.camera = camera

# World
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes.clear()

sky = world_nodes.new('ShaderNodeTexSky')
sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(45)
sky.sun_rotation = math.radians(135)

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 1.2

output = world_nodes.new('ShaderNodeOutputWorld')

links = world.node_tree.links
links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])

# Luci
bpy.ops.object.light_add(type='SUN', location=(8, -3, 12))
sole = bpy.context.active_object
sole.data.energy = 5.5
sole.data.angle = math.radians(0.53)
sole.rotation_euler = (math.radians(45), math.radians(20), math.radians(135))

bpy.ops.object.light_add(type='AREA', location=(-5, 3, 5))
fill = bpy.context.active_object
fill.data.energy = 120
fill.data.size = 4

# Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 512
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'High Contrast'

print("Beach umbrella with blue and white stripes!")