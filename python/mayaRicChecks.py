"""
Check classes to perform checks related to Richard
"""
import re
import os
import itertools
import maya.OpenMaya as om
import maya.cmds as cmds
import types

from pymel.core import *
import tank

from checkClasses import CheckMayaAbstract


class CheckShotStartEnd(CheckMayaAbstract):
	"""@brief Check if the start and end frame of the shot match with the start and end frame in shotgun.
	"""
	_name = "Shots start end match shotgun"
	_category = "Shots"

	_asSelection = False
	_asFix = True
	
	def check(self):
		"""@brief Check if the start and end frame of the shot match with the start and end frame of shotgun.
		"""
		# get the data from shotgun
		app = self.parent.app
		context = app.context
		self.shot = app.shotgun.find_one("Shot", [  ["project", "is", context.project], 
												["id", 'is', context.entity["id"] ],
												], ["sg_head_in", "sg_tail_out", "sg_cut_out", "sg_cut_in", "code", 
													"sg_shot" ]) 

		
		frMin = playbackOptions(q = 1, min = 1)
		frAst = playbackOptions(q = 1, ast = 1)
		frMax = playbackOptions(q = 1, max = 1)
		frAet = playbackOptions(q = 1, aet = 1)

		error = self.shot["sg_head_in"] != frMin or frMin != frAst or (self.shot["sg_tail_out"]) != frMax or frMax != frAet

		
				
		if not error :
			self.status = "OK"
		else :
			self.status = self.errorMode
			self.errorNodes = None
			self.addError("Playback range does not match the framerange in shotgun.")
			self.errorMessage = "Playback range does not match the framerange in shotgun."

	def fix(self):
		playbackOptions(e = 1, min=self.shot["sg_head_in"], ast = self.shot["sg_head_in"], 
						max = self.shot["sg_tail_out"], aet = self.shot["sg_tail_out"])


class CheckSoundOffset(CheckMayaAbstract):
	"""@brief Check if sound offset matches the start frame
	"""
	_name = "Sound starts at cut in"
	_category = "Shots"

	_asSelection = True
	_asFix = True
	
	def check(self):
		"""@brief Check if sound offset matches the start frame
		"""
		# get the data from shotgun
		app = self.parent.app
		context = app.context
		self.shot = app.shotgun.find_one("Shot", [  ["project", "is", context.project], 
												["id", 'is', context.entity["id"] ],
												], ["sg_head_in", "sg_tail_out", "sg_cut_out", "sg_cut_in", "code", 
													"sg_shot" ]) 

		#get the sound node
		aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
		self.soundNode = timeControl(aPlayBackSliderPython, q = 1, displaySound = 1, sound = 1)
		if not self.soundNode:
			if ls(type = "audio"):
				self.soundNode = ls(type = "audio")[0]
				timeControl(aPlayBackSliderPython, e = 1, displaySound = 1, sound = soundNode)
			else:
				self.status = "OK"
				return
		else:
			self.soundNode = PyNode(self.soundNode)
		soundCutin = self.soundNode.offset.get()

		error = self.shot["sg_cut_in"] != soundCutin        
				
		if not error :
			self.status = "OK"
		else :
			self.status = self.errorMode
			self.errorNodes = [self.soundNode]
			self.addError("Sound does not start at cut in.")
			self.errorMessage = "Sound does not start at cut in."

	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		pass

	def fix(self):
		if self.soundNode:
			self.soundNode.offset.set(self.shot["sg_cut_in"])

class CheckPrefixLocator(CheckMayaAbstract):
	"""@Check for prefix on locator
	"""
	_name = "locator Prefix"
	_category = "Scene"

	_asSelection = True
	_asFix = True
	def check (self):
		selectLocShapes = cmds.ls( typ ='locator', l= True)
		prefixes = ["SET","SUB","PRP","CHR"]
		MissingPrefixList = []
		for i in selectLocShapes:
			iShort=i.split('|')[-2]
			# print iShort
			if iShort.split("_")[0] in prefixes:
				# print iShort.split("_")[0]
				None
			else:
				MissingPrefixList.append(i)
		if MissingPrefixList:
			self.errorNodes = MissingPrefixList
			self.status = self.errorMode
			self.errorMessage = "%s locator(s) without prefix" % (len(MissingPrefixList))
		else:
			self.status = "OK"

	def fix(self):
		"""@add prefix
		"""
		for i in self.errorNodes:
			print i
		self.run()

	def select(self):
		"""@brief Select unprefix locator.
		"""
		select(self.errorNodes)

# '''
class CheckNameLocatorShapes(CheckMayaAbstract):
	"""@brief Check for unknown nodes.
	"""
	_name = "Locator Shape rename"
	_category = "Scene"

	_asSelection = True
	_asFix = True

	def check(self):
		"""@brief Check for unknown node and add them to errors node.
		"""
		selectLocShapes = cmds.ls( typ ='locator', l= True)
		WrongShapeNamesList = []
		for i in selectLocShapes:
			if i.split('|')[-1] != i.split('|')[-2]+"Shape":
				WrongShapeNamesList.append(i)
			self.status = self.errorMode
			self.errorNodes = WrongShapeNamesList
			for wrongShapeName in WrongShapeNamesList :
				self.addError("%s is missing right shape name" % wrongShapeName)
			self.errorMessage = "%s locator(s) without right shape name" % (len(WrongShapeNamesList))
		if not WrongShapeNamesList :
			self.status = "OK"	

	def fix(self):
		"""@brief rename shape 
		"""
		# for i in self.errorNodes:
			# print i.split('|')[-1] +"   >>>   " + i.split('|')[-2]+"Shape"
			# cmds.rename( i, i.split('|')[-2]+"Shape")
			

		for i in self.errorNodes:
			print i.split('|')[-1] +"   >>>   " + i.split('|')[-2]+"Shape"
			try:
				cmds.rename( i, i.split('|')[-2]+"Shape")
			except:
				print i + "cannot be renamed"
		self.run()

	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		
		
		
class UnInstanceObjs(CheckMayaAbstract):
	"""@brief Check for unknown nodes.
	"""
	_name = "Un-Instance"
	_category = "Scene"

	_asSelection = True
	_asFix = True

	def check(self):
		"""@brief Check for unknown node and add them to errors node.
		"""
		instances = []
		iterDag = om.MItDag(om.MItDag.kBreadthFirst)
		while not iterDag.isDone():
			instanced = om.MItDag.isInstanced(iterDag)
			if instanced:
				instances.append(iterDag.fullPathName())
			iterDag.next()
		self.status = self.errorMode
		self.errorNodes = instances
		self.errorMessage = "%s instances found" % (len(instances))
		if not instances:
			self.status = "OK"
			
	def fix(self):
		"""@brief rename shape 
		"""
		for i in self.errorNodes:
			if cmds.objExists(i):
				if cmds.objectType(i) != "mesh":
					parenttmp = cmds.listRelatives(i, parent=True, fullPath=True)
					parentname = str(parenttmp)
					currName = i.split('|')[-2]
					cmds.duplicate(parenttmp,n=currName+"tmpToRename")
					cmds.delete(parenttmp)
		AllScene = cmds.ls()
		for i in AllScene:
			if cmds.objExists(i):
				if cmds.objectType(i) != "mesh" and 'tmpToRename' in i:
						cmds.rename( i, i.split('tmpToRename')[0] )
		self.run()
		
	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		
		
class CheckIfEndNumbers(CheckMayaAbstract):
	"""@brief Check for unknown nodes.
	"""
	_name = "check if PRP_ ends with _###."
	_category = "Scene"

	_asSelection = True
	_asFix = True

	def check(self):
		"""@brief Check for unknown node and add them to errors node.
		"""

		exceptions = ["front","persp","side","top"]
		selectLocs = cmds.ls(tr=True,s=False)
		selectLocstest = cmds.ls(et="transform", g=False, st=True, dep=False)

		noEndDigitsList = []
		for i in selectLocs:
			if i.split("_")[-1].isdigit() is True and i not in exceptions and '|' not in i :
				None
			elif i.startswith("PRP") and i.split("_")[-1].isdigit() is False and i not in exceptions and '|' not in i and 'cam_' not in i.lower() :
				noEndDigitsList.append(i)
		self.errorNodes = noEndDigitsList
		if not noEndDigitsList:
			self.status = "OK"
		if noEndDigitsList:
			self.status = self.errorMode
			self.errorNodes = noEndDigitsList
			self.errorMessage = "%s props with no _### at the end of the name" % (len(noEndDigitsList))
			
	def fix(self):
		"""@brief rename shape 
		"""
		for i in self.errorNodes:
			iSel = cmds.ls(i+"_001")
			if iSel:
				print (i+"_001 exist.")
			else:
				cmds.rename( i, i+"_001")
		self.run()
		
	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		
# '''
class CheckUniqueNames(CheckMayaAbstract):
	"""@brief Check for unknown nodes.
	"""
	_name = "Check Unique Names"
	_category = "Scene"

	_asSelection = True
	_asFix = True

	def check(self):
		"""@brief Check for unknown node and add them to errors node.
		"""
		ListNonUniqueObjs= []
		objs = [x for x in cmds.ls(shortNames=True,typ ='locator') if '|' in x]
		# objs = [x.replace(x.split('|')[-1],"")[:-1] for x in cmds.ls(shortNames=True,typ ='locator') if '|' in x]
		objs.sort(key=lambda x : x.count('|'))
		objs.reverse()
		# print objs
		self.errorNodes = objs
		if not objs:
			self.status = "OK"
		if objs:
			self.status = self.errorMode
			self.errorNodes = objs
			self.errorMessage = "%s are non unique" % (len(objs))
			
	def fix(self):
		"""@brief rename shape 
		"""
		# for i in self.errorNodes:
		objs = self.errorNodes
		if objs:
			for i in range(len(objs)):
				print objs[i]
				objsShort = [x.split('|')[-2] for x in objs]
				NameWithoutDigit = [x.replace(x.split('_')[-1],"") for x in set(objsShort) if x.split('_')[-1].isdigit() ]
				# print NameWithoutDigit
			for i in range(len(NameWithoutDigit)):
				print NameWithoutDigit[i]
				#all props startswith NameWithoutDigit
				ListObjectsFromNonUnique =[x for x in cmds.ls(l=True,typ ='locator') if x.split('|')[-2].startswith(NameWithoutDigit[i])]
				# print ListObjectsFromNonUnique
				print 50*"*"
				for i in range(len(ListObjectsFromNonUnique)):
					# print i
					digits = ListObjectsFromNonUnique[i].split('|')[-2].split('_')[-1]
					digits4= "%04d"%(int(digits))
					# print str(digits4) +"  >>>  " + "%04d"%(i+1)
					print ListObjectsFromNonUnique[i] + "  >>>>  " +ListObjectsFromNonUnique[i].split('|')[-2].replace(ListObjectsFromNonUnique[i].split('|')[-2].split('_')[-1],"")+ "%03d"%(i+1)
					cmds.rename(ListObjectsFromNonUnique[i].replace(ListObjectsFromNonUnique[i].split('|')[-1],""), ListObjectsFromNonUnique[i].split('|')[-2].replace(ListObjectsFromNonUnique[i].split('|')[-2].split('_')[-1],"")+ "%03d"%(i+1))
		self.run()
		
	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		for i in  (self.errorNodes):
			print i
# '''
# '''
class CheckRealReferences(CheckMayaAbstract):
	"""@brief Check for unknown nodes.
	"""
	_name = "Check if References call external files"
	_category = "Scene"

	_asSelection = True
	_asFix = True

	def check(self):
		"""@brief Check for unknown node and add them to errors node.
		"""
		ListRefs = cmds.ls(type = 'reference')
		NoFiles = []
		for iRef in ListRefs:
			try:
				# print cmds.referenceQuery(iRef, f=True)
				cmds.referenceQuery(iRef, f=True)
			except:
				NoFiles.append(iRef)
		self.errorNodes = NoFiles
		if not NoFiles:
			self.status = "OK"
		if NoFiles:
			self.status = self.errorMode
			self.errorNodes = NoFiles
			self.errorMessage = "%s are non unique" % (len(NoFiles))
			
	def fix(self):
		"""@brief rename shape 
		"""
		# for i in self.errorNodes:
		NoFiles = self.errorNodes
		for a in NoFiles:
			cmds.lockNode(a, l = False)
			cmds.delete(a)
		self.run()
		
	def select(self):
		"""@brief Select the error nodes.
		"""
		select(self.errorNodes)
		for i in  (self.errorNodes):
			print i

# '''