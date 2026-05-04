import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.0
altezza_cancello = 2.0
profondita_palo = 0.12
num_verticali = 8
num_orizzontali = 8
spessore_barra = 0.03

# Pali laterali
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Sbarre verticali
larghezza_interna = larghezza_cancello - 2*profondita_palo
spaziatura_x = larghezza_interna / (num_verticali + 1)

for i in range(num_verticali):
    x_pos = -larghezza_cancello/2 + profondita_palo + spaziatura_x * (i + 1)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, altezza_cancello/2))
    sbarra_v = bpy.context.active_object
    sbarra_v.scale = (spessore_barra, spessore_barra, altezza_cancello)
    sbarra_v.name = f"Verticale_{i+1}"

# Sbarre orizzontali
spaziatura_z = altezza_cancello / (num_orizzontali + 1)

for i in range(num_orizzontali):
    z_pos = spaziatura_z * (i + 1)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_pos))
    sbarra_h = bpy.context.active_object
    sbarra_h.scale = (larghezza_interna, spessore_barra, spessore_barra)
    sbarra_h.name = f"Orizzontale_{i+1}"

# Materiale verde scuro
mat = bpy.data.materials.new(name="Verde_Cancello")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 0.7
bsdf.inputs['Roughness'].default_value = 0.4
bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.15, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello a griglia quadrata creato!")