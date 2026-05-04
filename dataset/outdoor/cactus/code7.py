import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create golden barrel cactus - nearly spherical
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.6,
    location=(0, 0, 0.6),
    segments=32,
    ring_count=24
)
barrel = bpy.context.active_object
barrel.name = "GoldenBarrel"
barrel.scale = (1, 1, 0.85)  # Slightly flattened

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode='OBJECT')

# Add deep ridges
mesh = barrel.data
bm = bmesh.new()
bm.from_mesh(mesh)

num_ribs = 21  # Golden barrels have many ribs

for vert in bm.verts:
    x, y, z = vert.co
    
    # Skip top and bottom vertices
    if abs(z) > 0.45:
        continue
    
    angle = math.atan2(y, x)
    
    # Create deep ribs
    rib_pattern = abs(math.sin(angle * num_ribs / 2)) 
    ridge_depth = rib_pattern * 0.12
    
    # Pull vertices inward on valleys, outward on peaks
    factor = 1 - ridge_depth + (rib_pattern * 0.15)
    vert.co.x *= factor
    vert.co.y *= factor

bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Create woolly crown at top
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=0.15,
    location=(0, 0, 1.05)
)
wool = bpy.context.active_object
wool.name = "WoolCrown"
wool.scale = (1.2, 1.2, 0.4)

def create_golden_spine(location, rotation, length=0.08):
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=0.008,
        radius2=0.0003,
        depth=length,
        location=location,
        rotation=rotation
    )
    spine = bpy.context.active_object
    spine.name = "GoldenSpine"
    return spine

# Add VERY dense spines following the ribs
all_spines = []

# Number of vertical rows along each rib
num_vertical_rows = 15

for rib in range(num_ribs):
    angle_base = (rib / num_ribs) * 2 * math.pi
    
    for v_row in range(num_vertical_rows):
        # Vertical position (avoid extreme top/bottom)
        z = -0.35 + (v_row * 0.8 / num_vertical_rows)
        
        # Calculate radius at this height
        height_factor = math.sqrt(max(0, 0.6**2 - z**2))
        
        # Position on the rib
        rib_offset = abs(math.sin(angle_base * num_ribs / 2)) * 0.1
        radius = height_factor * (1 + rib_offset)
        
        x = math.cos(angle_base) * radius
        y = math.sin(angle_base) * radius
        z_world = z + 0.6
        
        # Create cluster of spines at this point
        for cluster in range(4):
            offset_angle = random.uniform(-0.1, 0.1)
            offset_z = random.uniform(-0.02, 0.02)
            
            spine_x = x + math.cos(angle_base + offset_angle) * 0.02
            spine_y = y + math.sin(angle_base + offset_angle) * 0.02
            spine_z = z_world + offset_z
            
            rot_z = angle_base + offset_angle
            rot_y = math.radians(random.uniform(65, 85))
            
            # Vary spine length
            spine_length = random.uniform(0.06, 0.12)
            
            spine = create_golden_spine((spine_x, spine_y, spine_z), (0, rot_y, rot_z), spine_length)
            all_spines.append(spine)

# Add central spines on top
for i in range(20):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(0, 0.15)
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    z = 1.05 + random.uniform(-0.02, 0.05)
    
    rot_z = angle
    rot_y = math.radians(random.uniform(50, 70))
    
    spine = create_golden_spine((x, y, z), (0, rot_y, rot_z), random.uniform(0.08, 0.15))
    all_spines.append(spine)

# Create materials
def create_golden_barrel_material():
    mat = bpy.data.materials.new(name="GoldenBarrelMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 15.0
    
    # Yellow-green barrel color
    color_ramp.color_ramp.elements[0].color = (0.35, 0.42, 0.18, 1)
    color_ramp.color_ramp.elements[1].color = (0.45, 0.50, 0.25, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_golden_spine_material():
    mat = bpy.data.materials.new(name="GoldenSpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Golden yellow spines
    bsdf.inputs['Base Color'].default_value = (0.95, 0.85, 0.45, 1)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_wool_material():
    mat = bpy.data.materials.new(name="WoolMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Yellowish white wool
        bsdf.inputs['Base Color'].default_value = (0.92, 0.88, 0.70, 1)
        bsdf.inputs['Roughness'].default_value = 0.9
    return mat

barrel_mat = create_golden_barrel_material()
spine_mat = create_golden_spine_material()
wool_mat = create_wool_material()

barrel.data.materials.append(barrel_mat)
wool.data.materials.append(wool_mat)

for spine in all_spines:
    spine.data.materials.append(spine_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = [barrel, wool] + all_spines

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = barrel
bpy.ops.object.join()
barrel.name = "GoldenBarrelCactus"

# Create ground
bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.65, 0.55, 0.38, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

# Camera
bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(3, -3, 6))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.data.color = (1.0, 0.98, 0.9)  # Warm sunlight
sun.rotation_euler = (math.radians(45), math.radians(25), 0)

print("Golden Barrel Cactus created successfully!")