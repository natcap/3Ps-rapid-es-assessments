import xml.etree.ElementTree as ET

tree = ET.parse('N21E042.SRTMGL1.hgt.zip.xml')
root = tree.getroot()

filename = root.find('.//DistributedFileName').text
filesize = root.find('.//FileSize').text
checksumtype = root.find('.//ChecksumType').text
checksum = root.find('.//Checksum').text
print(filename, filesize, checksumtype, checksum)

bbox = root.find('.//BoundingRectangle')
west = bbox.find('WestBoundingCoordinate').text
north = bbox.find('NorthBoundingCoordinate').text
east = bbox.find('EastBoundingCoordinate').text
south = bbox.find('SouthBoundingCoordinate').text

print(west, north, east, south)
