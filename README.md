# Assys Montagehelfer

An application providing step by step building instructions for Asys blocks.

## Installation

### Install uv (Optional)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or on Windows:

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Virtual Environment

Using uv:
```bash
uv sync
```

Or using standard venv:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix-like systems
.venv\Scripts\activate     # On Windows
```

### Install Dependencies

With uv:
```bash
uv pip install -r requirements.txt
```

With pip:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Start the Flask application:

With uv:
```bash
uv run python app.py
```

With pip:
```bash
python app.py
```

The application will be available at `http://localhost:5000`.

### Using the Interface

1. Click "Log In" on the homepage to begin
2. Follow the step-by-step building instructions
3. Use the "Next" button to advance through the steps
4. The current brick to place is highlighted while previous steps are shown faded

### Development

For development purposes, the application runs in debug mode by default on port 5000.
