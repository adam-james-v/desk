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
        result = (cq.Workplane('XZ')
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
                self.base,
                self.height,
                centered=(False, True, True))
            .edges("|X").fillet(outer_radius)
        )
        inner = (cq.Workplane('XY')
            .box(
                self.length,
                self.base - self.thickness*2.0,
                self.height - self.thickness*2.0,
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


class Bearing(cqparts.Part):
    """Creates a roller bearing"""
    # PARAMS
    outer_diameter = par.PositiveFloat(2.045, doc="outer diameter of the bearing")
    inner_diameter = par.PositiveFloat(0.98, doc="inner diameter of the bearing")
    thickness = par.PositiveFloat(0.587, doc="thickness of the bearing")

    _render = render_props(template='aluminium')
    def make(self):
        result = (cq.Workplane('XY')
            .workplane(offset=-self.thickness/2.0)
            .circle(self.outer_diameter/2.0)
            .circle(self.inner_diameter/2.0)
            .extrude(self.thickness)
            .edges().fillet(0.06) #TODO: remove hardcoded fillet value?
        )
        return result

    @property
    def mate_concentric_front(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, self.thickness/2.0),
           xDir=(1, 0, 0),
           normal=(0, 0, 1)
        ))

    @property
    def mate_concentric_back(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, -self.thickness/2.0),
           xDir=(1, 0, 0),
           normal=(0, 0, -1)
        ))


class PivotArm(cqparts.Part):
    # hole_diameter = PositiveFloat(20, "diameter for shaft")
    inner = par.Boolean(True)    
    length = par.PositiveFloat(36.0)
    slot_thickness = Bearing.thickness
    slot_depth = Bearing.outer_diameter
    
    def make(self):
        if self.inner:
            b = 1.0
        else:
            b = 0.5
        #TODO: use proper inheritance here
        obj = (Tube(base=b, height=1.0, length=self.length).make()
            .faces('>Y').workplane()
            .moveTo(0, 0).circle(0.25)
            .moveTo(-(self.length/2.0 - 0.5), 0).circle(0.25)
            .moveTo( (self.length/2.0 - 0.5), 0).circle(0.25)
            .cutThruAll()
        )
        if self.inner:
            result = (obj
                .faces('<X').workplane()
                .rect(self.slot_thickness, self.height)
                .cutBlind(-self.slot_depth)
            )
        else:
            result = obj
        return result




class Bushing(cqparts.Part):
    """Creates a bushing for the roller bearing"""
    # PARAMS
    lip_diameter = par.PositiveFloat(1.155, doc="outer diameter of the bearing")
    body_diameter = par.PositiveFloat(0.98, doc="outer diameter of the bearing")
    inner_diameter = par.PositiveFloat(0.504, doc="inner diameter of the bearing")
    lip_thickness = par.PositiveFloat(0.092, doc="thickness of the bearing")
    body_thickness = par.PositiveFloat(0.285, doc="thickness of the bearing")

    _render = render_props(template='red')
    def make(self):
        result = (cq.Workplane('XY')
            .circle(self.lip_diameter/2.0)
            .extrude(self.lip_thickness)
            .faces('<Z').workplane()
            .circle(self.body_diameter/2.0)
            .extrude(self.body_thickness)
            .faces('<Z').workplane()
            .circle(self.inner_diameter/2.0)
            .cutThruAll()
        )
        return result

    @property
    def mate_concentric(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, 0),
           xDir=(1, 0, 0),
           normal=(0, -1, 0)
        ))

    @property
    def mate_concentric_outer(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, -(self.lip_thickness + 0.1)), # don't hardcode the offset???
           xDir=(1, 0, 0),
           normal=(0, 1, 0)
        ))


class Bolt(cqparts.Part):
    """Creates a bolt"""
    # PARAMS
    # TODO: USE proper bolt grades / specs as params. Use a lookup table? maybe pull from Wikipedia or eng. source
    length = par.PositiveFloat(2.0)
    diameter = par.PositiveFloat(0.5)

    _render = render_props(template='aluminium')
    def make(self):
        result = (cq.Workplane('XZ')
            .polygon(6, self.diameter*1.7)
            .extrude(self.diameter*0.55)
            .faces('<Y').workplane()
            .circle(self.diameter/2.0)
            .extrude(self.length)
            .edges('<Y')
            .fillet(0.1)
        )
        return result

    @property
    def mate_concentric(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, -self.diameter*0.55),
           xDir=(1, 0, 0),
           normal=(0, 0, 1)
        ))
    

class Nut(cqparts.Part):
    """Creats a nut"""
    # PARAMS 
    diameter = par.PositiveFloat(0.85) #TODO: Make this consistent with the bolt?
    thread_diameter = par.PositiveFloat(0.405)
    thickness = par.PositiveFloat(0.4)

    _render = render_props(template='aluminium')
    def make(self):
        result = (cq.Workplane('XZ')
            .polygon(6, self.diameter)
            .circle(self.thread_diameter/2.0)
            .extrude(self.thickness)           
        )
        return result

    @property
    def mate_concentric(self):
        return Mate(self, CoordSystem(
           origin=(0, 0, -self.thickness),
           xDir=(1, 0, 0),
           normal=(0, 0, 1)
        ))
    

class BearingASM(cqparts.Assembly):
    def make_components(self):
        components = {
            'bearing': Bearing(),
            'bushingA': Bushing(),
            'bushingB': Bushing(),
            'bolt': Bolt(),
            'nut': Nut(),
        }
        return components

    def make_constraints(self):
        constraints = [
            Fixed(self.components['bearing'].mate_origin, CoordSystem()),
            Coincident(
                self.components['bushingA'].mate_origin,
                self.components['bearing'].mate_concentric_front,
            ),
            Coincident(
                self.components['bushingB'].mate_origin,
                self.components['bearing'].mate_concentric_back,
            ),
            Coincident(
                self.components['bolt'].mate_concentric,
                self.components['bushingA'].mate_concentric_outer,
            ),  
            Coincident(
                self.components['nut'].mate_concentric,
                self.components['bushingB'].mate_concentric_outer,
            ),      
        ]
        return constraints


class Desk(cqparts.Assembly):
    def make_components(self):
        components = {
            'TableTop': desk_top,
            'Leg1': Tube(length=H),
            'Leg2': Tube(length=H),
            'Leg3': Tube(length=H),
            'Leg4': Tube(length=H),
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
        ]
        return constraints



# cqv.show_svg(leg.make())

PivotArm(inner=False).exporter('gltf')('web_view/result.gltf', embed=True)
# print(Bearing.outer_diameter())
