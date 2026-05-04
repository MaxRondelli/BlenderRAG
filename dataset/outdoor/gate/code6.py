import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.2
altezza_cancello = 1.8
profondita_palo = 0.12
num_listelli = 7
spessore_listello = 0.06
larghezza_listello = 0.15
gap_listelli = 0.05

# Pali laterali quadrati
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Cornice superiore e inferiore
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_cancello - 0.08))
cornice_sup = bpy.context.active_object
cornice_sup.scale = (larghezza_cancello, profondita_palo * 1.2, 0.08)
cornice_sup.name = "Cornice_Superiore"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.08))
cornice_inf = bpy.context.active_object
cornice_inf.scale = (larghezza_cancello, profondita_palo * 1.2, 0.08)
cornice_inf.name = "Cornice_Inferiore"

# Listelli verticali larghi con spazi tra loro
larghezza_interna = larghezza_cancello - 2*profondita_palo
altezza_listello = altezza_cancello - 0.16

for i in range(num_listelli):
    x_pos = -larghezza_interna/2 + (larghezza_listello/2) + i * (larghezza_listello + gap_listelli)
    z_pos = 0.08 + altezza_listello/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
    listello = bpy.context.active_object
    listello.scale = (larghezza_listello, spessore_listello, altezza_listello)
    listello.name = f"Listello_{i+1}"

# Materiale legno scuro naturale (cedro)
mat = bpy.data.materials.new(name="Cedro_Naturale")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.18, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7
bsdf.inputs['Specular IOR Level'].default_value = 0.3

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello giapponese minimalista creato!")