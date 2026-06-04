"""Backend plugins: compile a pattern-spec into a concrete, tested harness.

Each backend implements the interface in ``base.Backend`` and is registered in
``registry``. ``scaffold.py`` picks the backend whose ``supports(spec)`` scores
highest; ``verify.py`` re-loads the chosen backend from the harness manifest.

Package dirs use underscores (``hybrid_python``) so they import cleanly; the
brief's hyphenated labels (``hybrid-python``) are the conceptual names.
"""
