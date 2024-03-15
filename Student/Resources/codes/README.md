# MS Hack AI Studio

Contains codebase for MS Hack AI Studio

## Prerequisites

### Installation

1. Create conda environment
    ```
    conda create -n azureaistudio python=3.10.13
    ```
2. Activate conda environment
    ```
    conda activate azureaistudio
    ```
3. Install library
    ```
    # cd Student/Resources/codes
    pip install -e .
    ```
4. Install Azure CLI

    Azure CLI can be installed from the link provided [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

5. Login to azure ai studio
    ```
    az login
    ```

### Setup environment variables

1. Populate relevant environment variables in `configs/environment_variables.env`
2. Populate AI Studio project variables in `config.json`

## Steps to run the code

Code can be run through notebook which can be found at `notebooks/End to End.ipynb`.

## UI

Streamlit UI can be run as follows.

```
streamlit run src/rag_ai_studio/app.py
```