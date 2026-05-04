import bpy
import math
import bmesh

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Function to create a material with a specific color
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create shader nodes
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
# Rich burgundy velvet color
fabric_material = create_material("Fabric_Burgundy", (0.55, 0.15, 0.25, 1.0), roughness=0.9)
# Golden brass metal for legs
metal_material = create_material("Metal_Gold", (0.8, 0.65, 0.2, 1.0), roughness=0.1, metallic=0.95)

# ==================== SEAT BASE ====================
# Create the main seat cushion - wider and deeper
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
seat = bpy.context.active_object
seat.name = "Seat_Cushion"
seat.scale = (1.9, 1.9, 0.6)

# Apply scale
bpy.ops.object.transform_apply(scale=True)

# Add tufting details to seat
modifier = seat.modifiers.new(name="Subsurf", type='SUBSURF')
modifier.levels = 4
modifier.render_levels = 4

seat.data.materials.append(fabric_material)

# ==================== BACKREST ====================
# Create curved backrest - this connects directly to the seat
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.7, 1.1))
backrest = bpy.context.active_object
backrest.name = "Backrest"
backrest.scale = (1.4, 0.25, 1.4)

# Rotate backrest to angle it back (connecting at the rear of seat)
backrest.rotation_euler = (math.radians(12), 0, 0)

# Apply transformations
bpy.ops.object.transform_apply(scale=True, rotation=True)

# Enter edit mode to curve the backrest
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=4)
bpy.ops.object.mode_set(mode='OBJECT')

# Add array modifier for tufted segments (vertical divisions)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(backrest.data)
# Add horizontal subdivision for tufting
bpy.ops.mesh.subdivide(number_cuts=3)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subdivision surface for smooth curves
modifier = backrest.modifiers.new(name="Subsurf", type='SUBSURF')
modifier.levels = 4
modifier.render_levels = 4

backrest.data.materials.append(fabric_material)

# ==================== LEFT ARMREST ====================
# Create left armrest that flows from seat to backrest height
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.8, -0.1, 0.8))
left_armrest = bpy.context.active_object
left_armrest.name = "Left_Armrest"
left_armrest.scale = (0.3, 1.1, 0.7)

# Rotate to angle inward slightly
left_armrest.rotation_euler = (math.radians(8), 0, math.radians(-3))

# Apply transformations
bpy.ops.object.transform_apply(scale=True, rotation=True)

# Add subdivisions for tufting
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=3)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subdivision surface
modifier = left_armrest.modifiers.new(name="Subsurf", type='SUBSURF')
modifier.levels = 4
modifier.render_levels = 4

left_armrest.data.materials.append(fabric_material)

# ==================== RIGHT ARMREST ====================
# Mirror for right armrest
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.8, -0.1, 0.8))
right_armrest = bpy.context.active_object
right_armrest.name = "Right_Armrest"
right_armrest.scale = (0.3, 1.1, 0.7)

# Rotate to angle inward slightly (mirrored)
right_armrest.rotation_euler = (math.radians(8), 0, math.radians(3))

# Apply transformations
bpy.ops.object.transform_apply(scale=True, rotation=True)

# Add subdivisions for tufting
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=3)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subdivision surface
modifier = right_armrest.modifiers.new(name="Subsurf", type='SUBSURF')
modifier.levels = 4
modifier.render_levels = 4

right_armrest.data.materials.append(fabric_material)

# ==================== LEGS ====================
# Create 4 angled metal legs - they touch the bottom of the seat
# Front left leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55, location=(-0.6, 0.5, 0.275))
front_left_leg = bpy.context.active_object
front_left_leg.name = "Front_Left_Leg"
# Angle the leg outward
front_left_leg.rotation_euler = (math.radians(-12), 0, math.radians(-18))
front_left_leg.data.materials.append(metal_material)

# Front right leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55, location=(0.6, 0.5, 0.275))
front_right_leg = bpy.context.active_object
front_right_leg.name = "Front_Right_Leg"
front_right_leg.rotation_euler = (math.radians(-12), 0, math.radians(18))
front_right_leg.data.materials.append(metal_material)

# Back left leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55, location=(-0.6, -0.5, 0.275))
back_left_leg = bpy.context.active_object
back_left_leg.name = "Back_Left_Leg"
back_left_leg.rotation_euler = (math.radians(12), 0, math.radians(-18))
back_left_leg.data.materials.append(metal_material)

# Back right leg
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55, location=(0.6, -0.5, 0.275))
back_right_leg = bpy.context.active_object
back_right_leg.name = "Back_Right_Leg"
back_right_leg.rotation_euler = (math.radians(12), 0, math.radians(18))
back_right_leg.data.materials.append(metal_material)

# ==================== CAMERA AND LIGHTING ====================
# Set up camera for a nice view
bpy.ops.object.camera_add(location=(3.5, -3.5, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add area light for fill
bpy.ops.object.light_add(type='AREA', location=(-3, 2, 3))
area_light = bpy.context.active_object
area_light.data.energy = 200
area_light.data.size = 3

# Add rim light
bpy.ops.object.light_add(type='AREA', location=(2, 2, 2))
rim_light = bpy.context.active_object
rim_light.data.energy = 150
rim_light.data.size = 2

# ==================== RENDER SETTINGS ====================
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Set up world background
world = bpy.data.worlds['World']
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)  # Light gray background
bg_node.inputs[1].default_value = 1.0

# ==================== PARENT ALL PARTS ====================
# Create empty for the entire armchair
bpy.ops.object.empty_add(location=(0, 0, 0))
empty = bpy.context.active_object
empty.name = "Burgundy_Armchair"

# Select all armchair parts and parent them
armchair_parts = [obj for obj in bpy.data.objects if obj.type == 'MESH']
for obj in armchair_parts:
    obj.select_set(True)
empty.select_set(True)
bpy.context.view_layer.objects.active = empty
bpy.ops.object.parent_set(type='OBJECT')

# Deselect all
bpy.ops.object.select_all(action='DESELECT')