#!/usr/bin/env python3
"""Run against a built toolkit dylib: python3 tools/test-smart-page-breaks.py LIB DATA."""
import ctypes
import json
import sys
import xml.etree.ElementTree as ET

lib = ctypes.CDLL(sys.argv[1])
signatures = {
    "constructorResourcePath": (ctypes.c_void_p, [ctypes.c_char_p]),
    "destructor": (None, [ctypes.c_void_p]),
    "setOptions": (ctypes.c_bool, [ctypes.c_void_p, ctypes.c_char_p]),
    "loadData": (ctypes.c_bool, [ctypes.c_void_p, ctypes.c_char_p]),
    "getPageCount": (ctypes.c_int, [ctypes.c_void_p]),
    "renderToSVG": (ctypes.c_char_p, [ctypes.c_void_p, ctypes.c_int, ctypes.c_bool]),
}
for name, (result, args) in signatures.items():
    function = getattr(lib, "vrvToolkit_" + name)
    function.restype, function.argtypes = result, args


def mei(count=24, pages=(), systems=(), trailing=False, leading=False, notes=False):
    measures = []
    for index in range(1, count + 1):
        music = "".join(f'<note xml:id="n{index}-{n}" pname="c" oct="4" dur="8"/>' for n in range(8)) if notes else '<mRest/>'
        measures.append(f'<measure xml:id="m{index}" n="{index}"><staff n="1"><layer n="1">{music}</layer></staff></measure>')
        if index in pages: measures.append('<pb/>')
        if index in systems: measures.append('<sb/>')
    if trailing: measures.append('<pb/>')
    if leading: measures.insert(0, '<pb/>')
    return ('<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.1"><music><body><mdiv><score>'
            '<scoreDef meter.count="4" meter.unit="4"><staffGrp><staffDef n="1" lines="5" clef.shape="G" clef.line="2"/>'
            '</staffGrp></scoreDef><section>' + ''.join(measures) + '</section></score></mdiv></body></music></mei>')


def layout(source):
    toolkit = lib.vrvToolkit_constructorResourcePath(sys.argv[2].encode())
    try:
        options = dict(pageWidth=2100, pageHeight=2970, pageMarginTop=100, pageMarginBottom=100,
                       pageMarginLeft=100, pageMarginRight=100, unit=9, breaks="smart", breaksSmartSb=0,
                       svgHtml5=False, smuflTextFont="none", header="none", footer="none")
        assert lib.vrvToolkit_setOptions(toolkit, json.dumps(options).encode())
        assert lib.vrvToolkit_loadData(toolkit, source.encode())
        count = lib.vrvToolkit_getPageCount(toolkit)
        locations, system_locations = {}, {}
        for page in range(1, count + 1):
            svg = ET.fromstring(lib.vrvToolkit_renderToSVG(toolkit, page, False))
            for system_number, system in enumerate(e for e in svg.iter() if e.get('class') == 'system'):
                for element in system.iter():
                    if element.get('class') == 'measure':
                        locations[element.get('id')] = page
                        system_locations[element.get('id')] = (page, system_number)
        return count, locations, system_locations
    finally:
        lib.vrvToolkit_destructor(toolkit)


count, locations, _ = layout(mei(pages=(8, 16)))
assert count == 3, count
assert all(locations[f'm{i}'] == (i - 1) // 8 + 1 for i in range(1, 25)), locations
for leading, trailing in [(True, False), (False, True), (True, True)]:
    assert layout(mei(pages=(8, 16), leading=leading, trailing=trailing))[0] == 3
count, locations, systems = layout(mei(pages=(8, 16), systems=(4, 12, 20)))
assert count == 3
assert systems['m4'] != systems['m5'] and locations['m4'] == locations['m5']
count, locations, systems = layout(mei(count=256, pages=(8, 16), notes=True))
assert count > 3 and len(locations) == 256
assert locations['m8'] < locations['m9'] and locations['m16'] < locations['m17']
assert len(set(systems.values())) > count, 'Automatic system breaking was lost'
assert layout(mei(count=256, notes=True))[0] > 1
print('PASS: explicit pages, leading/trailing markers, system breaks, and natural overflow')
