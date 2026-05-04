import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.0
altezza_cancello = 2.0
profondita_palo = 0.15
num_sbarre = 10
spessore_sbarra = 0.05
spessore_traversa = 0.06
altezza_punta = 0.25

# Pali laterali
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Traverse
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_cancello - spessore_traversa/2))
traversa_sup = bpy.context.active_object
traversa_sup.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
traversa_sup.name = "Traversa_Superiore"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
traversa_inf = bpy.context.active_object
traversa_inf.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
traversa_inf.name = "Traversa_Inferiore"

# Sbarre verticali con punte
spaziatura = (larghezza_cancello - 2*profondita_palo) / (num_sbarre + 1)
altezza_sbarra = altezza_cancello - 0.4 - spessore_traversa

for i in range(num_sbarre):
    x_pos = -larghezza_cancello/2 + profondita_palo + spaziatura * (i + 1)
    z_pos = 0.4 + spessore_traversa/2 + altezza_sbarra/2
    
    # Sbarra
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
    sbarra = bpy.context.active_object
    sbarra.scale = (spessore_sbarra, spessore_sbarra, altezza_sbarra)
    sbarra.name = f"Sbarra_{i+1}"
    
    # Punta decorativa
    z_punta = altezza_cancello + altezza_punta/2
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=spessore_sbarra*1.5, depth=altezza_punta, location=(x_pos, 0, z_punta))
    punta = bpy.context.active_object
    punta.name = f"Punta_{i+1}"

# Materiale ferro battuto
mat = bpy.data.materials.new(name="Ferro_Battuto")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.5
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello con decorazioni a punta creato!")