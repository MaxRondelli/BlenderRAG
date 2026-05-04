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


def create_hexagonal_pedal_bin(
    radius=0.3,
    height=0.7,
    wall_thickness=0.02,
    bottom_thickness=0.02,
    lid_height=0.05,
    lid_overhang=0.03,
    pedal_length=0.15,
    pedal_width=0.08,
    pedal_height=0.02,
    hinge_radius=0.01,
    material_type="plastic",
    body_color=(0.3, 0.3, 0.3, 1.0),
    lid_color=(0.4, 0.4, 0.4, 1.0)
):
    """
    Create a hexagonal pedal bin with lid
    
    Parameters:
    - radius: radius of the hexagonal bin (distance from center to vertex)
    - height: height of the bin body
    - wall_thickness: thickness of the walls
    - bottom_thickness: thickness of the bottom
    - lid_height: height of the lid
    - lid_overhang: how much the lid extends beyond the body
    - pedal_length: length of the foot pedal
    - pedal_width: width of the foot pedal
    - pedal_height: thickness of the pedal
    - hinge_radius: radius of the hinge cylinder
    - material_type: "plastic", "metal", "rusty_metal", "wood"
    - body_color: RGBA tuple for body color
    - lid_color: RGBA tuple for lid color
    """
    
    # Create collection for the bin
    bin_collection = bpy.data.collections.new("HexagonalPedalBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # 1. Create outer hexagonal cylinder (body)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        vertices=6,  # Hexagon
        location=(0, 0, height/2)
    )
    outer_hex = bpy.context.active_object
    outer_hex.name = "Bin_Body_Outer"
    
    # Move to collection
    for coll in outer_hex.users_collection:
        coll.objects.unlink(outer_hex)
    bin_collection.objects.link(outer_hex)
    
    # 2. Create inner hexagonal cylinder (for hollow interior)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=height - bottom_thickness + 0.01,
        vertices=6,
        location=(0, 0, height/2 + bottom_thickness)
    )
    inner_hex = bpy.context.active_object
    inner_hex.name = "Bin_Body_Inner"
    
    # Move to collection
    for coll in inner_hex.users_collection:
        coll.objects.unlink(inner_hex)
    bin_collection.objects.link(inner_hex)
    
    # 3. Boolean modifier to make it hollow
    bpy.context.view_layer.objects.active = outer_hex
    bool_mod = outer_hex.modifiers.new(name="Hollow", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = inner_hex
    
    # Apply modifier
    bpy.ops.object.select_all(action='DESELECT')
    outer_hex.select_set(True)
    bpy.context.view_layer.objects.active = outer_hex
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner cylinder
    bpy.ops.object.select_all(action='DESELECT')
    inner_hex.select_set(True)
    bpy.ops.object.delete()
    
    # Apply body material
    body_mat = create_bin_material(material_type, body_color)
    if outer_hex.data.materials:
        outer_hex.data.materials[0] = body_mat
    else:
        outer_hex.data.materials.append(body_mat)
    
    # 4. Create lid (hexagonal)
    lid_radius = radius + lid_overhang
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=lid_radius,
        depth=lid_height,
        vertices=6,
        location=(0, 0, height + lid_height/2)
    )
    lid = bpy.context.active_object
    lid.name = "Bin_Lid"
    
    # Add bevel to lid edges
    lid_bevel = lid.modifiers.new(name="LidBevel", type='BEVEL')
    lid_bevel.width = 0.015
    lid_bevel.segments = 3
    lid_bevel.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = lid
    bpy.ops.object.modifier_apply(modifier="LidBevel")
    
    # Move to collection
    for coll in lid.users_collection:
        coll.objects.unlink(lid)
    bin_collection.objects.link(lid)
    
    # Apply lid material
    lid_mat = create_bin_material(material_type, lid_color)
    if lid.data.materials:
        lid.data.materials[0] = lid_mat
    else:
        lid.data.materials.append(lid_mat)
    
    # 5. Create hinge at the back
    hinge_y = -radius * 0.9
    hinge_z = height
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=hinge_radius,
        depth=radius * 0.4,
        vertices=16,
        location=(0, hinge_y, hinge_z)
    )
    hinge = bpy.context.active_object
    hinge.name = "Bin_Hinge"
    hinge.rotation_euler = (0, math.pi/2, 0)
    
    # Move to collection
    for coll in hinge.users_collection:
        coll.objects.unlink(hinge)
    bin_collection.objects.link(hinge)
    
    # Apply metal material to hinge
    hinge_mat = create_bin_material("metal", (0.6, 0.6, 0.65, 1.0))
    if hinge.data.materials:
        hinge.data.materials[0] = hinge_mat
    else:
        hinge.data.materials.append(hinge_mat)
    
    # 6. Create pedal mechanism
    pedal_y = radius * 0.9
    
    # Pedal plate
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, pedal_y, pedal_height/2)
    )
    pedal = bpy.context.active_object
    pedal.name = "Bin_Pedal"
    pedal.scale = (pedal_width, pedal_length, pedal_height)
    
    # Apply scale
    bpy.context.view_layer.objects.active = pedal
    bpy.ops.object.transform_apply(scale=True)
    
    # Bevel pedal edges
    pedal_bevel = pedal.modifiers.new(name="PedalBevel", type='BEVEL')
    pedal_bevel.width = 0.005
    pedal_bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier="PedalBevel")
    
    # Move to collection
    for coll in pedal.users_collection:
        coll.objects.unlink(pedal)
    bin_collection.objects.link(pedal)
    
    # Apply pedal material
    if pedal.data.materials:
        pedal.data.materials[0] = body_mat
    else:
        pedal.data.materials.append(body_mat)
    
    # 7. Create pedal arm (connects pedal to lid)
    arm_length = height * 0.8
    arm_thickness = 0.008
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, pedal_y - pedal_length/2 + 0.02, arm_length/2)
    )
    arm = bpy.context.active_object
    arm.name = "Bin_PedalArm"
    arm.scale = (arm_thickness, arm_thickness, arm_length)
    
    # Apply scale
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection
    for coll in arm.users_collection:
        coll.objects.unlink(arm)
    bin_collection.objects.link(arm)
    
    # Apply metal material to arm
    if arm.data.materials:
        arm.data.materials[0] = hinge_mat
    else:
        arm.data.materials.append(hinge_mat)
    
    # 8. Create rim around top of body
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=0.015,
        major_segments=6,
        minor_segments=8,
        location=(0, 0, height)
    )
    rim = bpy.context.active_object
    rim.name = "Bin_Rim"
    
    # Move to collection
    for coll in rim.users_collection:
        coll.objects.unlink(rim)
    bin_collection.objects.link(rim)
    
    # Apply rim material
    if rim.data.materials:
        rim.data.materials[0] = body_mat
    else:
        rim.data.materials.append(body_mat)
    
    # 9. Add decorative grip on lid top
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height + lid_height + 0.01)
    )
    grip = bpy.context.active_object
    grip.name = "Bin_LidGrip"
    grip.scale = (0.08, 0.04, 0.015)
    
    # Apply scale
    bpy.context.view_layer.objects.active = grip
    bpy.ops.object.transform_apply(scale=True)
    
    # Bevel grip
    grip_bevel = grip.modifiers.new(name="GripBevel", type='BEVEL')
    grip_bevel.width = 0.008
    grip_bevel.segments = 3
    bpy.ops.object.modifier_apply(modifier="GripBevel")
    
    # Move to collection
    for coll in grip.users_collection:
        coll.objects.unlink(grip)
    bin_collection.objects.link(grip)
    
    # Apply grip material
    if grip.data.materials:
        grip.data.materials[0] = lid_mat
    else:
        grip.data.materials.append(lid_mat)
    
    # Smooth shading for all objects
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Hexagonal pedal bin created with {material_type} material")
    return bin_collection


# Clear existing objects (optional)
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# Example 1: Dark gray plastic pedal bin (default)
bin_hex_pedal = create_hexagonal_pedal_bin(
    material_type="plastic",
    body_color=(0.3, 0.3, 0.3, 1.0),  # Dark gray
    lid_color=(0.4, 0.4, 0.4, 1.0)     # Lighter gray
)

# Example 2: Stainless steel pedal bin
# bin_hex_steel = create_hexagonal_pedal_bin(
#     radius=0.35,
#     height=0.75,
#     material_type="metal",
#     body_color=(0.8, 0.8, 0.85, 1.0),
#     lid_color=(0.75, 0.75, 0.8, 1.0)
# )

# Example 3: White plastic bathroom bin
# bin_hex_white = create_hexagonal_pedal_bin(
#     radius=0.25,
#     height=0.5,
#     material_type="plastic",
#     body_color=(0.95, 0.95, 0.95, 1.0),
#     lid_color=(0.9, 0.9, 0.9, 1.0)
# )

# Example 4: Rusty industrial bin
# bin_hex_rusty = create_hexagonal_pedal_bin(
#     radius=0.4,
#     height=0.8,
#     material_type="rusty_metal",
#     body_color=(0.5, 0.5, 0.55, 1.0),
#     lid_color=(0.45, 0.45, 0.5, 1.0)
# )