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

def create_black_metal_material():
    """Create black metallic material for base"""
    mat = bpy.data.materials.new(name="BlackMetal")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.12, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.2
    return mat

def create_gray_arm_material():
    """Create charcoal gray material for arms"""
    mat = bpy.data.materials.new(name="GrayArm")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.25, 0.25, 0.27, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.6
    bsdf.inputs["Roughness"].default_value = 0.4
    return mat

def create_copper_head_material():
    """Create copper material for lamp head"""
    mat = bpy.data.materials.new(name="CopperHead")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.85, 0.45, 0.25, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3
    return mat

# -------------------------
# Create Materials
# -------------------------
black_metal = create_black_metal_material()
gray_arm = create_gray_arm_material()
copper_head = create_copper_head_material()

# -------------------------
# Base (on ground) - slightly thicker and more rectangular
# -------------------------
base = make_cube("Base", (0.14, 0.10, 0.025), (0, 0, 0.0125))
base.data.materials.append(black_metal)

# -------------------------
# Vertical Stem (connected to base) - slightly thicker
# -------------------------
stem_height = 0.10
stem = make_cyl("Stem", 0.018, stem_height, (0, 0, 0.025 + stem_height/2))
stem.data.materials.append(gray_arm)

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
lower_arm.data.materials.append(gray_arm)

# -------------------------
# Joint (at end of lower arm) - slightly larger
# -------------------------
joint_y = lower_arm_length * math.cos(lower_arm_angle)
joint_z = lower_arm_start_z + lower_arm_length * math.sin(lower_arm_angle)
joint = make_cyl("Joint", 0.021, 0.025, (0, joint_y, joint_z))
joint.data.materials.append(black_metal)

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
upper_arm.data.materials.append(gray_arm)

# -------------------------
# Lamp Head (at end of upper arm) - slightly larger
# -------------------------
head_y = joint_y + upper_arm_length * math.cos(upper_arm_angle)
head_z = joint_z + upper_arm_length * math.sin(upper_arm_angle)
head = make_cube("Head", (0.12, 0.08, 0.03), (0, head_y, head_z))
head.data.materials.append(copper_head)

# -------------------------
# Add Camera for better view
# -------------------------
bpy.ops.object.camera_add(location=(0.9, -0.7, 0.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(50))
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

print("✅ Modern office lamp created successfully with materials!")
print("💡 Press 'Home' key to frame all objects in view")
print("💡 Press Numpad 0 to see camera view")