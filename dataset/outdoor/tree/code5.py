import bpy
import math
import random
from mathutils import Vector

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_joshua_tree(trunk_height=4.5, trunk_radius=0.35, max_depth=4):
    """Generate a Joshua tree with characteristic spiky desert appearance"""
    clear_scene()
    random.seed(1313)
    
    # Materials
    bark_mat = bpy.data.materials.new(name="JoshuaBark")
    bark_mat.use_nodes = True
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.45, 0.38, 0.28, 1.0)
    bark_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.95
    
    spine_mat = bpy.data.materials.new(name="Spine")
    spine_mat.use_nodes = True
    spine_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.45, 0.35, 1.0)
    
    leaf_mat = bpy.data.materials.new(name="JoshuaLeaf")
    leaf_mat.use_nodes = True
    leaf_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.45, 0.25, 1.0)
    
    sand_mat = bpy.data.materials.new(name="Sand")
    sand_mat.use_nodes = True
    sand_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.85, 0.75, 0.6, 1.0)
    
    # Create desert ground
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "DesertGround"
    ground.data.materials.append(sand_mat)
    
    def create_trunk_segment(base_loc, direction, length, radius, depth, has_spines=True):
        """Create a single trunk/branch segment with characteristic texture"""
        
        # Joshua tree trunks are more irregular
        segments = 5
        segment_objects = []
        
        for i in range(segments):
            t = i / segments
            
            # Slight taper
            seg_radius = radius * (1 - t * 0.15)
            seg_height = length / segments
            
            # Add texture bumps
            bump_scale = 1.0 + random.uniform(-0.08, 0.08)
            
            pos = base_loc + direction * (length * t + seg_height / 2)
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=8,
                radius=seg_radius * bump_scale,
                depth=seg_height,
                location=pos
            )
            
            segment = bpy.context.active_object
            segment.name = f"JoshuaTrunk_D{depth}_{i}"
            
            # Align with direction
            up = Vector((0, 0, 1))
            if direction.length > 0:
                rotation_axis = up.cross(direction.normalized())
                if rotation_axis.length > 0.001:
                    rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(direction.normalized()))))
                    segment.rotation_mode = 'AXIS_ANGLE'
                    segment.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
            
            segment.data.materials.append(bark_mat)
            segment_objects.append(segment)
        
        return segment_objects
    
    def create_leaf_cluster(center_pos, num_leaves=40):
        """Create a cluster of spiky leaves at branch end"""
        
        for i in range(num_leaves):
            # Leaves point outward and slightly upward
            angle = random.uniform(0, 2 * math.pi)
            elevation = random.uniform(math.pi/6, math.pi/3)
            
            leaf_length = random.uniform(0.25, 0.4)
            
            leaf_dir = Vector((
                math.sin(elevation) * math.cos(angle),
                math.sin(elevation) * math.sin(angle),
                math.cos(elevation)
            ))
            
            leaf_end = center_pos + leaf_dir * leaf_length
            
            # Create spiky leaf as thin cone
            bpy.ops.mesh.primitive_cone_add(
                vertices=4,
                radius1=0.02,
                radius2=0.005,
                depth=leaf_length,
                location=(center_pos + leaf_end) / 2
            )
            
            leaf = bpy.context.active_object
            leaf.name = "JoshuaLeaf"
            
            # Align leaf
            up = Vector((0, 0, 1))
            rotation_axis = up.cross(leaf_dir)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(leaf_dir))))
                leaf.rotation_mode = 'AXIS_ANGLE'
                leaf.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
            
            leaf.data.materials.append(leaf_mat)
            
            # Add spine at tip occasionally
            if random.random() < 0.3:
                spine_pos = leaf_end
                spine_length = 0.08
                
                bpy.ops.mesh.primitive_cone_add(
                    vertices=3,
                    radius1=0.008,
                    radius2=0.001,
                    depth=spine_length,
                    location=spine_pos + leaf_dir * (spine_length / 2)
                )
                
                spine = bpy.context.active_object
                spine.name = "Spine"
                
                # Align spine
                rotation_axis = up.cross(leaf_dir)
                if rotation_axis.length > 0.001:
                    rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(leaf_dir))))
                    spine.rotation_mode = 'AXIS_ANGLE'
                    spine.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
                
                spine.data.materials.append(spine_mat)
    
    def create_branch(base_loc, direction, length, radius, depth):
        """Recursively create Joshua tree branches"""
        
        if depth > max_depth or length < 0.5:
            # Create leaf cluster at end
            end_pos = base_loc + direction * length
            create_leaf_cluster(end_pos)
            return
        
        # Create trunk segment
        segments = create_trunk_segment(base_loc, direction, length, radius, depth)
        
        end_loc = base_loc + direction * length
        
        # Joshua trees have distinctive branching
        if depth < max_depth:
            # Usually fork into 2-3 branches
            num_branches = random.randint(2, 3) if depth < 2 else random.randint(1, 2)
            
            for i in range(num_branches):
                # Branches angle upward and outward
                angle_xz = (2 * math.pi * i / num_branches) + random.uniform(-0.4, 0.4)
                
                # Joshua trees have characteristic upward-angled branches
                angle_elevation = random.uniform(math.pi/6, math.pi/4)
                
                new_dir = Vector((
                    math.sin(angle_elevation) * math.cos(angle_xz),
                    math.sin(angle_elevation) * math.sin(angle_xz),
                    math.cos(angle_elevation)
                ))
                
                # Apply rotation relative to current direction
                rotation = direction.rotation_difference(Vector((0, 0, 1)))
                new_dir.rotate(rotation)
                
                new_length = length * random.uniform(0.6, 0.8)
                new_radius = radius * 0.7
                
                create_branch(end_loc, new_dir, new_length, new_radius, depth + 1)
        else:
            # Terminal leaf cluster
            create_leaf_cluster(end_loc)
    
    # Create main trunk (slightly leaning)
    lean_direction = Vector((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 1)).normalized()
    create_branch(Vector((0, 0, 0)), lean_direction, trunk_height, trunk_radius, 0)
    
    # Add some dead/dried leaves at base
    for _ in range(30):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.3, 1.5)
        
        leaf_pos = Vector((
            math.cos(angle) * distance,
            math.sin(angle) * distance,
            0
        ))
        
        # Dried leaf on ground
        bpy.ops.mesh.primitive_cone_add(
            vertices=4,
            radius1=0.015,
            radius2=0.003,
            depth=0.2,
            location=leaf_pos
        )
        
        dried_leaf = bpy.context.active_object
        dried_leaf.name = "DriedLeaf"
        
        # Lay flat on ground
        dried_leaf.rotation_euler = (math.pi/2, 0, random.uniform(0, 2*math.pi))
        
        # Dried color
        dried_mat = bpy.data.materials.new(name=f"DriedLeaf_{_}")
        dried_mat.use_nodes = True
        dried_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.55, 0.45, 0.3, 1.0)
        dried_leaf.data.materials.append(dried_mat)
    
    # Add some desert rocks
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(2, 5)
        
        rock_pos = Vector((
            math.cos(angle) * distance,
            math.sin(angle) * distance,
            random.uniform(0, 0.1)
        ))
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=random.uniform(0.2, 0.4),
            location=rock_pos
        )
        
        rock = bpy.context.active_object
        rock.scale = (random.uniform(0.8, 1.5), random.uniform(0.7, 1.2), random.uniform(0.5, 0.8))
        rock.name = "DesertRock"
        
        rock_mat = bpy.data.materials.new(name=f"Rock_{_}")
        rock_mat.use_nodes = True
        rock_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.5, 0.45, 0.4, 1.0)
        rock_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.9
        rock.data.materials.append(rock_mat)
    
    print("Joshua tree generated!")

create_joshua_tree()