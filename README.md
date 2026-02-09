# [IJCAI-ECAI 2026] BlenderRAG: High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis

BlenderRAG is a retrieval-augmented generation system for creating high-fidelity 3D objects in Blender from natural language descriptions, implemented as a native Blender Add-on.

## Setup
Clone the repository, create conda enviornment and install the required packages as follows.
```bash
conda create -n blender_rag python=3.12
conda activate blender_rag
pip install -r requirements.txt
```

## Blender Add-on installation
In this section we provide information about how to make the installation of the Add-on. We divide this section into three parts: 
1. Add the project into the Blender environment.
2. Download necessary dependencies. 
3. Use of BlenderRAG Add-on.

### Step 1. Add the Project into the Blender Environment
- To import the add-on into Blender, you must create a `.zip` file of this repository. Then, navigate through the Blender UI to **Edit > Preferences > Add-ons**.
- Click the dropdown menu in the top-right corner and select **Install from Disk**. Choose the `.zip` file of this repository. 
- Once imported, you can access the BlenderRAG UI in the right sidebar ( press `N` if hidden) of Blender's 3D viewport.

### Step 2. Download necessary dependencies.
- Once the add-on is installed, open the BlenderRAG panel in the right sidebar. Click the **Install Dependencies** button to download the required packages.
You can monitor the installation progress by opening the **Blender Python Console** (Window > Toggle System Console on Windows, or **Scripting** workspace > Python Console).
- **Important:** you MUST restart Blender once the installation is complete for the dependencies to be properly loaded. 

### Step 3. Use the Blender-RAG add-on
- Navigate to the **Settings** section in the UI to configure: 
    - LLM Selection: choose the prefered language model.
    - API Key: for closed models, provide the API key in the correspoding field. 
    - Retrieval Count: set the number of similar examples to retrieve from the vector db.  
- Enter your desired object description in the text box (e.g., "a modern wooden chair with armrests")

When you send your first prompt, the system automatically initializes the Qdrant vector database and indexes the custom dataset. This is a one-time process.

After the first initialization, subsequent prompts will:
1. Embed your text description using Nomic-AI.
2. Retrieve the k most semantically similar examples from the vector database.
3. Send the retrieved context (text + code) along with your prompt to the selected LLM.
4. Automatically execute the generated Python code in Blender.
5. Display the resulting 3D object in your current scene.

The entire process is seamless—once the LLM generates the code, execution happens automatically without manual intervention.