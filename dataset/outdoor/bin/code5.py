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


def create_dual_compartment_bin(
    width=0.6,
    depth=0.3,
    height=0.65,
    divider_thickness=0.015,
    wall_thickness=0.02,
    bottom_thickness=0.02,
    lid_height=0.08,
    lid_gap=0.005,
    opening_width_ratio=0.15,
    corner_radius=0.03,
    material_type="plastic",
    compartment1_color=(0.1, 0.6, 0.2, 1.0),  # Green for recycling
    compartment2_color=(0.2, 0.3, 0.8, 1.0),  # Blue for trash
    frame_color=(0.15, 0.15, 0.15, 1.0)
):
    """
    Create a dual-compartment recycling bin with separate lids
    
    Parameters:
    - width: total width of the bin
    - depth: depth of the bin
    - height: height of the bin body
    - divider_thickness: thickness of the center divider
    - wall_thickness: thickness of outer walls
    - bottom_thickness: thickness of bottom
    - lid_height: height of each lid
    - lid_gap: gap between body and lid
    - opening_width_ratio: ratio of opening width to compartment width
    - corner_radius: radius for rounded corners
    - material_type: material type
    - compartment1_color: color for left compartment
    - compartment2_color: color for right compartment
    - frame_color: color for frame/structure
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("DualCompartmentBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create materials
    mat1 = create_bin_material(material_type, compartment1_color)
    mat2 = create_bin_material(material_type, compartment2_color)
    frame_mat = create_bin_material(material_type, frame_color)
    
    compartment_width = (width - divider_thickness) / 2
    
    # 1. Create left compartment (recycling - green)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(-compartment_width/2 - divider_thickness/2, 0, height/2)
    )
    left_comp = bpy.context.active_object
    left_comp.name = "Bin_LeftCompartment"
    left_comp.scale = (compartment_width, depth, height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = left_comp
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded corners
    bevel1 = left_comp.modifiers.new(name="Bevel", type='BEVEL')
    bevel1.width = corner_radius
    bevel1.segments = 4
    bevel1.limit_method = 'ANGLE'
    
    # Move to collection and apply material
    for coll in left_comp.users_collection:
        coll.objects.unlink(left_comp)
    bin_collection.objects.link(left_comp)
    
    if left_comp.data.materials:
        left_comp.data.materials[0] = mat1
    else:
        left_comp.data.materials.append(mat1)
    
    # Create inner cavity for left compartment
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(-compartment_width/2 - divider_thickness/2, 0, height/2 + bottom_thickness)
    )
    left_inner = bpy.context.active_object
    left_inner.name = "Bin_LeftInner"
    left_inner.scale = (
        compartment_width - 2*wall_thickness,
        depth - 2*wall_thickness,
        height - bottom_thickness + 0.01
    )
    
    # Apply scale
    bpy.context.view_layer.objects.active = left_inner
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in left_inner.users_collection:
        coll.objects.unlink(left_inner)
    bin_collection.objects.link(left_inner)
    
    # Boolean to hollow out
    bpy.context.view_layer.objects.active = left_comp
    bool1 = left_comp.modifiers.new(name="Hollow", type='BOOLEAN')
    bool1.operation = 'DIFFERENCE'
    bool1.object = left_inner
    
    # 2. Create right compartment (trash - blue)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(compartment_width/2 + divider_thickness/2, 0, height/2)
    )
    right_comp = bpy.context.active_object
    right_comp.name = "Bin_RightCompartment"
    right_comp.scale = (compartment_width, depth, height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = right_comp
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded corners
    bevel2 = right_comp.modifiers.new(name="Bevel", type='BEVEL')
    bevel2.width = corner_radius
    bevel2.segments = 4
    bevel2.limit_method = 'ANGLE'
    
    # Move to collection and apply material
    for coll in right_comp.users_collection:
        coll.objects.unlink(right_comp)
    bin_collection.objects.link(right_comp)
    
    if right_comp.data.materials:
        right_comp.data.materials[0] = mat2
    else:
        right_comp.data.materials.append(mat2)
    
    # Create inner cavity for right compartment
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(compartment_width/2 + divider_thickness/2, 0, height/2 + bottom_thickness)
    )
    right_inner = bpy.context.active_object
    right_inner.name = "Bin_RightInner"
    right_inner.scale = (
        compartment_width - 2*wall_thickness,
        depth - 2*wall_thickness,
        height - bottom_thickness + 0.01
    )
    
    # Apply scale
    bpy.context.view_layer.objects.active = right_inner
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in right_inner.users_collection:
        coll.objects.unlink(right_inner)
    bin_collection.objects.link(right_inner)
    
    # Boolean to hollow out
    bpy.context.view_layer.objects.active = right_comp
    bool2 = right_comp.modifiers.new(name="Hollow", type='BOOLEAN')
    bool2.operation = 'DIFFERENCE'
    bool2.object = right_inner
    
    # Apply all modifiers
    for comp, inner in [(left_comp, left_inner), (right_comp, right_inner)]:
        bpy.ops.object.select_all(action='DESELECT')
        comp.select_set(True)
        bpy.context.view_layer.objects.active = comp
        bpy.ops.object.modifier_apply(modifier="Bevel")
        bpy.ops.object.modifier_apply(modifier="Hollow")
        
        # Delete inner
        bpy.ops.object.select_all(action='DESELECT')
        inner.select_set(True)
        bpy.ops.object.delete()
    
    # 3. Create center divider
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height/2 + bottom_thickness/2)
    )
    divider = bpy.context.active_object
    divider.name = "Bin_Divider"
    divider.scale = (divider_thickness, depth - 2*wall_thickness, height - bottom_thickness)
    
    # Apply scale
    bpy.context.view_layer.objects.active = divider
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in divider.users_collection:
        coll.objects.unlink(divider)
    bin_collection.objects.link(divider)
    
    if divider.data.materials:
        divider.data.materials[0] = frame_mat
    else:
        divider.data.materials.append(frame_mat)
    
    # 4. Create left lid with opening
    opening_width = compartment_width * opening_width_ratio
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(-compartment_width/2 - divider_thickness/2, 0, height + lid_gap + lid_height/2)
    )
    left_lid = bpy.context.active_object
    left_lid.name = "Bin_LeftLid"
    left_lid.scale = (compartment_width + wall_thickness, depth + wall_thickness, lid_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = left_lid
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel
    lid_bevel1 = left_lid.modifiers.new(name="LidBevel", type='BEVEL')
    lid_bevel1.width = corner_radius * 0.8
    lid_bevel1.segments = 3
    
    # Create opening in lid
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(-compartment_width/2 - divider_thickness/2, depth/4, height + lid_gap + lid_height/2)
    )
    left_opening = bpy.context.active_object
    left_opening.name = "Bin_LeftOpening"
    left_opening.scale = (opening_width, depth/3, lid_height + 0.02)
    
    # Apply scale
    bpy.context.view_layer.objects.active = left_opening
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in left_opening.users_collection:
        coll.objects.unlink(left_opening)
    bin_collection.objects.link(left_opening)
    
    # Boolean for opening
    bpy.context.view_layer.objects.active = left_lid
    opening_bool1 = left_lid.modifiers.new(name="Opening", type='BOOLEAN')
    opening_bool1.operation = 'DIFFERENCE'
    opening_bool1.object = left_opening
    
    # Apply modifiers
    bpy.ops.object.select_all(action='DESELECT')
    left_lid.select_set(True)
    bpy.context.view_layer.objects.active = left_lid
    bpy.ops.object.modifier_apply(modifier="LidBevel")
    bpy.ops.object.modifier_apply(modifier="Opening")
    
    # Delete opening object
    bpy.ops.object.select_all(action='DESELECT')
    left_opening.select_set(True)
    bpy.ops.object.delete()
    
    # Move to collection and apply material
    for coll in left_lid.users_collection:
        coll.objects.unlink(left_lid)
    bin_collection.objects.link(left_lid)
    
    if left_lid.data.materials:
        left_lid.data.materials[0] = mat1
    else:
        left_lid.data.materials.append(mat1)
    
    # 5. Create right lid with opening
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(compartment_width/2 + divider_thickness/2, 0, height + lid_gap + lid_height/2)
    )
    right_lid = bpy.context.active_object
    right_lid.name = "Bin_RightLid"
    right_lid.scale = (compartment_width + wall_thickness, depth + wall_thickness, lid_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = right_lid
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel
    lid_bevel2 = right_lid.modifiers.new(name="LidBevel", type='BEVEL')
    lid_bevel2.width = corner_radius * 0.8
    lid_bevel2.segments = 3
    
    # Create opening in lid
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(compartment_width/2 + divider_thickness/2, depth/4, height + lid_gap + lid_height/2)
    )
    right_opening = bpy.context.active_object
    right_opening.name = "Bin_RightOpening"
    right_opening.scale = (opening_width, depth/3, lid_height + 0.02)
    
    # Apply scale
    bpy.context.view_layer.objects.active = right_opening
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in right_opening.users_collection:
        coll.objects.unlink(right_opening)
    bin_collection.objects.link(right_opening)
    
    # Boolean for opening
    bpy.context.view_layer.objects.active = right_lid
    opening_bool2 = right_lid.modifiers.new(name="Opening", type='BOOLEAN')
    opening_bool2.operation = 'DIFFERENCE'
    opening_bool2.object = right_opening
    
    # Apply modifiers
    bpy.ops.object.select_all(action='DESELECT')
    right_lid.select_set(True)
    bpy.context.view_layer.objects.active = right_lid
    bpy.ops.object.modifier_apply(modifier="LidBevel")
    bpy.ops.object.modifier_apply(modifier="Opening")
    
    # Delete opening object
    bpy.ops.object.select_all(action='DESELECT')
    right_opening.select_set(True)
    bpy.ops.object.delete()
    
    # Move to collection and apply material
    for coll in right_lid.users_collection:
        coll.objects.unlink(right_lid)
    bin_collection.objects.link(right_lid)
    
    if right_lid.data.materials:
        right_lid.data.materials[0] = mat2
    else:
        right_lid.data.materials.append(mat2)
    
    # 6. Add labels/icons on lids (simple text representation with cubes)
    # Left lid - recycling symbol (simplified as 3 arrows in circle)
    for i, angle in enumerate([0, 2*math.pi/3, 4*math.pi/3]):
        icon_radius = opening_width * 0.6
        icon_x = -compartment_width/2 - divider_thickness/2 + icon_radius * math.cos(angle)
        icon_y = -depth/4 + icon_radius * math.sin(angle)
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(icon_x, icon_y, height + lid_gap + lid_height + 0.005)
        )
        arrow = bpy.context.active_object
        arrow.name = f"Bin_RecycleIcon_{i+1}"
        arrow.scale = (0.015, 0.04, 0.003)
        arrow.rotation_euler = (0, 0, angle + math.pi/6)
        
        # Apply transformations
        bpy.context.view_layer.objects.active = arrow
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        # Move to collection and apply material
        for coll in arrow.users_collection:
            coll.objects.unlink(arrow)
        bin_collection.objects.link(arrow)
        
        if arrow.data.materials:
            arrow.data.materials[0] = frame_mat
        else:
            arrow.data.materials.append(frame_mat)
    
    # Right lid - trash symbol (simplified as rectangle)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(compartment_width/2 + divider_thickness/2, -depth/4, height + lid_gap + lid_height + 0.005)
    )
    trash_icon = bpy.context.active_object
    trash_icon.name = "Bin_TrashIcon"
    trash_icon.scale = (0.05, 0.06, 0.003)
    
    # Apply scale
    bpy.context.view_layer.objects.active = trash_icon
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in trash_icon.users_collection:
        coll.objects.unlink(trash_icon)
    bin_collection.objects.link(trash_icon)
    
    if trash_icon.data.materials:
        trash_icon.data.materials[0] = frame_mat
    else:
        trash_icon.data.materials.append(frame_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Dual compartment bin created with {material_type} material")
    return bin_collection


# Example 1: Green/Blue recycling and trash bin (default)
bin_dual = create_dual_compartment_bin(
    material_type="plastic",
    compartment1_color=(0.1, 0.6, 0.2, 1.0),  # Green
    compartment2_color=(0.2, 0.3, 0.8, 1.0)   # Blue
)

# Example 2: Office recycling station
# bin_dual_office = create_dual_compartment_bin(
#     width=0.7,
#     depth=0.35,
#     height=0.7,
#     material_type="plastic",
#     compartment1_color=(0.85, 0.65, 0.1, 1.0),  # Yellow
#     compartment2_color=(0.15, 0.15, 0.2, 1.0),   # Dark gray
#     frame_color=(0.1, 0.1, 0.12, 1.0)
# )

# Example 3: Slim kitchen bin
# bin_dual_kitchen = create_dual_compartment_bin(
#     width=0.5,
#     depth=0.25,
#     height=0.6,
#     material_type="metal",
#     compartment1_color=(0.7, 0.7, 0.75, 1.0),
#     compartment2_color=(0.65, 0.65, 0.7, 1.0),
#     frame_color=(0.3, 0.3, 0.32, 1.0)
# )