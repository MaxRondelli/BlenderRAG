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


def create_wicker_basket_bin(
    bottom_radius=0.25,
    top_radius=0.35,
    height=0.5,
    num_vertical_strips=24,
    num_horizontal_bands=10,
    strip_width=0.015,
    strip_thickness=0.004,
    rim_height=0.025,
    rim_width=0.03,
    base_thickness=0.01,
    material_type="wood",
    color=(0.6, 0.4, 0.2, 1.0)
):
    """
    Create a tapered wicker-style basket bin
    
    Parameters:
    - bottom_radius: radius at the bottom
    - top_radius: radius at the top (larger for tapered look)
    - height: height of the basket
    - num_vertical_strips: number of vertical wicker strips
    - num_horizontal_bands: number of horizontal weaving bands
    - strip_width: width of each wicker strip
    - strip_thickness: thickness of the strips
    - rim_height: height of the decorative rim
    - rim_width: width of the rim
    - base_thickness: thickness of the base
    - material_type: material type
    - color: RGBA tuple for color
    """
    
    # Create collection
    bin_collection = bpy.data.collections.new("WickerBasketBin")
    bpy.context.scene.collection.children.link(bin_collection)
    
    # Create material
    mat = create_bin_material(material_type, color)
    
    # 1. Create base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=bottom_radius,
        depth=base_thickness,
        vertices=32,
        location=(0, 0, base_thickness/2)
    )
    base = bpy.context.active_object
    base.name = "Basket_Base"
    
    # Move to collection and apply material
    for coll in base.users_collection:
        coll.objects.unlink(base)
    bin_collection.objects.link(base)
    
    if base.data.materials:
        base.data.materials[0] = mat
    else:
        base.data.materials.append(mat)
    
    # 2. Create vertical strips (tapered)
    angle_step = (2 * math.pi) / num_vertical_strips
    
    for i in range(num_vertical_strips):
        angle = i * angle_step
        
        # Create a tapered strip using a cube scaled and positioned
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, 0, height/2 + base_thickness)
        )
        strip = bpy.context.active_object
        strip.name = f"Basket_VerticalStrip_{i+1}"
        
        # Position at bottom
        bottom_x = bottom_radius * math.cos(angle)
        bottom_y = bottom_radius * math.sin(angle)
        
        # Position at top
        top_x = top_radius * math.cos(angle)
        top_y = top_radius * math.sin(angle)
        
        # Average position
        avg_x = (bottom_x + top_x) / 2
        avg_y = (bottom_y + top_y) / 2
        
        strip.location = (avg_x, avg_y, height/2 + base_thickness)
        strip.scale = (strip_thickness, strip_width, height)
        
        # Rotate to face center
        strip.rotation_euler = (0, 0, angle)
        
        # Apply transformations
        bpy.context.view_layer.objects.active = strip
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        # Enter edit mode to taper the strip
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Use proportional editing to create taper effect
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Manual vertex adjustment for taper
        mesh = strip.data
        for vert in mesh.vertices:
            # Get relative height (0 at bottom, 1 at top)
            rel_height = (vert.co.z + height/2) / height
            
            # Scale outward based on height
            scale_factor = bottom_radius + (top_radius - bottom_radius) * rel_height
            original_radius = bottom_radius + (top_radius - bottom_radius) * 0.5
            
            if abs(vert.co.x) > 0.001 or abs(vert.co.y) > 0.001:
                # Adjust X and Y to create taper
                direction_x = math.cos(angle)
                direction_y = math.sin(angle)
                
                vert.co.x = direction_x * (scale_factor - strip_thickness/2)
                vert.co.y = direction_y * (scale_factor - strip_thickness/2)
        
        # Move to collection and apply material
        for coll in strip.users_collection:
            coll.objects.unlink(strip)
        bin_collection.objects.link(strip)
        
        if strip.data.materials:
            strip.data.materials[0] = mat
        else:
            strip.data.materials.append(mat)
    
    # 3. Create horizontal weaving bands
    band_spacing = height / (num_horizontal_bands + 1)
    
    for i in range(num_horizontal_bands):
        band_z = base_thickness + (i + 1) * band_spacing
        
        # Calculate radius at this height
        height_ratio = (band_z - base_thickness) / height
        band_radius = bottom_radius + (top_radius - bottom_radius) * height_ratio
        
        # Create band as a torus
        bpy.ops.mesh.primitive_torus_add(
            major_radius=band_radius,
            minor_radius=strip_thickness/2,
            major_segments=num_vertical_strips * 2,
            minor_segments=6,
            location=(0, 0, band_z)
        )
        band = bpy.context.active_object
        band.name = f"Basket_HorizontalBand_{i+1}"
        band.scale[2] = strip_width / strip_thickness
        
        # Apply scale
        bpy.context.view_layer.objects.active = band
        bpy.ops.object.transform_apply(scale=True)
        
        # Move to collection and apply material
        for coll in band.users_collection:
            coll.objects.unlink(band)
        bin_collection.objects.link(band)
        
        if band.data.materials:
            band.data.materials[0] = mat
        else:
            band.data.materials.append(mat)
    
    # 4. Create decorative rim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=top_radius + rim_width/2,
        minor_radius=rim_height/2,
        major_segments=48,
        minor_segments=12,
        location=(0, 0, height + base_thickness)
    )
    rim = bpy.context.active_object
    rim.name = "Basket_Rim"
    rim.scale[2] = rim_width / rim_height
    
    # Apply scale
    bpy.context.view_layer.objects.active = rim
    bpy.ops.object.transform_apply(scale=True)
    
    # Move to collection and apply material
    for coll in rim.users_collection:
        coll.objects.unlink(rim)
    bin_collection.objects.link(rim)
    
    # Darker rim material
    rim_color = (color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, color[3])
    rim_mat = create_bin_material(material_type, rim_color)
    
    if rim.data.materials:
        rim.data.materials[0] = rim_mat
    else:
        rim.data.materials.append(rim_mat)
    
    # Smooth shading
    for obj in bin_collection.objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    print(f"Wicker basket bin created with {material_type} material")
    return bin_collection


# Example 1: Natural wicker basket
bin_wicker = create_wicker_basket_bin(
    material_type="wood",
    color=(0.6, 0.4, 0.2, 1.0)  # Natural wicker color
)

# Example 2: White painted wicker
# bin_wicker_white = create_wicker_basket_bin(
#     bottom_radius=0.3,
#     top_radius=0.38,
#     height=0.55,
#     material_type="plastic",
#     color=(0.95, 0.95, 0.92, 1.0)
# )

# Example 3: Dark stained basket
# bin_wicker_dark = create_wicker_basket_bin(
#     bottom_radius=0.28,
#     top_radius=0.4,
#     height=0.6,
#     num_vertical_strips=32,
#     num_horizontal_bands=12,
#     material_type="wood",
#     color=(0.25, 0.15, 0.08, 1.0)
# )