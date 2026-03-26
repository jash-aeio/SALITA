/* ============================================ */
/* SALITA Sample - Complex Arithmetic           */
/* Demonstrates operator precedence and        */
/* parentheses for expression evaluation       */
/* ============================================ */

var a;
var b;
var c;
var result1;
var result2;

input a;
input b;
input c;

/* result1 = a + b * c   (multiplication first) */
result1 = a + b * c;

/* result2 = (a + b) * c  (parentheses override precedence) */
result2 = (a + b) * c;

output result1;
output result2;
