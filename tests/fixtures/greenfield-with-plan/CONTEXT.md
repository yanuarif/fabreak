# Todo API — domain model

## Glossary

- **Todo** — one item a user wants done. Has a title and a state.
- **State** — `open` or `done`. A todo starts `open`.
- **List** — all todos of one user, ordered by creation.

## Seams

- `createTodo(title)`, `completeTodo(id)`, `listTodos()` in `src/todo.js` — the public interface; tests live here.
