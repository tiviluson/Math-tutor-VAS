
import olympiad; import settings; size(600, 600);
pair O = (0,0);
real R = 2;
pair A = 2*R*dir(0);
pair B = tangent(A, O, R, 1);
pair C = tangent(A, O, R, 2);
pair D = -B;
pair E = intersectionpoint(A--D, circle(O,R));
pair H = intersectionpoint(B--C, A--O);

draw(circle(O, R));
draw(A--B);
draw(A--C);
draw(B--D);
draw(A--D);
draw(B--C);
draw(B--E);
draw(E--D);
draw(A--H);
draw(H--E);
draw(D--H);

label("$O$", O, S);
label("$A$", A, E);
label("$B$", B, NW);
label("$C$", C, NE);
label("$D$", D, SW);
label("$E$", E, SE);
label("$H$", H, S);
