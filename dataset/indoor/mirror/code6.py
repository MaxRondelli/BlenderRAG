import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Mirror dimensions (in meters)
mirror_width = 0.5
mirror_height = 1.4
mirror_thickness = 0.01
frame_width = 0.08  # Thicker ornate frame
frame_depth = 0.05  # Deeper frame
base_width = 0.6
base_depth = 0.4
base_height = 0.06  # Slightly taller base
stand_width = 0.04
stand_height = 0.3
tilt_angle = 0  # degrees - slight backward tilt

# Materials
def create_ornate_wood_frame_material():
    """Create an ornate carved wooden frame material"""
    mat = bpy.data.materials.new(name="OrnateWoodFrame")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add texture coordinate and mapping nodes for wood grain
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    
    # Wood grain texture using noise
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Color ramp for wood grain
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-200, 100)
    ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1.0)  # Dark mahogany
    ramp.color_ramp.elements[1].color = (0.4, 0.25, 0.15, 1.0)   # Light mahogany
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.6
    node_bsdf.inputs['IOR'].default_value = 1.4
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    # Link nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_vintage_mirror_material():
    """Create a vintage mirror material with slight aging"""
    mat = bpy.data.materials.new(name="VintageMirror")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.85, 1.0)  # Slightly yellowed
    node_bsdf.inputs['Metallic'].default_value = 1.0
    node_bsdf.inputs['Roughness'].default_value = 0.08  # Slightly less perfect
    node_bsdf.inputs['IOR'].default_value = 1.45
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_antique_base_material():
    """Create material for the antique base"""
    mat = bpy.data.materials.new(name="AntiqueBase")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.18, 0.12, 0.08, 1.0)  # Rich dark wood
    node_bsdf.inputs['Roughness'].default_value = 0.7
    node_bsdf.inputs['IOR'].default_value = 1.3
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_brass_accent_material():
    """Create brass material for corner accents"""
    mat = bpy.data.materials.new(name="BrassAccent")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.2, 1.0)  # Antique brass
    node_bsdf.inputs['Metallic'].default_value = 0.9
    node_bsdf.inputs['Roughness'].default_value = 0.3
    node_bsdf.inputs['IOR'].default_value = 1.5
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
ornate_wood_mat = create_ornate_wood_frame_material()
vintage_mirror_mat = create_vintage_mirror_material()
antique_base_mat = create_antique_base_material()
brass_accent_mat = create_brass_accent_material()

# Calculate base position
base_z = base_height / 2

# Calculate stand position (vertical supports on the base)
stand_z = base_height + stand_height / 2

# Calculate mirror assembly center position
mirror_center_z = base_height + stand_height + mirror_height / 2

# Create ornate base with curved edges
bpy.ops.mesh.primitive_cube_add(size=1)
base = bpy.context.active_object
base.name = "OrnateBbase"
base.dimensions = (base_width, base_depth, base_height)
base.location = (0, 0, base_z)
base.data.materials.append(antique_base_mat)

# Add more pronounced bevel to base
bpy.ops.object.modifier_add(type='BEVEL')
base.modifiers["Bevel"].width = 0.012
base.modifiers["Bevel"].segments = 5
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create left stand support
bpy.ops.mesh.primitive_cube_add(size=1)
left_stand = bpy.context.active_object
left_stand.name = "Stand_Left"
left_stand.dimensions = (stand_width, stand_width, stand_height)
left_stand.location = (-mirror_width/2 - frame_width/2, 0, stand_z)
left_stand.data.materials.append(ornate_wood_mat)

# Create right stand support
bpy.ops.mesh.primitive_cube_add(size=1)
right_stand = bpy.context.active_object
right_stand.name = "Stand_Right"
right_stand.dimensions = (stand_width, stand_width, stand_height)
right_stand.location = (mirror_width/2 + frame_width/2, 0, stand_z)
right_stand.data.materials.append(ornate_wood_mat)

# Create mirror surface
bpy.ops.mesh.primitive_cube_add(size=1)
mirror_surface = bpy.context.active_object
mirror_surface.name = "Mirror_Surface"
mirror_surface.dimensions = (mirror_width, mirror_thickness, mirror_height)
mirror_surface.location = (0, 0, mirror_center_z)
mirror_surface.data.materials.append(vintage_mirror_mat)

# Apply tilt to mirror
tilt_rad = math.radians(tilt_angle)
mirror_surface.rotation_euler = (tilt_rad, 0, 0)

# Adjust mirror position after tilt
y_shift = -mirror_height / 2 * math.sin(tilt_rad)
mirror_surface.location = (0, y_shift, mirror_center_z)

# Create ornate frame pieces with decorative elements
# Top frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_top = bpy.context.active_object
frame_top.name = "Frame_Top"
frame_top.dimensions = (mirror_width + 2 * frame_width, frame_depth, frame_width)
frame_top.location = (0, 0, mirror_center_z + mirror_height/2 + frame_width/2)
frame_top.rotation_euler = (tilt_rad, 0, 0)
y_shift_top = -(mirror_height/2 + frame_width/2) * math.sin(tilt_rad)
frame_top.location = (0, y_shift_top, mirror_center_z + mirror_height/2 + frame_width/2)
frame_top.data.materials.append(ornate_wood_mat)

# Add bevel for carved look
bpy.ops.object.modifier_add(type='BEVEL')
frame_top.modifiers["Bevel"].width = 0.008
frame_top.modifiers["Bevel"].segments = 4
bpy.ops.object.modifier_apply(modifier="Bevel")

# Bottom frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_bottom = bpy.context.active_object
frame_bottom.name = "Frame_Bottom"
frame_bottom.dimensions = (mirror_width + 2 * frame_width, frame_depth, frame_width)
frame_bottom.location = (0, 0, mirror_center_z - mirror_height/2 - frame_width/2)
frame_bottom.rotation_euler = (tilt_rad, 0, 0)
y_shift_bottom = -(-mirror_height/2 - frame_width/2) * math.sin(tilt_rad)
frame_bottom.location = (0, y_shift_bottom, mirror_center_z - mirror_height/2 - frame_width/2)
frame_bottom.data.materials.append(ornate_wood_mat)

# Add bevel for carved look
bpy.ops.object.modifier_add(type='BEVEL')
frame_bottom.modifiers["Bevel"].width = 0.008
frame_bottom.modifiers["Bevel"].segments = 4
bpy.ops.object.modifier_apply(modifier="Bevel")

# Left frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_left = bpy.context.active_object
frame_left.name = "Frame_Left"
frame_left.dimensions = (frame_width, frame_depth, mirror_height)
frame_left.location = (-mirror_width/2 - frame_width/2, 0, mirror_center_z)
frame_left.rotation_euler = (tilt_rad, 0, 0)
y_shift_left = 0 * math.sin(tilt_rad)
frame_left.location = (-mirror_width/2 - frame_width/2, y_shift_left, mirror_center_z)
frame_left.data.materials.append(ornate_wood_mat)

# Add bevel for carved look
bpy.ops.object.modifier_add(type='BEVEL')
frame_left.modifiers["Bevel"].width = 0.008
frame_left.modifiers["Bevel"].segments = 4
bpy.ops.object.modifier_apply(modifier="Bevel")

# Right frame
bpy.ops.mesh.primitive_cube_add(size=1)
frame_right = bpy.context.active_object
frame_right.name = "Frame_Right"
frame_right.dimensions = (frame_width, frame_depth, mirror_height)
frame_right.location = (mirror_width/2 + frame_width/2, 0, mirror_center_z)
frame_right.rotation_euler = (tilt_rad, 0, 0)
y_shift_right = 0 * math.sin(tilt_rad)
frame_right.location = (mirror_width/2 + frame_width/2, y_shift_right, mirror_center_z)
frame_right.data.materials.append(ornate_wood_mat)

# Add bevel for carved look
bpy.ops.object.modifier_add(type='BEVEL')
frame_right.modifiers["Bevel"].width = 0.008
frame_right.modifiers["Bevel"].segments = 4
bpy.ops.object.modifier_apply(modifier="Bevel")

# Create brass corner accents
accent_size = 0.02
# Top-left corner accent
bpy.ops.mesh.primitive_cube_add(size=1)
accent_tl = bpy.context.active_object
accent_tl.name = "Accent_TopLeft"
accent_tl.dimensions = (accent_size, accent_size, accent_size)
accent_tl.location = (-mirror_width/2 - frame_width/2, 0, mirror_center_z + mirror_height/2 + frame_width/2)
accent_tl.data.materials.append(brass_accent_mat)

# Top-right corner accent
bpy.ops.mesh.primitive_cube_add(size=1)
accent_tr = bpy.context.active_object
accent_tr.name = "Accent_TopRight"
accent_tr.dimensions = (accent_size, accent_size, accent_size)
accent_tr.location = (mirror_width/2 + frame_width/2, 0, mirror_center_z + mirror_height/2 + frame_width/2)
accent_tr.data.materials.append(brass_accent_mat)

# Bottom-left corner accent
bpy.ops.mesh.primitive_cube_add(size=1)
accent_bl = bpy.context.active_object
accent_bl.name = "Accent_BottomLeft"
accent_bl.dimensions = (accent_size, accent_size, accent_size)
accent_bl.location = (-mirror_width/2 - frame_width/2, 0, mirror_center_z - mirror_height/2 - frame_width/2)
accent_bl.data.materials.append(brass_accent_mat)

# Bottom-right corner accent
bpy.ops.mesh.primitive_cube_add(size=1)
accent_br = bpy.context.active_object
accent_br.name = "Accent_BottomRight"
accent_br.dimensions = (accent_size, accent_size, accent_size)
accent_br.location = (mirror_width/2 + frame_width/2, 0, mirror_center_z - mirror_height/2 - frame_width/2)
accent_br.data.materials.append(brass_accent_mat)

# Create connecting bars
connect_height = mirror_center_z - mirror_height/2 - (base_height + stand_height)

# Left connecting bar
bpy.ops.mesh.primitive_cube_add(size=1)
connect_left = bpy.context.active_object
connect_left.name = "Connect_Left"
connect_left.dimensions = (stand_width * 0.6, stand_width * 0.6, connect_height)
connect_left.location = (-mirror_width/2 - frame_width/2, 0, base_height + stand_height + connect_height/2)
connect_left.data.materials.append(ornate_wood_mat)

# Right connecting bar
bpy.ops.mesh.primitive_cube_add(size=1)
connect_right = bpy.context.active_object
connect_right.name = "Connect_Right"
connect_right.dimensions = (stand_width * 0.6, stand_width * 0.6, connect_height)
connect_right.location = (mirror_width/2 + frame_width/2, 0, base_height + stand_height + connect_height/2)
connect_right.data.materials.append(ornate_wood_mat)

# Add smooth shading to all objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

# Join frame components
bpy.ops.object.select_all(action='DESELECT')
frame_top.select_set(True)
frame_bottom.select_set(True)
frame_left.select_set(True)
frame_right.select_set(True)
bpy.context.view_layer.objects.active = frame_top
bpy.ops.object.join()
bpy.context.active_object.name = "Frame_Complete"

# Join brass accents
bpy.ops.object.select_all(action='DESELECT')
accent_tl.select_set(True)
accent_tr.select_set(True)
accent_bl.select_set(True)
accent_br.select_set(True)
bpy.context.view_layer.objects.active = accent_tl
bpy.ops.object.join()
bpy.context.active_object.name = "Brass_Accents"

# Join stand components
bpy.ops.object.select_all(action='DESELECT')
left_stand.select_set(True)
right_stand.select_set(True)
connect_left.select_set(True)
connect_right.select_set(True)
bpy.context.view_layer.objects.active = left_stand
bpy.ops.object.join()
bpy.context.active_object.name = "Stand_Complete"

# Create collection
collection = bpy.data.collections.new("Vintage_Mirror")
bpy.context.scene.collection.children.link(collection)

# Move objects to collection
for obj in list(bpy.context.scene.collection.objects):
    if obj.type == 'MESH':
        bpy.context.scene.collection.objects.unlink(obj)
        collection.objects.link(obj)

# Set up camera
camera_distance = 2.8
camera_height = 1.2
bpy.ops.object.camera_add(
    location=(camera_distance * 0.8, -camera_distance * 0.6, camera_height),
    rotation=(math.radians(70), 0, math.radians(50))
)
camera = bpy.context.active_object
camera.data.lens = 55
bpy.context.scene.camera = camera

# Point camera at mirror
track_constraint = camera.constraints.new(type='TRACK_TO')
track_constraint.target = mirror_surface
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
track_constraint.up_axis = 'UP_Y'

# Enhanced lighting setup
# Main sunlight
bpy.ops.object.light_add(type='SUN', location=(3, -2, 4))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(55), 0, math.radians(25))

# Warm area light for wood details
bpy.ops.object.light_add(type='AREA', location=(1, -3, 2))
area_light = bpy.context.active_object
area_light.data.energy = 180
area_light.data.size = 3.5
area_light.data.color = (1.0, 0.9, 0.7)
area_light.rotation_euler = (math.radians(75), 0, 0)

# Accent light for brass details
bpy.ops.object.light_add(type='SPOT', location=(-2, 1, 2.5))
spot_light = bpy.context.active_object
spot_light.data.energy = 120
spot_light.data.color = (1.0, 0.85, 0.6)
spot_light.data.spot_size = math.radians(60)
spot_light.rotation_euler = (math.radians(110), 0, math.radians(200))

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 300

# Warm background
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (0.95, 0.92, 0.88, 1.0)
bg_node.inputs['Strength'].default_value = 0.6

print("Ornate vintage standing mirror created successfully!")
print(f"Mirror dimensions: {mirror_width}m x {mirror_height}m")
print(f"Frame width: {frame_width}m (ornate style)")
print("Features: Carved wood frame, brass corner accents, vintage patina")