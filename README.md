<div align="center">

# 🎨 BlenderRAG

### High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis

<p>
  <a href="https://arxiv.org/abs/2605.00632"><img alt="Paper" src="https://img.shields.io/badge/📄_Paper-arXiv%3A2605.00632-b31b1b?style=for-the-badge"></a>
  <a href="https://huggingface.co/datasets/MaxRondelli/BlenderRAG"><img alt="Dataset" src="https://img.shields.io/badge/🤗_Dataset-HuggingFace-FFD21F?style=for-the-badge"></a>
  <a href="https://huggingface.co/papers/2605.00632"><img alt="HF Paper" src="https://img.shields.io/badge/📰_HF_Page-Discuss-3578E5?style=for-the-badge"></a>
  <a href="https://maxrondelli.github.io/BlenderRAG/"><img alt="Demo" src="https://img.shields.io/badge/🚀_Live_Demo-GitHub_Pages-2ea44f?style=for-the-badge"></a>
</p>

<p>
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/MaxRondelli/BlenderRAG?style=social">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Blender" src="https://img.shields.io/badge/Blender-4.0+-F5792A?logo=blender&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
</p>

<br/>

<h3>
  💬 <i>"a modern wooden chair with armrests"</i> &nbsp;➜&nbsp; 🪑 <i>generated mesh in your viewport</i>
</h3>

<br/>

<a href="https://maxrondelli.github.io/BlenderRAG/">
  <img alt="Live Demo" src="https://img.shields.io/badge/▶_Try_the_Live_Demo-Browse_500_meshes,_descriptions_and_code-e0223a?style=for-the-badge">
</a>

</div>

---

## 📑 Table of Contents

- [🎬 Demo](#-demo)
- [🔭 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Setup](#-setup)
- [🧩 Blender Add-on Installation](#-blender-add-on-installation)
- [🎨 Usage](#-usage)
- [📊 The Dataset](#-the-dataset)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [👥 Authors](#-authors)
- [📚 Citation](#-citation)

---

## 🎬 Demo

> 🌐 **Live site:** **<https://maxrondelli.github.io/BlenderRAG/>**

<div align="center">
  <a href="https://maxrondelli.github.io/BlenderRAG/">
    <img alt="Open the live demo" src="https://img.shields.io/badge/Open_the_Live_Demo-→-e0223a?style=for-the-badge&logo=github">
  </a>
</div>

The companion website is a **fully static page hosted on GitHub Pages** (sources in [`/docs`](./docs)) that ships:

| | |
|---|---|
| 🎠 **Infinite rotating gallery** | All 49 categories sliding past in two opposite-direction rows on the landing page. |
| 🧪 **Curated random sample** | A shuffleable 24-mesh sample, with a one-click *Shuffle* button — surfaces only the meshes that compiled cleanly. |
| 🔄 **Real 3D meshes** | Every card is an actual `.glb`, rendered in-browser with [`<model-viewer>`](https://modelviewer.dev/), auto-rotating with orbit/zoom controls. |
| 🖼️ **Original render side-by-side** | When you open a variant, you see the rotating mesh, the original PNG render, the natural-language description, and the generating Blender Python — all together. |
| 📋 **Copy / Download** | One-click copy of the Python script or download as `.py` to reproduce in your own Blender. |
| 🎥 **Walkthrough video** | A short demo of the add-on in action. |
| ⭐ **Live GitHub stars** | Star count fetched live from the GitHub API on page load. |

> 🔧 **First-time setup (admin only):** **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `/docs` → Save.** The site is then live at the URL above.

---

## 🔭 Overview

Generating 3D content from text remains challenging:

- ❌ **End-to-end mesh generators** often produce low-fidelity, blob-like geometry.
- ❌ **Code-driven approaches** struggle with the breadth of Blender's API and produce broken scripts.

**BlenderRAG bridges this gap** by retrieving semantically similar `(description, code)` pairs from a curated dataset and conditioning an LLM on them to produce executable Blender Python code.

> ✅ The result: **cleaner geometry, more controllable outputs, and a workflow that lives directly inside Blender** as a native add-on.

---

## ✨ Key Features

| | |
|---|---|
| 🧩 **Native Blender Add-on** | Install once, use from the 3D viewport sidebar. |
| 🔍 **Retrieval-Augmented Generation** | Grounds LLM output in a curated dataset of Blender code examples. |
| 🤖 **Multi-LLM Support** | Switch between open and closed-source language models. |
| ⚡ **Automatic Code Execution** | Generated Python runs in Blender without manual intervention. |
| 🗂️ **Local Vector Database** | Qdrant-based retrieval, initialized automatically on first use. |
| 🧠 **Semantic Embeddings** | Powered by Nomic-AI for high-quality similarity search. |

---

## ⚙️ How It Works

<p align="center">
  <img alt="BlenderRAG pipeline" src="assets/blender-rag-pipeline.jpg" width="850">
</p>

1. **Embed** — your description is encoded with Nomic-AI.
2. **Retrieve** — top-*k* similar `(description, code)` pairs are pulled from the local Qdrant vector DB.
3. **Prompt** — the selected LLM gets your description + retrieved context as in-context examples.
4. **Execute** — the generated Python is run inside Blender.
5. **Display** — the resulting mesh appears in your scene, ready to edit.

> 📝 On first run, the add-on bootstraps the local Qdrant DB and indexes the BlenderRAG dataset. This is a one-time process; subsequent prompts are fast.

---

## 🚀 Setup

### Prerequisites

| Requirement | Version |
|---|---|
| 🟧 [Blender](https://www.blender.org/) | 4.0+ |
| 🐍 Python | 3.12 |
| 📦 Conda *(recommended)* | any |
| 🔑 LLM API key | optional — only for closed-source models |

### Installation

```bash
git clone https://github.com/MaxRondelli/BlenderRAG.git
cd BlenderRAG

conda create -n blender_rag python=3.12
conda activate blender_rag
pip install -r requirements.txt
```

---

## 🧩 Blender Add-on Installation

<details open>
<summary><strong>① Import the project into Blender</strong></summary>

1. Create a `.zip` archive of the repository (compress the project folder).
2. In Blender, open **Edit → Preferences → Add-ons**.
3. Click the dropdown in the top-right corner → **Install from Disk**.
4. Choose the `.zip` you created.
5. Open the BlenderRAG panel in the **right sidebar** of the 3D viewport (press <kbd>N</kbd> if hidden).

</details>

<details>
<summary><strong>② Download dependencies</strong></summary>

1. Open the **BlenderRAG** panel in the sidebar.
2. Click **Install Dependencies**.
3. Monitor progress in the **Blender Python Console**:
   - **Windows:** *Window → Toggle System Console*
   - **macOS / Linux:** *Scripting* workspace → *Python Console*

> ⚠️ You **must restart Blender** after installation completes for the dependencies to load correctly.

</details>

<details>
<summary><strong>③ Configure the add-on</strong></summary>

In the **Settings** section of the BlenderRAG panel:

| Setting | Description |
|---|---|
| **LLM Selection** | Choose your preferred language model (open or closed source). |
| **API Key** | Required for closed models. Paste it into the corresponding field. |
| **Retrieval Count** (`k`) | Number of similar examples to retrieve from the vector DB. |

</details>

---

## 🎨 Usage

1. Open the BlenderRAG panel in the 3D viewport sidebar.
2. Enter a natural language description in the prompt box, e.g.:
   > `a modern wooden chair with armrests`
3. Click **Generate** ✨

> 💡 **Tip:** Increase the **Retrieval Count** for more contextually grounded outputs on complex objects. Decrease it for faster, more open-ended generations.

---

## 📊 The Dataset

The [BlenderRAG Hugging Face dataset](https://huggingface.co/datasets/MaxRondelli/BlenderRAG) contains:

<div align="center">

|  | Indoor | Outdoor | **Total** |
|---|:---:|:---:|:---:|
| **Categories** | 25 | 25 | **50** |
| **Variants per category** | 10 | 10 | **10** |
| **Objects** | 250 | 250 | **500** |

</div>

Each variant ships with three artifacts:

- 🖼️ **`imageN.png`** — high-resolution rendered preview
- 💻 **`codeN.py`** — Blender Python script that produces the mesh
- 📝 **`txtN.txt`** — natural-language description used for retrieval

🎮 **Browse it interactively** in the [live demo](https://maxrondelli.github.io/BlenderRAG/) — the site streams meshes, images and code straight from Hugging Face.

---

## 🛠️ Troubleshooting

<details>
<summary><strong>The add-on doesn't appear after installation</strong></summary>

Make sure it's enabled: **Edit → Preferences → Add-ons**, search for "BlenderRAG", and tick the checkbox.
</details>

<details>
<summary><strong>Dependencies fail to install</strong></summary>

Check that Blender has internet access and that you've launched it with sufficient permissions. On Windows, try running Blender as administrator. Then click **Install Dependencies** again.
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

## 👥 Authors

<div align="center">

| Massimo Rondelli | Francesco Pivi | Maurizio Gabbrielli |
|:---:|:---:|:---:|
| Department of Computer Science<br/>and Engineering | Department of Computer Science<br/>and Engineering | Department of Computer Science<br/>and Engineering |
| 🎓 University of Bologna | 🎓 University of Bologna | 🎓 University of Bologna |

</div>

---

## 📚 Citation

If you use BlenderRAG in your research, please cite:

```bibtex
@misc{rondelli2026blenderraghighfidelity3dobject,
  title         = {BlenderRAG: High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis},
  author        = {Massimo Rondelli and Francesco Pivi and Maurizio Gabbrielli},
  year          = {2026},
  eprint        = {2605.00632},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  url           = {https://arxiv.org/abs/2605.00632},
}
```

---

<div align="center">

⭐ **Star this repo** if BlenderRAG is useful in your work — it really helps the project!

<sub>Made with ❤️ at the University of Bologna</sub>

</div>
