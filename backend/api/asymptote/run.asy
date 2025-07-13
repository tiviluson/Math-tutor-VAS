import olympiad; import settings; size(600, 600);
pair M = (1, 2);
pair N = (4, 2);
pair O = (2, 1);
pair P = (3, 1);

pair M_prime = (M.x, -M.y);
pair N_prime = (N.x, -N.y);
pair O_prime = (O.x, -O.y);
pair P_prime = (P.x, -P.y);

draw(M--N--P--O--cycle);
draw(M_prime--N_prime--P_prime--O_prime--cycle);
draw(M--M_prime,dashed);
draw(N--N_prime,dashed);
draw(O--O_prime,dashed);
draw(P--P_prime,dashed);

draw((-1, 0)--(5, 0), linewidth(1));

label("$M$", M, N);
label("$N$", N, N);
label("$O$", O, S);
label("$P$", P, S);
label("$M'$", M_prime, S);
label("$N'$", N_prime, S);
label("$O'$", O_prime, N);
label("$P'$", P_prime, N);
label("$x-axis$",(5,0),E);