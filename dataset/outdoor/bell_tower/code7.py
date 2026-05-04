import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile ortodosso russo
larghezza_base = 3.5
altezza_base = 8.0
altezza_tamburo = 3.0

# Base quadrata con archi ciechi
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_base/2))
base = bpy.context.active_object
base.scale = (larghezza_base, larghezza_base, altezza_base)
base.name = "Base_Ortodossa"

# Archi ciechi decorativi sulla base
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    for z_arco in [2.5, 5.0]:
        x = math.cos(rot) * (larghezza_base/2 - 0.05)
        y = math.sin(rot) * (larghezza_base/2 - 0.05)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=(x, y, z_arco))
        arco = bpy.context.active_object
        arco.rotation_euler[1] = math.pi/2
        arco.rotation_euler[0] = rot
        arco.name = f"Arco_Cieco_{i+1}_{z_arco}"

# Tamburo ottagonale (zakomar)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/2.2, depth=altezza_tamburo, location=(0, 0, altezza_base + altezza_tamburo/2))
tamburo = bpy.context.active_object
tamburo.name = "Tamburo_Zakomar"

# Kokoshniki (archi decorativi semicircolari) sulla sommità del tamburo
num_kokoshniki = 8
for i in range(num_kokoshniki):
    angolo = (2 * math.pi / num_kokoshniki) * i
    raggio = larghezza_base/2.2
    x = math.cos(angolo) * (raggio + 0.15)
    y = math.sin(angolo) * (raggio + 0.15)
    z = altezza_base + altezza_tamburo
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(x, y, z))
    kokoshnik = bpy.context.active_object
    kokoshnik.rotation_euler[1] = math.pi/2
    kokoshnik.rotation_euler[0] = angolo
    kokoshnik.name = f"Kokoshnik_{i+1}"

# Cupola a cipolla (луковица)
altezza_cipolla = 3.5
z_cipolla = altezza_base + altezza_tamburo
bpy.ops.mesh.primitive_uv_sphere_add(radius=larghezza_base/3, location=(0, 0, z_cipolla + altezza_cipolla/2.5))
cipolla = bpy.context.active_object
cipolla.scale = (1.0, 1.0, 1.8)
cipolla.name = "Cupola_Cipolla"

# Colletto della cupola
bpy.ops.mesh.primitive_cylinder_add(radius=larghezza_base/6, depth=0.4, location=(0, 0, z_cipolla + altezza_cipolla - 0.2))
colletto = bpy.context.active_object
colletto.name = "Colletto_Cupola"

# Croce ortodossa a tre bracci
z_croce = z_cipolla + altezza_cipolla
# Braccio verticale
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce + 0.5))
croce_v = bpy.context.active_object
croce_v.scale = (0.04, 0.04, 1.0)
croce_v.name = "Croce_Verticale"

# Braccio orizzontale superiore (piccolo)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce + 0.8))
croce_o1 = bpy.context.active_object
croce_o1.scale = (0.3, 0.04, 0.04)
croce_o1.name = "Croce_Orizzontale_Sup"

# Braccio orizzontale principale
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce + 0.5))
croce_o2 = bpy.context.active_object
croce_o2.scale = (0.6, 0.04, 0.04)
croce_o2.name = "Croce_Orizzontale_Principale"

# Braccio obliquo inferiore
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce + 0.25))
croce_obliqua = bpy.context.active_object
croce_obliqua.scale = (0.5, 0.04, 0.04)
croce_obliqua.rotation_euler[1] = math.pi/8
croce_obliqua.name = "Croce_Obliqua"

# Materiale intonaco bianco con cupola dorata
mat_bianco = bpy.data.materials.new(name="Intonaco_Bianco")
mat_bianco.use_nodes = True
nodes = mat_bianco.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.92, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_oro = bpy.data.materials.new(name="Oro_Cupola")
mat_oro.use_nodes = True
nodes = mat_oro.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.9, 0.75, 0.2, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.2

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Cupola' in obj.name or 'Colletto' in obj.name:
            obj.data.materials.append(mat_oro)
        else:
            obj.data.materials.append(mat_bianco)

print("Campanile ortodosso russo creato!")
