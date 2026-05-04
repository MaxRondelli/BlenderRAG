import bpy
import random

# Pulisci
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1)
base = bpy.context.active_object
base.name = "Bush"

for v in base.data.vertices:
    v.co *= random.uniform(0.75, 1.25)

# Foglia
bpy.ops.mesh.primitive_plane_add(size=0.1)
leaf = bpy.context.active_object
leaf.name = "Leaf"

# Materiale ARANCIONE-ROSSO AUTUNNALE
mat = bpy.data.materials.new("AutumnOrange")
mat.use_nodes = True
principled = mat.node_tree.nodes["Principled BSDF"]
principled.inputs['Base Color'].default_value = (0.8, 0.3, 0.1, 1)
principled.inputs['Roughness'].default_value = 0.6
leaf.data.materials.append(mat)

# GEOMETRY NODES per distribuire foglie
base.select_set(True)
bpy.context.view_layer.objects.active = base

# Aggiungi modifier Geometry Nodes
geo_mod = base.modifiers.new(name="Leaves", type='NODES')
node_group = bpy.data.node_groups.new('LeafDistribution', 'GeometryNodeTree')
geo_mod.node_group = node_group

# Crea nodes
nodes = node_group.nodes
links = node_group.links
nodes.clear()

# Input/Output
input_node = nodes.new('NodeGroupInput')
output_node = nodes.new('NodeGroupOutput')
node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Distribute Points
distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
distribute.distribute_method = 'RANDOM'
distribute.inputs['Density'].default_value = 3500

# Instance on Points
instance = nodes.new('GeometryNodeInstanceOnPoints')

# Object Info per la foglia
object_info = nodes.new('GeometryNodeObjectInfo')
object_info.inputs['Object'].default_value = leaf

# Random rotation
random_value = nodes.new('FunctionNodeRandomValue')
random_value.data_type = 'FLOAT_VECTOR'

# Collegamenti
links.new(input_node.outputs[0], distribute.inputs['Mesh'])
links.new(distribute.outputs['Points'], instance.inputs['Points'])
links.new(object_info.outputs['Geometry'], instance.inputs['Instance'])
links.new(random_value.outputs['Value'], instance.inputs['Rotation'])
links.new(instance.outputs['Instances'], output_node.inputs[0])

# Posiziona nodes
input_node.location = (-400, 0)
distribute.location = (-200, 0)
object_info.location = (-200, -150)
random_value.location = (-200, -300)
instance.location = (0, 0)
output_node.location = (200, 0)

# Sun
bpy.ops.object.light_add(type='SUN', location=(5, -3, 8))
sun = bpy.context.active_object
sun.data.energy = 5

# Camera
bpy.ops.object.camera_add(location=(0, -4, 2))
cam = bpy.context.active_object
cam.rotation_euler = (1.2, 0, 0)
bpy.context.scene.camera = cam

# Cycles + Rendered
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'

print("Cespuglio autunnale con Geometry Nodes!")
