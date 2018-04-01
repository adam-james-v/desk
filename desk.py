import cadquery as cq
import cqmods.cqview as cqv
import cqmods.cqview as cqv
import cqparts
import cqparts.params as par
from cqparts.display import render_props
from cqparts.constraint import Mate, Fixed, Coincident
from cqparts.utils.geometry import CoordSystem

# USE INCHES AS UNIT
# PARAMS
W = 65.0
D = 30.0
H = 32.0

class Surface(cqparts.Part):
    """Thin box used for shelves, desk top, etc."""
    width = par.PositiveFloat(36.0, doc="width of the surface")
    depth = par.PositiveFloat(16.0, doc="depth of the surface")
    thickness = par.PositiveFloat(0.875, doc="thickness of the surface")
    
    _render = render_props(template='wood')
    def make(self):
        result = (cq.Workplane('XY')
            .box(self.width, self.thickness, self.depth, centered=(True, False, True))
        )
        return result

    @property
    def mate_bottom(self):
        return Mate(self, CoordSystem(
           origin=(0, self.thickness, 0),
           xDir=(0, 1, 0),
           normal=(0, 0, 1) 
        ))

    @property
    def mate_edge(self):
        return Mate(self, CoordSystem(
           origin=(self.width/2.0, 0, self.depth/2.0),
           xDir=(-1, 0, 0),
           normal=(0, 0, -1) 
        ))

    @property        
    def mate_L1(self):
        return Mate(self, CoordSystem(
           origin=(self.width/2.0, self.thickness, self.depth/2.0),
           xDir=(0, 1, 0),
           normal=(0, 0, 1) 
        ))

    @property    
    def mate_L2(self):
        return Mate(self, CoordSystem(
           origin=(self.width/2.0, self.thickness, -self.depth/2.0),
           xDir=(0, 1, 0),
           normal=(0, 0, 1) 
        ))

    @property        
    def mate_R1(self):
        return Mate(self, CoordSystem(
           origin=(-self.width/2.0, self.thickness, self.depth/2.0),
           xDir=(0, 1, 0),
           normal=(0, 0, 1) 
        ))

    @property                
    def mate_R2(self):
        return Mate(self, CoordSystem(
           origin=(-self.width/2.0, self.thickness, -self.depth/2.0),
           xDir=(0, 1, 0),
           normal=(0, 0, 1) 
        ))

desk_top = Surface(width=W, depth=D)

class Tube(cqparts.Part):
    """Creates a RECT metal tube"""
    # PROFILE PARAMS
    base = par.PositiveFloat(1.0, doc="base length of tube profile")
    height = par.PositiveFloat(1.0, doc="height of tube profile")
    thickness = par.PositiveFloat(0.063, doc="thickness of tube wall")
    # PART PARAMS
    length = par.PositiveFloat(12.0, doc="length of tube")

    _render = render_props(template='aluminium')
    def make(self):
        # CALCULATE INNER AND OUTER RADIUS
        outer_radius = self.thickness*1.5
        inner_radius = self.thickness
        outer = (cq.Workplane('XY')
            .box(
                self.length,
                self.height,
                self.base,
                centered=(False, True, True))
            .edges("|X").fillet(outer_radius)
        )
        inner = (cq.Workplane('XY')
            .box(
                self.length, 
                self.height - self.thickness*2.0, 
                self.base - self.thickness*2.0, 
                centered=(False, True, True))
            .edges("|X").fillet(inner_radius)
        )
        result = outer.cut(inner)
        return result

    @property
    def mate_front(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, 0),
           xDir=(1, 0, 0),
           normal=(0, 0, 1) 
        ))

    @property
    def mate_back(self):
        return Mate(self, CoordSystem(
           origin=(self.length, 0, 0),
           xDir=(1, 0, 0),
           normal=(0, -1, 0) 
        ))

    @property
    def mate_corner01(self):
        return Mate(self, CoordSystem(
           origin=(self.length, -self.height/2.0, self.base/2.0),
           xDir=(-1, 0, 0),
           normal=(0, -1, 0) 
        ))

    @property
    def mate_corner02(self):
        return Mate(self, CoordSystem(
           origin=(self.length, -self.height/2.0, -self.base/2.0),
           xDir=(-1, 0, 0),
           normal=(0, -1, 0) 
        ))

    @property
    def mate_corner03(self):
        return Mate(self, CoordSystem(
           origin=(self.length, self.height/2.0, self.base/2.0),
           xDir=(-1, 0, 0),
           normal=(0, -1, 0) 
        ))

    @property
    def mate_corner04(self):
        return Mate(self, CoordSystem(
           origin=(self.length, self.height/2.0, -self.base/2.0),
           xDir=(-1, 0, 0),
           normal=(0, -1, 0) 
        ))


class CableTray(cqparts.Part):
    """Creates a cable tray"""
    # PROFILE PARAMS
    base = par.PositiveFloat(5.5, doc="base length of tube profile")
    height = par.PositiveFloat(4.0, doc="height of tube profile")
    thickness = par.PositiveFloat(0.5, doc="thickness of tube wall")
    # PART PARAMS
    length = par.PositiveFloat(65.0, doc="length of tube")
    gap_width = par.PositiveFloat(1.0, doc="gap width")

    _render = render_props(template='aluminium')
    def make(self):
        # CALCULATE INNER AND OUTER RADIUS
        outer_radius = self.thickness*1.5
        inner_radius = self.thickness
        outer = (cq.Workplane('XY')
            .box(
                self.length,
                self.height,
                self.base,
                centered=(False, True, True))
        )
        inner = (cq.Workplane('XY')
            .box(
                self.length, 
                self.height - self.thickness*2.0, 
                self.base - self.thickness*2.0, 
                centered=(False, True, True))
        )
        gap = (cq.Workplane('XY')
            .box(
                self.length, 
                self.gap_width, 
                self.gap_width, 
                centered=(False, True, True))
                .findSolid().translate((0, self.height/2.0, 0))
        )
        result = outer.cut(inner).cut(gap)
        return result

    @property
    def mate_top(self):
        return Mate(self, CoordSystem(
           origin=(self.length, self.height/2.0, self.base/2.0),
           xDir=(-1, 0, 0),
           normal=(0, 0, 1) 
        ))


class Desk(cqparts.Assembly):
    def make_components(self):
        components = {
            'TableTop': desk_top,
            'Leg1': Tube(length=H),
            'Leg2': Tube(length=H),
            'Leg3': Tube(length=H),
            'Leg4': Tube(length=H),
            'Tray': CableTray(length=W),
        }
        return components

    def make_constraints(self):
        constraints = [
            Fixed(self.components['TableTop'].mate_origin, CoordSystem()),
            Coincident(
                self.components['Leg1'].mate_corner01,
                self.components['TableTop'].mate_L1,
            ),
            Coincident(
                self.components['Leg2'].mate_corner03,
                self.components['TableTop'].mate_L2,
            ),
            Coincident(
                self.components['Leg3'].mate_corner02,
                self.components['TableTop'].mate_R1,
            ),
            Coincident(
                self.components['Leg4'].mate_corner04,
                self.components['TableTop'].mate_R2,
            ),
            Coincident(
                self.components['Tray'].mate_top,
                self.components['TableTop'].mate_edge,
            ),
        ]
        return constraints




desk = Desk()
# tray = CableTray()
# cqv.show_svg(leg.make())

desk.exporter('gltf')('web_view/result.gltf', embed=True)