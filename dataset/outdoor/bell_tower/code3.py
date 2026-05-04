import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile veneziano
larghezza_base = 3.5
altezza_fusto = 10.0
altezza_cella = 3.5
altezza_attico = 1.0

# Fusto principale in mattoni
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_fusto/2))
fusto = bpy.context.active_object
fusto.scale = (larghezza_base, larghezza_base, altezza_fusto)
fusto.name = "Fusto_Veneziano"

# Cella campanaria con grandi arcate
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_fusto + altezza_cella/2))
cella = bpy.context.active_object
cella.scale = (larghezza_base + 0.3, larghezza_base + 0.3, altezza_cella)
cella.name = "Cella_Campanaria"

# Arcate su ogni lato
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    x = math.cos(rot) * (larghezza_base/2 + 0.2)
    y = math.sin(rot) * (larghezza_base/2 + 0.2)
    
    # Grande arco a tutto sesto
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.5, location=(x, y, altezza_fusto + altezza_cella/2))
    arco = bpy.context.active_object
    arco.rotation_euler[1] = math.pi/2
    arco.rotation_euler[0] = rot
    arco.name = f"Arcata_{i+1}"
    
    # Colonnine laterali
    for offset in [-0.6, 0.6]:
        x_col = x + math.cos(rot + math.pi/2) * offset
        y_col = y + math.sin(rot + math.pi/2) * offset
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=altezza_cella, location=(x_col, y_col, altezza_fusto + altezza_cella/2))
        colonna = bpy.context.active_object
        colonna.name = f"Colonna_{i+1}_{offset}"

# Attico decorativo
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_fusto + altezza_cella + altezza_attico/2))
attico = bpy.context.active_object
attico.scale = (larghezza_base + 0.5, larghezza_base + 0.5, altezza_attico)
attico.name = "Attico"

# Cupola a cipolla
altezza_cupola = 2.5
bpy.ops.mesh.primitive_uv_sphere_add(radius=larghezza_base/2.5, location=(0, 0, altezza_fusto + altezza_cella + altezza_attico + altezza_cupola/2))
cupola = bpy.context.active_object
cupola.scale[2] = 1.3
cupola.name = "Cupola_Cipolla"

# Angelo o statua sommitale
bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.3, depth=0.8, location=(0, 0, altezza_fusto + altezza_cella + altezza_attico + altezza_cupola + 0.4))
statua = bpy.context.active_object
statua.name = "Statua_Sommitale"

# Materiale mattoni rossi con dettagli bianchi
mat_mattoni = bpy.data.materials.new(name="Mattoni_Veneziani")
mat_mattoni.use_nodes = True
nodes = mat_mattoni.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.65, 0.35, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_pietra = bpy.data.materials.new(name="Pietra_Bianca")
mat_pietra.use_nodes = True
nodes = mat_pietra.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.9, 0.88, 0.85, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

fusto.data.materials.append(mat_mattoni)
cella.data.materials.append(mat_pietra)
attico.data.materials.append(mat_pietra)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and len(obj.data.materials) == 0:
        obj.data.materials.append(mat_pietra)

print("Campanile veneziano creato!")
