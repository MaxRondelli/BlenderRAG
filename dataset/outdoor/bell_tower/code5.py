import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile moderno minimalista
larghezza_base = 2.0
altezza_torre = 15.0
spessore = 0.3

# Torre principale slanciata e sottile
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre/2))
torre = bpy.context.active_object
torre.scale = (larghezza_base, larghezza_base, altezza_torre)
torre.name = "Torre_Moderna"

# Fessure verticali per le campane
num_fessure = 4
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    x = math.cos(rot) * (larghezza_base/2 - 0.05)
    y = math.sin(rot) * (larghezza_base/2 - 0.05)
    
    # Fessura alta e stretta
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, altezza_torre - 3))
    fessura = bpy.context.active_object
    fessura.scale = (0.1, spessore, 4.0)
    fessura.rotation_euler[2] = rot
    fessura.name = f"Fessura_{i+1}"

# Elemento sommitale geometrico (parallelepipedo sfalsato)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre + 0.5))
elemento_top = bpy.context.active_object
elemento_top.scale = (larghezza_base + 0.3, larghezza_base + 0.3, 0.2)
elemento_top.rotation_euler[2] = math.pi/4
elemento_top.name = "Elemento_Sommitale"

# Croce minimalista
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre + 1.0))
croce_v = bpy.context.active_object
croce_v.scale = (0.03, 0.03, 1.0)
croce_v.name = "Croce_Verticale"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_torre + 1.3))
croce_o = bpy.context.active_object
croce_o.scale = (0.5, 0.03, 0.03)
croce_o.name = "Croce_Orizzontale"

# Materiale cemento armato a vista
mat = bpy.data.materials.new(name="Cemento_Moderno")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.55, 0.55, 0.55, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Campanile moderno minimalista creato!")
