
import olympiad; import settings; size(600);
pair O = (0,0);
real R = 1;
pair A = (2*R,0);
pair B = tangent(A,O,R,1);
pair C = tangent(A,O,R,2);
pair D = -B;
pair E = intersectionpoint(A--D,Circle(O,R));
pair H = intersectionpoint(B--C,A--O);

draw(Circle(O,R));
draw(A--B--O--cycle);
draw(A--C);
draw(B--C);
draw(A--D);
draw(B--D);
draw(B--E);
draw(E--D);
draw(A--E);
draw(A--H);

label("$O$",O,S);
label("$A$",A,E);
label("$B$",B,NW);
label("$C$",C,NE);
label("$D$",D,SW);
label("$E$",E,S);
label("$H$",H,SE);

draw(rightanglemark(A,B,O,5));
draw(rightanglemark(B,E,D,5));
