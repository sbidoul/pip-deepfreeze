Normalize distribution names in the generated lock files. This change, which will cause
some changes in generated ``requirements*.txt`` files, was made following the change in
setuptools 69 that started preserving underscores in distribution names.
