## Plan

- restrict isort and black to just the user database interface
- introduce mypy, restricted to the user database interface
- name things better
- only return schemas from the database interface, since it's impossible to do
  anything without starting a session ansyways
