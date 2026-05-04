import bpy
import math

# Pulisci tutto
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_honey_wood_material():
    mat = bpy.data.materials.new("HoneyWood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.3, 1)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

def create_black_metal_material():
    mat = bpy.data.materials.new("BlackMetal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.08, 1)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.15
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    return mat

honey_wood_mat = create_honey_wood_material()
black_metal_mat = create_black_metal_material()

# SEDUTA - 5 listelli più spessi
seat_width = 2.4
seat_depth = 0.6
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, -seat_depth/2 + 0.1 + i*0.14, 0.5)
    )
    slat = bpy.context.active_object
    slat.scale = (seat_width/2, 0.06, 0.05)
    slat.data.materials.append(honey_wood_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    slat.modifiers["Bevel"].width = 0.008
    slat.modifiers["Bevel"].segments = 4

# SCHIENALE - top rail più spesso
bpy.ops.mesh.primitive_cube_add(location=(0, 0.4, 1.1))
top_rail = bpy.context.active_object
top_rail.scale = (seat_width/2, 0.05, 0.06)
top_rail.data.materials.append(honey_wood_mat)
bpy.ops.object.modifier_add(type='BEVEL')
top_rail.modifiers["Bevel"].width = 0.008
top_rail.modifiers["Bevel"].segments = 4

# SCHIENALE - listelli più spessi
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(
        location=(0, 0.35, 0.65 + i*0.13)
    )
    back_slat = bpy.context.active_object
    back_slat.scale = (seat_width/2, 0.035, 0.055)
    back_slat.data.materials.append(honey_wood_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    back_slat.modifiers["Bevel"].width = 0.006
    back_slat.modifiers["Bevel"].segments = 3

# GAMBE - anteriori nere più eleganti
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, -0.2, 0.25))
    leg = bpy.context.active_object
    leg.scale = (0.03, 0.03, 0.25)
    leg.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    leg.modifiers["Bevel"].width = 0.002
    leg.modifiers["Bevel"].segments = 2

# GAMBE - posteriori nere più eleganti
for x in [-seat_width/2 + 0.1, seat_width/2 - 0.1]:
    bpy.ops.mesh.primitive_cube_add(location=(x, 0.35, 0.55))
    leg = bpy.context.active_object
    leg.scale = (0.03, 0.03, 0.55)
    leg.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    leg.modifiers["Bevel"].width = 0.002
    leg.modifiers["Bevel"].segments = 2

# BRACCIOLI - design minimalista con metallo nero
for x_sign in [-1, 1]:
    x_pos = x_sign * (seat_width/2 + 0.08)
    
    bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0.05, 0.75))
    armrest = bpy.context.active_object
    armrest.scale = (0.025, 0.3, 0.025)
    armrest.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    armrest.modifiers["Bevel"].width = 0.003
    armrest.modifiers["Bevel"].segments = 2
    
    # Connessione alla gamba posteriore
    bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0.2, 0.6))
    connector = bpy.context.active_object
    connector.scale = (0.02, 0.02, 0.15)
    connector.data.materials.append(black_metal_mat)
    bpy.ops.object.modifier_add(type='BEVEL')
    connector.modifiers["Bevel"].width = 0.002
    connector.modifiers["Bevel"].segments = 2

# DECORAZIONI SCHIENALE - placche rettangolari minimaliste
for i in range(5):
    x_pos = -0.4 + i * 0.2
    for j in range(2):
        z_pos = 0.75 + j * 0.2
        
        bpy.ops.mesh.primitive_cube_add(
            location=(x_pos, 0.38, z_pos)
        )
        plate = bpy.context.active_object
        plate.scale = (0.04, 0.008, 0.08)
        plate.data.materials.append(black_metal_mat)
        bpy.ops.object.modifier_add(type='BEVEL')
        plate.modifiers["Bevel"].width = 0.002
        plate.modifiers["Bevel"].segments = 2

# ILLUMINAZIONE
bpy.ops.object.light_add(type='SUN', location=(8, -8, 12))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(-5, 3, 5))
area = bpy.context.active_object
area.data.energy = 180
area.data.size = 6

# Luce di riempimento per evidenziare i materiali
bpy.ops.object.light_add(type='AREA', location=(3, -2, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 80
fill_light.data.size = 4

# CAMERA
bpy.ops.object.camera_add(location=(4, -4, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(50))
bpy.context.scene.camera = camera

# RENDER
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.render.film_transparent = True

print("✓ Panca minimalista moderna creata!")