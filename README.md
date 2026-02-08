# ChemMiner: A Large Language Model Agent System for Chemical Literature Data Mining
This is the implementation for our paper [ChemMiner: A Large Language Model Agent System for Chemical Literature Data Mining](https://openreview.net/forum?id=H57HtksYpC)

## Literature Input
The literature input is stored in jsonl format. The size of data is too large for github and it can be downloaded from [Google Drive](https://drive.google.com/file/d/1uKBPmtdvT7OHVr5UO8KqsQApjkpXaKH9/view?usp=sharing).

### What it does

Given OCR-parsed paper text in `jsonl` format, `run_extraction.py` performs:

1. **Procedure-focused text slicing**
   - Searches for experimental procedure anchors such as **General Procedure / Typical Procedure / General Experimental Procedure**
   - Splits and merges nearby sentences into length-bounded sections that are suitable for LLM prompts

2. **Agent-style extraction from text**
   - **Coreference extraction** (`prompt_function_gpt4_1v1`): extracts mappings like *full chemical name → abbreviation/label* (e.g., “2-chloroquinoline → 1a”)
   - **Reaction schema extraction** (`prompt_function_general_procedure`): extracts structured fields in JSON:
     **yield / reactant / reagent / solvent / product**, using the general procedure as context to fill missing details when possible

3. **Optional multimodal coreference from figures/tables**
   - If images are stored under `IMAGE_ROOT/{paper_id}/...`, the script runs a vision prompt (`prompt_function_figure_abbrev`) to extract an **abbreviation → chemical name** dictionary from each figure/table image
   - Per-paper dictionaries are merged and exported as CSV

### Outputs (per paper)

- `GPT_input_coreference{paper_id}.csv` / `GPT_output_coreference{paper_id}.csv`  
  Text coreference prompts and results.

- `GPT_input_{paper_id}.csv` / `GPT_output_react{paper_id}.csv`  
  Reaction-schema prompts and results.

- `GPT_output_fig_abbrev_{paper_id}.csv`  
  Merged figure/table abbreviation maps (only if images exist).

### Why coreference-first?

Chemical papers frequently reference compounds using short labels (e.g., “1a”, “3aa”), and crucial reaction details may appear in figures/tables rather than in the main text. A **coreference-first → reaction extraction** workflow improves robustness when scaling literature mining across large corpora.
