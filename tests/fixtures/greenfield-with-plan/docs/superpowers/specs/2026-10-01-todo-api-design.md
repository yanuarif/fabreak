# Todo API design

A minimal todo API: create a todo, complete it, list them. In-memory store; one user.

## Interface

- `createTodo(title)` returns the todo `{ id, title, state: "open" }`. An empty title throws.
- `completeTodo(id)` sets `state` to `done`. An unknown id throws.
- `listTodos()` returns todos in creation order.
