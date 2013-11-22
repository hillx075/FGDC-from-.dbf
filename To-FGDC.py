#######################################################################
## Take attributes from MN Imagery shapefile and create minimal FGDC ##
## metadata for solr ingest process. - David Hill hillx075@umn.edu   ##
#######################################################################

import os, arcpy
import zipfile
import xml.etree.ElementTree as ET

# Open a sample empty xml file
file = open("SampleFGDCempty.xml", "r")
tree = ET.parse(file)
root = tree.getroot()
    
# make sure the path is in the right place for you
FC = os.path.abspath(".")+"/PGC_MN_AREA_test/pgc_105W50N_87W40N.dbf"

if os.path.exists((".")+"/PGC_MN_AREA_test/FGDCOutput"):
    OUTPUT_LOCATION = os.path.abspath(".")+"/PGC_MN_AREA_test/FGDCOutput/"
else:
    os.mkdir((".")+"/PGC_MN_AREA_test/FGDCOutput")
    OUTPUT_LOCATION = os.path.abspath(".")+"/PGC_MN_AREA_test/FGDCOutput/"

## Only Print 5000th row ##

NTH = 5000

#try:
if arcpy.Exists(FC):
    FIELDS = arcpy.ListFields(FC)              # extract field objects
    MAXRANGE = len(FIELDS)                     # var for range function
    MAXINDX = MAXRANGE - 1                     # top index for range(maxRange)

##    for i in range(MAXRANGE):
##        writeValue(FIELDS[i].name, "String", i==MAXINDX)

    # Establish search cursor and print every nth row...
    CURSOR = arcpy.SearchCursor(FC)
    for row in CURSOR:
        if row.getValue(FIELDS[0].name) % NTH == 0:
            for i in range(MAXRANGE):

##cursor = arcpy.SearchCursor(FC)

                ### Populate FGDC XML file with attribute table records and other static data

##for row in cursor:

                ##Entering information required for solr ingest 

                origin = root.find("idinfo/citation/citeinfo/origin") #inferred from Sensor attribute in attribute table
                if row.getValue("Sensor") == 'GE01':
                    origin.text = "GEOEYE"
                elif row.getValue("Sensor") == 'IK01':
                    origin.text = "GEOEYE"
                elif row.getValue("Sensor") == 'OV03':
                    origin.text = "ORB View"
                elif row.getValue("Sensor") == 'QB02':
                    origin.text = "Digital Globe (QuickBird)"
                elif row.getValue("Sensor") == 'WV01':
                    origin.text = "Digital Globe"
                elif row.getValue("Sensor") == 'WV02':
                    origin.text = "Digital Globe"
                else:
                    origin.text = "No Sensor Listed"

                title = root.find("idinfo/citation/citeinfo/title")
                title.text = "Minnesota Satellite Imagery " + row.getValue("SCENE_ID") #Should be more descriptive  than Scene_ID

                publish =  root.find("idinfo/citation/citeinfo/pubinfo/publish")
                publish.text = "University of Minnesota"
                
                accconst = root.find("idinfo/accconst")
                accconst.text = "Restricted Access Online: Access granted to licensee only. Available only to University of Minnesota affiliates."
                    
                themekey = root.find("idinfo/keywords/theme/themekey")
                themekey.text = "Satellite imagery of the Upper Midwest"
                
                placekey = root.find("idinfo/keywords/place/placekey")
                placekey.text = "Minnesota North Dakota South Dakota Wisconsin Iowa Nebraska Montana Illinois"
                    
                caldate = root.find("idinfo/timeperd/timeinfo/sngdates/caldate")
                caldate.text = row.getValue("ACQ_TIME")[0:10]

                extent = row.getValue("Shape").extent
                    
                westbc = root.find("idinfo/spdom/bounding/westbc")
                westbc.text = str(extent.XMin)

                eastbc = root.find("idinfo/spdom/bounding/eastbc")
                eastbc.text = str(extent.XMax)

                southbc = root.find("idinfo/spdom/bounding/southbc")
                southbc.text = str(extent.YMin)

                northbc = root.find("idinfo/spdom/bounding/northbc")
                northbc.text = str(extent.YMax)

                direct = root.find("spdoinfo/direct")
                direct.text = "Raster"
                
                #entering additional information
                
                tree.write(OUTPUT_LOCATION + (row.getValue("O_Filename")) + ".xml")
                print "Output file: " + OUTPUT_LOCATION + (row.getValue("O_Filename")) + ".xml"
#
else:
    sys.stderr.write("Target feature class does not exist\n(%s)" % (FC))

del row, CURSOR

file.close()

#deal with all of these darned files.
zf = zipfile.ZipFile("ZippedFGDCXMLFiles.zip", "w", zipfile.ZIP_DEFLATED)
for dirname, subdirs, files in os.walk(OUTPUT_LOCATION):
    zf.write(dirname)
    for filename in files:
        zf.write(os.path.join(dirname, filename))
zf.close

#print 'Output Location: ", OUTPUT_LOCATION
