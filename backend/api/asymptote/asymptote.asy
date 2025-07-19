
import olympiad; import settings; size(600, 600);
pair O = (0,0);
real R = 50;
pair A = (2*R,0);
pair B = tangent(A, O, R, 1);
pair C = tangent(A, O, R, 2);
pair D = -B;
pair E = intersectionpoints(A--D, Circle(O,R))[0];
pair H = intersectionpoint(B--C, A--O);

draw(Circle(O, R));
draw(A--B--O--C--cycle);
draw(A--D);
draw(B--C);
draw(A--O);
draw(O--D);
draw(C--D);

label("$O$", O, SW);
label("$A$", A, N);
label("$B$", B, N);
label("$C$", C, S);
label("$D$", D, S);
label("$E$", E, NW);
label("$H$", H, SE);
