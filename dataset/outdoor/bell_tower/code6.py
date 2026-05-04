import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile toscano
larghezza_base = 3.2
altezza_livelli = [5.0, 4.5, 4.0, 3.5]
z_corrente = 0

# Quattro livelli rastremati
for i, altezza in enumerate(altezza_livelli):
    larghezza_livello = larghezza_base - i * 0.3
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_corrente + altezza/2))
    livello = bpy.context.active_object
    livello.scale = (larghezza_livello, larghezza_livello, altezza)
    livello.name = f"Livello_{i+1}"
    
    # Monofore (finestre singole ad arco) 
    if i >= 1:  # A partire dal secondo livello
        for j, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
            x = math.cos(rot) * (larghezza_livello/2 - 0.05)
            y = math.sin(rot) * (larghezza_livello/2 - 0.05)
            
            bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.3, location=(x, y, z_corrente + altezza/2))
            monofora = bpy.context.active_object
            monofora.rotation_euler[1] = math.pi/2
            monofora.rotation_euler[0] = rot
            monofora.name = f"Monofora_L{i+1}_{j+1}"
    
    # Marcapiano (cornice tra i livelli)
    if i < len(altezza_livelli) - 1:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_corrente + altezza))
        cornice = bpy.context.active_object
        cornice.scale = (larghezza_livello + 0.2, larghezza_livello + 0.2, 0.15)
        cornice.name = f"Marcapiano_{i+1}"
    
    z_corrente += altezza

# Tetto a padiglione (piramide con base quadrata)
altezza_tetto = 2.0
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=larghezza_base - 1.2, depth=altezza_tetto, location=(0, 0, z_corrente + altezza_tetto/2))
tetto = bpy.context.active_object
tetto.rotation_euler[2] = math.pi/4
tetto.name = "Tetto_Padiglione"

# Banderuola segnavento
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.6, location=(0, 0, z_corrente + altezza_tetto + 0.3))
asta = bpy.context.active_object
asta.name = "Asta_Segnavento"

bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.2, depth=0.3, location=(0, 0.2, z_corrente + altezza_tetto + 0.6))
freccia = bpy.context.active_object
freccia.rotation_euler[0] = math.pi/2
freccia.name = "Freccia_Vento"

# Materiale pietra serena toscana
mat_pietra = bpy.data.materials.new(name="Pietra_Serena")
mat_pietra.use_nodes = True
nodes = mat_pietra.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.65, 0.62, 0.58, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_tetto = bpy.data.materials.new(name="Coppi_Terracotta")
mat_tetto.use_nodes = True
nodes = mat_tetto.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.4, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.75

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Tetto' in obj.name:
            obj.data.materials.append(mat_tetto)
        else:
            obj.data.materials.append(mat_pietra)

print("Campanile toscano creato!")
