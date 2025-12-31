---
description: Workflow to build the Chart Visualizer application
---
# Workflow for Building the Chart Visualizer

This workflow outlines the steps to build the Chart Visualizer application from scratch, following the implementation plan.

## Prerequisites
- Python 3.8+ installed
- pip installed

## Steps

1.  **Initialize Project**
    - Create the directory structure.
    - Create a virtual environment (optional but recommended).

2.  **Install Dependencies**
    - Create `requirements.txt` with `pandas`, `matplotlib`, `openpyxl`, `openai`.
    - Run `pip install -r requirements.txt`.

3.  **Implement Data Loader (`src/dataloader.py`)**
    - Create the module to load CSV/Excel files.
    - Implement profiling logic (statistics, types, samples).
    - *Verification*: Create a dummy CSV and ensure it loads correctly.

4.  **Implement Safe Executor (`src/executor.py`)**
    - Implement AST validation to block dangerous imports.
    - Implement the `exec()` wrapper to run code with `df` and `plt` context.
    - Handle image capture (save to bytes/file).

5.  **Implement Tokenizer/Prompt Engine (`src/prompt_builder.py`)**
    - Create templates that inject the JSON profile into the system prompt.
    - Define rules for the LLM (no markdown, only python, etc.).

6.  **Implement LLM Client (`src/llm_client.py`)**
    - Setup OpenAI client (or generic interface).
    - Implement a "Mock" provider for strictly testing without cost/keys.

7.  **Main Entry Point (`main.py`)**
    - Orchestrate the flow: File -> Profile -> Prompt -> LLM -> Code -> Execution.
    - Handle CLI arguments or hardcoded test paths.

8.  **Testing**
    - Run the pipeline with a known dataset (e.g., `data/sales.csv`) and a query "Show sales by region".
    - Check if `output.png` is generated.
