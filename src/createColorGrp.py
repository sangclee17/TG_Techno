from xml.etree import ElementTree as ET
from Logger import Logger

class ColorGroup():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
        self._RGB_GRP_DICT = {"Green": "0.0 1.0 0.0",
                "Yellow": "1.0 1.0 0.0",
                "Pink": "1.0 0.196078 0.588235",
                "Orange": "1.0 0.392157 0.0",
                "White": "1.0 1.0 1.0"}

    def _indent(self, elem, level=0):
        i = "\n" + level* "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _add_To_RGB_Dict(self, key, value):
        self._RGB_GRP_DICT[key] = value

    def _createCustomColor(self, md):
        result = True
        customCol = True if md["A066"].lower()== "true" else False
        if customCol:
            try:
                self.Logger.info("Adding custom color RGB...")
                rgb = md["B007"]
                rgb_sp = rgb.split(",")
                red_min = 0
                red_max = int(rgb_sp[0])
                green_min = 0
                green_max = int(rgb_sp[1])
                blue_min = 0
                blue_max = int(rgb_sp[2])
                blueMax_float = float(blue_max/255)
                counter = 1
                if blue_max > blue_min:
                    for j in range(blue_min, blue_max + 1):
                        bluF = float(j/255)
                        key = "CustomColor{}".format(counter)
                        thisColor = "{0:.6f} {1:.6f} {2:.6f}".format(red_min, green_min, bluF)
                        self._add_To_RGB_Dict(key, thisColor)
                        counter += 1
                if green_max > green_min:
                    for j in range(green_min + 1, green_max + 1):
                        grnF = float(j/255)
                        key = "CustomColor{}".format(counter)
                        thisColor = "{0:.6f} {1:.6f} {2:.6f}".format(red_min, grnF, blueMax_float)
                        self._add_To_RGB_Dict(key, thisColor)
                        counter += 1
            except Exception as e:
                result = False
                self.Logger.error(e)
        return result

    def _buildTree(self, fName):
        try:
            self.Logger.info("Creating {}".format(fName))
            grpControl = ET.Element("Groups_Control")
            grpControl.set("version", "1.0")

            bodyGrps = ET.SubElement(grpControl, "Body_Groups")

            bodyDetails = ET.SubElement(bodyGrps, "Body_Details")
            name = ET.SubElement(bodyDetails, "Name")
            name.text = ""

            grpDetails = ET.SubElement(bodyGrps, "Group_Details")

            for key in self._RGB_GRP_DICT:
                grpType = ET.SubElement(grpDetails, "Group_Type")
                grpType.set("Name", "Face Group")
                name = ET.SubElement(grpType, "Name")
                name.text = key
                grpColor = ET.SubElement(grpType, "Group_Color")
                grpColor.text = "0.000000 0.000000 0.000000"
                colorList = ET.SubElement(grpType, "List")
                geom_color = ET.SubElement(colorList, "Geom_Color")
                geom_color.text = self._RGB_GRP_DICT[key]

            self._indent(grpControl)

            tree = ET.ElementTree(grpControl)
            tree.write(fName)
        except Exception as e:
            self.Logger.error(e)
            return 0
        return 1

    def makeGrp(self, fName, md):
        result = self._createCustomColor(md)
        if result: return self._buildTree(fName)
        else: return 0
