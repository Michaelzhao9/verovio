#!/usr/bin/env python3
"""Non-TAB MusicXML fret markings must warn, never assert or dereference a rest."""
import ctypes
import sys

lib = ctypes.CDLL(sys.argv[1])
for name, result, arguments in [
    ('constructorResourcePath', ctypes.c_void_p, [ctypes.c_char_p]),
    ('destructor', None, [ctypes.c_void_p]),
    ('loadData', ctypes.c_bool, [ctypes.c_void_p, ctypes.c_char_p]),
    ('getLog', ctypes.c_char_p, [ctypes.c_void_p]),
    ('enableLogToBuffer', None, [ctypes.c_bool]),
]:
    fn = getattr(lib, name if name == 'enableLogToBuffer' else 'vrvToolkit_' + name)
    fn.restype, fn.argtypes = result, arguments
lib.enableLogToBuffer(True)
for content in ['<pitch><step>C</step><octave>4</octave></pitch>', '<rest/>']:
    source = f'''<score-partwise version="4.0"><part-list><score-part id="P1"><part-name>Guitar</part-name>
    </score-part></part-list><part id="P1"><measure number="1"><attributes><divisions>1</divisions>
    <time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
    <note>{content}<duration>4</duration><type>whole</type><notations><technical><string>1</string><fret>3</fret>
    </technical></notations></note></measure></part></score-partwise>'''
    toolkit = lib.vrvToolkit_constructorResourcePath(sys.argv[2].encode())
    try:
        assert lib.vrvToolkit_loadData(toolkit, source.encode())
        if content.startswith('<pitch>'):
            assert b'non-tablature' in lib.vrvToolkit_getLog(toolkit)
    finally:
        lib.vrvToolkit_destructor(toolkit)
print('PASS: frets on standard staff notes and rests produce warnings without crashing')
