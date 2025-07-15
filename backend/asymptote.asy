
import olympiad; import settings; size(600, 600);
pair A = (0,0);
pair B = (3,0);
pair C = (0,4);

draw(A--B--C--cycle);
draw(rightanglemark(B,A,C,10));

label("$A$",A,SW);
label("$B$",B,SE);
label("$C$",C,N);
