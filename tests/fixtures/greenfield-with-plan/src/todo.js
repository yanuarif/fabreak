const todos = [];
let nextId = 1;

function createTodo(title) {
  const todo = { id: nextId++, title, state: "open" };
  todos.push(todo);
  return todo;
}

function listTodos() {
  return todos.slice();
}

module.exports = { createTodo, listTodos };
