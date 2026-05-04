import bpy
import math
import random
from mathutils import Vector, Euler

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_coconut_palm(trunk_height=7, num_fronds=10):
    """Generate a coconut palm with curved trunk and coconuts"""
    clear_scene()
    random.seed(4444)
    
    # Materials
    trunk_mat = bpy.data.materials.new(name="CoconutTrunk")
    trunk_mat.use_nodes = True
    trunk_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.55, 0.45, 0.35, 1.0)
    trunk_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.85
    
    frond_mat = bpy.data.materials.new(name="PalmFrond")
    frond_mat.use_nodes = True
    frond_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.55, 0.2, 1.0)
    
    coconut_mat = bpy.data.materials.new(name="Coconut")
    coconut_mat.use_nodes = True
    coconut_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.4, 0.35, 0.25, 1.0)
    coconut_mat.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.9
    
    # Create curved trunk using multiple segments
    segments = 15
    curve_direction = Vector((random.uniform(0.3, 0.5), random.uniform(-0.2, 0.2), 0))
    
    for i in range(segments):
        t = i / segments
        segment_height = trunk_height / segments
        
        # Create curve using sine wave
        curve_amount = math.sin(t * math.pi) * 0.8
        offset = curve_direction * curve_amount
        
        # Trunk gets thinner towards top
        radius = 0.25 * (1 - t * 0.35)
        
        # Add texture rings
        if i % 2 == 0:
            radius *= 1.05
        
        position = Vector((offset.x, offset.y, trunk_height * t + segment_height/2))
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12,
            radius=radius,
            depth=segment_height,
            location=position
        )
        
        segment = bpy.context.active_object
        segment.name = f"PalmTrunk_Seg{i}"
        segment.data.materials.append(trunk_mat)
        
        # Slight rotation for curve
        if i > 0:
            tilt = curve_direction.normalized() * 0.1 * math.sin(t * math.pi)
            segment.rotation_euler = Euler((tilt.y, -tilt.x, 0))
    
    # Crown position (top of curved trunk)
    crown_offset = curve_direction * math.sin(math.pi) * 0.8
    crown_pos = Vector((crown_offset.x, crown_offset.y, trunk_height))
    
    # Create coconut cluster
    num_coconuts = random.randint(4, 7)
    for i in range(num_coconuts):
        coconut_offset = Vector((
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            random.uniform(-0.4, -0.1)
        ))
        
        coconut_pos = crown_pos + coconut_offset
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=10,
            radius=0.18,
            location=coconut_pos
        )
        
        coconut = bpy.context.active_object
        coconut.scale = (1.0, 1.0, 1.15)  # Slightly elongated
        coconut.name = "Coconut"
        coconut.data.materials.append(coconut_mat)
    
    # Create palm fronds
    for i in range(num_fronds):
        angle = (2 * math.pi * i / num_fronds) + random.uniform(-0.3, 0.3)
        
        # Fronds arch outward and down
        frond_length = random.uniform(3.8, 4.5)
        
        # Create frond stem (midrib)
        stem_segments = 12
        
        for seg in range(stem_segments):
            t_seg = seg / stem_segments
            
            # Curve: starts upward, arches down
            elevation = math.pi/12 - t_seg * (math.pi/6)
            horizontal_spread = 1.0 + t_seg * 0.5
            
            segment_dir = Vector((
                math.cos(angle) * horizontal_spread,
                math.sin(angle) * horizontal_spread,
                0
            )) * 0.3
            
            segment_pos = crown_pos + segment_dir * seg + Vector((0, 0, -t_seg * t_seg * 1.5))
            next_segment_pos = crown_pos + segment_dir * (seg + 1) + Vector((0, 0, -(t_seg + 1/stem_segments)**2 * 1.5))
            
            segment_length = (next_segment_pos - segment_pos).length
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.04 * (1 - t_seg * 0.5),
                depth=segment_length,
                location=(segment_pos + next_segment_pos) / 2
            )
            
            stem_seg = bpy.context.active_object
            stem_seg.name = f"FrondStem_{i}_{seg}"
            stem_seg.data.materials.append(frond_mat)
            
            # Align segment
            direction = (next_segment_pos - segment_pos).normalized()
            up = Vector((0, 0, 1))
            rotation_axis = up.cross(direction)
            if rotation_axis.length > 0.001:
                rotation_angle = math.acos(min(1.0, max(-1.0, up.dot(direction))))
                stem_seg.rotation_mode = 'AXIS_ANGLE'
                stem_seg.rotation_axis_angle = (rotation_angle, *rotation_axis.normalized())
            
            # Add leaflets (pinnae) to this segment
            if seg > 2:  # Don't add leaflets to base
                num_leaflets = 4
                for leaflet_idx in range(num_leaflets):
                    side = 1 if leaflet_idx % 2 == 0 else -1
                    t_leaf = leaflet_idx / num_leaflets
                    
                    leaflet_pos = segment_pos + (next_segment_pos - segment_pos) * t_leaf
                    
                    # Perpendicular direction for leaflet
                    forward = (next_segment_pos - segment_pos).normalized()
                    right = Vector((forward.y, -forward.x, 0)).normalized()
                    
                    leaflet_length = 0.5 * (1 - t_seg * 0.3)
                    leaflet_offset = right * side * leaflet_length
                    
                    # Create leaflet as scaled plane
                    bpy.ops.mesh.primitive_plane_add(
                        size=1,
                        location=leaflet_pos + leaflet_offset * 0.5
                    )
                    
                    leaflet = bpy.context.active_object
                    leaflet.scale = (leaflet_length, 0.12, 1)
                    leaflet.name = f"Leaflet_{i}_{seg}_{leaflet_idx}"
                    leaflet.data.materials.append(frond_mat)
                    
                    # Rotate leaflet
                    angle_to_stem = math.atan2(right.y, right.x)
                    leaflet.rotation_euler = Euler((
                        random.uniform(-0.15, 0.15),
                        random.uniform(-0.2, 0.2),
                        angle_to_stem + side * math.pi/2
                    ))
    
    print("Coconut palm generated!")

create_coconut_palm()