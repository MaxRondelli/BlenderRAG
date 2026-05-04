import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
radius = 1.5  # meters
thickness = 0.02
num_rings = 8

# Create the base mesh of the rug - SIMPLE
bpy.ops.mesh.primitive_circle_add(vertices=32, radius=radius, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Mandala_Rug"

# Fill - NO SUBDIVISION
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.fill()
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Create single material with procedural rings (NO LOOP NEEDED)
def create_mandala_material(name, num_rings):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    # Texture Coordinate
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-800, 0)
    
    # Separate XYZ to get X and Y coordinates
    separate = nodes.new(type='ShaderNodeSeparateXYZ')
    separate.location = (-600, 0)
    
    # Math nodes to calculate distance from center
    math_power_x = nodes.new(type='ShaderNodeMath')
    math_power_x.location = (-400, 100)
    math_power_x.operation = 'POWER'
    math_power_x.inputs[1].default_value = 2.0
    
    math_power_y = nodes.new(type='ShaderNodeMath')
    math_power_y.location = (-400, -100)
    math_power_y.operation = 'POWER'
    math_power_y.inputs[1].default_value = 2.0
    
    math_add = nodes.new(type='ShaderNodeMath')
    math_add.location = (-200, 0)
    math_add.operation = 'ADD'
    
    math_sqrt = nodes.new(type='ShaderNodeMath')
    math_sqrt.location = (0, 0)
    math_sqrt.operation = 'SQRT'
    
    # Multiply by number of rings
    math_multiply = nodes.new(type='ShaderNodeMath')
    math_multiply.location = (200, 0)
    math_multiply.operation = 'MULTIPLY'
    math_multiply.inputs[1].default_value = num_rings / radius
    
    # ColorRamp for rings
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (400, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    
    # Add color stops for three colors
    while len(ramp.color_ramp.elements) < 3:
        ramp.color_ramp.elements.new(0.5)
    
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.7, 0.3, 0.2, 1.0)  # Terracotta
    
    ramp.color_ramp.elements[1].position = 0.33
    ramp.color_ramp.elements[1].color = (0.9, 0.85, 0.7, 1.0)  # Cream
    
    ramp.color_ramp.elements[2].position = 0.66
    ramp.color_ramp.elements[2].color = (0.4, 0.25, 0.15, 1.0)  # Brown
    
    # Noise for variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (200, -200)
    noise.inputs['Scale'].default_value = 100.0
    noise.inputs['Detail'].default_value = 10.0
    
    # Mix noise with base color
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (600, -100)
    mix.blend_type = 'MIX'
    mix.inputs['Fac'].default_value = 0.15
    
    # Voronoi for fiber texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (200, -400)
    voronoi.inputs['Scale'].default_value = 180.0
    
    # Bump
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (400, -300)
    bump.inputs['Strength'].default_value = 0.4
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], separate.inputs['Vector'])
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])
    
    links.new(separate.outputs['X'], math_power_x.inputs[0])
    links.new(separate.outputs['Y'], math_power_y.inputs[0])
    links.new(math_power_x.outputs[0], math_add.inputs[0])
    links.new(math_power_y.outputs[0], math_add.inputs[1])
    links.new(math_add.outputs[0], math_sqrt.inputs[0])
    links.new(math_sqrt.outputs[0], math_multiply.inputs[0])
    links.new(math_multiply.outputs[0], ramp.inputs['Fac'])
    
    links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    if 'Distance' in voronoi.outputs:
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    else:
        links.new(voronoi.outputs[0], bump.inputs['Height'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create and assign material
mandala_mat = create_mandala_material("Mandala_Material", num_rings)
rug.data.materials.append(mandala_mat)

# Add Subdivision Surface modifier for realism
subsurf = rug.modifiers.new(name="Subdivision", type="SUBSURF")
subsurf.levels = 2
subsurf.render_levels = 3

# Position light and camera for better visualization
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
light = bpy.context.active_object
light.data.energy = 4.0

bpy.ops.object.camera_add(location=(2.5, -3.5, 3.0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set rendering engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Mandala rug created successfully!")
print("=" * 50)
print("Radius: {} meters".format(radius))
print("Rings: {} (in earth tones)".format(num_rings))
print("")
print("INSTRUCTIONS:")
print("1. Press Z in viewport and select 'Material Preview' or 'Rendered'")
print("2. To render final image: press F12")
print("3. You can modify parameters at the beginning of the script")
print("=" * 50)