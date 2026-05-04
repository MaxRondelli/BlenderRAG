import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_simple_tree(trunk_height=5, trunk_radius=0.3, max_depth=4, leaf_count=200):
    """Generate a simple, clean tree with basic structure"""
    clear_scene()
    random.seed(1414)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="Bark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="Leaves")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.2, 0.6, 0.2, 1.0)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.4:
            return
        
        # Create simple cylinder for branch
        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=length,
            location=base_loc + direction * (length / 2)
        )
        
        branch = bpy.context.active_object
        branch.name = f"Branch_D{depth}"
        
        # Rotate to align with direction
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
        
        # Create child branches
        if depth < max_depth:
            num_branches = 3 if depth < 2 else 2
            
            for i in range(num_branches):
                angle = (2 * math.pi * i / num_branches) + random.uniform(-0.3, 0.3)
                elevation = random.uniform(math.pi/4, math.pi/3)
                
                new_dir = Vector((
                    math.sin(elevation) * math.cos(angle),
                    math.sin(elevation) * math.sin(angle),
                    math.cos(elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                new_length = length * 0.7
                new_radius = radius * 0.7
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create trunk
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add simple spherical leaves
    tree_objects = [obj for obj in bpy.context.scene.objects if "Branch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            random.uniform(0, 0.5)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.2,
            location=world_pos
        )
        
        leaf = bpy.context.active_object
        leaf.name = "Leaf"
        leaf.data.materials.append(leaf_mat)
    
    print("Simple tree generated!")

create_simple_tree()