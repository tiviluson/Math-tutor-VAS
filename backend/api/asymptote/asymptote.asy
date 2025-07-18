
import olympiad; import settings; size(600, 600);
pair B = (0,0);
pair C = (4,0);
pair A = (0,3);
pair H = foot(A,B,C);

draw(A--B--C--cycle);
draw(A--H);

label("$A$",A,N);
label("$B$",B,SW);
label("$C$",C,SE);
label("$H$",H,S);

draw(rightanglemark(B,A,C,10));
draw(rightanglemark(A,H,C,10));
