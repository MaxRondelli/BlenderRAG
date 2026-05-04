import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile Art Déco
larghezza_base = 3.0
altezza_base = 10.0
num_setback = 4

z_corrente = 0

# Struttura a setback (gradoni rastremati tipici Art Déco)
for i in range(num_setback):
    larghezza = larghezza_base - i * 0.5
    altezza = altezza_base / num_setback - i * 0.3
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_corrente + altezza/2))
    setback = bpy.context.active_object
    setback.scale = (larghezza, larghezza, altezza)
    setback.name = f"Setback_{i+1}"
    
    # Linee verticali decorative (pilastri stilizzati)
    if i < num_setback - 1:
        for j in range(4):
            angolo = (math.pi/2) * j + math.pi/4
            x = math.cos(angolo) * larghezza/2.5
            y = math.sin(angolo) * larghezza/2.5
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_corrente + altezza/2))
            pilastro = bpy.context.active_object
            pilastro.scale = (0.08, 0.08, altezza)
            pilastro.name = f"Pilastro_Decorativo_S{i+1}_{j+1}"
    
    # Fasce orizzontali (elemento Art Déco)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_corrente + altezza - 0.1))
    fascia = bpy.context.active_object
    fascia.scale = (larghezza + 0.1, larghezza + 0.1, 0.15)
    fascia.name = f"Fascia_Orizzontale_{i+1}"
    
    z_corrente += altezza

# Cella campanaria con geometria ottagonale
altezza_cella = 2.5
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/3.5, depth=altezza_cella, location=(0, 0, z_corrente + altezza_cella/2))
cella = bpy.context.active_object
cella.name = "Cella_Campanaria_Ottagonale"

# Aperture verticali geometriche
num_aperture = 8
for i in range(num_aperture):
    angolo = (2 * math.pi / num_aperture) * i
    raggio = larghezza_base/3.5
    x = math.cos(angolo) * (raggio + 0.05)
    y = math.sin(angolo) * (raggio + 0.05)
    z = z_corrente + altezza_cella/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    apertura = bpy.context.active_object
    apertura.scale = (0.1, 0.15, 1.5)
    apertura.rotation_euler[2] = angolo
    apertura.name = f"Apertura_{i+1}"

z_corrente += altezza_cella

# Elemento sommitale a gradoni (ziggurat style)
num_gradoni = 3
for i in range(num_gradoni):
    raggio = (larghezza_base/3) - i * 0.2
    altezza_gradone = 0.3
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=raggio, depth=altezza_gradone, location=(0, 0, z_corrente + altezza_gradone/2))
    gradone = bpy.context.active_object
    gradone.name = f"Gradone_Sommitale_{i+1}"
    
    z_corrente += altezza_gradone

# Antenna o guglia geometrica
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, depth=2.0, location=(0, 0, z_corrente + 1.0))
antenna = bpy.context.active_object
antenna.rotation_euler[2] = math.pi/4
antenna.name = "Antenna_Geometrica"

# Sfera Art Déco sulla punta
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, z_corrente + 2.0))
sfera = bpy.context.active_object
sfera.name = "Sfera_Decorativa"

# Elementi a raggio (sunburst) tipici Art Déco
num_raggi = 8
for i in range(num_raggi):
    angolo = (2 * math.pi / num_raggi) * i
    x = math.cos(angolo) * 0.3
    y = math.sin(angolo) * 0.3
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_corrente + 2.0))
    raggio = bpy.context.active_object
    raggio.scale = (0.5, 0.02, 0.02)
    raggio.rotation_euler[2] = angolo
    raggio.name = f"Raggio_Sunburst_{i+1}"

# Materiale: combinazione di calcestruzzo chiaro e accenti metallici dorati
mat_calcestruzzo = bpy.data.materials.new(name="Calcestruzzo_ArtDeco")
mat_calcestruzzo.use_nodes = True
nodes = mat_calcestruzzo.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.85, 0.83, 0.78, 1.0)
bsdf.inputs['Roughness'].default_value = 0.65

mat_ottone = bpy.data.materials.new(name="Ottone_Decorativo")
mat_ottone.use_nodes = True
nodes = mat_ottone.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.8, 0.65, 0.3, 1.0)
bsdf.inputs['Metallic'].default_value = 0.85
bsdf.inputs['Roughness'].default_value = 0.3

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Fascia' in obj.name or 'Pilastro' in obj.name or 'Raggio' in obj.name or 'Sfera' in obj.name:
            obj.data.materials.append(mat_ottone)
        else:
            obj.data.materials.append(mat_calcestruzzo)

print("Campanile Art Déco creato!")
