import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_willow_tree(trunk_height=6, trunk_radius=0.4, max_depth=6, leaf_count=400):
    """Generate a weeping willow with drooping branches"""
    clear_scene()
    random.seed(202)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="WillowBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.35, 0.3, 0.25, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="WillowLeaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.7, 0.3, 1.0)
    
    def create_branch(base_loc, direction, length, radius, depth, is_drooping=False):
        if depth > max_depth or length < 0.2:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"WillowBranch_D{depth}"
        
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
            num_branches = random.randint(2, 3) if depth < 3 else random.randint(1, 2)
            
            for i in range(num_branches):
                angle_xz = random.uniform(0, 2 * math.pi)
                
                # Willow branches droop down
                if depth > 2 or is_drooping:
                    # Downward angle increases with depth
                    angle_elevation = random.uniform(math.pi * 0.6, math.pi * 0.8)
                    new_drooping = True
                else:
                    angle_elevation = random.uniform(math.pi/5, math.pi/3)
                    new_drooping = False
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                new_length = length * random.uniform(0.7, 0.85)
                new_radius = radius * 0.65
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1, new_drooping)
    
    # Create trunk and branches
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add leaves along drooping branches
    tree_objects = [obj for obj in bpy.context.scene.objects if "WillowBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.2, 0.2),
            random.uniform(-0.2, 0.2),
            random.uniform(-0.4, 0.4)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.12, location=world_pos)
        leaf = bpy.context.active_object
        leaf.scale = (1.5, 0.5, 0.5)
        leaf.name = "WillowLeaf"
        leaf.data.materials.append(leaf_mat)
    
    print("Weeping willow generated!")

create_willow_tree()