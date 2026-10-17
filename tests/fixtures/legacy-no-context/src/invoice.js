// Legacy: amounts are floats in currency units; discount is a percentage.
function lineTotal(line) {
  var gross = line.qty * line.unitPrice;
  var discount = gross * (line.discountPct || 0) / 100;
  return Math.round((gross - discount) * 100) / 100;
}

function invoiceTotal(invoice) {
  var total = 0;
  for (var i = 0; i < invoice.lines.length; i++) {
    total = total + lineTotal(invoice.lines[i]);
  }
  return Math.round(total * 100) / 100;
}

module.exports = { lineTotal: lineTotal, invoiceTotal: invoiceTotal };
