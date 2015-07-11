// 2,75, 5,5
$fn=32;

for (x = [0:5]) {
    for (y = [0:5]) {
        translate([x*7, y*7, 0]) difference() { cylinder(r=5.5/2, h=6, center=true); cylinder(r=2.75/2, h=7, center=true); };
    }
}
