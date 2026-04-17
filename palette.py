# %%

from build123d import *
#from ocp_vscode import show

# mixers half width
well_count = 8
wells_per_mixer = 2
# we need whole number of mixers!
assert(well_count % wells_per_mixer == 0)
mixer_count = well_count // wells_per_mixer
# using default unit MM
well_width = 10
well_wall = 1
well_length = 31
well_depth = 3
# the extra high divider which helps the well side slot into the mixer side
well_divider_depth = 5
well_divider_extra = well_divider_depth - well_depth
well_divider_clearance = 0.5
well_side_skirt = 1
well_side_thickness = 2

mixer_wall = well_wall
mixer_width = well_width * wells_per_mixer + mixer_wall * (wells_per_mixer - 1)
mixer_depth = 3
mixer_divider_depth = mixer_depth - well_divider_extra
# needs to cover
mixer_length = well_length + 2 * well_wall

mixer_side_skirt = 0
mixer_side_thickness = 2

total_height = (mixer_side_thickness + well_side_thickness + well_depth + mixer_divider_depth)
# maximise hinge!
hinge_radius = total_height / 2
hinge_axel_radius = hinge_radius * 0.75
hinge_axel_length = hinge_axel_radius
hinge_gap = 0.5
# gap between axel and socket
hinge_clearance = 0.5
# space between body and hinge
hinge_offset = 1

hinge_offset = 2

total_x_length = well_count * (well_wall + well_width) + well_wall + well_side_skirt * 2
total_y_length = well_length + 2 * well_wall + 2 * well_side_skirt

hinge_section_x_length = (total_x_length - 2 * hinge_gap) / 3 # should be 30 

assembly_rotation = 0 # flat - use 180 to rotate mixer side about hinge to lay closed

fitting_clearance = 0.2

# %%

with BuildPart() as hinge_well_side:
    # left side first
    with BuildSketch(Plane.YZ) as hinge_section:
        with Locations((0, hinge_radius)):
            Circle(hinge_radius)
    extrude(amount=hinge_section_x_length)

    # cut a notch for rubber band
    with BuildSketch(Plane.YZ) as notch_section:#hinge_well_side.faces().sort_by(Axis.X)[0])) as notch_section:
        with Locations((0, hinge_radius*2)):
            Circle(hinge_axel_radius, align=(Align.CENTER, Align.CENTER))
    extrude(amount=hinge_section_x_length*0.75, taper=5, mode=Mode.SUBTRACT)

    with BuildSketch(faces().sort_by(Axis.X)[-1]) as rod_section:
        Circle(hinge_axel_radius)
    extrude(amount=hinge_axel_length,taper=44)
    
    # add connector for stregth
    with BuildSketch(Plane.YZ) as hinge_connection:
        with Locations((hinge_radius, hinge_radius)):
            Rectangle(2*hinge_radius + hinge_offset + well_side_skirt, hinge_radius, align=Align.MAX)
    extrude(amount=hinge_section_x_length)



# %%

hinge_right_well_side = mirror(hinge_well_side.part, about=Plane.YZ.offset(total_x_length/2))

# %%

with BuildPart() as wells:
    # base
    with BuildSketch(Plane.YZ) as well_section:
        with Locations((-(hinge_radius + hinge_offset), well_side_thickness)):
            Rectangle(total_y_length, well_side_thickness, align=Align.MAX)
    extrude(amount=total_x_length)

    # get well plane before filleting
    base_surface = wells.faces().sort_by(Axis.Z)[-1]
    base_origin = base_surface.vertices().sort_by(Axis.X).sort_by(Axis.Y)[0]

    # soften corners
    # fillet(wells.edges().filter_by(Axis.Z), radius=1)

    # layout wells
    with BuildSketch(
        Plane(
            z_dir=base_surface.normal_at(),
            origin=base_origin
        )
    ) as well_plan:
        with Locations((well_side_skirt, well_side_skirt)):
            Rectangle(
                well_count * (well_wall + well_width) + well_wall,
                2 * well_wall + well_length,
                align = Align.MIN
            )
            for well_num in range(0, well_count):
                with Locations((well_wall + well_num * (well_width + well_wall), well_wall)):
                    Rectangle(
                        well_width,
                        well_length,
                        align=Align.MIN,
                        mode=Mode.SUBTRACT
                    )
    extrude(amount=well_depth - (mixer_depth - mixer_divider_depth))

    inside_edges = wells.edges().filter_by(lambda e: e.is_interior)
    fillet(inside_edges, radius=0.6)

    extrude(faces().sort_by(Axis.Z)[-1], amount=(mixer_depth - mixer_divider_depth),taper=5)
    # inside_edges = wells.edges().filter_by(lambda e: e.is_interior)
    # fillet(inside_edges, radius=0.2)


with BuildPart() as hinge_mixer_side:
    # create a half length piece since we want to mirror the socket at the other end
    with BuildSketch(Plane.YZ.offset(hinge_section_x_length + hinge_gap)) as hinge_section:
        with Locations((0, hinge_radius)):
            Circle(hinge_radius)
    extrude(amount=hinge_section_x_length/2)
    # add the connection to the base
    with BuildSketch(Plane.YZ.offset(hinge_section_x_length + hinge_gap)) as hinge_connection:
        with Locations((-hinge_radius, hinge_radius)):
            Rectangle(2*hinge_radius + hinge_offset, hinge_radius, align=(Align.MIN, Align.MAX))
    extrude(amount=hinge_section_x_length/2)
    # finally subtract socket
    #with BuildSketch(hinge_mixer_side.faces().sort_by(Axis.X)[0]) as socket_section:
    with BuildSketch(Plane.YZ.offset(hinge_section_x_length + hinge_gap)) as socket_section:
        with Locations((0,hinge_radius)):
            Circle(hinge_axel_radius, align=Align.CENTER)
    extrude(amount=hinge_axel_length,taper=44, mode=Mode.SUBTRACT)
    # mirror about central section of part
    mirror(hinge_mixer_side.part, about=Plane(hinge_mixer_side.faces().sort_by(Axis.X)[-1]), mode=Mode.ADD)


# %%

with BuildPart() as mixer:
    # base
    with BuildSketch(Plane.YZ) as mixer_section:
        with Locations(((hinge_radius + hinge_offset), well_side_thickness)):
            Rectangle(total_y_length, mixer_side_thickness, align=(Align.MIN, Align.MAX))
    extrude(amount=total_x_length)

    # wells
    base_surface = mixer.faces().sort_by(Axis.Z)[-1]
    base_origin = base_surface.vertices().sort_by(Axis.X).sort_by(Axis.Y)[0]
    
    with BuildSketch(
        Plane(
            z_dir=base_surface.normal_at(),
            origin=base_origin
        )
    ) as mixer_plan:
        with Locations((mixer_side_skirt, mixer_side_skirt)):
            Rectangle(
                mixer_count * (mixer_wall + mixer_width) + mixer_wall + 2 * well_wall,
                2 * mixer_wall + mixer_length,
                align = Align.MIN
            )
            for mixer_num in range(0, mixer_count):
                overlap_shim = 0
                offset_shim = 0
                if mixer_num == 0 or mixer_num == mixer_count - 1:
                    overlap_shim = well_wall
                if mixer_num != 0:
                    offset_shim = well_wall
                with Locations((mixer_wall + mixer_num * (mixer_width + mixer_wall) + offset_shim, mixer_wall)):
                    Rectangle(
                        mixer_width + overlap_shim,
                        mixer_length,
                        align=Align.MIN,
                        mode=Mode.SUBTRACT
                    )
    extrude(amount=mixer_depth - fitting_clearance)

    # fillet it a bit
    inside_edges = mixer.edges().filter_by(lambda e: e.is_interior)
    fillet(inside_edges, radius=0.6)

    # cut down the dividers to allow wells to fit inside
    base_surface = mixer.faces().sort_by(Axis.Z)[-1]
    base_origin = base_surface.vertices().sort_by(Axis.X).sort_by(Axis.Y)[0]
    with BuildSketch(
        Plane(
            z_dir=base_surface.normal_at(),
            origin=base_origin
        )
    ) as cutout_plan:
        with Locations((mixer_side_skirt + mixer_wall, mixer_side_skirt + mixer_wall)):
            Rectangle(
                mixer_count * (mixer_wall + mixer_width) - mixer_wall + 2 * well_wall,
                mixer_length,
                align = Align.MIN
            )
            # TODO calculate offset and taper for fitting
            offset(amount=0.4)

    extrude(amount=-(mixer_depth-mixer_divider_depth), taper=7, mode=Mode.SUBTRACT)


# %%

# show(wells, mixer, hinge_mixer_side, hinge_right_well_side, hinge_well_side)

# %%

assembly = Compound(label="palette", children=[
        wells.part,
        mixer.part,
        hinge_mixer_side.part,
        hinge_right_well_side,
        hinge_well_side.part
    ]
)
# %% 

export_stl(assembly, "palette_build123d.stl")
