<h1 align="center"> BlenderRAG: High-Fidelity 3D Object Generation via Retrieval-Augmented Code Synthesis </h1>
<p align="center">
  <strong>Massimo Rondelli</strong><sup> 1</sup>,
  <strong>Francesco Pivi</strong><sup> 1,2</sup>,
  <strong>Maurizio Gabbrielli</strong><sup> 1</sup>
</p>
<p align="center">
  <sup>1 </sup>University of Bologna, Bologna, Italy<br>
  <sup>2 </sup>Ferrari S.p.A., Maranello, Italy
</p>

<p align="center">
   <!-- <a href="https://maxrondelli.github.io/BlenderRAG/"><img src="https://img.shields.io/badge/Project%20Page-Live-2ea44f.svg?style=flat-square" alt="Project Page"></a> -->
   <a href="https://arxiv.org/abs/2605.00632"><img src="https://img.shields.io/badge/arXiv-2605.00632-b31b1b.svg?style=flat-square" alt="Paper"></a>
   <a href="https://huggingface.co/datasets/MaxRondelli/BlenderRAG"><img src="https://img.shields.io/badge/Hugging%20Face-Dataset-FFD21F.svg?style=flat-square" alt="Dataset"></a>
   <a href="https://huggingface.co/papers/2605.00632"><img src="https://img.shields.io/badge/Hugging%20Face-Paper-3578E5.svg?style=flat-square" alt="HF Paper"></a>
</p>

<p align="center">
  <a href="https://maxrondelli.github.io/BlenderRAG/">
    <img src="https://img.shields.io/badge/🌐%20Visit%20Project%20Page-2ea44f?style=for-the-badge" alt="Project Page" height="40">
  </a>
</p>

## Abstract
Automatic generation of executable Blender code from natural language remains challenging, with
state-of-the-art LLMs producing frequent syntactic errors and geometrically inconsistent objects. We
present BlenderRAG, a retrieval-augmented generation system that operates on a curated multimodal dataset of 500 expert-validated examples (text, code, image) across 50 object categories.
By retrieving semantically similar examples during generation, BlenderRAG improves compilation
success rates from 40.8% to 70.0% and semantic normalized alignment from 0.41 to 0.77 (CLIP
similarity) across four state-of-the-art LLMs, without requiring fine-tuning or specialized hardware,
making it immediately accessible for deployment.

## Method
Given a natural-language description, BlenderRAG executes the following pipeline:
1. **Embed.** The query is encoded with a Nomic-AI sentence-embedding model.
2. **Retrieve.** The top-*k* most similar *(description, code)* pairs are
   retrieved from a local Qdrant vector database initialised on first launch.
3. **Synthesize.** A user-selected LLM is prompted with the query and the
   retrieved exemplars; it returns a Blender Python script.
4. **Execute.** The script is run in the active Blender session.
5. **Edit.** The resulting mesh is left selected in the viewport, ready for
   downstream editing.

The vector database is built once per machine and re-used across sessions.
<p align="center">
  <img alt="BlenderRAG pipeline" src="assets/blender-rag-pipeline.jpg" width="1920">
</p>

## Dataset
The [BlenderRAG dataset](https://huggingface.co/datasets/MaxRondelli/BlenderRAG)
has **500 objects** organised into **50 categories** (25 indoor, 25 outdoor),
with **10 variants per category**. Each variant comprises three artifacts:

| File | Type | Description |
|---|---|---|
| `image_N.png` | PNG | Snapshot of the mesh |
| `code_N.py`   | Python | Blender script that generates the mesh |
| `txt_N.txt`   | UTF-8 text | Natural-language description of the mesh |

Splits `indoor` and `outdoor` are also available as Parquet files for direct ingestion via 🤗 `datasets`.

## Add-on Setup
```bash
git clone https://github.com/MaxRondelli/BlenderRAG.git
cd BlenderRAG

conda create -n blender_rag python=3.12 -y
conda activate blender_rag
pip install -r requirements.txt
```


**1. Install the add-on in Blender.**
Zip the current repository and load it via *Edit → Preferences → Add-ons →
Install from Disk*. After installation, open the BlenderRAG panel from the 3D
viewport sidebar (<kbd>N</kbd>).

**2. Install runtime dependencies.**
In the BlenderRAG panel, click *Install Dependencies*. Track progress in the
Blender Python Console:

- *Windows*: Window → Toggle System Console
- *macOS / Linux*: Scripting workspace → Python Console

NOTE: Restart Blender after installation completes.

**3. Configure the add-on.**

| Setting | Description |
|---|---|
| LLM Selection | Choose your preferred language model (open or closed source). |
| API Key | Required for closed models. |
| Retrieval Count (`k`) | Number of similar examples retrieved from the vector DB. |

## Usage

1. Open the BlenderRAG panel in the 3D viewport sidebar.
2. Enter a description, e.g. *"a modern wooden chair with armrests"*.
3. Click **Generate**.

On the first prompt the system initialises the local Qdrant vector store and
indexes the dataset; this is a one-time cost. Subsequent generations are fast.
Larger values of *k* yield more grounded outputs at the cost of latency; smaller
values are more open-ended.


## Troubleshooting

<details>
<summary>The add-on does not appear after installation.</summary>

Open *Edit → Preferences → Add-ons*, search for "BlenderRAG", and tick the
checkbox.
</details>

<details>
<summary>Dependency installation fails.</summary>

Verify that Blender has network access and was launched with sufficient
permissions. On Windows, run Blender as Administrator and retry.
</details>

<details>
<summary><code>ModuleNotFoundError</code> after installing dependencies.</summary>

Restart Blender. Dependencies installed at runtime are only loaded after a
fresh start.
</details>

<details>
<summary>The first prompt is slow.</summary>

Expected behaviour: the local Qdrant index is being built. Subsequent prompts
are several orders of magnitude faster.
</details>

<details>
<summary>The generated script fails to execute.</summary>

Inspect the Blender System Console for the traceback. Common causes are
unsupported Blender versions or invalid API keys. Increasing *k* often produces
more grounded scripts.
</details>

## Citation
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