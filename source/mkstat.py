from fontTools.otlLib import builder
from fontTools import ttLib
import sys
import argparse

whichFont = "neither"
argparser = argparse.ArgumentParser(prog='mkstat',
                                    description='Fix STAT and name tables for Junicode Two.')
argparser.add_argument("inputfile", help='Font to process.')
argparser.add_argument("outputfile", help="Font to output.")
args = argparser.parse_args()

inFont = args.inputfile
outFont = args.outputfile

if "Italic" in inFont:
    whichFont = "italic"
else:
    whichFont = "roman"

weightDict = dict(
    tag="wght",
    name="Weight",
    values=[
        dict(nominalValue=300, name="Light", rangeMinValue=300, rangeMaxValue=350),
        # Glyphs includes both format 1 and 3 entries for Regular. Does not stop crash.
        dict(nominalValue=400, name="Regular", flags=0x2, rangeMinValue=350, rangeMaxValue=450),
        #dict(value=400, name="Regular", linkedValue=700, flags=0x2),
        dict(nominalValue=500, name="Medium", rangeMinValue=450, rangeMaxValue=550),
        dict(nominalValue=600, name="SmBold", rangeMinValue=550, rangeMaxValue=650),
        dict(nominalValue=700, name="Bold", rangeMinValue=650, rangeMaxValue=700),
        # dict(value=400, name="Regular", linkedValue=700, flags=0x2)
    ]
)

widthDict = dict(
    tag="wdth",
    name="Width",
    values=[
        dict(nominalValue=75, name="Cond", rangeMinValue=75.0, rangeMaxValue=81.25),
        dict(nominalValue=87.5, name="SmCond", rangeMinValue=81.25, rangeMaxValue=93.75),
        dict(nominalValue=100, name="Normal", flags=0x2, rangeMinValue=93.75, rangeMaxValue=106.25),
        dict(nominalValue=112.5, name="SmExp", rangeMinValue=106.25, rangeMaxValue=118.75),
        dict(nominalValue=125, name="Exp", rangeMinValue=118.75, rangeMaxValue=125),
    ]
)

enlargeDict = dict(
    tag="ENLA",
    name="Enlarge",
    values=[
        dict(nominalValue=0, name="Normal", flags=0x2, rangeMinValue=0, rangeMaxValue=23.5),
        dict(nominalValue=47, name="Enlarged", rangeMinValue=23.5, rangeMaxValue=73.5),
        dict(nominalValue=100, name="CapSize", rangeMinValue=73.5, rangeMaxValue=100),
    ]
)

format2RomanAxes = [
    weightDict, widthDict, enlargeDict,
    dict(
        tag="ital",
        name="Italic",
        values=[dict(value=0, name="Roman", linkedValue=1, flags=0x2)]
    )
]

format2ItalicAxes = [
    weightDict, widthDict, enlargeDict,
    dict(
        tag="ital",
        name="Italic",
        values=[dict(value=1, name="Italic", linkedValue=0.0)]
    )
]

ttfont = ttLib.TTFont(inFont)
if whichFont == "italic":
    print("Adding STAT table to italic font "  + inFont)
    builder.buildStatTable(ttfont,format2ItalicAxes)
    # Add stuff to name table. First the Variations PostScript Name Prefix (table entry 25).
    psNamePrefix = "JunicodeVFItalic"
    ttfont['name'].setName(psNamePrefix, 25, 3, 1, 0x409)
    # Glyphs takes care of the naming table now.
    # Cycle through fvar, getting instance names, building a correct postscriptNameID,
    # recording that in the name table, and adding the ID to the postscriptNameID field
    # of the fvar instance. Whew!
    for inst in ttfont['fvar'].instances:
        if (inst.coordinates['wght'] == 400.0 and inst.coordinates['wdth'] == 100.0
            and inst.coordinates['ENLA'] == 0.0):
            inst.subfamilyNameID = 2
            inst.postscriptNameID = 6
        else:
            subfamilyName = ttfont['name'].getName(inst.subfamilyNameID,3,1,0x409).toUnicode()
            if subfamilyName == "Italic":
                subfamilyName = "Regular"
            else:
                subfamilyName = subfamilyName.replace("Italic", "").replace(" ", "")
            # subfamilyName = subfamilyName.replace(" ", "")
            inst.postscriptNameID = ttfont['name'].addName("JunicodeVFItalic-" + subfamilyName,
                                                       platforms=((3,1,0x409),))
    # We don't need platform 1 names. If there are any, remove them.
    ttfont['name'].removeNames(platformID=1)
    ttfont.save(outFont)
elif whichFont == "roman":
    print("Adding STAT table to roman font " + inFont)
    ttfont = ttLib.TTFont(inFont)
    builder.buildStatTable(ttfont,format2RomanAxes)
    # Add stuff to name table. First the Variations PostScript Name Prefix (table entry 25).
    psNamePrefix = "JunicodeVFRoman"
    ttfont['name'].setName(psNamePrefix, 25, 3, 1, 0x409)
    # Cycle through fvar, getting instance names, building a correct postscriptNameID,
    # recording that in the name table, and adding the ID to the postscriptNameID field
    # of the fvar instance. Whew!
    for inst in ttfont['fvar'].instances:
        if (inst.coordinates['wght'] == 400.0 and inst.coordinates['wdth'] == 100.0
            and inst.coordinates['ENLA'] == 0.0):
            inst.subfamilyNameID = 2
            inst.postscriptNameID = 6
        else:
            subfamilyName = ttfont['name'].getName(inst.subfamilyNameID,3,1,0x409).toUnicode().replace(" ","")
            inst.postscriptNameID = ttfont['name'].addName("JunicodeVFRoman" + "-" + subfamilyName,
                                                       platforms=((3,1,0x409),(1,0,0)))
    # We don't need platform 1 names. If there are any, remove them.
    ttfont['name'].removeNames(platformID=1)
    ttfont.save(outFont)
