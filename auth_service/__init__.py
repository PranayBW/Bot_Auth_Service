"""Compatibility package for running the service from the repository root.

The Docker image copies this repository into `/app/auth_service`, so imports like
`auth_service.api.authorize` work there naturally. Local development often runs
`uvicorn app:app` from this folder, where the real modules are siblings of this
shim instead.
"""

from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent

__path__ = [str(_project_root), *__path__]
