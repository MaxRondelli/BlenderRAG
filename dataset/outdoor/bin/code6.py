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


def create_swing_lid_bin(
    radius=0.28,
    body_height=0.55,
    wall_thickness=0.02,
    bottom_thickness=0.02,
    base_height=0.08,
    base_radius_multiplier=1.15,
    lid_ring_height=0.04,
    swing_lid_radius=0.22,
    swing_lid_thickness=0.015,
    swing_pin_radius=0.006,
    material_type="plastic",
    body_color=(0.15, 0.15, 0.18, 1.0),
    lid_color=(0.2, 0.2, 0.22, 1.0),
    accent_color=(0.7, 0.1, 0.1, 1.0)
):
    """
    Create a bin with swing-top lid mechanism
    
    Parameters:
    - radius: radius of the bin body
    - body_height: height of the main body
    - wall_thickness: thickness of walls
    - bottom_thickness: thickness of bottom
    - base_height: height of the base platform
    - base_radius_multiplier: how much wider the base is
    - lid_ring_height: height of the top ring that holds swing lid
    - swing_lid_radius: radius of the circular swing lid
    - swing_lid_thickness: thickness of the swing lid
    - swing_pin_radius: radius of the pivot pins
    - material_type: material type
    - body_color: color of main body
    - lid_color: color of swing lid
    - accent_color: color of accents/pins
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("SwingLidBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create materials
    body_mat = create_bin_material(material_type, body_color)
    lid_mat = create_bin_material(material_type, lid_color)
    accent_mat = create_bin_material(material_type, accent_color)
    
    # 1. Create base platform
    base_radius = radius * base_radius_multiplier
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=base_radius,
        depth=base_height,
        vertices=32,
        location=(0, 0, base_height/2)
    )
    base = bpy.context.active_object
    base.name = "Bin_Base"
    
    # Add bevel to base edges
    base_bevel = base.modifiers.new(name="BaseBevel", type='BEVEL')
    base_bevel.width = 0.015
    base_bevel.segments = 3
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.modifier_apply(modifier="BaseBevel")
    
    # Move to collection and apply material
    for coll in base.users_collection:
        coll.objects.unlink(base)
    bin_collection.objects.link(base)
    
    if base.data.materials:
        base.data.materials[0] = body_mat
    else:
        base.data.materials.append(body_mat)
    
    # 2. Create main body (outer cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=body_height,
        vertices=32,
        location=(0, 0, base_height + body_height/2)
    )
    outer_body = bpy.context.active_object
    outer_body.name = "Bin_Body_Outer"
    
    # Move to collection
    for coll in outer_body.users_collection:
        coll.objects.unlink(outer_body)
    bin_collection.objects.link(outer_body)
    
    # 3. Create inner cylinder for hollowing
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=body_height - bottom_thickness + 0.01,
        vertices=32,
        location=(0, 0, base_height + body_height/2 + bottom_thickness)
    )
    inner_body = bpy.context.active_object
    inner_body.name = "Bin_Body_Inner"
    
    # Move to collection
    for coll in inner_body.users_collection:
        coll.objects.unlink(inner_body)
    bin_collection.objects.link(inner_body)
    
    # Boolean to hollow
    bpy.context.view_layer.objects.active = outer_body
    hollow_bool = outer_body.modifiers.new(name="Hollow", type='BOOLEAN')
    hollow_bool.operation = 'DIFFERENCE'
    hollow_bool.object = inner_body
    
    # Apply modifier
    bpy.ops.object.select_all(action='DESELECT')
    outer_body.select_set(True)
    bpy.context.view_layer.objects.active = outer_body
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner body
    bpy.ops.object.select_all(action='DESELECT')
    inner_body.select_set(True)
    bpy.ops.object.delete()
    
    # Apply material to body
    if outer_body.data.materials:
        outer_body.data.materials[0] = body_mat
    else:
        outer_body.data.materials.append(body_mat)
    
    # 4. Create top ring (lid holder)
    top_z = base_height + body_height
    
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=lid_ring_height/2,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, top_z)
    )
    top_ring = bpy.context.active_object
    top_ring.name = "Bin_TopRing"
    top_ring.scale[2] = 1.2
    
    # Apply scale
    bpy.context.view_layer.objects.active = top_ring
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in top_ring.users_collection:
        coll.objects.unlink(top_ring)
    bin_collection.objects.link(top_ring)
    
    if top_ring.data.materials:
        top_ring.data.materials[0] = body_mat
    else:
        top_ring.data.materials.append(body_mat)
    
    # 5. Create swing lid (circular disc)
    lid_z = top_z + lid_ring_height/2 + swing_lid_thickness/2
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=swing_lid_radius,
        depth=swing_lid_thickness,
        vertices=32,
        location=(0, 0, lid_z)
    )
    swing_lid = bpy.context.active_object
    swing_lid.name = "Bin_SwingLid"
    
    # Add bevel to lid edges
    lid_bevel = swing_lid.modifiers.new(name="LidBevel", type='BEVEL')
    lid_bevel.width = 0.008
    lid_bevel.segments = 3
    bpy.context.view_layer.objects.active = swing_lid
    bpy.ops.object.modifier_apply(modifier="LidBevel")
    
    # Move to collection and apply material
    for coll in swing_lid.users_collection:
        coll.objects.unlink(swing_lid)
    bin_collection.objects.link(swing_lid)
    
    if swing_lid.data.materials:
        swing_lid.data.materials[0] = lid_mat
    else:
        swing_lid.data.materials.append(lid_mat)
    
    # 6. Create pivot pins (2 opposite sides)
    pin_y = swing_lid_radius * 0.95
    
    for i, y_mult in enumerate([-1, 1]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=swing_pin_radius,
            depth=0.04,
            vertices=12,
            location=(0, pin_y * y_mult, lid_z)
        )
        pin = bpy.context.active_object
        pin.name = f"Bin_SwingPin_{i+1}"
        pin.rotation_euler = (math.pi/2, 0, 0)
        
        # Move to collection and apply material
        for coll in pin.users_collection:
            coll.objects.unlink(pin)
        bin_collection.objects.link(pin)
        
        if pin.data.materials:
            pin.data.materials[0] = accent_mat
        else:
            pin.data.materials.append(accent_mat)
        
        # Create pin holders on the ring
        bpy.ops.mesh.primitive_cylinder_add(
            radius=swing_pin_radius * 1.8,
            depth=0.02,
            vertices=12,
            location=(0, (radius + 0.01) * y_mult, top_z)
        )
        holder = bpy.context.active_object
        holder.name = f"Bin_PinHolder_{i+1}"
        holder.rotation_euler = (math.pi/2, 0, 0)
        
        # Move to collection and apply material
        for coll in holder.users_collection:
            coll.objects.unlink(holder)
        bin_collection.objects.link(holder)
        
        if holder.data.materials:
            holder.data.materials[0] = accent_mat
        else:
            holder.data.materials.append(accent_mat)
    
    # 7. Create push area on lid (textured surface)
    push_radius = swing_lid_radius * 0.4
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=push_radius,
        depth=0.008,
        vertices=32,
        location=(0, 0, lid_z + swing_lid_thickness/2 + 0.004)
    )
    push_area = bpy.context.active_object
    push_area.name = "Bin_PushArea"
    
    # Move to collection and apply material
    for coll in push_area.users_collection:
        coll.objects.unlink(push_area)
    bin_collection.objects.link(push_area)
    
    if push_area.data.materials:
        push_area.data.materials[0] = accent_mat
    else:
        push_area.data.materials.append(accent_mat)
    
    # 8. Add decorative ridges on body
    num_ridges = 3
    ridge_spacing = body_height / (num_ridges + 1)
    
    for i in range(num_ridges):
        ridge_z = base_height + (i + 1) * ridge_spacing
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius + 0.005,
            minor_radius=0.008,
            major_segments=32,
            minor_segments=8,
            location=(0, 0, ridge_z)
        )
        ridge = bpy.context.active_object
        ridge.name = f"Bin_Ridge_{i+1}"
        
        # Move to collection and apply material
        for coll in ridge.users_collection:
            coll.objects.unlink(ridge)
        bin_collection.objects.link(ridge)
        
        if ridge.data.materials:
            ridge.data.materials[0] = body_mat
        else:
            ridge.data.materials.append(body_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Swing-lid bin created with {material_type} material")
    return bin_collection


# Example 1: Dark gray bin with red accents (default)
bin_swing = create_swing_lid_bin(
    material_type="plastic",
    body_color=(0.15, 0.15, 0.18, 1.0),
    lid_color=(0.2, 0.2, 0.22, 1.0),
    accent_color=(0.7, 0.1, 0.1, 1.0)
)

# Example 2: Stainless steel bin
# bin_swing_steel = create_swing_lid_bin(
#     radius=0.32,
#     body_height=0.65,
#     material_type="metal",
#     body_color=(0.75, 0.75, 0.8, 1.0),
#     lid_color=(0.7, 0.7, 0.75, 1.0),
#     accent_color=(0.3, 0.3, 0.35, 1.0)
# )

# Example 3: White bathroom bin
# bin_swing_white = create_swing_lid_bin(
#     radius=0.22,
#     body_height=0.45,
#     material_type="plastic",
#     body_color=(0.95, 0.95, 0.95, 1.0),
#     lid_color=(0.9, 0.9, 0.9, 1.0),
#     accent_color=(0.8, 0.8, 0.82, 1.0)
# )