import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_autumn_tree(trunk_height=5.5, trunk_radius=0.35, max_depth=5, leaf_count=400):
    """Generate a tree with autumn foliage colors"""
    clear_scene()
    random.seed(909)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="AutumnBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.32, 0.25, 0.18, 1.0)
    
    # Multiple autumn colors
    autumn_colors = [
        (0.9, 0.5, 0.1, 1.0),   # Orange
        (0.95, 0.3, 0.1, 1.0),  # Red-orange
        (0.8, 0.2, 0.15, 1.0),  # Deep red
        (0.95, 0.8, 0.2, 1.0),  # Yellow
        (0.85, 0.6, 0.15, 1.0), # Gold
        (0.6, 0.3, 0.1, 1.0),   # Brown
    ]
    
    leaf_materials = []
    for i, color in enumerate(autumn_colors):
        mat = bpy.data.materials.new(name=f"AutumnLeaf_{i}")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = color
        mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.7
        leaf_materials.append(mat)
    
    def create_branch(base_loc, direction, length, radius, depth):
        if depth > max_depth or length < 0.35:
            return
        
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                            location=base_loc + direction * (length / 2))
        branch = bpy.context.active_object
        branch.name = f"AutumnBranch_D{depth}"
        
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
            # Natural spreading branches
            num_branches = random.randint(3, 4) if depth < 2 else random.randint(2, 3)
            
            for i in range(num_branches):
                angle_xz = (2 * math.pi * i / num_branches) + random.uniform(-0.4, 0.4)
                angle_elevation = random.uniform(math.pi/5, math.pi/2.8)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                new_length = length * random.uniform(0.6, 0.75)
                new_radius = radius * 0.72
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
    
    # Create trunk
    create_branch(Vector((0, 0, 0)), Vector((0, 0, 1)), trunk_height, trunk_radius, 0)
    
    # Add colorful autumn leaves
    tree_objects = [obj for obj in bpy.context.scene.objects if "AutumnBranch" in obj.name]
    
    for _ in range(leaf_count):
        if not tree_objects:
            continue
        branch = random.choice(tree_objects)
        
        local_pos = Vector((
            random.uniform(-0.4, 0.4),
            random.uniform(-0.4, 0.4),
            random.uniform(-0.2, 0.4)
        ))
        world_pos = branch.matrix_world @ local_pos
        
        # Random autumn color
        leaf_mat = random.choice(leaf_materials)
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, 
                                               radius=random.uniform(0.15, 0.25), 
                                               location=world_pos)
        leaf = bpy.context.active_object
        leaf.name = "AutumnLeaf"
        leaf.data.materials.append(leaf_mat)
        leaf.rotation_euler = (random.uniform(0, 2*math.pi), 
                               random.uniform(0, 2*math.pi), 
                               random.uniform(0, 2*math.pi))
    
    # Add some fallen leaves on ground
    for _ in range(50):
        pos = Vector((
            random.uniform(-3, 3),
            random.uniform(-3, 3),
            random.uniform(0, 0.1)
        ))
        
        leaf_mat = random.choice(leaf_materials)
        
        bpy.ops.mesh.primitive_plane_add(size=0.2, location=pos)
        fallen_leaf = bpy.context.active_object
        fallen_leaf.name = "FallenLeaf"
        fallen_leaf.data.materials.append(leaf_mat)
        fallen_leaf.rotation_euler = (random.uniform(-0.3, 0.3), 
                                      random.uniform(-0.3, 0.3), 
                                      random.uniform(0, 2*math.pi))
        fallen_leaf.scale = (random.uniform(0.8, 1.5), random.uniform(0.6, 1.2), 1)
    
    print("Autumn tree generated!")

create_autumn_tree()