import bpy
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove existing materials
for material in bpy.data.materials:
    bpy.data.materials.remove(material)

def create_material(name, color):
    """Create a material with given name and color"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = (*color, 1)
    node_bsdf.inputs['Roughness'].default_value = 0.4
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_book(location, rotation, scale, color):
    """Create a single book"""
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation, scale=scale)
    book = bpy.context.active_object
    book.name = "Book"
    
    mat = create_material(f"BookMat_{random.randint(0, 10000)}", color)
    book.data.materials.append(mat)
    
    return book

def create_bookshelf(location, num_shelves=5):
    """Create a bookshelf with multiple shelves"""
    shelf_height = 2.5
    shelf_width = 2.0
    shelf_depth = 0.4
    
    # Darker walnut wood color
    wood_color = (0.25, 0.15, 0.08)
    wood_mat = create_material("WoodMat", wood_color)
    
    # Create vertical sides
    for x_offset in [-shelf_width/2, shelf_width/2]:
        bpy.ops.mesh.primitive_cube_add(
            location=(location[0] + x_offset, location[1], location[2] + shelf_height/2),
            scale=(0.05, shelf_depth/2, shelf_height/2)
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
    
    # Create shelves with increased thickness
    for i in range(num_shelves + 1):
        shelf_z = location[2] + (i * shelf_height / num_shelves)
        bpy.ops.mesh.primitive_cube_add(
            location=(location[0], location[1], shelf_z),
            scale=(shelf_width/2, shelf_depth/2, 0.04)
        )
        shelf = bpy.context.active_object
        shelf.data.materials.append(wood_mat)
        
        # Add books on each shelf (except top)
        if i < num_shelves:
            num_books = random.randint(8, 15)
            for j in range(num_books):
                # Warmer book colors
                book_colors = [
                    (0.9, 0.3, 0.2), (0.8, 0.5, 0.2), (0.6, 0.4, 0.2),
                    (0.7, 0.2, 0.3), (0.9, 0.7, 0.3), (0.6, 0.35, 0.2),
                    (0.8, 0.4, 0.3), (0.7, 0.5, 0.2)
                ]
                
                book_x = location[0] - shelf_width/2 + 0.2 + (j * (shelf_width - 0.4) / num_books)
                
                # Slightly larger books
                book_height = random.uniform(0.15, 0.25)
                book_thickness = random.uniform(0.025, 0.045)
                book_width = random.uniform(0.1, 0.14)
                
                book_y = location[1] + shelf_depth/4 - book_width/2 + random.uniform(-0.02, 0.02)
                book_z = shelf_z + 0.04 + book_height
                
                rotation = (0, 0, random.uniform(-0.05, 0.05))
                
                create_book(
                    (book_x, book_y, book_z),
                    rotation,
                    (book_thickness, book_width, book_height),
                    random.choice(book_colors)
                )

def main():
    # Create bookshelves along the walls
    bookshelf_positions = [
        (0, 0, 0),
    ]
    
    for pos in bookshelf_positions:
        create_bookshelf(pos)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(3.5, -3.5, 2))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)

main()