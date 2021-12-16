# Glm-Entities-Preset-tool

Introduction
----------

This is a pure python's tool to improves functionality and optimize some processes related to Autodesk Maya's plugin for crowds simulation Golaem. 
Glm Entities Preset tool enable user to store entities data into preset file and reload on different cacheproxy node by automate Golaem Layout Editor nodes creations and edits.

Features:

* store cache Proxy entity data as Xml format
* load entity data on selected entity by automate Layout's node creation with all data needed and connection. 

Preset Data structure:

* gcha's file (string) 
* Maya scene origi (string) 
* cacheProxy node (string) 
* CrowdField name (string) 
* entity ID (int) 
* Meshes (string[]) 
* Shading Group (string[])
* Shaders Attributes (string[])
* Blindata (string[])
* TODO: WorldPosition (float[]) 



Install
-------

Just drag and drop the install.mel file on to the Maya's viewport. A new shelf button will be created on the active shelve/tab.

Licensing
--------

Copyright (C) 2021  Adriano Sanna. 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

<https://www.gnu.org/licenses/>
