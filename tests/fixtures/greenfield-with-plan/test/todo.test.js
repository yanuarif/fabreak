const test = require("node:test");
const assert = require("node:assert/strict");
const { createTodo, listTodos } = require("../src/todo");

test("createTodo returns an open todo and listTodos keeps creation order", () => {
  const a = createTodo("write spec");
  const b = createTodo("write plan");
  assert.equal(a.state, "open");
  assert.deepEqual(listTodos().map((t) => t.id), [a.id, b.id]);
});
