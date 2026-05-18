"""
Test harness for AppTest.

Streamlit's AppTest.from_function loses module-level imports when it
exec's the function body, so we use AppTest.from_file pointed at this
script instead. Keep this file minimal — its only job is to expose
auth.login_page() as a runnable Streamlit script.
"""

import sys
from pathlib import Path

# Make the project root importable when AppTest exec's this file.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import auth  # noqa: E402  — must come after sys.path adjustment

auth.login_page()
