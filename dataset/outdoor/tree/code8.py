import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_cypress_tree(trunk_height=10, trunk_radius=0.25, max_depth=5, leaf_count=350):
    """Generate a tall, narrow cypress tree"""
    clear_scene()
    random.seed(808)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="CypressBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.28, 0.2, 0.15, 1.0)
    
    foliage_mat = bpy.data.materials.new(name="CypressFoliage")
    foliage_mat.use_nodes = True
    foliage_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.08, 0.35, 0.12, 1.0)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.3:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"CypressBranch_D{depth}"
        
        up = Vector((0, 0, 1))
        if direction.length > 0:
            direction_normalized = direction.normalized()
            rotation_axis = up.cross(direction_normalized)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(direction_normalized))))
                branch.rotation_mode = 'AXIS_ANGLE'
                branch.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
        
        branch.data.materials.append(bark_mat)
        
        end_loc = base_loc + direction * length
        
        if depth < max_depth:
            # Cypress: short, upward branches close to trunk
            height_ratio = end_loc.z / trunk_height
            num_branches = random.randint(3, 5) if depth < 2 else random.randint(2, 3)
            
            for i in range(num_branches):
                angle_xz = (2 * math.pi * i / num_branches) + random.uniform(-0.2, 0.2)
                
                # Very upward pointing, shorter at top
                base_elevation = math.pi/8 if depth == 0 else math.pi/5
                angle_elevation = base_elevation * (1 + height_ratio * 0.5)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                # Short branches, narrower at top
                new_length = length * random.uniform(0.4, 0.55) * (1 - height_ratio * 0.4)
                new_radius = radius * 0.65
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create tall trunk
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add dense, compact foliage
    tree_objects = [obj for obj in bpy.context.scene.objects if "CypressBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        # Keep foliage close to branches for columnar shape
        local_pos = Vector((
            random.uniform(-0.2, 0.2),
            random.uniform(-0.2, 0.2),
            random.uniform(0, 0.4)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        # Small, dense foliage clumps
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.12, location=world_pos)
        foliage = bpy.context.active_object
        foliage.scale = (0.8, 0.8, 1.2)
        foliage.name = "CypressFoliage"
        foliage.data.materials.append(foliage_mat)
    
    # Add extra foliage along trunk for columnar appearance
    for i in range(80):
        height = random.uniform(trunk_height * 0.2, trunk_height * 0.95)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.15, 0.35)
        
        pos = Vector((
            math.cos(angle) * distance,
            math.sin(angle) * distance,
            height
        ))
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15, location=pos)
        foliage = bpy.context.active_object
        foliage.scale = (0.7, 0.7, 1.5)
        foliage.name = "CypressFoliage"
        foliage.data.materials.append(foliage_mat)
    
    print("Cypress tree generated!")

create_cypress_tree()