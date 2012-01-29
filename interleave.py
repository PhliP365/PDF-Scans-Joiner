# PDF Scans Joiner Copyright (C) 2011-2012 365multimedia.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
from Quartz.CoreGraphics import *
from AppKit import *
#from ScriptingBridge import SBApplication


def createPdf(filePath):
	return CGPDFDocumentCreateWithURL(
				CFURLCreateFromFileSystemRepresentation(
					kCFAllocatorDefault, 
					filePath, 
					len(filePath), 
					False))


def moveToTrash(filePath1, filePath2):
	folder = os.path.dirname(filePath1)
	fileNames = [os.path.basename(filePath1), os.path.basename(filePath2)]
	ws = NSWorkspace.sharedWorkspace()
	ws.performFileOperation_source_destination_files_tag_(
			NSWorkspaceRecycleOperation, 
			folder, 
			"", 
			fileNames, 
			None)

#	finder = SBApplication.applicationWithBundleIdentifier_("com.apple.Finder")
#	
#	fileUrl = NSURL.fileURLWithPath_(filePath1)
#	file = finder.items().objectAtLocation_(fileUrl)
#	file.delete()
#	
#	fileUrl = NSURL.fileURLWithPath_(filePath2)
#	file = finder.items().objectAtLocation_(fileUrl)
#	file.delete()


def alert(title, details):
	NSRunAlertPanel(
        title, 
        details, 
        u"OK", 
        None, 
        None)


def writePageFromPdfDoc(writeContext, pdfDoc, pageNb):
	page = CGPDFDocumentGetPage(pdfDoc, pageNb)
	if page:
		mediaBox = CGPDFPageGetBoxRect(page, kCGPDFMediaBox)
		if CGRectIsEmpty(mediaBox):
			mediaBox = None
			
		CGContextBeginPage(writeContext, mediaBox)
		CGContextDrawPDFPage(writeContext, page)
		CGContextEndPage(writeContext)


def main():
	# Check the number of files
	if len(sys.argv) != 3:
		alert(u"Invalid Number of Files", u"PDF Combiner requires:\n* one PDF file containing the odd pages\n* one PDF file containing the even pages")
		return
	
	# Check the first argument is a file
	oddPath = sys.argv[1]
	if not os.path.isfile(oddPath):
		alert(u"Not a File", u"The following item is not a file:\n" + oddPath)
		return
	
	# Check the second argument is a file
	evenPath = sys.argv[2]
	if not os.path.isfile(evenPath):
		alert(u"Not a File", u"The following item is not a file:\n" + evenPath)
		return

	# Determine which file is odd and which file is even based on date
	# The even file is expected to be more recent
	if os.path.getmtime(oddPath) > os.path.getmtime(evenPath):
		oddPath, evenPath = evenPath, oddPath

	# Check if odd file has has a .pdf extension
	(dummy, extension) = os.path.splitext(oddPath)
	if extension.lower() != ".pdf":
		alert(u"Not a Valid PDF File", u"The following item is not a PDF file:\n" + oddPath)
		return

	# Check if even file has has a .pdf extension
	(dummy, extension) = os.path.splitext(evenPath)
	if extension.lower() != ".pdf":
		alert(u"Not a Valid PDF File", u"The following item is not a PDF file:\n" + evenPath)
		return
	
	# Check if odd file is a valid PDF by counting its pages
	oddPdf = createPdf(oddPath)
	oddNbPages = CGPDFDocumentGetNumberOfPages(oddPdf)
	if oddNbPages <= 0:
		alert(u"Not a Valid PDF File", u"The following item is not a valid PDF file:\n" + oddPath)
		return

	# Check if even file is a valid PDF by counting its pages
	evenPdf = createPdf(evenPath)
	evenNbPages = CGPDFDocumentGetNumberOfPages(evenPdf)
	if evenNbPages <= 0:
		alert(u"Not a Valid PDF File", u"The following item is not a valid PDF file:\n" + evenPath)
		return
	
	# Check if both files have the sanme number of pages
	if oddNbPages != evenNbPages:
		alert(u"Files Do Not Match", u"The PDF file containing the odd pages has a different number of pages than the PDF file containing the even pages.")
		return

	# Create a new file that will hold the result
	outputPath = os.path.join(os.path.dirname(oddPath), "Combined.pdf")
	writeContext = CGPDFContextCreateWithURL(
						CFURLCreateFromFileSystemRepresentation(
							kCFAllocatorDefault, 
							outputPath, 
							len(outputPath), 
							False), 
						None, 
						None)

	# Interleave the pages
	for pageNb in xrange(1, oddNbPages + 1):
		writePageFromPdfDoc(writeContext, oddPdf, pageNb)
		writePageFromPdfDoc(writeContext, evenPdf, oddNbPages + 1 - pageNb)

	# Clean up
	CGPDFContextClose(writeContext)
	del writeContext
	moveToTrash(oddPath, evenPath)

	return

main()


#itemNames = os.listdir(folder)
#for itemName in itemNames:
#	itemPath = os.path.join(folder, itemName)
#	res = isPdf(itemPath)
#	if isPdf(itemPath):
#		itemTime = os.path.getmtime(itemPath)
#		if itemTime > evenTime:
#			oddPath = evenPath
#			oddTime = evenTime
#			evenPath = itemPath
#			evenTime = itemTime
#		elif itemTime > oddTime:
#			oddPath = itemPath
#			oddTime = itemTime