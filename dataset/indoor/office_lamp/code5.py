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

def create_metallic_material(name, base_color, metallic_value, roughness_value):
    """Create a metallic material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic_value
    bsdf.inputs['Roughness'].default_value = roughness_value
    
    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_led_material(name):
    """Create LED emission material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add Emission shader
    emission = nodes.new(type='ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Color'].default_value = (1.0, 0.9, 0.7, 1.0)  # Warm white
    emission.inputs['Strength'].default_value = 3.0
    
    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # Link nodes
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    return mat

# -------------------------
# Create Materials
# -------------------------
metallic_material = create_metallic_material("MetallicGray", (0.2, 0.2, 0.22, 1.0), 0.9, 0.1)
led_material = create_led_material("LEDLight")

# -------------------------
# Base (on ground) - slightly thicker
# -------------------------
base = make_cube("Base", (0.14, 0.14, 0.025), (0, 0, 0.0125))
base.data.materials.append(metallic_material)

# -------------------------
# Vertical Stem (connected to base) - slightly thicker
# -------------------------
stem_height = 0.10
stem = make_cyl("Stem", 0.018, stem_height, (0, 0, 0.025 + stem_height/2))
stem.data.materials.append(metallic_material)

# -------------------------
# Lower Arm (starts at top of stem, angled upward) - thicker
# -------------------------
lower_arm_length = 0.35
lower_arm_angle = 1.1  # radians, about 63 degrees
lower_arm_start_z = 0.025 + stem_height

# Calculate end position of lower arm
lower_arm_center_y = lower_arm_length/2 * math.cos(lower_arm_angle)
lower_arm_center_z = lower_arm_start_z + lower_arm_length/2 * math.sin(lower_arm_angle)

lower_arm = make_cube("LowerArm", (0.018, lower_arm_length, 0.018), 
                      (0, lower_arm_center_y, lower_arm_center_z), 
                      (lower_arm_angle, 0, 0))
lower_arm.data.materials.append(metallic_material)

# -------------------------
# Joint (at end of lower arm) - slightly larger
# -------------------------
joint_y = lower_arm_length * math.cos(lower_arm_angle)
joint_z = lower_arm_start_z + lower_arm_length * math.sin(lower_arm_angle)
joint = make_cyl("Joint", 0.022, 0.025, (0, joint_y, joint_z))
joint.data.materials.append(metallic_material)

# -------------------------
# Upper Arm (starts at joint, angled differently) - thicker
# -------------------------
upper_arm_length = 0.30
upper_arm_angle = 0.4  # radians, about 23 degrees

# Upper arm center position
upper_arm_center_y = joint_y + upper_arm_length/2 * math.cos(upper_arm_angle)
upper_arm_center_z = joint_z + upper_arm_length/2 * math.sin(upper_arm_angle)

upper_arm = make_cube("UpperArm", (0.018, upper_arm_length, 0.018), 
                      (0, upper_arm_center_y, upper_arm_center_z), 
                      (upper_arm_angle, 0, 0))
upper_arm.data.materials.append(metallic_material)

# -------------------------
# Lamp Head (at end of upper arm)
# -------------------------
head_y = joint_y + upper_arm_length * math.cos(upper_arm_angle)
head_z = joint_z + upper_arm_length * math.sin(upper_arm_angle)
head = make_cube("Head", (0.10, 0.07, 0.025), (0, head_y, head_z))
head.data.materials.append(metallic_material)

# -------------------------
# LED Light Panel (inside lamp head)
# -------------------------
led_panel = make_cube("LEDPanel", (0.08, 0.05, 0.005), (0, head_y - 0.032, head_z))
led_panel.data.materials.append(led_material)

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
light.data.energy = 2

# -------------------------
# Select all objects to see them
# -------------------------
bpy.ops.object.select_all(action='SELECT')

print("✅ Modern metallic desk lamp created successfully!")
print("💡 Press 'Home' key to frame all objects in view")
print("💡 Press Numpad 0 to see camera view")