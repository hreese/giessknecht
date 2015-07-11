// 2,75, 5,5
$fn=32;

for (x = [0:5]) {
    for (y = [0:5]) {
        translate([x*9, y*9, 0]) difference() { cylinder(r=7/2, h=8, center=true); cylinder(r=2.85/2, h=9, center=true); };
    }
}
