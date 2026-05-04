import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Mirror dimensions (in meters)
mirror_width = 0.5
mirror_height = 1.4
mirror_thickness = 0.01
frame_width = 0.06
frame_depth = 0.04
base_width = 0.6
base_depth = 0.4
base_height = 0.06
stand_width = 0.045
stand_height = 0.3
tilt_angle = 5  # degrees - slight backward tilt

# Materials
def create_wood_frame_material():
    """Create a walnut frame material"""
    mat = bpy.data.materials.new(name="WalnutFrame")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.15, 0.08, 0.05, 1.0)  # Dark walnut
    node_bsdf.inputs['Roughness'].default_value = 0.3
    node_bsdf.inputs['Metallic'].default_value = 0.0
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_brass_frame_material():
    """Create a brass frame material"""
    mat = bpy.data.materials.new(name="BrassFrame")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.7, 0.5, 0.2, 1.0)  # Brass color
    node_bsdf.inputs['Metallic'].default_value = 0.9
    node_bsdf.inputs['Roughness'].default_value = 0.15
    node_bsdf.inputs['IOR'].default_value = 1.5
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_mirror_material():
    """Create a reflective mirror material"""
    mat = bpy.data.materials.new(name="Mirror")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.03
    node_bsdf.inputs['IOR'].default_value = 1.45
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_base_material():
    """Create material for the base"""
    mat = bpy.data.materials.new(name="Base")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.12, 0.06, 0.04, 1.0)  # Very dark walnut
    node_bsdf.inputs['Roughness'].default_value = 0.4
    node_bsdf.inputs['Metallic'].default_value = 0.0
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
wood_frame_mat = create_wood_frame_material()
brass_frame_mat = create_brass_frame_material()
mirror_mat = create_mirror_material()
base_mat = create_base_material()

# Calculate base position
base_z = base_height / 2

# Calculate stand position (vertical supports on the base)
stand_z = base_height + stand_height / 2

# Calculate mirror assembly center position
# The mirror will be tilted, so we need to calculate its position
mirror_center_z = base_height + stand_height + mirror_height / 2

# Create base
bpy.ops.mesh.primitive_cube_add(size=1)
base = bpy.context.active_object
base.name = "Base"
base.dimensions = (base_width, base_depth, base_height)
base.location = (0, 0, base_z)
base.data.materials.append(base_mat)

# Add bevel to base edges for realism
bpy.ops.object.modifier_add(type='BEVEL')
base.modifiers["Bevel"].width = 0.008
base.modifiers["Bevel"].segments = 4
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create left stand support
bpy.ops.mesh.primitive_cube_add(size=1)
left_stand = bpy.context.active_object
left_stand.name = "Stand_Left"
left_stand.dimensions = (stand_width, stand_width, stand_height)
left_stand.location = (-mirror_width/2 - frame_width/2, 0, stand_z)
left_stand.data.materials.append(wood_frame_mat)

# Create right stand support
bpy.ops.mesh.primitive_cube_add(size=1)
right_stand = bpy.context.active_object
right_stand.name = "Stand_Right"
right_stand.dimensions = (stand_width, stand_width, stand_height)
right_stand.location = (mirror_width/2 + frame_width/2, 0, stand_z)
right_stand.data.materials.append(wood_frame_mat)

# Create mirror surface
bpy.ops.mesh.primitive_cube_add(size=1)
mirror_surface = bpy.context.active_object
mirror_surface.name = "Mirror_Surface"
mirror_surface.dimensions = (mirror_width, mirror_thickness, mirror_height)
mirror_surface.location = (0, 0, mirror_center_z)
mirror_surface.data.materials.append(mirror_mat)

# Apply tilt to mirror
tilt_rad = math.radians(tilt_angle)
mirror_surface.rotation_euler = (tilt_rad, 0, 0)

# Adjust mirror position after tilt (pivot point compensation)
# When tilted, the mirror shifts, so we compensate
y_shift = -mirror_height / 2 * math.sin(tilt_rad)
mirror_surface.location = (0, y_shift, mirror_center_z)

# Create frame pieces with brass material
# Top frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_top = bpy.context.active_object
frame_top.name = "Frame_Top"
frame_top.dimensions = (mirror_width + 2 * frame_width, frame_depth, frame_width)
frame_top.location = (0, 0, mirror_center_z + mirror_height/2 + frame_width/2)
frame_top.rotation_euler = (tilt_rad, 0, 0)
# Adjust position for tilt
y_shift_top = -(mirror_height/2 + frame_width/2) * math.sin(tilt_rad)
frame_top.location = (0, y_shift_top, mirror_center_z + mirror_height/2 + frame_width/2)
frame_top.data.materials.append(brass_frame_mat)

# Bottom frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_bottom = bpy.context.active_object
frame_bottom.name = "Frame_Bottom"
frame_bottom.dimensions = (mirror_width + 2 * frame_width, frame_depth, frame_width)
frame_bottom.location = (0, 0, mirror_center_z - mirror_height/2 - frame_width/2)
frame_bottom.rotation_euler = (tilt_rad, 0, 0)
# Adjust position for tilt
y_shift_bottom = -(-mirror_height/2 - frame_width/2) * math.sin(tilt_rad)
frame_bottom.location = (0, y_shift_bottom, mirror_center_z - mirror_height/2 - frame_width/2)
frame_bottom.data.materials.append(brass_frame_mat)

# Left frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_left = bpy.context.active_object
frame_left.name = "Frame_Left"
frame_left.dimensions = (frame_width, frame_depth, mirror_height)
frame_left.location = (-mirror_width/2 - frame_width/2, 0, mirror_center_z)
frame_left.rotation_euler = (tilt_rad, 0, 0)
# Adjust position for tilt
y_shift_left = 0 * math.sin(tilt_rad)
frame_left.location = (-mirror_width/2 - frame_width/2, y_shift_left, mirror_center_z)
frame_left.data.materials.append(brass_frame_mat)

# Right frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_right = bpy.context.active_object
frame_right.name = "Frame_Right"
frame_right.dimensions = (frame_width, frame_depth, mirror_height)
frame_right.location = (mirror_width/2 + frame_width/2, 0, mirror_center_z)
frame_right.rotation_euler = (tilt_rad, 0, 0)
# Adjust position for tilt
y_shift_right = 0 * math.sin(tilt_rad)
frame_right.location = (mirror_width/2 + frame_width/2, y_shift_right, mirror_center_z)
frame_right.data.materials.append(brass_frame_mat)

# Create connecting bars between stands and frame (optional but adds stability)
# Left connecting bar
bpy.ops.mesh.primitive_cube_add(size=1)
connect_left = bpy.context.active_object
connect_left.name = "Connect_Left"
connect_height = mirror_center_z - mirror_height/2 - (base_height + stand_height)
connect_left.dimensions = (stand_width * 0.7, stand_width * 0.7, connect_height)
connect_left.location = (-mirror_width/2 - frame_width/2, 0, base_height + stand_height + connect_height/2)
connect_left.data.materials.append(wood_frame_mat)

# Right connecting bar
bpy.ops.mesh.primitive_cube_add(size=1)
connect_right = bpy.context.active_object
connect_right.name = "Connect_Right"
connect_right.dimensions = (stand_width * 0.7, stand_width * 0.7, connect_height)
connect_right.location = (mirror_width/2 + frame_width/2, 0, base_height + stand_height + connect_height/2)
connect_right.data.materials.append(wood_frame_mat)

# Add smooth shading to all objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

# Optional: Join frame components
bpy.ops.object.select_all(action='DESELECT')
frame_top.select_set(True)
frame_bottom.select_set(True)
frame_left.select_set(True)
frame_right.select_set(True)
bpy.context.view_layer.objects.active = frame_top
bpy.ops.object.join()
bpy.context.active_object.name = "Frame_Complete"

# Optional: Join stand components
bpy.ops.object.select_all(action='DESELECT')
left_stand.select_set(True)
right_stand.select_set(True)
connect_left.select_set(True)
connect_right.select_set(True)
bpy.context.view_layer.objects.active = left_stand
bpy.ops.object.join()
bpy.context.active_object.name = "Stand_Complete"

# Create collection for organization
collection = bpy.data.collections.new("Vintage_Mirror")
bpy.context.scene.collection.children.link(collection)

# Move all mirror objects to collection
for obj in list(bpy.context.scene.collection.objects):
    if obj.type == 'MESH':
        bpy.context.scene.collection.objects.unlink(obj)
        collection.objects.link(obj)

# Set up camera
camera_distance = 2.8
camera_height = 1.2
bpy.ops.object.camera_add(
    location=(camera_distance * 0.6, -camera_distance * 0.8, camera_height),
    rotation=(math.radians(70), 0, math.radians(40))
)
camera = bpy.context.active_object
camera.data.lens = 55
bpy.context.scene.camera = camera

# Point camera at mirror center
track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = mirror_surface
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
track_constraint.up_axis = 'UP_Y'

# Set up lighting
# Main sunlight from side
bpy.ops.object.light_add(type='SUN', location=(4, -2, 5))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(55), 0, math.radians(35))

# Softer fill light from front
bpy.ops.object.light_add(type='AREA', location=(1, -3.5, 2.5))
area_light = bpy.context.active_object
area_light.data.energy = 180
area_light.data.size = 4.5
area_light.rotation_euler = (math.radians(75), 0, 0)

# Back light for definition
bpy.ops.object.light_add(type='AREA', location=(-1.5, 2.5, 1.8))
back_light = bpy.context.active_object
back_light.data.energy = 100
back_light.data.size = 3.5
back_light.rotation_euler = (math.radians(95), 0, math.radians(170))

# Set render engine to Cycles for realistic reflections
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 300

# Enable transparent background for renders
bpy.context.scene.render.film_transparent = False

# Set background
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.85, 0.85, 0.9, 1.0)
bg_node.inputs['Strength'].default_value = 0.9

print("Vintage mirror created successfully!")
print(f"Mirror dimensions: {mirror_width}m x {mirror_height}m")
print(f"Total height: {base_height + stand_height + mirror_height + frame_width}m")
print(f"Base dimensions: {base_width}m x {base_depth}m")
print(f"Mirror tilt angle: {tilt_angle} degrees")