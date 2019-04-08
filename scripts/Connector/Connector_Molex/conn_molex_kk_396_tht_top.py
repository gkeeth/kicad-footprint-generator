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
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))  # load parent path of KicadModTree
from math import sqrt
import argparse
import yaml
from helpers import *
from KicadModTree import *

sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))  # load parent path of tools
from footprint_text_fields import addTextFields

series = "KK-396"
series_long = 'KK-396 Interconnect System'
manufacturer = 'Molex'
orientation = 'V'
number_of_rows = 1
datasheet = 'https://www.molex.com/pdm_docs/sd/026614040_sd.pdf'

pitch = 3.96
drill = 1.70 # square pins:1.14mm -> touching circle: ~1.61mm -> minimum drill accourding to KLC: 1.81mm. Datasheet specifies 1.70mm +/- 0.05mm
start_pos_x = 0 # Where should pin 1 be located.
pad_to_pad_clearance = 0.8
max_annular_ring = 0.5 #How much copper should be in y direction?
min_annular_ring = 0.15

pad_size = [pitch - pad_to_pad_clearance, drill + 2*max_annular_ring]
if pad_size[0] - drill < 2*min_annular_ring:
    pad_size[0] = drill + 2*min_annular_ring
if pad_size[0] - drill > 2*max_annular_ring:
    pad_size[0] = drill + 2*max_annular_ring

pad_shape=Pad.SHAPE_OVAL
if pad_size[1] == pad_size[0]:
    pad_shape=Pad.SHAPE_CIRCLE

eng_mpn = 'A-41791-00{n:02d}'
new_mpn_example = '26-60-4{n:02d}0'

def generate_one_footprint(pincount, configuration):

    mpn = eng_mpn.format(n=pincount)
    new_mpn = new_mpn_example.format(n=pincount)

    # handle arguments
    orientation_str = configuration['orientation_options'][orientation]
    footprint_name = configuration['fp_name_format_string'].format(man=manufacturer,
        series=series,
        mpn=mpn, num_rows=number_of_rows, pins_per_row=pincount, mounting_pad = "",
        pitch=pitch, orientation=orientation_str)

    kicad_mod = Footprint(footprint_name)
    descr_format_str = "Molex {:s}, old/engineering part number: {:s} example for new part number: {:s}, {:d} Pins ({:s}), generated with kicad-footprint-generator"
    kicad_mod.setDescription(descr_format_str.format(series_long, mpn, new_mpn, pincount, datasheet))
    kicad_mod.setTags(configuration['keyword_fp_string'].format(series=series,
        orientation=orientation_str, man=manufacturer,
        entry=configuration['entry_direction'][orientation]))

    # calculate working values
    end_pos_x = (pincount-1) * pitch
    centre_x = (end_pos_x - start_pos_x) / 2.0
    nudge = configuration['silk_fab_offset']
    silk_w = configuration['silk_line_width']
    fab_w = configuration['fab_line_width']


    edge_offset = 1.91
    body_edge={
        'left':start_pos_x - edge_offset,
        'right':end_pos_x + edge_offset,
        'top':-5.11,
        'bottom':10.01 - 5.11
        }

    # create pads
    # kicad_mod.append(Pad(number=1, type=Pad.TYPE_THT, shape=Pad.SHAPE_RECT,
    #                     at=[0, 0], size=pad_size,
    #                     drill=drill, layers=Pad.LAYERS_THT))

    optional_pad_params = {}
    if configuration['kicad4_compatible']:
        optional_pad_params['tht_pad1_shape'] = Pad.SHAPE_RECT
    else:
        optional_pad_params['tht_pad1_shape'] = Pad.SHAPE_ROUNDRECT

    kicad_mod.append(PadArray(initial=1, start=[start_pos_x, 0],
        x_spacing=pitch, pincount=pincount,
        size=pad_size, drill=drill,
        type=Pad.TYPE_THT, shape=Pad.SHAPE_OVAL, layers=Pad.LAYERS_THT,
        **optional_pad_params))

    # create fab outline
    ramp_thickness = 10.01 - 5.11 - 2.41
    yr1=body_edge['bottom']+nudge
    yr2 = yr1 - ramp_thickness
    fab = [
        {'x': body_edge['left'], 'y': body_edge['top']},
        {'x': body_edge['right'], 'y': body_edge['top']},
        {'x': body_edge['right'], 'y': yr2 - nudge},
        {'x': end_pos_x, 'y': yr2 - nudge},
        {'x': end_pos_x, 'y': body_edge['bottom']},
        {'x': start_pos_x, 'y': body_edge['bottom']},
        {'x': start_pos_x, 'y': yr2 - nudge},
        {'x': body_edge['left'], 'y': yr2 - nudge},
        {'x': body_edge['left'], 'y': body_edge['top']}
    ]

    kicad_mod.append(PolygoneLine(polygone=fab, layer='F.Fab', width=fab_w))
    # kicad_mod.append(RectLine(start=[body_edge['left'], body_edge['top']],\
    #     end=[body_edge['right'], body_edge['bottom']], layer='F.Fab', width=fab_w))

    # create silkscreen
    silk = [
        {'x': body_edge['left'] - nudge, 'y': body_edge['top'] - nudge},
        {'x': body_edge['right'] + nudge, 'y': body_edge['top'] - nudge},
        {'x': body_edge['right'] + nudge, 'y': yr2},
        {'x': end_pos_x + nudge, 'y': yr2},
        {'x': end_pos_x + nudge, 'y': yr1},
        {'x': start_pos_x - nudge, 'y': yr1},
        {'x': start_pos_x - nudge, 'y': yr2},
        {'x': body_edge['left'] - nudge, 'y': yr2},
        {'x': body_edge['left'] - nudge, 'y': body_edge['top'] - nudge}
    ]
    kicad_mod.append(PolygoneLine(polygone=silk, layer='F.SilkS', width=silk_w))

    # pin 1 markers
    # TODO: should this size be increased?
    # kicad_mod.append(Line(start=[body_edge['left']-0.4, -2.0],\
    #     end=[body_edge['left']-0.4, 2.0], layer='F.SilkS', width=silk_w))

    kicad_mod.append(Line(start=[body_edge['left']-0.4, -yr2 - 0.4 + nudge],\
        end=[body_edge['left']-0.4, yr2 + 0.4 - nudge], layer='F.SilkS', width=silk_w))
    kicad_mod.append(Line(start=[body_edge['left']-0.4, yr2 + 0.4 - nudge],\
        end=[start_pos_x - 0.4, yr2 + 0.4 - nudge], layer='F.SilkS', width=silk_w))

    sl=1
    poly_pin1_marker = [
        {'x': body_edge['left'], 'y': -sl/2},
        {'x': body_edge['left'] + sl/sqrt(2), 'y': 0},
        {'x': body_edge['left'], 'y': sl/2}
    ]
    kicad_mod.append(PolygoneLine(polygone=poly_pin1_marker, layer='F.Fab', width=fab_w))

    slot_locations = {
        1: (),
        2: (),
        3: (),
        4: (),
        5: (),
        6: (3.5,),
        7: (4.5,),
        8: (4.5,),
        9: (5.5,),
        10: (5.5,),
        11: (6.5,),
        12: (4.5, 8.5),
        13: (4.5, 9.5),
        14: (5.5, 9.5),
        15: (5.5, 10.5),
        16: (5.5, 11.5),
        17: (6.5, 11.5),
        18: (6.5, 12.5)
    }

    slot_location = slot_locations[pincount]
    slot_width = 2.00 # TODO: measure actual slot width. By eye, could be smaller
    yr3 = yr1 - 0.8

    if len(slot_location) == 0:
        # no slot
        poly1 = [
            {'x': start_pos_x - nudge, 'y':  yr1},
            {'x': start_pos_x - nudge, 'y':  yr2},
            {'x': end_pos_x + nudge, 'y':  yr2},
            {'x': end_pos_x + nudge, 'y':  yr1}
        ]
        poly2 = [
            {'x': start_pos_x - nudge, 'y':  yr1},
            {'x': start_pos_x - nudge, 'y':  yr3},
            {'x': end_pos_x + nudge, 'y':  yr3},
            {'x': end_pos_x + nudge, 'y':  yr1}
        ]
        kicad_mod.append(PolygoneLine(polygone=poly1, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly2, layer='F.SilkS', width=silk_w))

    elif len(slot_location) == 1:
        # 1 slot
        poly1=[
            {'x': start_pos_x - nudge, 'y': yr1},
            {'x': start_pos_x - nudge, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr1}
        ]
        poly2=[
            {'x': end_pos_x + nudge, 'y': yr1},
            {'x': end_pos_x + nudge, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr1}
        ]
        poly3 = [
            {'x': start_pos_x - nudge, 'y':  yr1},
            {'x': start_pos_x - nudge, 'y':  yr3},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr1}
        ]
        poly4 = [
            {'x': end_pos_x + nudge, 'y':  yr1},
            {'x': end_pos_x + nudge, 'y':  yr3},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr1}
        ]

        kicad_mod.append(PolygoneLine(polygone=poly1, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly2, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly3, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly4, layer='F.SilkS', width=silk_w))
    else:
        # 2 slots
        poly1=[
            {'x': start_pos_x - nudge, 'y': yr1},
            {'x': start_pos_x - nudge, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr1}
        ]
        poly2=[
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr1},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[1] - slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[1] - slot_width/2, 'y': yr1}
        ]
        poly3=[
            {'x': end_pos_x + nudge, 'y': yr1},
            {'x': end_pos_x + nudge, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[1] + slot_width/2, 'y': yr2},
            {'x': start_pos_x + pitch*slot_location[1] + slot_width/2, 'y': yr1}
        ]
        poly4 = [
            {'x': start_pos_x - nudge, 'y':  yr1},
            {'x': start_pos_x - nudge, 'y':  yr3},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[0] - slot_width/2, 'y': yr1}
        ]
        poly5=[
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr1},
            {'x': start_pos_x + pitch*slot_location[0] + slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[1] - slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[1] - slot_width/2, 'y': yr1}
        ]
        poly6=[
            {'x': end_pos_x + nudge, 'y': yr1},
            {'x': end_pos_x + nudge, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[1] + slot_width/2, 'y': yr3},
            {'x': start_pos_x + pitch*slot_location[1] + slot_width/2, 'y': yr1}
        ]

        kicad_mod.append(PolygoneLine(polygone=poly1, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly2, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly3, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly4, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly5, layer='F.SilkS', width=silk_w))
        kicad_mod.append(PolygoneLine(polygone=poly6, layer='F.SilkS', width=silk_w))


    for i in range(0, pincount):
        middle_x = start_pos_x + i * pitch
        start_x = middle_x - 2.6/2
        end_x = middle_x + 2.6/2
        y1 = body_edge['top'] - nudge
        y2 = y1 + 1.62
        kicad_mod.append(PolygoneLine(polygone=[[start_x, y1], [start_x, y2],\
            [end_x, y2], [end_x, y1]], layer='F.SilkS', width=silk_w))

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
        courtyard={'top':cy1, 'bottom':cy2}, fp_name=footprint_name, text_y_inside_position='top')

    ##################### Output and 3d model ############################
    model3d_path_prefix = configuration.get('3d_model_prefix','${KISYS3DMOD}/')

    lib_name = configuration['lib_name_format_string'].format(series=series, man=manufacturer)
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
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='../../tools/global_config_files/config_KLCv3.0.yaml')
    parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='../conn_config_KLCv3.yaml')
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

    for pincount in range(2, 19):
        generate_one_footprint(pincount, configuration)
