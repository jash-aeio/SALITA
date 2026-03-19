/* ============================================ */
/* SALITA Sample 3 - Kumplikadong Arithmetic    */
/* (Complex arithmetic expression)              */
/*                                              */
/* Layunin: Ipakita ang expression evaluation   */
/* na may tamang operator precedence at         */
/* paggamit ng parentheses.                     */
/* ============================================ */

baryabol a;
baryabol b;
baryabol c;
baryabol sagot;
baryabol sagot2;

kuha a;
kuha b;
kuha c;

/* sagot = a + b * c   (multiplication first) */
lagay sagot = a + b * c;

/* sagot2 = (a + b) * c  (parentheses override precedence) */
lagay sagot2 = (a + b) * c;

ipakita sagot;
ipakita sagot2;
