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


def create_industrial_drum_bin(
    radius=0.35,
    height=0.7,
    wall_thickness=0.025,
    bottom_thickness=0.03,
    num_reinforcement_bands=4,
    band_height=0.03,
    band_thickness=0.015,
    top_rim_height=0.04,
    rivet_radius=0.008,
    rivets_per_band=12,
    handle_ring_radius=0.06,
    handle_ring_thickness=0.012,
    material_type="metal",
    body_color=(0.25, 0.25, 0.28, 1.0),
    band_color=(0.15, 0.15, 0.17, 1.0)
):
    """
    Create an industrial drum-style bin with reinforcement bands
    
    Parameters:
    - radius: radius of the drum
    - height: height of the drum
    - wall_thickness: thickness of drum walls
    - bottom_thickness: thickness of bottom
    - num_reinforcement_bands: number of horizontal bands
    - band_height: height of each band
    - band_thickness: how much bands protrude
    - top_rim_height: height of top rim
    - rivet_radius: radius of decorative rivets
    - rivets_per_band: number of rivets per band
    - handle_ring_radius: radius of side handle rings
    - handle_ring_thickness: thickness of handle rings
    - material_type: material type
    - body_color: color of drum body
    - band_color: color of reinforcement bands
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("IndustrialDrumBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create materials
    body_mat = create_bin_material(material_type, body_color)
    band_mat = create_bin_material(material_type, band_color)
    
    # 1. Create main drum body (outer cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        vertices=32,
        location=(0, 0, height/2)
    )
    outer_drum = bpy.context.active_object
    outer_drum.name = "Drum_Body_Outer"
    
    # Move to collection
    for coll in outer_drum.users_collection:
        coll.objects.unlink(outer_drum)
    bin_collection.objects.link(outer_drum)
    
    # 2. Create inner cylinder for hollowing
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - wall_thickness,
        depth=height - bottom_thickness + 0.01,
        vertices=32,
        location=(0, 0, height/2 + bottom_thickness)
    )
    inner_drum = bpy.context.active_object
    inner_drum.name = "Drum_Body_Inner"
    
    # Move to collection
    for coll in inner_drum.users_collection:
        coll.objects.unlink(inner_drum)
    bin_collection.objects.link(inner_drum)
    
    # Boolean to hollow
    bpy.context.view_layer.objects.active = outer_drum
    hollow_bool = outer_drum.modifiers.new(name="Hollow", type='BOOLEAN')
    hollow_bool.operation = 'DIFFERENCE'
    hollow_bool.object = inner_drum
    
    # Apply modifier
    bpy.ops.object.select_all(action='DESELECT')
    outer_drum.select_set(True)
    bpy.context.view_layer.objects.active = outer_drum
    bpy.ops.object.modifier_apply(modifier="Hollow")
    
    # Delete inner drum
    bpy.ops.object.select_all(action='DESELECT')
    inner_drum.select_set(True)
    bpy.ops.object.delete()
    
    # Apply material to body
    if outer_drum.data.materials:
        outer_drum.data.materials[0] = body_mat
    else:
        outer_drum.data.materials.append(body_mat)
    
    # 3. Create top rim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=top_rim_height/2,
        major_segments=32,
        minor_segments=12,
        location=(0, 0, height)
    )
    top_rim = bpy.context.active_object
    top_rim.name = "Drum_TopRim"
    top_rim.scale[2] = 1.3
    
    # Apply scale
    bpy.context.view_layer.objects.active = top_rim
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in top_rim.users_collection:
        coll.objects.unlink(top_rim)
    bin_collection.objects.link(top_rim)
    
    if top_rim.data.materials:
        top_rim.data.materials[0] = band_mat
    else:
        top_rim.data.materials.append(band_mat)
    
    # 4. Create reinforcement bands
    band_spacing = height / (num_reinforcement_bands + 1)
    
    for i in range(num_reinforcement_bands):
        band_z = (i + 1) * band_spacing
        
        # Create band
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius + band_thickness/2,
            minor_radius=band_height/2,
            major_segments=32,
            minor_segments=8,
            location=(0, 0, band_z)
        )
        band = bpy.context.active_object
        band.name = f"Drum_Band_{i+1}"
        
        # Move to collection and apply material
        for coll in band.users_collection:
            coll.objects.unlink(band)
        bin_collection.objects.link(band)
        
        if band.data.materials:
            band.data.materials[0] = band_mat
        else:
            band.data.materials.append(band_mat)
        
        # 5. Add rivets to this band
        rivet_angle_step = (2 * math.pi) / rivets_per_band
        
        for j in range(rivets_per_band):
            angle = j * rivet_angle_step
            rivet_x = (radius + band_thickness) * math.cos(angle)
            rivet_y = (radius + band_thickness) * math.sin(angle)
            
            # Create rivet
            bpy.ops.mesh.primitive_cylinder_add(
                radius=rivet_radius,
                depth=band_thickness + 0.005,
                vertices=8,
                location=(rivet_x, rivet_y, band_z)
            )
            rivet = bpy.context.active_object
            rivet.name = f"Drum_Rivet_B{i+1}_R{j+1}"
            rivet.rotation_euler = (0, math.pi/2, angle)
            
            # Move to collection and apply material
            for coll in rivet.users_collection:
                coll.objects.unlink(rivet)
            bin_collection.objects.link(rivet)
            
            if rivet.data.materials:
                rivet.data.materials[0] = band_mat
            else:
                rivet.data.materials.append(band_mat)
    
    # 6. Create handle rings on sides (2 opposite)
    handle_height = height * 0.7
    
    for i, angle in enumerate([0, math.pi]):
        handle_x = (radius + wall_thickness + 0.02) * math.cos(angle)
        handle_y = (radius + wall_thickness + 0.02) * math.sin(angle)
        
        # Create handle ring
        bpy.ops.mesh.primitive_torus_add(
            major_radius=handle_ring_radius,
            minor_radius=handle_ring_thickness/2,
            major_segments=24,
            minor_segments=12,
            location=(handle_x, handle_y, handle_height)
        )
        handle_ring = bpy.context.active_object
        handle_ring.name = f"Drum_HandleRing_{i+1}"
        handle_ring.rotation_euler = (0, math.pi/2, angle)
        
        # Move to collection and apply material
        for coll in handle_ring.users_collection:
            coll.objects.unlink(handle_ring)
        bin_collection.objects.link(handle_ring)
        
        if handle_ring.data.materials:
            handle_ring.data.materials[0] = band_mat
        else:
            handle_ring.data.materials.append(band_mat)
        
        # Create handle mount plate
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(handle_x * 0.85, handle_y * 0.85, handle_height)
        )
        mount = bpy.context.active_object
        mount.name = f"Drum_HandleMount_{i+1}"
        mount.scale = (0.04, 0.04, handle_ring_radius * 2.2)
        mount.rotation_euler = (0, 0, angle)
        
        # Apply transformations
        bpy.context.view_layer.objects.active = mount
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        # Move to collection and apply material
        for coll in mount.users_collection:
            coll.objects.unlink(mount)
        bin_collection.objects.link(mount)
        
        if mount.data.materials:
            mount.data.materials[0] = band_mat
        else:
            mount.data.materials.append(band_mat)
    
    # 7. Create bottom ring (base reinforcement)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius - 0.02,
        minor_radius=0.015,
        major_segments=32,
        minor_segments=8,
        location=(0, 0, 0.015)
    )
    bottom_ring = bpy.context.active_object
    bottom_ring.name = "Drum_BottomRing"
    
    # Move to collection and apply material
    for coll in bottom_ring.users_collection:
        coll.objects.unlink(bottom_ring)
    bin_collection.objects.link(bottom_ring)
    
    if bottom_ring.data.materials:
        bottom_ring.data.materials[0] = band_mat
    else:
        bottom_ring.data.materials.append(band_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Industrial drum bin created with {material_type} material")
    return bin_collection


# Example 1: Dark metal drum (default)
bin_drum = create_industrial_drum_bin(
    material_type="metal",
    body_color=(0.25, 0.25, 0.28, 1.0),
    band_color=(0.15, 0.15, 0.17, 1.0)
)

# Example 2: Rusty industrial drum
# bin_drum_rusty = create_industrial_drum_bin(
#     radius=0.4,
#     height=0.8,
#     material_type="rusty_metal",
#     body_color=(0.45, 0.45, 0.5, 1.0),
#     band_color=(0.35, 0.35, 0.4, 1.0),
#     num_reinforcement_bands=5
# )

# Example 3: Oil drum style
# bin_drum_oil = create_industrial_drum_bin(
#     radius=0.38,
#     height=0.75,
#     material_type="metal",
#     body_color=(0.1, 0.15, 0.2, 1.0),
#     band_color=(0.7, 0.5, 0.1, 1.0),  # Yellow bands
#     num_reinforcement_bands=3
# )