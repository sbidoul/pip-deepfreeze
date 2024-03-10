Use ``uv``'s ``--python`` option to select the interpreter, instead of passing it as a
``VIRTUAL_ENV`` environment variable. This is more explicit and hopefully more resilient
to changes in ``uv``'s Python detection logic.
