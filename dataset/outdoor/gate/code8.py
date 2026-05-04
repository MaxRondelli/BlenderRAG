import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.0
altezza_cancello = 2.0
raggio_palo = 0.08
num_sbarre = 14
raggio_sbarra = 0.02
raggio_traversa = 0.03

# Pali laterali cilindrici
bpy.ops.mesh.primitive_cylinder_add(radius=raggio_palo, depth=altezza_cancello, location=(-larghezza_cancello/2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cylinder_add(radius=raggio_palo, depth=altezza_cancello, location=(larghezza_cancello/2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.name = "Palo_Destro"

# Traverse circolari
for z_height in [0.3, altezza_cancello - 0.2]:
    bpy.ops.mesh.primitive_cylinder_add(radius=raggio_traversa, depth=larghezza_cancello - 2*raggio_palo, location=(0, 0, z_height))
    traversa = bpy.context.active_object
    traversa.rotation_euler[1] = math.pi / 2
    traversa.name = f"Traversa_Z{z_height}"

# Sbarre verticali cilindriche
spaziatura = (larghezza_cancello - 2*raggio_palo) / (num_sbarre + 1)
altezza_sbarra = altezza_cancello - 0.5

for i in range(num_sbarre):
    x_pos = -larghezza_cancello/2 + raggio_palo + spaziatura * (i + 1)
    z_pos = 0.25 + altezza_sbarra/2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=raggio_sbarra, depth=altezza_sbarra, location=(x_pos, 0, z_pos))
    sbarra = bpy.context.active_object
    sbarra.name = f"Sbarra_{i+1}"

# Materiale acciaio inox
mat = bpy.data.materials.new(name="Acciaio_Inox")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.15
bsdf.inputs['Base Color'].default_value = (0.85, 0.85, 0.88, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello con tubi circolari creato!")