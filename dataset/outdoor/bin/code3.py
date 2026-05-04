import bpy
import math

def create_bin_material(material_type="plastic", color=(0.2, 0.3, 0.8, 1.0)):
    """
    Create a material for the bin
    
    Parameters:
    - material_type: "plastic", "metal", "rusty_metal", "wood"
    - color: RGBA tuple for base color
    """
    
    mat = bpy.data.materials.new(name=f"Bin_{material_type}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create output node
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    if material_type == "plastic":
        # Create Principled BSDF for plastic
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Plastic settings
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.4
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
        
        # Connect
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "metal":
        # Create Principled BSDF for metal
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Metal settings
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.3
        
        # Connect
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "rusty_metal":
        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 0)
        
        # Noise texture for rust
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-600, 0)
        noise.inputs['Scale'].default_value = 15.0
        noise.inputs['Detail'].default_value = 5.0
        
        # Color ramp for rust pattern
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 0)
        color_ramp.color_ramp.elements[0].color = (0.3, 0.15, 0.05, 1.0)  # Dark rust
        color_ramp.color_ramp.elements[1].color = (0.6, 0.3, 0.1, 1.0)   # Light rust
        
        # Mix with metal color
        mix_rgb = nodes.new(type='ShaderNodeMix')
        mix_rgb.data_type = 'RGBA'
        mix_rgb.location = (-200, 100)
        mix_rgb.inputs[6].default_value = color  # Metal color
        
        # Roughness variation
        rough_ramp = nodes.new(type='ShaderNodeValToRGB')
        rough_ramp.location = (-200, -200)
        rough_ramp.color_ramp.elements[0].position = 0.3
        rough_ramp.color_ramp.elements[1].position = 0.8
        
        # Connections
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs[0])  # Factor
        links.new(color_ramp.outputs['Color'], mix_rgb.inputs[7])  # Color2
        links.new(mix_rgb.outputs[2], bsdf.inputs['Base Color'])
        
        links.new(noise.outputs['Fac'], rough_ramp.inputs['Fac'])
        links.new(rough_ramp.outputs['Color'], bsdf.inputs['Roughness'])
        
        bsdf.inputs['Metallic'].default_value = 0.8
        
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
        
    elif material_type == "wood":
        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (200, 0)
        
        # Wave texture for wood grain
        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-600, 0)
        wave.wave_type = 'BANDS'
        wave.inputs['Scale'].default_value = 5.0
        wave.inputs['Distortion'].default_value = 2.0
        
        # Color ramp for wood colors
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-400, 0)
        color_ramp.color_ramp.elements[0].color = (0.3, 0.15, 0.05, 1.0)  # Dark wood
        color_ramp.color_ramp.elements[1].color = (0.5, 0.3, 0.15, 1.0)  # Light wood
        
        # Connections
        links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.6
        
        links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat


def create_wire_mesh_bin(
    radius=0.3,
    height=0.6,
    frame_thickness=0.015,
    wire_thickness=0.003,
    mesh_divisions_vertical=12,
    mesh_divisions_horizontal=16,
    base_ring_height=0.04,
    top_ring_height=0.03,
    leg_height=0.05,
    leg_radius=0.008,
    num_legs=4,
    material_type="metal",
    frame_color=(0.2, 0.2, 0.25, 1.0),
    wire_color=(0.3, 0.3, 0.35, 1.0)
):
    """
    Create a wire mesh waste bin with decorative frame
    
    Parameters:
    - radius: radius of the bin
    - height: height of the bin (without legs)
    - frame_thickness: thickness of the frame rings
    - wire_thickness: thickness of the mesh wires
    - mesh_divisions_vertical: number of vertical wire divisions
    - mesh_divisions_horizontal: number of horizontal wire rings
    - base_ring_height: height of bottom decorative ring
    - top_ring_height: height of top decorative ring
    - leg_height: height of the legs
    - leg_radius: radius of the legs
    - num_legs: number of legs (3, 4, or 6)
    - material_type: "plastic", "metal", "rusty_metal", "wood"
    - frame_color: RGBA tuple for frame color
    - wire_color: RGBA tuple for wire mesh color
    """
    
    # Create collection for the bin
    bin_collection = bpy.data.collections.new("WireMeshBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create materials
    frame_mat = create_bin_material(material_type, frame_color)
    wire_mat = create_bin_material(material_type, wire_color)
    
    # 1. Create bottom ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=frame_thickness/2,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, leg_height + base_ring_height/2)
    )
    bottom_ring = bpy.context.active_object
    bottom_ring.name = "Bin_BottomRing"
    bottom_ring.scale[2] = base_ring_height / (frame_thickness)
    
    # Apply scale
    bpy.context.view_layer.objects.active = bottom_ring
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in bottom_ring.users_collection:
        coll.objects.unlink(bottom_ring)
    bin_collection.objects.link(bottom_ring)
    
    if bottom_ring.data.materials:
        bottom_ring.data.materials[0] = frame_mat
    else:
        bottom_ring.data.materials.append(frame_mat)
    
    # 2. Create top ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=frame_thickness/2,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, leg_height + height - top_ring_height/2)
    )
    top_ring = bpy.context.active_object
    top_ring.name = "Bin_TopRing"
    top_ring.scale[2] = top_ring_height / (frame_thickness)
    
    # Apply scale
    bpy.context.view_layer.objects.active = top_ring
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in top_ring.users_collection:
        coll.objects.unlink(top_ring)
    bin_collection.objects.link(top_ring)
    
    if top_ring.data.materials:
        top_ring.data.materials[0] = frame_mat
    else:
        top_ring.data.materials.append(frame_mat)
    
    # 3. Create vertical wires
    angle_step = (2 * math.pi) / mesh_divisions_vertical
    
    for i in range(mesh_divisions_vertical):
        angle = i * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Create vertical wire
        bpy.ops.mesh.primitive_cylinder_add(
            radius=wire_thickness/2,
            depth=height - base_ring_height - top_ring_height,
            vertices=8,
            location=(x, y, leg_height + base_ring_height + (height - base_ring_height - top_ring_height)/2)
        )
        v_wire = bpy.context.active_object
        v_wire.name = f"Bin_VerticalWire_{i+1}"
        
        # Move to collection and apply material
        for coll in v_wire.users_collection:
            coll.objects.unlink(v_wire)
        bin_collection.objects.link(v_wire)
        
        if v_wire.data.materials:
            v_wire.data.materials[0] = wire_mat
        else:
            v_wire.data.materials.append(wire_mat)
    
    # 4. Create horizontal wire rings
    ring_spacing = (height - base_ring_height - top_ring_height) / (mesh_divisions_horizontal + 1)
    
    for i in range(mesh_divisions_horizontal):
        ring_z = leg_height + base_ring_height + (i + 1) * ring_spacing
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius - wire_thickness,
            minor_radius=wire_thickness/2,
            major_segments=32,
            minor_segments=8,
            location=(0, 0, ring_z)
        )
        h_ring = bpy.context.active_object
        h_ring.name = f"Bin_HorizontalRing_{i+1}"
        
        # Move to collection and apply material
        for coll in h_ring.users_collection:
            coll.objects.unlink(h_ring)
        bin_collection.objects.link(h_ring)
        
        if h_ring.data.materials:
            h_ring.data.materials[0] = wire_mat
        else:
            h_ring.data.materials.append(wire_mat)
    
    # 5. Create legs
    leg_angle_step = (2 * math.pi) / num_legs
    
    for i in range(num_legs):
        angle = i * leg_angle_step
        leg_x = (radius - frame_thickness) * math.cos(angle)
        leg_y = (radius - frame_thickness) * math.sin(angle)
        
        # Create leg
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_radius,
            depth=leg_height,
            vertices=12,
            location=(leg_x, leg_y, leg_height/2)
        )
        leg = bpy.context.active_object
        leg.name = f"Bin_Leg_{i+1}"
        
        # Move to collection and apply material
        for coll in leg.users_collection:
            coll.objects.unlink(leg)
        bin_collection.objects.link(leg)
        
        if leg.data.materials:
            leg.data.materials[0] = frame_mat
        else:
            leg.data.materials.append(frame_mat)
        
        # Create foot cap (small sphere at bottom)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=leg_radius * 1.3,
            segments=12,
            ring_count=8,
            location=(leg_x, leg_y, leg_radius * 1.3)
        )
        foot = bpy.context.active_object
        foot.name = f"Bin_Foot_{i+1}"
        
        # Move to collection and apply material
        for coll in foot.users_collection:
            coll.objects.unlink(foot)
        bin_collection.objects.link(foot)
        
        if foot.data.materials:
            foot.data.materials[0] = frame_mat
        else:
            foot.data.materials.append(frame_mat)
    
    # 6. Create bottom mesh base (optional - can be a solid disk)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - frame_thickness - wire_thickness,
        depth=0.002,
        vertices=32,
        location=(0, 0, leg_height + base_ring_height + 0.001)
    )
    base = bpy.context.active_object
    base.name = "Bin_Base"
    
    # Move to collection and apply material
    for coll in base.users_collection:
        coll.objects.unlink(base)
    bin_collection.objects.link(base)
    
    if base.data.materials:
        base.data.materials[0] = frame_mat
    else:
        base.data.materials.append(frame_mat)
    
    # 7. Create decorative handle/grip on sides (2 opposite handles)
    handle_height = leg_height + height * 0.6
    
    for i, angle in enumerate([0, math.pi]):
        # Handle position
        handle_x = (radius + frame_thickness) * math.cos(angle)
        handle_y = (radius + frame_thickness) * math.sin(angle)
        
        # Create handle arc (torus section)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.04,
            minor_radius=0.008,
            major_segments=16,
            minor_segments=8,
            location=(handle_x, handle_y, handle_height)
        )
        handle = bpy.context.active_object
        handle.name = f"Bin_Handle_{i+1}"
        
        # Rotate to face outward
        handle.rotation_euler = (0, math.pi/2, angle)
        
        # Move to collection and apply material
        for coll in handle.users_collection:
            coll.objects.unlink(handle)
        bin_collection.objects.link(handle)
        
        if handle.data.materials:
            handle.data.materials[0] = frame_mat
        else:
            handle.data.materials.append(frame_mat)
    
    # Smooth shading for all curved objects
    for obj in bin_collection.objects:
        if "Wire" in obj.name or "Ring" in obj.name or "Leg" in obj.name or "Foot" in obj.name or "Handle" in obj.name:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
    
    print(f"Wire mesh bin created with {material_type} material")
    return bin_collection


# Clear existing objects (optional)
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# Example 1: Dark metal wire mesh bin (default)
bin_wire = create_wire_mesh_bin(
    material_type="metal",
    frame_color=(0.2, 0.2, 0.25, 1.0),  # Dark metal
    wire_color=(0.3, 0.3, 0.35, 1.0)     # Slightly lighter
)

# Example 2: Bronze/copper wire bin
# bin_wire_bronze = create_wire_mesh_bin(
#     radius=0.35,
#     height=0.65,
#     material_type="metal",
#     frame_color=(0.7, 0.4, 0.2, 1.0),   # Bronze
#     wire_color=(0.75, 0.45, 0.25, 1.0),
#     mesh_divisions_vertical=20,
#     mesh_divisions_horizontal=8
# )

# Example 3: White painted metal bin
# bin_wire_white = create_wire_mesh_bin(
#     radius=0.25,
#     height=0.5,
#     material_type="metal",
#     frame_color=(0.95, 0.95, 0.95, 1.0),
#     wire_color=(0.9, 0.9, 0.9, 1.0),
#     num_legs=3
# )

# Example 4: Rusty industrial wire bin
# bin_wire_rusty = create_wire_mesh_bin(
#     radius=0.4,
#     height=0.7,
#     material_type="rusty_metal",
#     frame_color=(0.5, 0.5, 0.55, 1.0),
#     wire_color=(0.45, 0.45, 0.5, 1.0),
#     mesh_divisions_vertical=12,
#     mesh_divisions_horizontal=10,
#     num_legs=4
# )

# Example 5: Fine mesh office bin
# bin_wire_fine = create_wire_mesh_bin(
#     radius=0.28,
#     height=0.55,
#     material_type="metal",
#     frame_color=(0.1, 0.1, 0.12, 1.0),  # Black
#     wire_color=(0.15, 0.15, 0.17, 1.0),
#     mesh_divisions_vertical=24,
#     mesh_divisions_horizontal=15,
#     wire_thickness=0.002,
#     num_legs=4
# )