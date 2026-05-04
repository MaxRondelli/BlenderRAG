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
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

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
    """Create metallic material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic_value
    bsdf.inputs["Roughness"].default_value = roughness_value
    return mat

def create_textured_material(name, base_color):
    """Create textured material with noise"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    bsdf = nodes["Principled BSDF"]
    
    # Add noise texture
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs["Scale"].default_value = 15.0
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.5
    
    # Add ColorRamp
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = base_color
    ramp.color_ramp.elements[1].color = (base_color[0] * 1.2, base_color[1] * 1.2, base_color[2] * 1.2, 1.0)
    
    # Connect nodes
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3
    
    return mat

# -------------------------
# Create Materials
# -------------------------
base_material = create_metallic_material("BaseMetal", (0.2, 0.2, 0.25, 1.0), 0.9, 0.2)
arm_material = create_metallic_material("ArmMetal", (0.15, 0.15, 0.2, 1.0), 0.8, 0.25)
head_material = create_textured_material("HeadMaterial", (0.3, 0.3, 0.35, 1.0))

# -------------------------
# Base (on ground) - slightly larger
# -------------------------
base = make_cube("Base", (0.14, 0.14, 0.025), (0, 0, 0.0125))
base.data.materials.append(base_material)

# -------------------------
# Vertical Stem (connected to base) - thicker
# -------------------------
stem_height = 0.10
stem = make_cyl("Stem", 0.02, stem_height, (0, 0, 0.025 + stem_height/2))
stem.data.materials.append(arm_material)

# -------------------------
# Lower Arm (starts at top of stem, angled upward) - thicker
# -------------------------
lower_arm_length = 0.35
lower_arm_angle = 1.1  # radians, about 63 degrees
lower_arm_start_z = 0.025 + stem_height

# Calculate end position of lower arm
lower_arm_center_y = lower_arm_length/2 * math.cos(lower_arm_angle)
lower_arm_center_z = lower_arm_start_z + lower_arm_length/2 * math.sin(lower_arm_angle)

lower_arm = make_cube("LowerArm", (0.02, lower_arm_length, 0.02), 
                      (0, lower_arm_center_y, lower_arm_center_z), 
                      (lower_arm_angle, 0, 0))
lower_arm.data.materials.append(arm_material)

# -------------------------
# Joint (at end of lower arm) - slightly larger
# -------------------------
joint_y = lower_arm_length * math.cos(lower_arm_angle)
joint_z = lower_arm_start_z + lower_arm_length * math.sin(lower_arm_angle)
joint = make_cyl("Joint", 0.022, 0.025, (0, joint_y, joint_z))
joint.data.materials.append(base_material)

# -------------------------
# Upper Arm (starts at joint, angled differently) - thicker
# -------------------------
upper_arm_length = 0.30
upper_arm_angle = 0.4  # radians, about 23 degrees

# Upper arm center position
upper_arm_center_y = joint_y + upper_arm_length/2 * math.cos(upper_arm_angle)
upper_arm_center_z = joint_z + upper_arm_length/2 * math.sin(upper_arm_angle)

upper_arm = make_cube("UpperArm", (0.02, upper_arm_length, 0.02), 
                      (0, upper_arm_center_y, upper_arm_center_z), 
                      (upper_arm_angle, 0, 0))
upper_arm.data.materials.append(arm_material)

# -------------------------
# Lamp Head (at end of upper arm) - larger and more rectangular
# -------------------------
head_y = joint_y + upper_arm_length * math.cos(upper_arm_angle)
head_z = joint_z + upper_arm_length * math.sin(upper_arm_angle)
head = make_cube("Head", (0.12, 0.085, 0.035), (0, head_y, head_z))
head.data.materials.append(head_material)

# -------------------------
# Add Camera for better view
# -------------------------
bpy.ops.object.camera_add(location=(0.9, -0.9, 0.7))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(50))
bpy.context.scene.camera = camera

# -------------------------
# Add Light
# -------------------------
bpy.ops.object.light_add(type='SUN', location=(3, -3, 6))
light = bpy.context.active_object
light.data.energy = 3

# -------------------------
# Select all objects to see them
# -------------------------
bpy.ops.object.select_all(action='SELECT')

print("✅ Modern metallic desk lamp created successfully!")
print("💡 Press 'Home' key to frame all objects in view")
print("💡 Press Numpad 0 to see camera view")