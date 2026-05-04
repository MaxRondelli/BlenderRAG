import bpy
import math

# -------------------------
# Force Object Mode
# -------------------------
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# -------------------------
# Clear Scene (Safe way)
# -------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Also clear mesh data
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)

# Clear materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

# -------------------------
# Helper Functions
# -------------------------
def make_cube(name, dimensions, location, rotation=(0, 0, 0)):
    """Create cube with actual dimensions instead of scale"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def make_cyl(name, radius, depth, location, rotation=(0, 0, 0)):
    """Create cylinder with proper dimensions"""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    return obj

# -------------------------
# Create Materials
# -------------------------
def create_metallic_material(name, base_color, metallic=0.8, roughness=0.3):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set properties
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Position nodes
    output.location = (300, 0)
    bsdf.location = (0, 0)
    
    return mat

# Create materials
charcoal_mat = create_metallic_material("Charcoal_Metal", (0.15, 0.15, 0.18, 1.0), 0.9, 0.2)
copper_mat = create_metallic_material("Copper_Accent", (0.7, 0.4, 0.2, 1.0), 1.0, 0.1)

# -------------------------
# Base (on ground)
# -------------------------
base = make_cube("Base", (0.12, 0.12, 0.02), (0, 0, 0.01))
base.data.materials.append(charcoal_mat)

# -------------------------
# Vertical Stem (connected to base)
# -------------------------
stem_height = 0.10
stem = make_cyl("Stem", 0.018, stem_height, (0, 0, 0.02 + stem_height/2))
stem.data.materials.append(charcoal_mat)

# -------------------------
# Lower Arm (starts at top of stem, angled upward)
# -------------------------
lower_arm_length = 0.35
lower_arm_angle = 1.1  # radians, about 63 degrees
lower_arm_start_z = 0.02 + stem_height

# Calculate end position of lower arm
lower_arm_center_y = lower_arm_length/2 * math.cos(lower_arm_angle)
lower_arm_center_z = lower_arm_start_z + lower_arm_length/2 * math.sin(lower_arm_angle)

lower_arm = make_cube("LowerArm", (0.020, lower_arm_length, 0.020), 
                      (0, lower_arm_center_y, lower_arm_center_z), 
                      (lower_arm_angle, 0, 0))
lower_arm.data.materials.append(charcoal_mat)

# -------------------------
# Joint (at end of lower arm)
# -------------------------
joint_y = lower_arm_length * math.cos(lower_arm_angle)
joint_z = lower_arm_start_z + lower_arm_length * math.sin(lower_arm_angle)
joint = make_cyl("Joint", 0.022, 0.025, (0, joint_y, joint_z))
joint.data.materials.append(copper_mat)

# -------------------------
# Upper Arm (starts at joint, angled differently)
# -------------------------
upper_arm_length = 0.30
upper_arm_angle = 0.4  # radians, about 23 degrees

# Upper arm center position
upper_arm_center_y = joint_y + upper_arm_length/2 * math.cos(upper_arm_angle)
upper_arm_center_z = joint_z + upper_arm_length/2 * math.sin(upper_arm_angle)

upper_arm = make_cube("UpperArm", (0.020, upper_arm_length, 0.020), 
                      (0, upper_arm_center_y, upper_arm_center_z), 
                      (upper_arm_angle, 0, 0))
upper_arm.data.materials.append(charcoal_mat)

# -------------------------
# Lamp Head (at end of upper arm)
# -------------------------
head_y = joint_y + upper_arm_length * math.cos(upper_arm_angle)
head_z = joint_z + upper_arm_length * math.sin(upper_arm_angle)
head = make_cube("Head", (0.10, 0.07, 0.025), (0, head_y, head_z))
head.data.materials.append(charcoal_mat)

# Add copper accent to head rim
head_rim = make_cube("HeadRim", (0.102, 0.072, 0.008), (0, head_y, head_z - 0.015))
head_rim.data.materials.append(copper_mat)

# -------------------------
# Add Camera for better view
# -------------------------
bpy.ops.object.camera_add(location=(0.8, -0.8, 0.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# -------------------------
# Add Light
# -------------------------
bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
light = bpy.context.active_object
light.data.energy = 3

# -------------------------
# Select all objects to see them
# -------------------------
bpy.ops.object.select_all(action='SELECT')

print("✅ Modern metallic desk lamp created successfully!")
print("💡 Press 'Home' key to frame all objects in view")
print("💡 Press Numpad 0 to see camera view")