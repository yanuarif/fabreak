const test = require("node:test");
const assert = require("node:assert/strict");
const { invoiceTotal } = require("../src/invoice");

test("invoiceTotal sums line totals without discount", () => {
  const invoice = { lines: [{ qty: 2, unitPrice: 10 }, { qty: 1, unitPrice: 5.5 }] };
  assert.equal(invoiceTotal(invoice), 25.5);
});
