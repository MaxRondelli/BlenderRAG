# BlenderRAG

### High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis

[![Paper](https://img.shields.io/badge/Paper-arXiv-b31b1b.svg)](https://arxiv.org/abs/2605.00632)
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow.svg)](https://huggingface.co/datasets/MaxRondelli/BlenderRAG)
[![HF Page](https://img.shields.io/badge/HF-Page-blue.svg)](https://huggingface.co/papers/2605.00632)
[![Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-2ea44f.svg)](https://maxrondelli.github.io/BlenderRAG/)

**BlenderRAG** is a retrieval-augmented generation system that turns natural language descriptions into high-fidelity 3D objects in Blender. Distributed as a native Blender Add-on, it combines semantic retrieval over a curated code dataset with LLM-driven Python synthesis — so you can describe an object and watch it appear in your scene.

> 💬 *"a modern wooden chair with armrests"* → 🪑 *generated mesh in your viewport*

---

## 🎬 Demo

🌐 **Live site:** **[maxrondelli.github.io/BlenderRAG](https://maxrondelli.github.io/BlenderRAG/)**

The companion website lets you:

- 📄 Read the paper and grab the BibTeX citation in one click.
- 🧭 **Browse the dataset** — 50 categories (25 indoor + 25 outdoor), 10 variants each.
- 🖼️ **Inspect each generated mesh** — high-resolution rendered preview, natural-language description, and the full Blender Python script that produces it.
- 📋 **Copy or download** the generating code with a single click and run it directly in Blender to reproduce the mesh.
- 🔍 Filter by scene (Indoor / Outdoor) and search categories by name.

The site is a static page hosted on **GitHub Pages** (sources live in [`/docs`](./docs)) and streams images, code, and descriptions live from the [Hugging Face dataset](https://huggingface.co/datasets/MaxRondelli/BlenderRAG) — no separate backend required.

> 🚀 **Enabling the demo (one-time):** in the repo settings go to **Settings → Pages → Build and deployment**, set **Source: Deploy from a branch**, **Branch: `main` / `/docs`**, and save. The site will be live at the URL above within a minute.

---

## 🔭 Overview

Generating 3D content from text remains challenging: end-to-end mesh generators often produce low-fidelity results, while code-driven approaches struggle with the breadth of Blender's API. **BlenderRAG** bridges this gap by retrieving semantically similar (description, code) pairs from a curated dataset and conditioning an LLM on them to produce executable Blender Python code.

The result: cleaner geometry, more controllable outputs, and a workflow that lives directly inside Blender.

---

## ✨ Key Features

- 🧩 **Native Blender Add-on** — install once, use from the 3D viewport sidebar.
- 🔍 **Retrieval-Augmented Generation** — grounds LLM output in a curated dataset of Blender code examples.
- 🤖 **Multi-LLM Support** — switch between open and closed-source language models.
- ⚡ **Automatic Code Execution** — generated Python runs in Blender without manual intervention.
- 🗂️ **Local Vector Database** — Qdrant-based retrieval, initialized automatically on first use.
- 🧠 **Semantic Embeddings** — powered by Nomic-AI for high-quality similarity search.

---

## ⚙️ How It Works

![alt text](assets/blender-rag-pipeline.jpg)

On first run, the add-on initializes a local Qdrant database and indexes the BlenderRAG dataset. Each subsequent prompt retrieves the top-*k* most similar examples and conditions the LLM on them to synthesize Blender Python code, which is then executed directly in your scene.

---

## 🚀 Setup

### Prerequisites

- **Blender** 4.0 or later
- **Python** 3.12
- **Conda** (recommended) or any Python environment manager
- An API key for your chosen LLM provider (if using a closed model)

### Installation

Clone the repository and set up the Python environment:

```bash
git clone https://github.com/<your-org>/BlenderRAG.git
cd BlenderRAG

conda create -n blender_rag python=3.12
conda activate blender_rag
pip install -r requirements.txt
```

---

## 🧩 Blender Add-on Installation

The add-on is installed in three steps: import the project, download dependencies, and configure.

### Step 1 — Import the project into Blender

1. Create a `.zip` archive of the repository (compress the project folder).
2. In Blender, open **Edit → Preferences → Add-ons**.
3. Click the dropdown in the top-right corner and select **Install from Disk**.
4. Choose the `.zip` file you created.
5. Once imported, open the BlenderRAG panel in the **right sidebar** of the 3D viewport (press `N` if it's hidden).

### Step 2 — Download necessary dependencies

1. Open the **BlenderRAG** panel in the sidebar.
2. Click **Install Dependencies** to download the required packages.
3. Monitor progress in the **Blender Python Console**:
   - **Windows:** *Window → Toggle System Console*
   - **macOS / Linux:** *Scripting* workspace → *Python Console*

> ⚠️ **Important:** You **must restart Blender** after installation completes for the dependencies to load correctly.

### Step 3 — Configure the add-on

In the **Settings** section of the BlenderRAG panel, configure:

| Setting | Description |
|---|---|
| **LLM Selection** | Choose your preferred language model (open or closed source). |
| **API Key** | Required for closed models. Paste it into the corresponding field. |
| **Retrieval Count** (`k`) | Number of similar examples to retrieve from the vector database. |

---

## 🎨 Usage

1. Open the BlenderRAG panel in the 3D viewport sidebar.
2. Enter a natural language description in the prompt box, for example:
   > `a modern wooden chair with armrests`
3. Click **Generate**.

   > 📝 **First-run note:** On your first prompt, the system automatically initializes the Qdrant vector database and indexes the dataset. This is a **one-time process** and may take a few minutes.

After initialization, every prompt follows this pipeline:

1. **Embed** your description using Nomic-AI.
2. **Retrieve** the *k* most semantically similar examples from the vector DB.
3. **Prompt** the selected LLM with your description plus the retrieved context (text + code).
4. **Execute** the generated Python code in Blender.
5. **Display** the resulting 3D object in your active scene.

The entire flow is seamless — once the LLM responds, execution happens automatically.

> 💡 **Tip:** Increase the **Retrieval Count** for more contextually grounded outputs on complex objects. Decrease it for faster, more open-ended generations.

---

## 🛠️ Troubleshooting

<details>
<summary><strong>The add-on doesn't appear after installation</strong></summary>

Make sure it's enabled: **Edit → Preferences → Add-ons**, search for "BlenderRAG", and tick the checkbox.
</details>

<details>
<summary><strong>Dependencies fail to install</strong></summary>

Check that Blender has internet access and that you've launched Blender with sufficient permissions. On Windows, try running Blender as administrator. Then click **Install Dependencies** again.
</details>

<details>
<summary><strong>"Module not found" errors after installing dependencies</strong></summary>

You probably skipped the Blender restart. Close Blender completely and reopen it.
</details>

<details>
<summary><strong>The first prompt is very slow</strong></summary>

Expected — the vector database is being built and indexed. Subsequent prompts will be much faster.
</details>

<details>
<summary><strong>Generated code fails to execute</strong></summary>

Check the Blender System Console for the error. Common causes are unsupported Blender versions or API key issues. Try regenerating with a higher retrieval count for more grounded output.
</details>

---

## 📚 Citation

If you use BlenderRAG in your research, please cite us:

```bibtex
@misc{rondelli2026blenderraghighfidelity3dobject,
      title={BlenderRAG: High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis},
      author={Massimo Rondelli and Francesco Pivi and Maurizio Gabbrielli},
      year={2026},
      eprint={2605.00632},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2605.00632},
}
```
