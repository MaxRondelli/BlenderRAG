bl_info = {
    "name": "BlenderRAG",
    "author": "Rondelli et al.",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BlenderRAG",
    "description": "BlenderRAG Add-On for indoor and outdoor objects generation",
    "category": "3D View",
}

import os
import sys
import bpy
from .properties import RAGProperties
from .panels import RAG_PT_Main, RAG_PT_Settings
from bpy.props import PointerProperty
import subprocess

# add the 'lib' folder to the Python path
libs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

_dependencies_ready = False
_import_error = ""
def install_dependencies():
    """Install required packages to lib folder"""
    
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    lib_path = os.path.join(addon_dir, "lib")
    
    print(f"Installing to: {lib_path}")
    
    os.makedirs(lib_path, exist_ok=True)

    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    
    try:
        # Step 1: Install PyTorch 2.8.0 specifically (CPU version)
        print("Installing PyTorch 2.8.0 (CPU)...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0",
            "-t", lib_path,
            "--no-cache-dir",
            "--upgrade"
        ])
        
        # Step 2: Install sentence-transformers and its dependencies WITHOUT torch
        print("Installing sentence-transformers dependencies (excluding torch)...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "transformers", "huggingface-hub", "safetensors", 
            "tqdm", "scikit-learn", "scipy", "requests",
            "tokenizers", "filelock", "numpy", "packaging",
            "pyyaml", "regex", "pillow", "einops",
            "-t", lib_path,
            "--no-cache-dir",
            "--upgrade"
        ])
        
        # Step 3: Install sentence-transformers with --no-deps to prevent torch reinstall
        print("Installing sentence-transformers (no dependencies)...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "sentence-transformers",
            "-t", lib_path,
            "--no-cache-dir",
            "--no-deps",
            "--upgrade"
        ])
        
        # Step 4: Install qdrant-client dependencies first
        print("Installing qdrant-client dependencies...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "grpcio", "grpcio-tools", "httpx", "portalocker",
            "-t", lib_path,
            "--no-cache-dir",
            "--upgrade"
        ])
        
        # Step 5: Install qdrant-client with --no-deps
        print("Installing qdrant-client (no dependencies)...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "qdrant-client",
            "-t", lib_path,
            "--no-cache-dir",
            "--no-deps",
            "--upgrade"
        ])
        
        # Step 6: Install datapizza-ai WITHOUT --no-deps but with --no-dependencies for torch
        print("Installing datapizza-ai...")
        subprocess.check_call([
            python_exe, "-m", "pip", "install",
            "datapizza-ai", "datapizza-ai-clients-mistral", "datapizza-ai-clients-anthropic", 
            "datapizza-ai-clients-google", "datapizza-ai-clients-openai",
            "-t", lib_path,
            "--no-cache-dir",
            "--upgrade"
        ])
        
        # Step 7: Verify torch version hasn't changed
        print("\nVerifying PyTorch installation...")
        lib_path_escaped = lib_path.replace('\\', '\\\\')
        result = subprocess.check_output([
            python_exe, "-c", 
            f"import sys; sys.path.insert(0, '{lib_path_escaped}'); import torch; print(f'PyTorch version: {{torch.__version__}}')"
        ])
        print(result.decode())
        print("Installation complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def check_dependencies():
    """Check if dependencies are available"""
    global _dependencies_ready, _import_error
    
    try:
        import torch
        import sentence_transformers
        from datapizza.core.vectorstore import Distance
        from qdrant_client import QdrantClient
        # Verify torch version
        print(f"Blender500: PyTorch version: {torch.__version__}")
        if not torch.__version__.startswith("2.8"):
            print(f"WARNING: Expected PyTorch 2.8.x but found {torch.__version__}")
        
        _dependencies_ready = True
        print("Blender500: All dependencies loaded successfully!")
        return True
    except ImportError as e:
        _import_error = str(e)
        print(f"Blender500: Dependencies missing - {e}")
        _dependencies_ready = False
        return False

# Check dependencies but don't fail if missing
check_dependencies()
# Install operator - must be defined before checking dependencies
class RAG_OT_InstallDependencies(bpy.types.Operator):
    bl_idname = "rag.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Install required Python packages"
    
    def execute(self, context):
        self.report({'INFO'}, "Installing dependencies... This may take a few minutes.")
        print("Starting dependency installation...")
        
        if install_dependencies():
            # Recheck dependencies
            if check_dependencies():
                self.report({'INFO'}, "Dependencies installed successfully! Please restart Blender.")
            else:
                self.report({'WARNING'}, "Packages installed but imports failed. Please restart Blender.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to install dependencies. Check console for details.")
            return {'CANCELLED'}

def get_classes():
    """Return classes to register based on dependency availability"""
    base_classes = [
        RAG_OT_InstallDependencies,
        RAGProperties,
        RAG_PT_Main,
        RAG_PT_Settings,
    ]
    
    if _dependencies_ready:
        try:
            from .operators import RAG_OT_Generate, RAG_OT_Clear
            return tuple(base_classes + [RAG_OT_Generate, RAG_OT_Clear])
        except ImportError as e:
            print(f"Warning: Could not import operators - {e}")
            return tuple(base_classes)
    
    return tuple(base_classes)


def register():
    global classes
    classes = get_classes()

    print(f"Registering {len(classes)} classes...")
    for cls in classes:
        print(f"  Registering: {cls.__name__}")
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.rag_props = PointerProperty(type=RAGProperties)
    
    if _dependencies_ready:
        print("Blender500: Ready to use!")
    else:
        print("Blender500: Dependencies missing - use 'Install Dependencies' button")

def unregister():
    global classes
    
    if _dependencies_ready:
        try:
            from .rag import get_rag_manager
            rag = get_rag_manager()
            rag.unload()
        except Exception as e:
            print(f"Error during unload: {e}")
    
    del bpy.types.Scene.rag_props
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {e}")

if __name__ == "__main__":
    register()
