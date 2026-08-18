# Pre-commit tutorial

> This repo is a read-only template maintained by the Permafrost org. Do not
> commit or push changes to it directly. Use the template to create your own
> copy and do all your work there.

This tutorial walks through setting up and running pre-commit hooks on a
Permafrost PoC project. You will start with broken delivery artifacts, run
the hooks, fix what cannot be auto-fixed, and end with a clean commit.

---

## What this repo contains

```
precommit-tutorial/
  .pre-commit-config.yaml       # Hook configuration
  package.sh                    # Script to zip delivery/ for client handoff
  README.md                     # This file
  delivery/
    python/
      transform.py              # Python script with formatting and debug violations
      config.py                 # Config file with unreplaced placeholders
    sql/
      01_create_objects.sql     # SQL script with style and naming violations
    notebooks/
      analysis.ipynb            # Notebook with outputs, placeholders, and credentials
  scripts/
    check_naming.py             # Custom hook: flags bad object names in SQL
    check_temp_objects.py       # Custom hook: flags debug code across all file types
    check_config.py             # Custom hook: flags unreplaced placeholders in config files
```

---

## What each hook does

| Hook | Auto-fixes | Flags only |
|---|---|---|
| `sqlfluff-fix` | Casing, indentation, trailing whitespace | `SELECT *`, unfixable rules |
| `sqlfluff-lint` | - | Any remaining SQL violations after fix |
| `black` | All Python formatting | - |
| `isort` | Import ordering in Python files | - |
| `nbstripout` | Strips cell outputs and execution counts | - |
| `nbqa-black` | Python formatting in notebook cells | - |
| `nbqa-isort` | Import ordering in notebook cells | - |
| `check-naming` | - | Bad object names in SQL (e.g. `_v2`, `tmp_`, `_final`) |
| `check-temp-objects` | - | Debug code, hardcoded paths, credentials |
| `check-config` | - | Unreplaced `YOUR_<SOMETHING>` placeholders in config files |

---

## Prerequisites

You need Python 3.11+ and Git. If you do not have Python 3.11+, install it
from [python.org](https://www.python.org/downloads/) before continuing.

---

## Step 0: Create your own copy from the template

This repo is a GitHub template. Do not clone it directly. Create your own
copy first and do all your work there.

1. Go to `https://github.com/permafrost/precommit-tutorial`.
2. Click "Use this template" and select "Create a new repository".
3. Set yourself or your personal account as the owner and give the repo a name.
4. Clone your new repo locally and cd into it:

```bash
git clone https://github.com/<your-account>/<your-repo-name>.git
cd <your-repo-name>
```

All steps from here on are run from inside your cloned repo.

---

## Step 1: Set up a virtual environment

A virtual environment keeps the tools for this project separate from your
system Python. Pick one of the two approaches below.

### Option A: uv (recommended)

uv is faster than pip and handles both the environment and package installs
in one tool. Install it if you do not have it:

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Create and activate the environment, then install pre-commit:

```bash
uv venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
uv pip install pre-commit
```

### Option B: Python native venv

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install pre-commit
```

You need to activate the environment every time you open a new terminal
session before running any `pre-commit` commands.

---

## Step 2: Install the hooks

Run this once from the repo root. It registers the hooks so they fire on every
`git commit`.

```bash
pre-commit install
```

---

## Step 3: Try to commit the broken artifacts

Stage all the files and try to commit.

```bash
git add .
git commit -m "initial delivery artifacts"
```

The commit will be blocked. You will see output from each hook. Some hooks
will have modified files automatically. Others will have printed errors that
you need to fix by hand.

---

## Step 4: Stage the auto-fixed files and commit again

After the first run, check what changed:

```bash
git diff
```

The following hooks will have already rewritten files for you:

- `sqlfluff-fix` rewrote `01_create_objects.sql` to fix keyword casing and indentation.
- `black` rewrote `transform.py` and `config.py` to fix spacing and line length.
- `isort` rewrote the import blocks in `transform.py` and `config.py`.
- `nbstripout` removed cell outputs and execution counts from `analysis.ipynb`.
- `nbqa-black` and `nbqa-isort` reformatted the Python cells inside `analysis.ipynb`.

Stage the auto-fixed files:

```bash
git add .
git commit -m "initial delivery artifacts"
```

The commit will be blocked again. The auto-fixers are done, but violations that
require manual fixes are still present.

---

## Step 5: Fix the remaining violations by hand

The hooks that flag but do not fix will have printed specific errors. Work
through each one.

### check-naming

The hook flagged bad object names in `01_create_objects.sql`:

- `stg_orders_v2` contains a version suffix `_v2`. Rename it to `stg_orders`.
- `vw_orders_final` contains `_final`. Rename it to `vw_orders`.
- `tmp_order_summary` has a `tmp_` prefix. Rename it to `order_summary`.

Open `01_create_objects.sql` and rename the objects. Update every reference to
each name in the file.

### check-temp-objects

The hook flagged several issues across `transform.py`, `01_create_objects.sql`,
and `analysis.ipynb`.

**transform.py**

- Lines with `print()` calls. Remove them or replace with `logging`.
- A `# HACK` comment. Remove the comment and the workaround, or fix the
  underlying issue.
- A hardcoded Snowflake account URL and password in the `__main__` block.
  Remove the hardcoded values. Connection params should come from environment
  variables or a Snowflake CLI connection, not from a script.
- A block of four or more consecutive commented-out lines at the top of the
  file. Remove the block.

**01_create_objects.sql**

- A block of four commented-out lines above the view definition. Remove the
  block or replace it with a single `-- TODO:` placeholder if the note is
  still needed.

**analysis.ipynb**

- A hardcoded account URL and password in cell 1. Remove them. The notebook
  uses `get_active_session()` which does not need credentials.

### check-config

The hook flagged unreplaced placeholders in `config.py` and `analysis.ipynb`.

**config.py**

Replace all `YOUR_<SOMETHING>` values with real values for your environment:

```python
ACCOUNT   = "myorg-myaccount"
USER      = "myuser"
WAREHOUSE = "MY_WAREHOUSE"
DATABASE  = "MY_DATABASE"
SCHEMA    = "MY_SCHEMA"
ROLE      = "MY_ROLE"
```

**analysis.ipynb**

Replace `YOUR_WAREHOUSE`, `YOUR_DATABASE`, and `YOUR_SCHEMA` in cell 1 with
real values.

### sqlfluff-lint

After `sqlfluff-fix` ran, one violation remains in `01_create_objects.sql`:

- `SELECT *` in the view definition. SQLFluff flags this but cannot rewrite it
  because it does not know which columns you want. Replace `select *` with
  the explicit column list:

```sql
CREATE OR REPLACE VIEW vw_orders AS
    SELECT
        order_id,
        customer_id,
        order_date,
        amount,
        status
    FROM stg_orders
    WHERE status = 'COMPLETE';
```

---

## Step 6: Commit the clean artifacts

Once all manual fixes are done, stage and commit:

```bash
git add .
git commit -m "initial delivery artifacts"
```

All hooks should pass and the commit goes through.

---

## Step 7: Package for client handoff

When the PoC is ready to ship, run the package script from the repo root:

```bash
bash package.sh
```

This produces a zip file named `delivery-YYYYMMDD.zip` containing only the
`delivery/` folder. Hand this zip to the client.
