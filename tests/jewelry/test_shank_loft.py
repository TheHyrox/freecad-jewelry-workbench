import math
import FreeCAD
import Part

r_in = 16.92 / 2.0 # US 6.5

def make_profile_wire(cx, cz, nx, nz, w, t, profile_type="ComfortFit"):
    # Center on inner circle is (cx, 0, cz)
    # Radial outward normal is (nx, 0, nz)
    # Axial is (0, 1, 0)
    radial = FreeCAD.Vector(nx, 0, nz)
    axial = FreeCAD.Vector(0, 1, 0)
    
    # 4 corners of cross section
    # P1: inner left, P2: inner right, P3: outer right, P4: outer left
    p1 = FreeCAD.Vector(cx, -w/2.0, cz)
    p2 = FreeCAD.Vector(cx, w/2.0, cz)
    
    if profile_type == "RoundWire":
        # Circular wire centered at r_in + t/2
        c = FreeCAD.Vector(cx, 0, cz) + radial * (t / 2.0)
        circ = Part.Circle(c, FreeCAD.Vector(nx, 0, nz).cross(axial), t / 2.0)
        return Part.Wire(circ.toShape())
        
    elif profile_type == "ComfortFit":
        # Curved outer crown with 3 points
        p_mid_outer = FreeCAD.Vector(cx, 0, cz) + radial * t
        p3 = FreeCAD.Vector(cx, w/2.0, cz) + radial * (t * 0.65)
        p4 = FreeCAD.Vector(cx, -w/2.0, cz) + radial * (t * 0.65)
        
        # Outer arc through p4 -> p_mid_outer -> p3
        arc_outer = Part.Arc(p4, p_mid_outer, p3).toShape()
        e_right = Part.makeLine(p3, p2)
        e_inner = Part.makeLine(p2, p1)
        e_left = Part.makeLine(p1, p4)
        return Part.Wire([e_inner, e_right, arc_outer, e_left])
        
    else: # Flat or HalfRound
        p3 = FreeCAD.Vector(cx, w/2.0, cz) + radial * t
        p4 = FreeCAD.Vector(cx, -w/2.0, cz) + radial * t
        return Part.makePolygon([p1, p2, p3, p4, p1])

# Make right half (theta from -pi/2 (bottom) to +pi/2 (top))
n_steps = 12
wires = []
for i in range(n_steps):
    theta = -math.pi/2.0 + (math.pi) * i / (n_steps - 1)
    # Blend parameter from bottom (0) to top (1)
    k = (theta + math.pi/2.0) / math.pi
    # Taper: bottom is 2.2mm width, 1.8mm thick; shoulder is 1.4mm width, 1.2mm thick
    w = 2.2 * (1 - k) + 1.4 * k
    t = 1.8 * (1 - k) + 1.2 * k
    
    # Position: ring in XZ plane, top is +Z, bottom is -Z
    cx = r_in * math.cos(theta)
    cz = r_in * math.sin(theta)
    nx = math.cos(theta)
    nz = math.sin(theta)
    
    wire = make_profile_wire(cx, cz, nx, nz, w, t, "ComfortFit")
    wires.append(wire)

half = Part.makeLoft(wires, True, False)
print("Half loft valid?", half.isValid(), "Volume:", half.Volume)

# Mirror across YZ plane (x -> -x)
mirrored = half.mirror(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
shank = half.fuse(mirrored)
print("Shank fused valid?", shank.isValid(), "Volume:", shank.Volume)
