/* LUMA revision A / millimetres / 2026-09-04
   Original parametric mechanical prototype. Vendor metal horns remain installed.
   Select part with -D 'part="upper_rail"'. STL coordinates are print coordinates.
   See mechanical.md for assembly and fit checks. */
$fn=96;
part="assembly_preview";
base_d=216; head_d=176; upper_pitch=140; forearm_pitch=120;
clearance=0.35; m3=3.4; horn_pcd=14; servo_back=35.11;
module hole(d,h=100){translate([0,0,-1]) cylinder(d=d,h=h);}
module ring(od,id,h){difference(){cylinder(d=od,h=h);hole(id,h+2);}}
module rr(w,h,t,r=3){linear_extrude(t) hull() for(x=[-w/2+r,w/2-r],y=[-h/2+r,h/2-r]) translate([x,y])circle(r=r,$fn=24);}
module screw4(x,y,d=m3,h=100){for(a=[-x,x],b=[-y,y])translate([a,b,0])hole(d,h);}
module hornholes(h=20){hole(6.5,h);for(a=[0:90:270])rotate(a)translate([horn_pcd/2,0,0])hole(3.3,h);}
module capsule(l,w,t){hull(){cylinder(d=w,h=t);translate([l,0,0])cylinder(d=w,h=t);}}

// Ballast: separate purchased steel disc Ø180 x 6; bolted retention.
module base_tub(){difference(){union(){ring(base_d,base_d-7,50);cylinder(d=base_d,h=3);for(a=[30:60:330])rotate(a)translate([99,0,2])cylinder(d=12,h=45);}for(a=[30:60:330])rotate(a)translate([99,0,0])hole(2.8,52);for(x=[-45,45],y=[-35,35])translate([x,y,0])hole(4.4,15);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(m3,8);translate([0,-107,23])rotate([90,0,0])cylinder(d=13,h=10,center=true);translate([55,-92,23])rotate([90,0,-30])cube([23,9,12],center=true);for(a=[0:20:160])rotate(a)translate([100,0,17])cube([15,3.5,20],center=true);}}
module base_lid(){difference(){union(){cylinder(d=base_d,h=5);translate([0,0,5])ring(62,52.15,7);translate([0,0,-2])ring(208.4,204,2.2);}hole(40.8,15);for(a=[30:60:330])rotate(a)translate([99,0,0])hole(m3,8);for(x=[-65:10:-25],y=[35,65])translate([x,y,0])cube([4,19,20],center=true);}}
module electronics_tray(){difference(){rr(166,90,3);for(x=[-70:10:70],y=[-30,0,30])translate([x,y,0])hull(){hole(m3,6);translate([5,0,0])hole(m3,6);}for(x=[-45,45],y=[-35,35])translate([x,y,0])hole(4.4,8);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(7,8);translate([0,-13,-1])rr(36,54,8);translate([65,0,0])hole(12,6);}for(x=[-81,-32],y=[-20,38])translate([x,y,3])difference(){cylinder(d=7,h=6);hole(2.1,8);}}
module yaw_mount(){difference(){union(){translate([0,-22,0])rr(64,46,3);translate([-16,-39,3])cube([32,17,35]);}translate([-12.7,-35.5,3])cube([25.4,46,40]);hole(22,8);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(m3,8);for(x=[-18.5,18.5])translate([x,-25,0])hole(m3,45);}}
module yaw_cap(){difference(){translate([0,-30,0])rr(47,16,2.6);for(x=[-18.5,18.5])translate([x,-25,0])hole(m3,8);}}
module turntable(){difference(){union(){translate([0,0,14.2])ring(82,22,6);ring(39.75,22,14.3);translate([0,0,0.5])cylinder(d=24,h=3);}hornholes(8);screw4(26,18,3.4,24);}}
module shoulder_tower(){difference(){union(){rr(64,50,6);translate([-22,-23,6])cube([44,46,28]);}translate([-17.8,-12.7,11.4])cube([50,25.4,38]);translate([17.8,-24,6])cube([10,48,40]);screw4(26,18,m3,10);for(y=[-18.5,18.5])translate([-25,y,23])rotate([0,90,0])cylinder(d=m3,h=60);}}
module shoulder_cap(){difference(){rr(46,28,4);for(x=[-18.5,18.5])translate([x,0,0])hole(m3,8);}}
// Rails terminate behind distal servo horns. A rear-body cassette holds each servo.
module rail(l){difference(){union(){capsule(l-38,30,5);translate([l-28,0,0])rr(21,46,5);}hornholes(8);translate([l-25,0,0])for(y=[-18.5,18.5])translate([0,y,0])hole(m3,10);for(x=[35,l-52])translate([x,0,0])hole(m3,10);translate([44,-4,-1])cube([max(2,l-103),8,8]);}}
module cassette(){difference(){translate([-26.4,0,0])rr(26,46,39.8);translate([-35.5,-12.7,4.2])cube([30,25.4,45]);for(y=[-18.5,18.5])translate([-25,y,0])hole(m3,50);translate([-40,-9,12])cube([10,18,18]);}}
module cassette_cap(){difference(){translate([-26.4,0,0])rr(26,46,4.2);for(y=[-18.5,18.5])translate([-25,y,0])hole(m3,7);}}
module cross_spacer(){difference(){cylinder(d=12,h=44);hole(m3,47);}}
module horn_spacer(){difference(){cylinder(d=20,h=3.3);hornholes(6);}}
module head_yoke(){difference(){union(){translate([0,0,30])rr(66,44,6);for(x=[-27,22])translate([x,0,15])rotate([0,90,0])linear_extrude(5)hull(){circle(r=15);translate([-15,0])square([15,30],center=true);}}for(x=[-30,20])translate([x,0,15])rotate([0,90,0])hornholes(15);translate([0,0,29])screw4(27,15,m3,10);translate([-50,-50,36])cube([100,100,10]);translate([-18.2,-9,29.8])cube([36.4,18,2]);}}

module head_mount_bosses(){for(a=[45:90:315])rotate(a)translate([60,0,2])difference(){cylinder(d=10,h=33);hole(2.8,39);}for(a=[0:90:270])rotate(a)translate([45,0,2])difference(){cylinder(d=8,h=30.5);hole(2.8,35);}for(x=[-34,34],y=[-34,34])translate([x,y,2])difference(){cylinder(d=8,h=12);hole(2.8,16);}for(x=[-27,27],y=[-15,15])translate([x,y,0])difference(){cylinder(d=9,h=9);hole(2.8,12);}}
module head_shell(){difference(){union(){cylinder(d=head_d,h=3);ring(head_d,head_d-6,36);head_mount_bosses();for(a=[0:90:270])rotate(a)translate([82,-18,0])cube([6,36,26]);for(a=[0:45:315])rotate(a)translate([76,0,3])cylinder(d=8,h=21);for(a=[22.5:45:337.5])rotate(a)translate([83,0,3])cylinder(d=9,h=32);}for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(2.8,44);translate([0,0,0])hole(12,6);for(x=[-27,27],y=[-15,15])translate([x,y,0])hole(m3,12);translate([0,54,0]){hole(12,7);for(x=[-17,17])translate([x,0,0])hole(m3,6);}for(a=[0,180,270])rotate(a)translate([84,0,14])rotate([0,90,0]){cylinder(d=12,h=12,center=true);for(y=[-17,17])translate([0,y,0])cylinder(d=m3,h=12,center=true);}for(a=[200:10:340])rotate(a)translate([65,0,0])hull(){hole(3.5,6);translate([8,0,0])hole(3.5,6);}}}
module outer_bezel(){difference(){union(){ring(176,160.5,4);translate([0,0,0])ring(171.5,165.6,7);}translate([0,0,-0.1])cylinder(d=165.5,h=1.5);for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(m3,10);}}
module face_center(){difference(){cylinder(d=142.6,h=4);hole(68.6,8);translate([0,0,-0.1])ring(145,140.5,1.5);for(a=[45:90:315])rotate(a)translate([60,0,0])hole(m3,8);translate([0,54,0]){hole(12,8);for(x=[-17,17])translate([x,0,0])hole(m3,8);}}}
module white_carrier(){difference(){union(){ring(68,51,2);for(a=[0:90:270])rotate(a)translate([39.5,0,0])rr(23,10,2);}for(a=[0:90:270])rotate(a)translate([45,0,0])hole(m3,6);}}
module lcd_cradle(){difference(){union(){rr(77,77,3);translate([0,0,3])difference(){rr(61.8,61.8,12);rr(55.8,55.8,14,0.4);}for(x=[-34,34],y=[-34,34])translate([x,y,3])cylinder(d=8,h=12);}translate([0,0,0])rr(49,49,5);for(x=[-34,34],y=[-34,34])translate([x,y,0])hole(m3,23);translate([0,-29,7])cube([19,14,13],center=true);}}
module lcd_retainer(){difference(){rr(77,77,3);hole(70,6);for(x=[-34,34],y=[-34,34])translate([x,y,0])hole(m3,7);}}
module outer_diffuser(){difference(){union(){ring(160,143,1.2);translate([0,0,1.1])ring(160,158.8,4.8);translate([0,0,1.1])ring(144.2,143,4.8);translate([0,0,5]){ring(165,158.8,1.2);ring(144.2,141,1.2);}}for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(3.6,9);}}
module inner_diffuser(){union(){ring(68,47.8,1.2);translate([0,0,1.1])ring(67.8,65.8,4.8);translate([0,0,1.1])ring(49.8,47.8,4.8);}}
module sensor_pod(){difference(){union(){rr(40,30,3);translate([0,0,3])difference(){rr(32,24,7);rr(26.1,18.1,9,1);}}translate([0,0,0])rr(21,12,6,1);for(x=[-17,17])translate([x,0,0])hole(m3,12);for(x=[-13.7,13.7])translate([x,8.9,0])hole(2.2,14);for(x=[-18,12])translate([x,-4,3.5])cube([6,8,9]);}}
module sensor_retainer(){difference(){rr(32,24,2);rr(24.9,16.9,4,1);for(x=[-13.7,13.7])translate([x,8.9,0])hole(2.2,5);}}
module cable_clip(){difference(){rr(18,12,8);translate([0,0,4])rotate([90,0,0])cylinder(d=6,h=15,center=true);for(x=[-6,6])translate([x,0,0])hole(2.5,12);}}
module fit_coupon(){difference(){rr(68,30,3);for(i=[0:3])translate([-24+i*16,0,0])hole(3.0+0.2*i,7);}translate([0,26,0])difference(){cylinder(d=25,h=5);hole(19.2+clearance,9);}}

if(part=="base_tub")base_tub();
else if(part=="base_lid")translate([0,0,2])base_lid();
else if(part=="electronics_tray")electronics_tray();
else if(part=="yaw_mount")yaw_mount();
else if(part=="yaw_cap")yaw_cap();
else if(part=="turntable")turntable();
else if(part=="shoulder_tower")shoulder_tower();
else if(part=="shoulder_cap")shoulder_cap();
else if(part=="upper_rail")rail(upper_pitch);
else if(part=="forearm_rail")rail(forearm_pitch);
else if(part=="servo_cassette")cassette();
else if(part=="cassette_cap")cassette_cap();
else if(part=="cross_spacer")cross_spacer();
else if(part=="horn_spacer")horn_spacer();
else if(part=="head_yoke")head_yoke();
else if(part=="head_shell")head_shell();
else if(part=="outer_bezel")outer_bezel();
else if(part=="face_center")face_center();
else if(part=="white_carrier")white_carrier();
else if(part=="lcd_cradle")lcd_cradle();
else if(part=="lcd_retainer")lcd_retainer();
else if(part=="outer_diffuser")outer_diffuser();
else if(part=="inner_diffuser")inner_diffuser();
else if(part=="sensor_pod")sensor_pod();
else if(part=="sensor_retainer")sensor_retainer();
else if(part=="cable_clip")cable_clip();
else if(part=="fit_coupon")fit_coupon();
else {base_tub();translate([0,0,50])base_lid();translate([0,0,58])turntable();translate([0,0,71])shoulder_tower();}
