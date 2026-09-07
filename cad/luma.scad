/* LUMA revision C / millimetres / 2026-09-07
   Original parametric mechanical prototype. Vendor metal horns remain installed.
   Revision C: five pedestal-wall ToF mounts and DS3218MG/PCA9685 motion hardware.
   Select part with -D 'part="upper_arm_left"'. STL coordinates are print coordinates.
   See mechanical.md for assembly and fit checks. */
$fn=96;
part="assembly_preview";
base_d=216; head_d=176; upper_pitch=140; forearm_pitch=120;
clearance=0.35; m3=3.4; m5=5.3; servo_back=30;
sensor_angles=[18,90,162,234,306]; sensor_z=25;
sensor_hole_y=10.16; sensor_hole_z=6.35; sensor_board_r=99;
lid_angles=[42,66,126,198,258,342];
module hole(d,h=100){translate([0,0,-1]) cylinder(d=d,h=h);}
module ring(od,id,h){difference(){cylinder(d=od,h=h);hole(id,h+2);}}
module rr(w,h,t,r=3){linear_extrude(t) hull() for(x=[-w/2+r,w/2-r],y=[-h/2+r,h/2-r]) translate([x,y])circle(r=r,$fn=24);}
module rr2(w,h,r=4){hull() for(x=[-w/2+r,w/2-r],y=[-h/2+r,h/2-r]) translate([x,y])circle(r=r,$fn=32);}
module screw4(x,y,d=m3,h=100){for(a=[-x,x],b=[-y,y])translate([a,b,0])hole(d,h);}
module servo_arm_holes(h=20){hole(7,h);hull(){translate([12,0,0])hole(3.4,h);translate([18,0,0])hole(3.4,h);}hull(){translate([20,0,0])hole(3.4,h);translate([25,0,0])hole(3.4,h);}}
module capsule(l,w,t){hull(){cylinder(d=w,h=t);translate([l,0,0])cylinder(d=w,h=t);}}

// Ballast: separate purchased steel disc Ø180 x 6; bolted retention.
// Five Adafruit 3967 boards sit tangent to the inside wall. Their component faces point outward.
module base_sensor_bosses(){for(a=sensor_angles)rotate(a)for(y=[-sensor_hole_y,sensor_hole_y],z=[sensor_z-sensor_hole_z,sensor_z+sensor_hole_z])translate([sensor_board_r,y,z])rotate([0,90,0])cylinder(d=6,h=6.5);}
module base_sensor_cuts(){for(a=sensor_angles)rotate(a){translate([104,0,sensor_z])cube([12,10,10],center=true);for(y=[-sensor_hole_y,sensor_hole_y],z=[sensor_z-sensor_hole_z,sensor_z+sensor_hole_z])translate([sensor_board_r-.5,y,z])rotate([0,90,0])cylinder(d=2.1,h=7.5);}}
module base_tub(){difference(){union(){ring(base_d,base_d-7,56);cylinder(d=base_d,h=3);for(a=lid_angles)rotate(a)translate([99,0,2])cylinder(d=12,h=51);base_sensor_bosses();}for(a=lid_angles)rotate(a)translate([99,0,0])hole(2.8,58);for(x=[-45,45],y=[-35,35])translate([x,y,0])hole(4.4,15);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(m3,8);rotate(270)translate([106,0,23])rotate([0,90,0])cylinder(d=13,h=12,center=true);rotate(282)translate([106,0,23])cube([12,23,9],center=true);base_sensor_cuts();}}
module base_lid(){difference(){union(){cylinder(d=base_d,h=5);translate([0,0,5])ring(62,52.15,7);translate([0,0,-2])ring(208.4,204,2.2);}hole(40.8,15);for(a=lid_angles)rotate(a)translate([99,0,0])hole(m3,8);for(x=[-65:10:-25],y=[35,65])translate([x,y,0])cube([4,19,20],center=true);}}
module electronics_tray(){difference(){rr(166,90,3);for(x=[-70:10:70],y=[-30,0,30])translate([x,y,0])hull(){hole(m3,6);translate([5,0,0])hole(m3,6);}for(x=[-45,45],y=[-35,35])translate([x,y,0])hole(4.4,8);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(7,8);translate([0,-13,-1])rr(36,54,8);translate([65,0,0])hole(12,6);}for(x=[-81,-32],y=[-20,38])translate([x,y,3])difference(){cylinder(d=7,h=6);hole(2.1,8);}}
module yaw_mount(){difference(){union(){translate([0,-22,0])rr(64,46,3);translate([-14,-39,3])cube([28,21,40.5]);}translate([-10.35,-38,3])cube([20.7,50,46]);hole(22,8);for(x=[-26,26],y=[-36,-8])translate([x,y,0])hole(m3,8);for(x=[-18.5,18.5])translate([x,-27,0])hole(m3,50);}}
module yaw_cap(){difference(){translate([0,-30,0])rr(47,16,2.6);for(x=[-18.5,18.5])translate([x,-27,0])hole(m3,8);}}
module turntable(){difference(){union(){translate([0,0,15])ring(82,22,6);ring(39.75,22,15.1);cylinder(d=24,h=3);rotate(90)linear_extrude(3)hull(){circle(d=14);translate([25,0])circle(d=10);}}rotate(90)servo_arm_holes(8);screw4(26,18,3.4,25);}}
module shoulder_tower(){difference(){union(){rr(70,50,6);translate([-26,-23,6])cube([52,46,34]);translate([-26,0,47])rotate([0,90,0])cylinder(d=20,h=5.4);}translate([-20.6,-10.35,16.5])cube([54,20.7,45]);translate([6,-10.35,9.5])cube([3,20.7,32]);translate([20.6,-24,15])cube([10,48,30]);screw4(26,18,m3,10);for(y=[-18.5,18.5])translate([-30,y,27])rotate([0,90,0])cylinder(d=m3,h=65);translate([-27,0,47])rotate([0,90,0])cylinder(d=m5,h=8);translate([-24.8,0,47])rotate([0,90,0])cylinder(d=9.4,h=4.4,$fn=6);}}
module shoulder_cap(){difference(){rr(46,24,4);for(x=[-18.5,18.5])translate([x,0,0])hole(m3,8);}}

// ---- Revision C enclosed links. Each link has an idler half and a driven half, printed plate-down.
// Half = 5 plate + 2.4 walls 26 deep, meeting at the link mid-plane with 52 mm between plates.
// Proximal clevis (x<28) stays open so the previous joint's servo body and block can rotate through it.
// The distal block is the integral servo pocket half (replaces the separate cassette and cap).
plate_t=5; wall_t=2.4; half_w=26; floor_t=5.4; wall_start=28;
module link_profile(l){hull(){circle(r=16);translate([l-29.75,0])rr2(24.5,46,4);}}
module arm_half(l,idler=false){difference(){union(){
  linear_extrude(plate_t)link_profile(l);
  translate([0,0,plate_t])linear_extrude(half_w)intersection(){difference(){link_profile(l);offset(r=-wall_t)link_profile(l);}translate([wall_start,-40])square([l,80]);}
  translate([35,0,plate_t])cylinder(d=8,h=half_w);
  translate([l-29.75,0,plate_t])linear_extrude(half_w)rr2(24.5,46,4);
  if(idler)translate([0,0,plate_t])linear_extrude(floor_t)hull(){translate([l-24,0])circle(r=10);translate([l,0])circle(r=10);}}
 if(idler)translate([0,0,-1])cylinder(d=16.2,h=plate_t+2);else servo_arm_holes(plate_t+2);
 translate([35,0,0])hole(m3,40);
 for(y=[-18.5,18.5])translate([l-25,y,0])hole(m3,40);
 translate([l-37.6,-10.35,plate_t+floor_t])cube([35,20.7,40]);
 translate([l-43,-8,plate_t+11])cube([15,16,24]);
 if(idler){translate([l,0,plate_t-1])cylinder(d=m5,h=floor_t+2);translate([l,0,plate_t+floor_t-4.2])cylinder(d=9.4,h=4.5,$fn=6);}
 translate([l-53,-40,plate_t+half_w])rotate([-90,0,0])hull(){for(x=[-6,6])translate([x,0,0])cylinder(d=9,h=40);}}}
module arm_right(l){mirror([0,1,0])arm_half(l,false);}
module horn_spacer(){difference(){linear_extrude(3.3)hull(){circle(d=14);translate([25,0])circle(d=10);}servo_arm_holes(6);}}
module head_yoke(){difference(){union(){translate([0,0,30])rr(74,44,6);for(x=[-31,26])translate([x,0,15])rotate([0,90,0])linear_extrude(5)hull(){circle(r=15);translate([-15,0])square([15,30],center=true);}}translate([24,0,15])rotate([0,90,0])cylinder(d=16.2,h=10);translate([-33,0,15])rotate([0,90,0])rotate(90)servo_arm_holes(10);translate([0,0,29])screw4(27,15,m3,10);translate([-50,-50,36])cube([100,100,10]);translate([-18.2,-9,29.8])cube([36.4,18,2]);translate([-10,-11,29])cube([5,22,8]);translate([0,0,28])rr(26,8,10);}}

// ---- Head shells. shell_shared() carries everything both variants have in common; children() adds the variant bosses.
module shell_shared(vents){difference(){union(){cylinder(d=head_d,h=3);ring(head_d,head_d-6,36);children();for(a=[0:90:270])rotate(a)translate([82,-18,0])cube([6,36,26]);for(a=[0:45:315])rotate(a)translate([76,0,3])cylinder(d=8,h=21);for(a=[22.5:45:337.5])rotate(a)translate([83,0,3])cylinder(d=9,h=32);}for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(2.8,44);translate([0,0,-1])rr(26,8,8);for(x=[-27,27],y=[-15,15])translate([x,y,0])hole(m3,12);for(a=vents)rotate(a)translate([65,0,0])hull(){hole(3.5,6);translate([8,0,0])hole(3.5,6);}}}
module head_mount_bosses(){for(a=[45:90:315])rotate(a)translate([60,0,2])difference(){cylinder(d=10,h=33);hole(2.8,39);}for(a=[0:90:270])rotate(a)translate([45,0,2])difference(){cylinder(d=8,h=30.5);hole(2.8,35);}for(x=[-34,34],y=[-34,34])translate([x,y,2])difference(){cylinder(d=8,h=12);hole(2.8,16);}for(x=[-27,27],y=[-15,15])translate([x,y,0])difference(){cylinder(d=9,h=9);hole(2.8,12);}}
module head_shell(){shell_shared([200:10:340])head_mount_bosses();}
module outer_bezel(){difference(){union(){ring(176,160.5,4);translate([0,0,0])ring(171.5,165.6,7);}translate([0,0,-0.1])cylinder(d=165.5,h=1.5);for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(m3,10);}}
module face_center(){difference(){cylinder(d=142.6,h=4);hole(68.6,8);translate([0,0,-0.1])ring(145,140.5,1.5);for(a=[45:90:315])rotate(a)translate([60,0,0])hole(m3,8);}}
module white_carrier(){difference(){union(){ring(68,51,2);for(a=[0:90:270])rotate(a)translate([39.5,0,0])rr(23,10,2);}for(a=[0:90:270])rotate(a)translate([45,0,0])hole(m3,6);}}
module lcd_cradle(){difference(){union(){rr(77,77,3);translate([0,0,3])difference(){rr(61.8,61.8,12);rr(55.8,55.8,14,0.4);}for(x=[-34,34],y=[-34,34])translate([x,y,3])cylinder(d=8,h=12);}translate([0,0,0])rr(49,49,5);for(x=[-34,34],y=[-34,34])translate([x,y,0])hole(m3,23);translate([0,-29,7])cube([19,14,13],center=true);}}
module lcd_retainer(){difference(){rr(77,77,3);hole(70,6);for(x=[-34,34],y=[-34,34])translate([x,y,0])hole(m3,7);}}
module outer_diffuser(){difference(){union(){ring(160,143,1.2);translate([0,0,1.1])ring(160,158.8,4.8);translate([0,0,1.1])ring(144.2,143,4.8);translate([0,0,5]){ring(165,158.8,1.2);ring(144.2,141,1.2);}}for(a=[22.5:45:337.5])rotate(a)translate([83,0,0])hole(3.6,9);}}
module inner_diffuser(){union(){ring(68,47.8,1.2);translate([0,0,1.1])ring(67.8,65.8,4.8);translate([0,0,1.1])ring(49.8,47.8,4.8);}}
module cable_clip(){difference(){rr(18,12,8);translate([0,0,4])rotate([90,0,0])cylinder(d=6,h=15,center=true);for(x=[-6,6])translate([x,0,0])hole(2.5,12);}}
module fit_coupon(){difference(){rr(96,34,5);for(i=[0:3])translate([-38+i*13,0,0])hole(3.0+0.2*i,9);translate([20,0,-1])cylinder(d=16.2,h=8);translate([34,0,0])servo_arm_holes(9);}}

// ---- Optional head retained from revision B: Waveshare 4inch DSI LCD (C), Ø126 case, four M4 bosses.
// Ø7.1 x4 at (±37.5,±37.5) on the rear, PCB 85.5 x65 offset toward -Y, components to 8.2 behind the boss ends.
// Head Z datums: LCD rim front 35.5; case rear plate 29.5; boss ends 25.5; carrier plate 20.5-23.5 with pads to 25.5.
lcd4_bosses=[[-37.5,-37.5],[37.5,-37.5],[-37.5,37.5],[37.5,37.5]];
carrier_bosses=[[-55,-38],[55,-38],[-55,38],[55,38]];
face_boss_r=67.8;
module head_mount_bosses_dsi(){for(a=[45:90:315])rotate(a)translate([face_boss_r,0,2])difference(){cylinder(d=7.5,h=33);hole(2.8,39);}for(p=carrier_bosses)translate([p[0],p[1],2])difference(){cylinder(d=7,h=18.5);hole(2.8,24);}for(x=[-27,27],y=[-15,15])translate([x,y,0])difference(){cylinder(d=9,h=9);hole(2.8,12);}}
module head_shell_dsi(){shell_shared([200,230,240,250,260,270,280,290,300,310,340])head_mount_bosses_dsi();}
module lcd4_carrier(){difference(){union(){cylinder(d=140,h=3);for(p=lcd4_bosses)translate([p[0],p[1],0])cylinder(d=8,h=5);}translate([6,-1.5,-1])rr(100,63,8,4);translate([-10.5,-36,-1])rr(43,10,8,3);for(p=lcd4_bosses)translate([p[0],p[1],0])hole(4.4,8);for(p=carrier_bosses)translate([p[0],p[1],0])hole(m3,8);for(a=[45:90:315])rotate(a)translate([face_boss_r,0,0])hole(8.5,8);}}
module face_ring_dsi(){difference(){cylinder(d=142.6,h=4);translate([0,0,-1])cylinder(d1=106,d2=118,h=6);translate([0,0,-0.1])ring(145,140.5,1.5);for(a=[45:90:315])rotate(a)translate([face_boss_r,0,0])hole(m3,8);}}

if(part=="base_tub")base_tub();
else if(part=="base_lid")translate([0,0,2])base_lid();
else if(part=="electronics_tray")electronics_tray();
else if(part=="yaw_mount")yaw_mount();
else if(part=="yaw_cap")yaw_cap();
else if(part=="turntable")turntable();
else if(part=="shoulder_tower")shoulder_tower();
else if(part=="shoulder_cap")shoulder_cap();
else if(part=="upper_arm_left")arm_half(upper_pitch,true);
else if(part=="upper_arm_right")arm_right(upper_pitch);
else if(part=="forearm_left")arm_half(forearm_pitch,true);
else if(part=="forearm_right")arm_right(forearm_pitch);
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
else if(part=="cable_clip")cable_clip();
else if(part=="fit_coupon")fit_coupon();
else if(part=="head_shell_dsi")head_shell_dsi();
else if(part=="lcd4_carrier")lcd4_carrier();
else if(part=="face_ring_dsi")face_ring_dsi();
else {base_tub();translate([0,0,56])base_lid();translate([0,0,64])turntable();translate([0,0,77])shoulder_tower();}
