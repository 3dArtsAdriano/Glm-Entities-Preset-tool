'''Copyright (C) 2021  Adriano Sanna

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Golaem and Golaem trademark are property of Golaem S.A.'''



from PySide2 import QtCore, QtGui, QtWidgets
import sys
import os

from glm.layout.layout import *
import glm.ui.windowMayaWrapper as wrapper
import glm.layout.layoutEditorWrapper as layoutWrapper
import os
import copy
import xml.etree.ElementTree as ET
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm 
import maya.OpenMayaUI as omui
import shiboken2

asToolPath= "C:/Users/adriano.sanna/Documents/maya/2019/scripts/GEP/"
if asToolPath not in sys.path:
	sys.path.append(asToolPath)
import asWindow as GepW
reload(GepW)

def getMayaWindow():
    pointer = omui.MQtUtil.mainWindow()
    if pointer is not None:
        return shiboken2.wrapInstance(long(pointer),QtWidgets.QWidget)
        
def getPath():
    path=asToolPath
    return path
    
class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        
        self.wrapper = wrapper.WindowMayaWrapper()
        self.infos = EntitiesInformation()
        self.infosIdx = 0
        
        self.ui= GepW.Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        #self.preset=''
        #init UI
        self.init_ui()
        self.create_layout()
        self.create_connections()
        
    def init_ui(self):
        #set icons
        self.ui.saveButton.setIcon(QtGui.QIcon(getPath()+"icons/save.png"))
        self.ui.refreshButton.setIcon(QtGui.QIcon(getPath()+"icons/refresh.png"))
        self.ui.loadPresetFolderButton.setIcon(QtGui.QIcon(getPath()+"icons/open.png"))
        self.ui.refreshLoadButton.setIcon(QtGui.QIcon(getPath()+"icons/refresh.png"))
        self.ui.importToLayoutButton.setIcon(QtGui.QIcon(getPath()+"icons/import.png"))
        self.ui.loadLayoutFileButton.setIcon(QtGui.QIcon(getPath()+"icons/open.png"))
        
        self.updateEntityInformation()
        
        
    def create_layout(self):
       # self.ui.layout().setContentsMargins(6, 6, 6, 6)
       pass
        
        
    def create_connections(self):
        self.ui.saveButton.clicked.connect(self.exportXML) #savepreset
        self.ui.refreshButton.clicked.connect(self.updateEntityInformation) #refresh entity data
        self.ui.loadPresetFolderButton.clicked.connect(self.loadPresetFolder) #loadPresetFolder
        self.ui.refreshLoadButton.clicked.connect(self.loadRefreshData)
        self.ui.loadLayoutFileButton.clicked.connect(self.loadLayoutFile)
        self.ui.importToLayoutButton.clicked.connect(self.createLayoutNode)
        
    def updateEntityInformation(self):
        cacheProxies = self.wrapper.getObjectsOfType('SimulationCacheProxy')
        entitiesInfos = []
        # fetch selection for all proxies
        self.infos.clear()
        for cacheProxy in cacheProxies:
            entitiesInfos = cmds.glmLayoutTool(cacheProxy=cacheProxy, getSelectedEntitiesInfos=True)
            characterFiles = cmds.getAttr(cacheProxy + '.characterFiles').split(';')
            self.infos.add(entitiesInfos, characterFiles, cacheProxy)
        self.infosIdx = max(min(self.infosIdx, self.infos.count() - 1), 0)
        self.displayCurrEntityInformation()
        
    #------------------------------------------------------------------
    # Add Items in listWidget
    #------------------------------------------------------------------
    def addItemsInListWidget(self, listWidget, items):
        listWidget.clear()
        for item in items:
            listWidget.addItem(item)
    #------------------------------------------------------------------
    # EXPORT XML  
    #------------------------------------------------------------------
    def exportXML(self):
        entity = self.infos.entities[self.infosIdx]
        
        entities = ET.Element('entity')
        entities.set('id', entity.entityId )
        entities.set('characterName', entity.characterName)
        entities.set('characterFile', entity.characterFile)

        meshes = ET.SubElement(entities, 'meshes')
        #write mesh-------------------------------
        for i, val in enumerate(entity.meshes):
            sg = ET.SubElement(meshes, 'mesh')
            sg.set('name',entity.meshes[i])

        shadingGroups = ET.SubElement(entities, 'shadingGroups')
        #write shading group----------------------
        for i, val in enumerate(entity.shadingGroups):
            sg = ET.SubElement(shadingGroups, 'sg')
            sg.set('name',entity.shadingGroups[i])

        shaderAttr = ET.SubElement(entities, 'shadingAttr')
        #write shading attributes----------------------
        for i, val in enumerate(entity.shadingAttrbs):
            sg = ET.SubElement(shaderAttr, 'shAttr')
            values= entity.shadingAttrbs[i].replace(":","")
            sg.set('attr',values)

        blindDataS = ET.SubElement(entities, 'blindData')
        #write shading attributes----------------------
        for i, val in enumerate(entity.blindData):
            sg = ET.SubElement(blindDataS, 'bditm')
           # values= entity.shadingAttrbs[i].replace(":","")
            sg.set('name',entity.blindData[i])

        
        # create a new XML file with the results
        mydata = ET.tostring(entities)
        fileIn = QtWidgets.QFileDialog.getSaveFileName(self,"Save Entity Preset File", getPath(), "Golaem Entity Preset files (*.gepml)")
        myfile = open(fileIn[0], 'w')
        myfile.write(mydata)
        print('xml saved!')
    

    #------------------------------------------------------------------
    # Displays Current Entity
    #------------------------------------------------------------------
    def displayCurrEntityInformation(self):
        if self.infos.count() > 0:
            # fill data
            entity = self.infos.entities[self.infosIdx]
          
            #set entityInfo
            self.ui.cacheProxyValueLabel.setText(entity.nodeName)
            self.ui.entityIdValueLabel.setText(entity.entityId)
            self.ui.gchaFileValueLabel.setText(".."+entity.characterFile[-27:])
            filepath = cmds.file(q=True, sn=True)
            filename = os.path.basename(filepath)
            raw_name, extension = os.path.splitext(filename)
            self.ui.mayaSceneValueLabel.setText(raw_name+extension)
            
            #set selected entity Data on tabs (save/load)
            #save tab
            self.addItemsInListWidget(self.ui.meshesListWidget, entity.meshes)
            self.addItemsInListWidget(self.ui.shadingGroupsListWidget, entity.shadingGroups)
            self.addItemsInListWidget(self.ui.shaderAttrListWidget, entity.shadingAttrbs)
            self.addItemsInListWidget(self.ui.blindDataListWidget, entity.blindData)
            #load tab
            self.addItemsInListWidget(self.ui.selectedMeshesListWidget,entity.meshes)
            self.addItemsInListWidget(self.ui.selectedShadingGroupListWidget,entity.shadingGroups)
            self.addItemsInListWidget(self.ui.selectedShaderAttrListWidget,entity.shadingAttrbs)
            self.addItemsInListWidget(self.ui.selectedBlindDataListWidget,entity.blindData)
            #update first layoutFile path from selected entity
            cpLayouts= entity.nodeName+".layoutFiles[0].path"
            self.ui.layoutFileLineEdit.setText(cmds.getAttr(str(cpLayouts)))
            
    def loadPresetFolder(self):
        
        folderPath = QtWidgets.QFileDialog.getExistingDirectory(self,"Set Entity Preset Folder", getPath(), QtWidgets.QFileDialog.ShowDirsOnly)
        self.ui.presetFolderLineEdit.setText(folderPath)
        myPresetList= os.listdir(folderPath)
        self.ui.presetListComboBox.insertItems(0,myPresetList)
        
    def getPrestPath(self):
        preset= self.ui.presetListComboBox.currentText()#return text from comboBoxIndex
        presetPath= self.ui.presetFolderLineEdit.text()
        
        self.preset=str(presetPath+"/"+preset)
        
        return self.preset
        
    def loadLayoutFile(self):
        layoutFile = QtWidgets.QFileDialog.getOpenFileName(self,"Set Layout Editor File", getPath(), "Golaem Layout files (*.gscl)")
        self.ui.layoutFileLineEdit.setText(layoutFile[0])
        
    def loadArray(self):
        self.getXMLData= XmlEntityData()#xml class
        
        preset= self.ui.presetListComboBox.currentText()#return text from comboBoxIndex
        presetPath= self.ui.presetFolderLineEdit.text()
        
        self.preset=str(presetPath+"/"+preset)
        print ("folder: "+str(presetPath+"/"+preset))
        self.getXMLData.setPresetFile(str(presetPath+"/"+preset))
        myData= self.getXMLData.getAllData(str(presetPath+"/"+preset))
        
        return myData
    
    def loadRefreshData(self):
        self.updateEntityInformation()
       
        myData=self.loadArray()
        #update ui
        self.addItemsInListWidget(self.ui.xmlMeshesListWidget,myData[0])
        self.addItemsInListWidget(self.ui.xmlShadingGroupsListWidget,myData[2])
        self.addItemsInListWidget(self.ui.xmlShaderAttrListWidget,myData[1])
        self.addItemsInListWidget(self.ui.xmlBlindDataListWidget,myData[3])
                
    def createLayoutNode(self):
        
        rootId=None
        previousRootNode=None
        
        #filePaths = list()
        filePath=self.ui.layoutFileLineEdit.text()
        
        preset= self.ui.presetListComboBox.currentText()#return text from comboBoxIndex
        presetPath= self.ui.presetFolderLineEdit.text()
        #print ("folder: "+str(presetPath+"/"+preset))
      
        
        
        print("processing file {}".format(filePath))
        fileHandle = openLayoutFile(filePath)
        if (fileHandle is not None):

           # entity = self.infos.entities[self.infosIdx]
          # get current Root Node Id for main graph
            rootId = getRootId(fileHandle)
            previousRootNode = getNodeById(fileHandle, rootId)
          # get current Root Node from Id (to be able to link next nodes)

            if self.ui.meshesCheckBox.isChecked()== True:
                print('>>>> meshes export')
                data=self.loadArray()
                rootId = getRootId(fileHandle)
                previousRootNode = getNodeById(fileHandle, rootId)
                
                #fix
                #creare nodo setMeshAssets ; connetterlo all'ultimo nodo disponibile; fare query mesh print(cmds.glmLayoutTool(cacheProxy="cacheProxyShape1", getAvailableMeshAssets=True, requestSourceNode="42")) e comparare stringhe per ricavare la lista degli indici;
               
                meshListIndex=[]
                nodeName = self.infos.entities[self.infosIdx].nodeName
                
                #disable other cacheProxies
                self.disableCache(nodeName)
                
                selMeshesAssets= cmds.glmLayoutTool(cacheProxy=nodeName, getAvailableMeshAssets=True, requestSourceNode=rootId)
                print(selMeshesAssets)

                if selMeshesAssets==None:
                    print('no root node or sel node')
                    entityId = self.infos.entities[self.infosIdx].entityId
                    nodeSel= self.createRootSelector(entityId,fileHandle,nodeName)
                    nodeOp= createOperator(fileHandle , 'SetMeshAssets',nodeSel[0] )
                    nodeOpId= getNodeID(nodeOp)
                    connect(fileHandle , nodeSel[1], nodeOpId)
                    print(nodeName)
                    print(nodeOp)
                    print (fileHandle)
                    print (filePath)
                    print (filePaths)
                    
                    setNodeAttribute(nodeOp, 'sourceMeshAssetIndices', [], [[0]])
                 
                    
                    rootId = getRootId(fileHandle)
                    print(rootId)
                    previousRootNode = getNodeById(fileHandle, rootId)
                    print(previousRootNode)
                    selMeshesAssets= cmds.glmLayoutTool(cacheProxy=nodeName, getAvailableMeshAssets=True, requestSourceNode=rootId)
                    print(selMeshesAssets)
                    
                    #compare list on preset with selection and extract the index
                    for x,value in enumerate(selMeshesAssets):
                        print(x)
                        
                        for y,compareItem in enumerate(data[0]):
                            fixValue=compareItem.replace(';','')
                            if(value==fixValue):
                                meshListIndex.append(x)
                                print('>>item match')
                            else:
                                pass
                               
                    print (meshListIndex)
                    setNodeAttribute(nodeOp, 'sourceMeshAssetIndices', [], [meshListIndex])
                  
                    
                else:
                    print('root exist!')
                    
                    entityId = self.infos.entities[self.infosIdx].entityId
                    nodeSel= self.createRootSelector(entityId,fileHandle,nodeName)
                    connect(fileHandle , rootId, nodeSel[1])
                    nodeOp= createOperator(fileHandle , 'SetMeshAssets',nodeSel[0] )
                    nodeOpId= getNodeID(nodeOp)
                    connect(fileHandle , nodeSel[1], nodeOpId)
                    print(nodeName)
                    print(nodeOp)
                    
                    
                    setNodeAttribute(nodeOp, 'sourceMeshAssetIndices', [], [[0]])
                 
                    
                    rootId = getRootId(fileHandle)
                    previousRootNode = getNodeById(fileHandle, rootId)
                    selMeshesAssets= cmds.glmLayoutTool(cacheProxy=nodeName, getAvailableMeshAssets=True, requestSourceNode=rootId)
                    print(selMeshesAssets)
                    
                    #compare list on preset with selection and extract the index
                    for x,value in enumerate(selMeshesAssets):
                        print(x)
                        
                        for y,compareItem in enumerate(data[0]):
                            fixValue=compareItem.replace(';','')
                            if(value==fixValue):
                                meshListIndex.append(x)
                                print('>>item match')
                            else:
                                pass
                               
                    print (meshListIndex)
                    setNodeAttribute(nodeOp, 'sourceMeshAssetIndices', [], [meshListIndex])
                    
                   
                   
                    
                   
            if self.ui.shaderAttrCheckBox.isChecked()== True:
                
                data=self.loadArray()
                attrbs= str(data[1]).replace(',','')
                attrbs= attrbs.replace("'",'')
                attrbs= attrbs.replace('[','')
                attrbs= attrbs.replace(']','')
                
                self.sdItemDoubleClicked(attrbs)
            #if self.ui.shadingGroupCheckBox.isChecked()== True:
            #    print('TODO Shading Group export')
            #    self.sgItemDoubleClicked()
           # if self.ui.blindDataCheckBox.isChecked()== True:
            #    print('TODO blind data export')
            
                
            saveLayoutFile(fileHandle)
            mel.eval('glmSimulationCacheLayoutFocusCacheCmd("'+nodeName+'.layoutFiles[0]path")')
            #cmds.glmLayoutTool(cacheProxy=nodeName, dirtyAssetsRepartition=True)
            self.enableCache(nodeName)
            #mel.eval('AESC_refreshProxy('+nodeName+'.layoutNeedRefresh")')
            
    #------------------------------------------------------------------
    # Meshes
    #------------------------------------------------------------------
    def meshItemDoubleClicked(self,meshlist):
        layoutEWrapper = layoutWrapper.getTheLayoutEditorWrapperInstance(True)
        if layoutEWrapper is not None:
            nodeName = self.infos.entities[self.infosIdx].nodeName
            layoutIndex = cmds.glmLayoutTool(cacheProxy=nodeName, getLayoutIndex=True)
            entityId = self.infos.entities[self.infosIdx].entityId
            layoutEWrapper.addOrEditLayoutTransformation('{} {}'.format(nodeName, layoutIndex), '{}'.format(entityId), 'SetMeshAssets', 'sourceMeshAssetIndices', [0], None, 0)

    #------------------------------------------------------------------
    # SG !!TODO!!
    #------------------------------------------------------------------
    #def sgItemDoubleClicked(self):
    #    layoutEWrapper = layoutWrapper.getTheLayoutEditorWrapperInstance(True)
    #    if layoutEWrapper is not None:
    #        nodeName = self.infos.entities[self.infosIdx].nodeName
    #        layoutIndex = cmds.glmLayoutTool(cacheProxy=nodeName, getLayoutIndex=True)
    #        entityId = self.infos.entities[self.infosIdx].entityId
    #        layoutEWrapper.addOrEditLayoutTransformation('{} {}'.format(nodeName, layoutIndex), '{}'.format(entityId), 'ReplaceShader', 'replaceShaderString', None, None, 0)

    #------------------------------------------------------------------
    # Shader's Attributes 
    #------------------------------------------------------------------
    def sdItemDoubleClicked(self,list):
        layoutEWrapper = layoutWrapper.getTheLayoutEditorWrapperInstance(True)
        if layoutEWrapper is not None:
            nodeName = self.infos.entities[self.infosIdx].nodeName
            layoutIndex = cmds.glmLayoutTool(cacheProxy=nodeName, getLayoutIndex=True)
            entityId = self.infos.entities[self.infosIdx].entityId
            #shaderAttr = item.text().replace(':', '')
            layoutEWrapper.addOrEditLayoutTransformation('{} {}'.format(nodeName, layoutIndex), '{}'.format(entityId), 'SetShaderAttribute', 'shaderAttribute', ['{}'.format(list)], None, 0)
    #------------------------------------------------------------------
    # BlinData !!TODO!!
    #------------------------------------------------------------------
    #def bdItemDoubleClicked(self):
    #    layoutEWrapper = layoutWrapper.getTheLayoutEditorWrapperInstance(True)
    #    if layoutEWrapper is not None:
    #        nodeName = self.infos.entities[self.infosIdx].nodeName
    #        layoutIndex = cmds.glmLayoutTool(cacheProxy=nodeName, getLayoutIndex=True)
    #        entityId = self.infos.entities[self.infosIdx].entityId
    #        #shaderAttr = item.text().replace(':', '')
    #        layoutEWrapper.addOrEditLayoutTransformation('{} {}'.format(nodeName, layoutIndex), '{}'.format(entityId), 'BlindData', None, None, None, 0)
   
    def createRootSelector(self,entityId,filehandle,cacheNode):
        selNode= createSelector(filehandle , entityId, None, None)
        selId= getNodeID(selNode)    
        setRootId(filehandle , selId, groupNodeId=None)
        cmds.glmLayoutTool(cacheProxy=cacheNode, selectEntities=entityId)
        
        selInfos=[selNode,selId]
        
        return selInfos
        
    def disableCache(self, cacheNode):
        allObjects = pm.ls(type='SimulationCacheProxy')
        for obj in allObjects:
            print obj
            if obj!= cacheNode:
                #todo disable cacheproxy
                #setAttr "walkingguysShape.enable" 1;
                obj.setAttr('enable',False)
                
            else:
                #do nothing
                pass
                
    def enableCache(self,cacheNode):
        allObjects = pm.ls(type='SimulationCacheProxy')
        for obj in allObjects:
            print obj
            enabAttr= obj.getAttr('enable')
            if enabAttr== False:
                obj.setAttr('enable',True)
                
            else:
                pass
                
        mel.eval('AESC_refreshProxy('+cacheNode+'.layoutNeedRefresh")')
        
        
        
class XmlEntityData(object):
    def __init__(self):
        self.meshesList=[]
        self.shadingGroupsList=[]
        self.shaderAttrList=[]
        self.blindDataList=[]
        self.presetFile=''
        self.init()
    
    def init(self):
        print('init XML...')
        #self.getAllData(self.presetFile)
    
    def getAllData(self,preset):
        
        tree = ET.parse(preset)
        root = tree.getroot()
        
        self.getEntityItemListFromXml(root,self.meshesList,'mesh','name')#0
        self.getEntityItemListFromXml(root,self.shaderAttrList,'shAttr','attr')#1
        self.getEntityItemListFromXml(root,self.shadingGroupsList,'sg','name')#2
        self.getEntityItemListFromXml(root,self.blindDataList,'blindData','name')#3
        
        mylist=[self.meshesList,self.shaderAttrList,self.shadingGroupsList,self.blindDataList]
        return mylist
    
    def setPresetFile(self,presetPath):
        self.presetFile= presetPath
        print('got preset file: '+self.presetFile)
    
    def getEntityItemListFromXml(self,xmlRoot, mylist, subelemString, subelemenAttr):

        for elem in xmlRoot:
            for subelem in elem.findall(subelemString):

                # if we don't need to know the name of the attribute(s), get the dict
                #print(subelem.attrib)      

                # if we know the name of the attribute, access it directly
                #print(subelem.get(subelemenAttr))    
                myitem=subelem.get(subelemenAttr)
               #myitem= myitem.decode('utf-8')
                mylist.append(myitem+';')
    
#**********************************************************************
#
# EntitiesInformation
#
#**********************************************************************
class EntitiesInformation(object):
    #------------------------------------------------------------------
    # Constructor
    #------------------------------------------------------------------
    def __init__(self):
        self.entities = []
        self.charFiles = []
        self.shared = EntityInformation()
        
    
    #------------------------------------------------------------------
    # Add
    #------------------------------------------------------------------
    def add(self, infosArray, charFilesArray, cacheName):
        for info in infosArray:
            entityInfo = EntityInformation()
            entityInfo.init(info, charFilesArray, cacheName)
            if entityInfo.isInitialized() is True:
                self.entities.append(entityInfo)
                # update shared properties
                if self.shared.isInitialized() is False:
                    self.shared = copy.deepcopy(self.entities[0])
                else:
                    self.shared.computeInCommon(entityInfo)
    #------------------------------------------------------------------
    # Clear
    #------------------------------------------------------------------
    def clear(self):
        self.shared.clear()
        del self.entities[:]

    #------------------------------------------------------------------
    # Count
    #------------------------------------------------------------------
    def count(self):
        return len(self.entities)
#**********************************************************************
#
# EntityInformation
#
#**********************************************************************
class EntityInformation(object):
    #------------------------------------------------------------------
    # Constructor
    #------------------------------------------------------------------
    def __init__(self):
        self.entityId = 0
        self.crowdFieldIdx = -1
        self.entityTypeIdx = -1
        self.characterIdx = -1
        self.characterFile = ''
        self.characterName = ''
        self.nodeName = ''
        self.meshes = []
        self.shadingGroups = []
        self.shadingAttrbs = []
        self.shadingAttrVs = []
        self.blindData = []
        self.initialized = False

    #------------------------------------------------------------------
    # Init Function
    #------------------------------------------------------------------
    def init(self, infosStr, charFiles, nodeName):
        entityInfos = infosStr.split(';')
        if len(entityInfos) < 5:
            return

        # ids
        entityIds = entityInfos[0].split(',')
        self.entityId = entityIds[0]
        self.crowdFieldIdx = entityIds[1]
        self.entityTypeIdx = entityIds[2]
        self.characterIdx = entityIds[3]
        self.characterFile = charFiles[int(self.characterIdx)] if int(self.characterIdx) < len(charFiles) else 'NA'
        self.characterName = entityIds[4]
        self.nodeName = nodeName

        # other data
        self.meshes = entityInfos[1].split(',')
        self.shadingGroups = entityInfos[2].split(',')
        self.shadingAttrbs = entityInfos[3].split(',')
        self.blindData = entityInfos[4].split(',')
        self.initialized = True

    #------------------------------------------------------------------
    # Clear
    #------------------------------------------------------------------
    def clear(self):
        self.entityId = 0
        self.crowdFieldIdx = -1
        self.entityTypeIdx = -1
        self.characterIdx = -1
        self.characterName = ''
        self.nodeName = ''
        del self.meshes[:]
        del self.shadingGroups[:]
        del self.shadingAttrbs[:]
        del self.shadingAttrVs[:]
        del self.blindData[:]
        self.initialized = False

    #------------------------------------------------------------------
    #
    #------------------------------------------------------------------
    def computeInCommon(self, other):
        default = EntityInformation()
        self.entityId = self.entityId if self.entityId == other.entityId else default.entityId
        self.crowdFieldIdx = self.crowdFieldIdx if self.crowdFieldIdx == other.crowdFieldIdx else default.crowdFieldIdx
        self.entityTypeIdx = self.entityTypeIdx if self.entityTypeIdx == other.entityTypeIdx else default.entityTypeIdx
        self.characterIdx = self.characterIdx if self.characterIdx == other.characterIdx else default.characterIdx
        self.characterName = self.characterName if self.characterName == other.characterName else default.characterName
        self.nodeName = self.nodeName if self.nodeName == other.nodeName else default.nodeName
        self.meshes = [value for value in self.meshes if value in other.meshes]
        self.shadingGroups = [value for value in self.shadingGroups if value in other.shadingGroups]
        self.shadingAttrbs = [value for value in self.shadingAttrbs if value in other.shadingAttrbs]
        self.blindData = [value for value in self.blindData if value in other.blindData]

    #------------------------------------------------------------------
    # Initialized
    #------------------------------------------------------------------
    def isInitialized(self):
        return self.initialized
        
        
if __name__ == "__main__":

    try:
        mainWindow.close() # pylint: disable=E0601
        mainWindow.deleteLater()
    except:
        pass

    mainWindow= MainWindow(getMayaWindow())
    mainWindow.show()
