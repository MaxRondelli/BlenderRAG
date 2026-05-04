import bpy
import random
import math
# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
# Remove existing materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

def create_material(name, color, metallic=0.0, roughness=0.7):
    """Create a material with given name, color, and properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (*color, 1)
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_book(location, rotation, scale, color):
    """Create a single book"""
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation, scale=scale)
    book = bpy.context.active_object
    book.name = "Book"
    
    mat = create_material(f"BookMat_{random.randint(0, 10000)}", color, roughness=0.8)
    book.data.materials.append(mat)
    
    return book

def create_bookshelf(location, num_shelves=5):
    """Create a bookshelf with multiple shelves"""
    shelf_height = 2.5
    shelf_width = 2.0
    shelf_depth = 0.4
    
    # Darker walnut wood color
    wood_color = (0.25, 0.15, 0.1)
    wood_mat = create_material("WalnutMat", wood_color, roughness=0.4)
    
    # Metallic brass accent material
    brass_color = (0.6, 0.45, 0.2)
    brass_mat = create_material("BrassMat", brass_color, metallic=0.8, roughness=0.2)
    
    # Create vertical sides
    for x_offset in [-shelf_width/2, shelf_width/2]:
        bpy.ops.mesh.primitive_cube_add(
            location=(location[0] + x_offset, location[1], location[2] + shelf_height/2),
            scale=(0.06, shelf_depth/2, shelf_height/2)
        )
        side = bpy.context.active_object
        side.data.materials.append(wood_mat)
    
    # Create back panel
    bpy.ops.mesh.primitive_cube_add(
        location=(location[0], location[1] - shelf_depth/2 + 0.025, location[2] + shelf_height/2),
        scale=(shelf_width/2, 0.025, shelf_height/2)
    )
    back = bpy.context.active_object
    back.data.materials.append(wood_mat)
    
    # Create shelves with brass accents
    for i in range(num_shelves + 1):
        shelf_z = location[2] + (i * shelf_height / num_shelves)
        
        # Main shelf
        bpy.ops.mesh.primitive_cube_add(
            location=(location[0], location[1], shelf_z),
            scale=(shelf_width/2, shelf_depth/2, 0.03)
        )
        shelf = bpy.context.active_object
        shelf.data.materials.append(wood_mat)
        
        # Brass accent strip on front edge
        bpy.ops.mesh.primitive_cube_add(
            location=(location[0], location[1] + shelf_depth/2 - 0.01, shelf_z + 0.035),
            scale=(shelf_width/2 - 0.1, 0.005, 0.008)
        )
        accent = bpy.context.active_object
        accent.data.materials.append(brass_mat)
        
        # Add books on each shelf (except top)
        if i < num_shelves:
            num_books = random.randint(8, 15)
            for j in range(num_books):
                # More sophisticated, muted color palette
                book_colors = [
                    (0.35, 0.25, 0.2), (0.2, 0.3, 0.4), (0.25, 0.35, 0.25),
                    (0.4, 0.3, 0.35), (0.45, 0.35, 0.25), (0.3, 0.25, 0.2),
                    (0.25, 0.3, 0.35), (0.4, 0.3, 0.25), (0.3, 0.3, 0.3)
                ]
                
                book_x = location[0] - shelf_width/2 + 0.2 + (j * (shelf_width - 0.4) / num_books)
                
                book_height = random.uniform(0.12, 0.22)
                book_thickness = random.uniform(0.02, 0.04)
                book_width = random.uniform(0.08, 0.12)
                
                book_y = location[1] + shelf_depth/4 - book_width/2 + random.uniform(-0.02, 0.02)
                book_z = shelf_z + 0.03 + book_height
                
                rotation = (0, 0, random.uniform(-0.05, 0.05))
                
                create_book(
                    (book_x, book_y, book_z),
                    rotation,
                    (book_thickness, book_width, book_height),
                    random.choice(book_colors)
                )

def main():
    # Create bookshelf
    bookshelf_positions = [
        (0, 0, 0),
    ]
    
    for pos in bookshelf_positions:
        create_bookshelf(pos)
    
    # Position camera for best view
    bpy.ops.object.camera_add(location=(4, -3, 2))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    bpy.context.scene.camera = camera

main()