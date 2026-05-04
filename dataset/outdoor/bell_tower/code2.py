import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile gotico
larghezza_base = 2.5
altezza_torre = 12.0
altezza_guglia = 4.0

# Torre principale slanciata
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre/2))
torre = bpy.context.active_object
torre.scale = (larghezza_base, larghezza_base, altezza_torre)
torre.name = "Torre_Gotica"

# Pinnacoli angolari
for i, (x, y) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
    pos_x = x * larghezza_base/2
    pos_y = y * larghezza_base/2
    
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.15, depth=1.5, location=(pos_x, pos_y, altezza_torre + 0.75))
    pinnacolo = bpy.context.active_object
    pinnacolo.name = f"Pinnacolo_{i+1}"

# Finestre ogivali (archi acuti) su ogni lato
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    x = math.cos(rot) * (larghezza_base/2 - 0.05)
    y = math.sin(rot) * (larghezza_base/2 - 0.05)
    
    # Finestra alta e stretta
    for z_offset in [altezza_torre - 3, altezza_torre - 5, altezza_torre - 7]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_offset))
        finestra = bpy.context.active_object
        finestra.scale = (0.15, 0.4, 1.0)
        finestra.rotation_euler[2] = rot
        finestra.name = f"Finestra_Gotica_{i+1}_{z_offset}"

# Guglia centrale ottagonale
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=larghezza_base*0.6, depth=altezza_guglia, location=(0, 0, altezza_torre + altezza_guglia/2))
guglia = bpy.context.active_object
guglia.name = "Guglia_Ottagonale"

# Croce sommitale
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre + altezza_guglia + 0.3))
croce_v = bpy.context.active_object
croce_v.scale = (0.05, 0.05, 0.6)
croce_v.name = "Croce_Verticale"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre + altezza_guglia + 0.4))
croce_o = bpy.context.active_object
croce_o.scale = (0.3, 0.05, 0.05)
croce_o.name = "Croce_Orizzontale"

# Materiale pietra grigia
mat = bpy.data.materials.new(name="Pietra_Gotica")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.45, 0.45, 0.48, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Campanile gotico creato!")
