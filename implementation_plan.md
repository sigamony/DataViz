# Implementation Plan: LLM-Based Chart Visualizer

## Overview
We are building a code generation system that takes a dataset (CSV/Excel) and a natural language user query, and uses an LLM to generate Python visualization code (matplotlib/pandas). This code is then safely executed to produce a chart.

## Architecture
1.  **Data Ingestion**: Load CSV/XLSX files.
2.  **Data Profiling**: Extract metadata (column names, types, samples, stats) to inform the LLM without sending the entire dataset.
3.  **Prompt Engineering**: Construct a precise prompt containing the profile and user constraints.
4.  **Code Generation**: Interface with an LLM (Simulated or API) to get executable Python code.
5.  **Safe Execution**: Validate AST and execute the code in a sandboxed environment.
6.  **Rendering**: Output the resulting image.

## Project Structure
```text
Chart-Visualizer/
├── data/                   # Sample datasets
├── src/
│   ├── __init__.py
│   ├── dataloader.py       # Handles file reading and profiling
│   ├── llm_client.py       # Handles LLM communication (with mock mode)
│   ├── prompt_builder.py   # Constructs the system/user prompts
│   └── executor.py         # Handles AST validation and code execution
├── main.py                 # CLI entry point to run the pipeline
├── requirements.txt        # Dependencies
└── implementation_plan.md  # This file
```

## Step-by-Step Implementation

### Phase 1: Foundation (Data & Profiling)
- **Goal**: Load a file and generate a JSON-serializable profile.
- **Tasks**:
    - Implement `load_data(path)` to handling CSV/Excel.
    - Implement `generate_profile(df)` to extract columns, dtypes, samples, and numeric summaries.
    - **Verification**: Run on a sample CSV and print the profile dictionary.

### Phase 2: Execution Engine (The "Runtime")
- **Goal**: Execute arbitrary string-based Python code safely against a loaded DataFrame.
- **Tasks**:
    - Implement `validate_safe_code(code_str)` using Python's `ast` module to block `os`, `subprocess`, etc.
    - Implement `run_visualization(code, df)` to execute code and capture the matplotlib figure.
    - **Verification**: Pass a hardcoded string `df.plot(kind='bar'); plt.show()` and ensure it generates an image output without errors.

### Phase 3: The Brain (LLM & Prompts)
- **Goal**: Translate user intent into the code format expected by the Runtime.
- **Tasks**:
    - Design the prompt template in `prompt_builder.py`.
    - Implement `get_code_from_llm(profile, query)` in `llm_client.py`.
    - *Note*: We will implement a "Mock" mode first that returns pre-written code for testing, then add OpenAI integration.

### Phase 4: Integration
- **Goal**: Connect all components into a seamless pipeline.
- **Tasks**:
    - Create `main.py` which takes a file path and a query string.
    - Chain: Load -> Profile -> Prompt -> LLM -> Execute -> Save Image.

## Dependencies
- pandas
- matplotlib
- openpyxl (for Excel)
- openai (optional, for real LLM)

## Security Considerations
- **AST Validation**: Prevent imports of system modules.
- **Globals Control**: Only pass `df`, `pd`, and `plt` to the `exec()` environment.
- **Backend**: Use Matplotlib `Agg` backend to avoid GUI window requirements.
