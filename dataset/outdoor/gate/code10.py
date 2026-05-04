import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.0
altezza_cancello = 2.4
profondita_palo = 0.16
num_sbarre = 11
spessore_sbarra = 0.04
spessore_traversa = 0.06

# Pali laterali con capitelli decorativi
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

# Capitello sinistro
bpy.ops.mesh.primitive_uv_sphere_add(radius=profondita_palo*1.3, location=(-larghezza_cancello/2.2, 0, altezza_cancello + 0.15))
capitello_sx = bpy.context.active_object
capitello_sx.scale[2] = 0.6
capitello_sx.name = "Capitello_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Capitello destro
bpy.ops.mesh.primitive_uv_sphere_add(radius=profondita_palo*1.3, location=(larghezza_cancello/2.2, 0, altezza_cancello + 0.15))
capitello_dx = bpy.context.active_object
capitello_dx.scale[2] = 0.6
capitello_dx.name = "Capitello_Destro"

# Traverse con decorazioni
for z_height in [0.4, altezza_cancello/2.2, altezza_cancello - 0.25]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_height))
    traversa = bpy.context.active_object
    traversa.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
    traversa.name = f"Traversa_Z{z_height}"

# Sbarre verticali con variazione di altezza (ondulate)
spaziatura = (larghezza_cancello - 2*profondita_palo) / (num_sbarre + 1)

for i in range(num_sbarre):
    if i != (num_sbarre -1):
        x_pos = -larghezza_cancello/2.2 + profondita_palo + spaziatura * (i + 1)
        
        # Altezza variabile per creare effetto ondulato
        altezza_sbarra = altezza_cancello
        z_pos = 0.25 + altezza_sbarra/2.2
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
        sbarra = bpy.context.active_object
        sbarra.scale = (spessore_sbarra, spessore_sbarra, altezza_sbarra)
        sbarra.name = f"Sbarra_{i+1}"
        
        # Lance decorative sulle sbarre più alte
        if i % 2 == 0 and i != (num_sbarre-1):
            z_lancia = altezza_cancello +0.25
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=spessore_sbarra*1.8, depth=0.35, location=(x_pos, 0, z_lancia))
            lancia = bpy.context.active_object
            lancia.name = f"Lancia_{i+1}"
            
            # Sfera decorativa sotto la lancia
            bpy.ops.mesh.primitive_uv_sphere_add(radius=spessore_sbarra*1.5, location=(x_pos, 0, altezza_cancello - 0.1))
            sfera = bpy.context.active_object
            sfera.name = f"Sfera_Decorativa_{i+1}"

# Volute decorative centrali (spirali)
num_volute = 3
for i in range(num_volute):
    x_offset = -0.3 + i * 0.3
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.015, location=(x_offset, 0, altezza_cancello/2))
    voluta = bpy.context.active_object
    voluta.rotation_euler[0] = math.pi / 2
    voluta.scale[2] = 0.3
    voluta.name = f"Voluta_{i+1}"



# Materiale ferro battuto con finitura nera opaca
mat = bpy.data.materials.new(name="Ferro_Vittoriano")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 0.7
bsdf.inputs['Roughness'].default_value = 0.6
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello vittoriano elaborato creato!")