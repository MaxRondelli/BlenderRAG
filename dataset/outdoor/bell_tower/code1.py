import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile romanico
larghezza_base = 3.0
altezza_base = 8.0
altezza_cella = 3.0
spessore_muro = 0.3

# Base quadrata massiccia
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_base/2))
base = bpy.context.active_object
base.scale = (larghezza_base, larghezza_base, altezza_base)
base.name = "Base_Romanica"

# Cella campanaria con bifore
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_base + altezza_cella/2))
cella = bpy.context.active_object
cella.scale = (larghezza_base - 0.2, larghezza_base - 0.2, altezza_cella)
cella.name = "Cella_Campanaria"

# Bifore (finestre gemelle ad arco) su ogni lato
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    x = math.cos(rot) * (larghezza_base/2 - 0.1)
    y = math.sin(rot) * (larghezza_base/2 - 0.1)
    
    # Arco bifora
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.4, location=(x, y, altezza_base + altezza_cella/2))
    arco = bpy.context.active_object
    arco.rotation_euler[1] = math.pi/2
    arco.rotation_euler[0] = rot
    arco.name = f"Bifora_{i+1}"

# Tetto a piramide
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=larghezza_base*0.7, depth=2.0, location=(0, 0, altezza_base + altezza_cella + 1.0))
tetto = bpy.context.active_object
tetto.rotation_euler[2] = math.pi/4
tetto.name = "Tetto_Piramidale"

# Materiale pietra chiara
mat = bpy.data.materials.new(name="Pietra_Romanica")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.85, 0.82, 0.75, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Campanile romanico creato!")
