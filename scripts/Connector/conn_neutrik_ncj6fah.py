#!/usr/bin/env python3

# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2016 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>

import sys
import os
#sys.path.append(os.path.join(sys.path[0],"..","..","kicad_mod")) # load kicad_mod path

# export PYTHONPATH="${PYTHONPATH}<path to kicad-footprint-generator directory>"
sys.path.append(os.path.join(sys.path[0], "..", ".."))  # load parent path of KicadModTree
from math import sqrt
import argparse
import yaml
# from helpers import *
from KicadModTree import *

sys.path.append(os.path.join(sys.path[0], "..", "tools"))  # load parent path of tools
from footprint_text_fields import addTextFields

def roundToBase(value, base):
    if base == 0:
        return value
    return round(value/base) * base

series = "Combo-A"
series_long = 'Combo A Series'
manufacturer = 'Neutrik'
orientation = 'H'
datasheet = 'https://www.neutrik.com/en/product/ncj6fa-h'
mpn = "NCJ6FA-H"
lib_category = "Audio"

drill_small = 1.2
drill_large = 1.6
annular_ring_large = 0.35
annular_ring_small = 0.25
min_annular_ring = 0.15

pad_size_small = drill_small + 2*annular_ring_small
pad_size_large = drill_large + 2*annular_ring_large
# pad_size_large = drill_large + 2*min_annular_ring

pad_shape=Pad.SHAPE_CIRCLE

def generate_one_footprint(configuration):
    # handle arguments
    orientation_str = configuration['orientation_options'][orientation]
    footprint_name = "Jack_Combo_{manufacturer:s}_{mpn:s}_{orientation:s}".format(
            manufacturer=manufacturer, mpn=mpn, orientation=orientation_str)
    keyword_string = configuration['keyword_fp_string'].format(series=series,
        orientation=orientation_str, man=manufacturer,
        entry=configuration['entry_direction'][orientation])
    lib_name = configuration['lib_name_specific_function_format_string'].format(category=lib_category)

    kicad_mod = Footprint(footprint_name)
    descr_format_str = "Neutrik {series_long:s}, part number: {mpn:s}, 3 pole XLR female receptacle with 1/4\" stereo jack, {orientation:s} PCB mount ({datasheet:s}), generated with kicad-footprint-generator"
    description = descr_format_str.format(series_long=series_long, mpn=mpn, orientation=orientation_str, datasheet=datasheet)
    kicad_mod.setDescription(description)
    kicad_mod.setTags(keyword_string)

    # calculate working values
    nudge = configuration['silk_fab_offset']
    silk_w = configuration['silk_line_width']
    fab_w = configuration['fab_line_width']


    x_offset = -13.97 / 2.0
    y_offset = 18.415

    width = 25.0
    length_to_bulkhead = 24.5
    length_overhang = 5.7
    body_edge = {
        'left': -width/2.0 - x_offset,
        'right': width/2.0 - x_offset,
        'top': -length_overhang - y_offset,
        'bottom': length_to_bulkhead - y_offset
        }

    # create pads
    pads = [
        Pad(number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(-6.985 - x_offset, 18.415 - y_offset),
            size=pad_size_small, drill=drill_small, layers=Pad.LAYERS_THT),
        Pad(number=2, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(6.985 - x_offset, 19.05 - y_offset),
            size=pad_size_small, drill=drill_small, layers=Pad.LAYERS_THT),
        Pad(number=3, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(0 - x_offset, 23.495 - y_offset),
            size=pad_size_small, drill=drill_small, layers=Pad.LAYERS_THT),
        Pad(number="T", type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(-4.445 - x_offset, 15.875 - y_offset),
            size=pad_size_large, drill=drill_large, layers=Pad.LAYERS_THT),
        Pad(number="T", type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(4.445 - x_offset, 15.875 - y_offset),
            size=pad_size_large, drill=drill_large, layers=Pad.LAYERS_THT),
        Pad(number="R", type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(2.8575 - x_offset, 22.876 - y_offset),
            size=pad_size_small, drill=drill_small, layers=Pad.LAYERS_THT),
        Pad(number="S", type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(-2.8575 - x_offset, 22.876 - y_offset),
            size=pad_size_small, drill=drill_small, layers=Pad.LAYERS_THT),
        Pad(number="G", type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=(-8.255 - x_offset, 6.985 - y_offset),
            size=pad_size_large, drill=drill_large, layers=Pad.LAYERS_THT),
        Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=(-5.715 - x_offset, 6.35 - y_offset),
            size=drill_large, drill=drill_large, layers=Pad.LAYERS_NPTH),
        Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=(5.715 - x_offset, 6.35 - y_offset),
            size=drill_large, drill=drill_large, layers=Pad.LAYERS_NPTH),
        Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, at=(0 - x_offset, 9.525 - y_offset),
            size=drill_large, drill=drill_large, layers=Pad.LAYERS_NPTH)
        ]

    for pad in pads:
        kicad_mod.append(pad)

    # create silkscreen and fab outline
    y_flange_top = 0.0 - y_offset
    y_flange_bottom = y_flange_top + 6.25 # approx
    y_shell_top = y_flange_top - 3.4 # approx
    y_connector_front = body_edge['top']
    y_tab_front = y_flange_top - 7.6 # approx

    x_connector_face_left = -15.5/2 - x_offset # approx
    x_connector_face_right = 15.5/2 - x_offset # approx
    x_flange_right = body_edge['right']
    x_flange_left = body_edge['left']
    x_body_right = 22.0/2 - x_offset
    x_body_left = -22.0/2 - x_offset

    silk_outline = [
        {'x': x_flange_right + nudge, 'y': y_flange_top},
        {'x': x_flange_right + nudge, 'y': y_flange_bottom + nudge},
        {'x': x_body_right + nudge, 'y': y_flange_bottom + nudge},
        {'x': x_body_right + nudge, 'y': body_edge['bottom'] + nudge},
        {'x': x_body_left - nudge, 'y': body_edge['bottom'] + nudge},
        {'x': x_body_left - nudge, 'y': body_edge['bottom'] + nudge},
        {'x': x_body_left - nudge, 'y': y_flange_bottom + nudge},
        {'x': x_flange_left - nudge, 'y': y_flange_bottom + nudge},
        {'x': x_flange_left - nudge, 'y': y_flange_top},
    ]
    fab_outline = [
        {'x': x_body_left, 'y': body_edge['bottom']},
        {'x': x_body_left, 'y': y_flange_bottom},
        {'x': x_flange_left, 'y': y_flange_bottom},
        {'x': x_flange_left, 'y': y_flange_top},
        {'x': x_body_left, 'y': y_flange_top},
        {'x': x_body_left, 'y': y_shell_top},
        {'x': x_body_right, 'y': y_shell_top},
        {'x': x_body_right, 'y': y_flange_top},
        {'x': x_flange_right, 'y': y_flange_top},
        {'x': x_flange_right, 'y': y_flange_bottom},
        {'x': x_body_right, 'y': y_flange_bottom},
        {'x': x_body_right, 'y': body_edge['bottom']},
        {'x': x_body_left, 'y': body_edge['bottom']},
    ]
    connector_face = [
        {'x': x_connector_face_left, 'y': y_shell_top},
        {'x': x_connector_face_left, 'y': y_connector_front},
        {'x': x_connector_face_right, 'y': y_connector_front},
        {'x': x_connector_face_right, 'y': y_shell_top},
    ]


    kicad_mod.append(PolygoneLine(polygone=silk_outline, layer='F.SilkS', width=silk_w))
    kicad_mod.append(PolygoneLine(polygone=fab_outline, layer='F.Fab', width=fab_w))
    kicad_mod.append(PolygoneLine(polygone=connector_face, layer='F.Fab', width=fab_w))

    # bulkhead marker on user drawings layer
    kicad_mod.append(Line(start=[x_flange_left - 5.0, y_flange_top], end=[x_flange_right + 5.0, y_flange_top], layer='Dwgs.User', width=configuration['courtyard_line_width']))
    kicad_mod.append(Text(text="Bulkhead", type="user", at=[x_flange_left - 2.5, y_flange_top - 0.5], size=[0.5, 0.5], thickness=0.075, layer='Dwgs.User'))

    # pin 1 markers
    # kicad_mod.append(Line(start=[body_edge['left']-0.4, -2.0],\
    #     end=[body_edge['left']-0.4, 2.0], layer='F.SilkS', width=silk_w))

    sl=1
    marker_x_offset = 3.5
    poly_pin1_marker = [
        {'x': body_edge['left'] + marker_x_offset, 'y': -sl/2},
        {'x': body_edge['left'] + sl/sqrt(2) + marker_x_offset, 'y': 0},
        {'x': body_edge['left'] + marker_x_offset, 'y': sl/2}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_pin1_marker, layer='F.Fab', width=fab_w))

    ########################### CrtYd #################################
    cx1 = roundToBase(body_edge['left']-configuration['courtyard_offset']['connector'], configuration['courtyard_grid'])
    cy1 = roundToBase(body_edge['top']-configuration['courtyard_offset']['connector'], configuration['courtyard_grid'])

    cx2 = roundToBase(body_edge['right']+configuration['courtyard_offset']['connector'], configuration['courtyard_grid'])
    cy2 = roundToBase(body_edge['bottom']+configuration['courtyard_offset']['connector'], configuration['courtyard_grid'])

    kicad_mod.append(RectLine(
        start=[cx1, cy1], end=[cx2, cy2],
        layer='F.CrtYd', width=configuration['courtyard_line_width']))

    ######################### Text Fields ###############################
    addTextFields(kicad_mod=kicad_mod, configuration=configuration, body_edges=body_edge,
        courtyard={'top':cy1, 'bottom':cy2}, fp_name=footprint_name, text_y_inside_position='center')

    ##################### Output and 3d model ############################
    model3d_path_prefix = configuration.get('3d_model_prefix','${KISYS3DMOD}/')

    lib_name = configuration['lib_name_specific_function_format_string'].format(category=lib_category)
    model_name = '{model3d_path_prefix:s}{lib_name:s}.3dshapes/{fp_name:s}.wrl'.format(
        model3d_path_prefix=model3d_path_prefix, lib_name=lib_name, fp_name=footprint_name)
    kicad_mod.append(Model(filename=model_name))

    output_dir = '{lib_name:s}.pretty/'.format(lib_name=lib_name)
    if not os.path.isdir(output_dir): #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(output_dir)
    filename =  '{outdir:s}{fp_name:s}.kicad_mod'.format(outdir=output_dir, fp_name=footprint_name)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='use confing .yaml files to create footprints.')
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='../tools/global_config_files/config_KLCv3.0.yaml')
    parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='./conn_config_KLCv3.yaml')
    parser.add_argument('--kicad4_compatible', action='store_true', help='Create footprints kicad 4 compatible')
    args = parser.parse_args()

    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open(args.series_config, 'r') as config_stream:
        try:
            configuration.update(yaml.load(config_stream))
        except yaml.YAMLError as exc:
            print(exc)

    configuration['kicad4_compatible'] = args.kicad4_compatible
    generate_one_footprint(configuration)

