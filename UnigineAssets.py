import xml.etree.ElementTree as ET
import os
# import shutil

from def_globals import *
# from fbx_processor import *



# =============================================================================
# Models.
# =============================================================================
def ParseModelsXmlList():
	'''
	
	'''
	# print("XML file: " + MODELS_XML)

	tree = ET.parse(MODELS_XML)
	root = tree.getroot()

	#all_textures = root.iter('Texture')
	#textures_count = sum(1 for _ in all_textures)

	# for tex in all_textures:
	for mod in root.iter('Model'):
		# parse textures
		path_xml = xml_get(mod, "path")

		path_orig = os.path.normpath(os.path.join(CRYENGINE_ASSETS_PATH, path_xml))
		path_rel = os.path.normpath(os.path.join(DESTINATION_ASSETS_PATH, path_xml))

		if (not os.path.exists(path_orig)):
			continue

		#
		if (not os.path.exists(os.path.dirname(path_rel))):
			os.makedirs(os.path.dirname(path_rel))
        
		# print("\n" + path_orig + "\n" + path_rel + "\n\n")
		import shutil
		shutil.copy2(path_orig, path_rel)

		# Work with fbx.
		# Convert_fbx_model_to_unigine(path_rel, path_rel)

	pass


# =============================================================================
# Materials.
# =============================================================================
def ParseCryMtlFile(xml_file):
	'''
	Parsing cry mtl file.
	return {object}
	'''

	tree = ET.parse(xml_file)
	root = tree.getroot()

	cry_mtl_obj = {}
	cry_mtl_obj["mtl_file"] = xml_file
	cry_mtl_obj["materials"] = []

	submat_root = root

	if (root.find('SubMaterials') != None): submat_root = root.find('SubMaterials')


	for mat in submat_root.iter('Material'):
		# parse materials
		cry_material = {}
		cry_material["name"] = xml_get(mat, "Name")
		cry_material["shader"] = xml_get(mat, "Shader")
		cry_material["gen_mask"] = xml_get(mat, "GenMask")
		cry_material["string_gen_mask"] = xml_get(mat, "StringGenMask")
		cry_material["surface_type"] = xml_get(mat, "SurfaceType")
		cry_material["diffuse"] = xml_get(mat, "Diffuse")
		cry_material["specular"] = xml_get(mat, "Specular")
		cry_material["opacity"] = xml_get(mat, "Opacity")
		cry_material["shininess"] = xml_get(mat, "Shininess")
		cry_material["alpha_test"] = xml_get(mat, "AlphaTest")
		cry_material["emissive"] = xml_get(mat, "Emissive")

		cry_material["textures"] = []

		for tex in mat.iter('Texture'):
			# parse textures.
			cry_texture = {}
			cry_texture["map"] = xml_get(tex, "Map")
			cry_texture["file"] = xml_get(tex, "File")

			cry_material["textures"].append(cry_texture)
		
		# fix
		# if (cry_material["name"] == None): cry_material["name"] = os.path.splitext(os.path.basename(xml_file))[0]
	
		cry_mtl_obj["materials"].append(cry_material)
	
	return cry_mtl_obj



def CreateUnigineXmlMaterial(cry_xml_root, unigine_mat_path):
	'''
	Create unigine material and link existing textures.

	'''

	import uuid
	import hashlib

	mat_file_path = xml_get(cry_xml_root, "mtl_file")

	mat_name = xml_get(cry_xml_root, "name")
	mat_shader = xml_get(cry_xml_root, "shader")
	mat_gen_mask = xml_get(cry_xml_root, "gen_mask")

	# <?xml version="1.0" encoding="utf-8"?>

	xml_root = ET.Element('material')
	xml_root.set('version', "2.11.0.0")
	xml_root.set('name', mat_name)

	unigine_uuid = hashlib.sha1(unigine_mat_path.encode('utf-8'))
	xml_root.set('guid', unigine_uuid.hexdigest())
	# print("==================================================")
	# print(unigine_uuid.hexdigest())
	# print(unigine_mat_path)
	# print("==================================================")

	# material base type.
	if (mat_shader == "Illum"):
		xml_root.set('base_material', "mesh_base")
	# if (mat_shader == "Illum"):
	# 	xml_root.set('base_material', "decal_base")
	if (mat_shader == "Vegetation"):
		xml_root.set('base_material', "grass_base")


	# parse textures.
	for tex in cry_xml_root.iter('Texture'):
		tex_map = xml_get(tex, "map")
		tex_file = xml_get(tex, "file")

		# to unigine texture paths
		filename, file_extension = os.path.splitext(os.path.basename(tex_file))
		new_filename = convert_suffixes_to_unigine(filename)
		rel_path = os.path.normpath(os.path.join(os.path.dirname(tex_file), new_filename)).replace("\\", "/") + ".tga"
		full_path = os.path.normpath(os.path.join(DESTINATION_ASSETS_PATH, rel_path)).replace("\\", "/")
		

		xml_child = ET.SubElement(xml_root, 'texture')
		xml_child.text = rel_path

		if (tex_map == "Diffuse"):
			# albedo
			xml_child.set('name', "albedo")
			if (os.path.isfile(full_path)):
				xml_child.text = rel_path
			else:
				# xml_child.text = "guid://5219d6ddb5dbd1520e843a369ad2b64326bb24e2"	# white texture from core/textures/common/
				xml_child.text = "Textures/cry_missing/pink_alb.tga"


			
		if (tex_map == "Bumpmap"):
			# normal map
			xml_child.set('name', "normal")
			if (os.path.isfile(full_path)):
				xml_child.text = rel_path
			else:
				# xml_child.text = "guid://692dbb7d56d633e22551bd47f4d92cd2d498270d" # default normal
				xml_child.text = "Textures/cry_missing/normal_n.tga"

			# shading
			rel_path = rel_path[:-6] + "_sh.tga"
			full_path = os.path.normpath(os.path.join(DESTINATION_ASSETS_PATH, rel_path)).replace("\\", "/")
			xml_child = ET.SubElement(xml_root, 'texture')

			xml_child.set('name', "shading")
			if (os.path.isfile(full_path)):
				xml_child.text = rel_path
			else:
				xml_child.text = "Textures/cry_missing/normal_sh.tga"


		
		

	

	# Parameters.
	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1"
	xml_child.set('name', "metalness")
	xml_child.set('expression', "0")


	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1 1 1 1"
	xml_child.set('name', "specular_color")
	xml_child.set('expression', "0")


	xml_child = ET.SubElement(xml_root, 'parameter')
	xml_child.text = "1"
	xml_child.set('name', "gloss")
	xml_child.set('expression', "0")

	alpha_test = xml_get(cry_xml_root, "alpha_test")
	if (alpha_test != ""):
		# Alpha test.
		xml_child = ET.SubElement(xml_root, 'options')
		xml_child.set('transparent', "1")
		
		xml_child = ET.SubElement(xml_root, 'parameter')
		xml_child.text = "1.3"
		xml_child.set('name', "transparent")
		xml_child.set('expression', "0")


	# print("==================================================")
	# print(xml_prettify(xml_root))
	# print("==================================================")
	
	return xml_root


def Create_default_materials():
	'''
	Root materials.

	'''

	pass

def ParseMaterialsXmlList():
	'''
	
	'''

	#
	Create_default_materials()

	#
	tree = ET.parse(MATERIALS_XML)
	root = tree.getroot()

	for mat in root.iter('Material'):
		# print(' > name: ' + xml_get(mat, "name") + " shader: " + xml_get(mat, "shader"))

		if (xml_get(mat, "shader") == "Nodraw"):
			continue

		# put *.mat in materials subfolder
		cry_mat_file_path = xml_get(mat, "mtl_file")

		# path_orig = os.path.normpath(os.path.join(CRYENGINE_ASSETS_PATH, path_xml))
		path_rel = os.path.normpath(os.path.join(DESTINATION_ASSETS_PATH, os.path.dirname(cry_mat_file_path), "materials"))
		unigine_mat_path = os.path.join(path_rel, xml_get(mat, "name")) + ".mat"
		unigine_mat_path_rel = os.path.join(os.path.dirname(cry_mat_file_path), "materials") + "\\" + xml_get(mat, "name") + ".mat"

		unigine_mat_xml = CreateUnigineXmlMaterial(mat, unigine_mat_path_rel)

		if not os.path.exists(path_rel):
			os.makedirs(path_rel)
		# print("========================================" + unigine_mat_path)
		tree = ET.ElementTree(unigine_mat_xml)
		try:
			tree.write(unigine_mat_path)
		except OSError:
			logging.error("\nUnable save material: " + cry_mat_file_path + "\n")

		# logging.info("\n\n" + cry_mat_file_path + "\n" + xml_prettify(tree.getroot()) + "\n\n")
	

	pass


# =============================================================================
# Textures.
# =============================================================================

def ParseTexturesXmlList():
	'''
	Convert and copy all tif textures from textures_xml.
	Convert and copy all textures (tif, dds) from materials_xml.
	'''

	# from wand_processor import ImageConvert
	from pillow_processor import ImageConvert

	# Collect all dds and tif paths in project.
	# all_textures = get_filepaths(CRYENGINE_ASSETS_PATH, "image")

	exported_textures = []


	# parse textures_xml file.
	tree = ET.parse(TEXTURES_XML)
	root = tree.getroot()

	for tex in root.iter('Texture'):
		# parse textures
		path_xml = xml_get(tex, "path")
		path_orig = os.path.normpath(os.path.join(CRYENGINE_ASSETS_PATH, path_xml))
		path_rel = os.path.normpath(os.path.join(DESTINATION_ASSETS_PATH, os.path.dirname(path_xml)))

		if (not os.path.exists(path_orig)): continue
		
		if (not os.path.exists(path_rel)): os.makedirs(path_rel)

		ImageConvert(path_orig, path_rel)
		exported_textures.append(os.path.normpath(path_orig.lower()))
	

	# parse materials_xml file.
	tree = ET.parse(MATERIALS_XML)
	root = tree.getroot()

	for mat in root.iter('Material'):
		mat_file_path = xml_get(mat, "mtl_file")

		for tex in mat.iter('Texture'):
			# parse textures.
			tex_map = xml_get(tex, "map")
			tex_file = xml_get(tex, "file")
			
			full_path = os.path.normpath(os.path.join(CRYENGINE_ASSETS_PATH, tex_file))

			if (os.path.normpath(full_path.lower()) in exported_textures):
				# texture already convered.
				continue

			if (os.path.isfile(full_path)):
				ImageConvert(full_path, path_rel)
				exported_textures.append(os.path.normpath(full_path.lower()))
			else:
				logging.error("\n\t\t\tTexture missing: " + full_path + "\n\t\t\t" + xml_get(tex, "file_orig") +"\n\t\t\t")
				continue

			
	
	# converted textures info
	logging.info("\n\n\n\tTexture convert done !!! \n\tTextures: " + str(len(exported_textures)) + "\n\n")
	

	pass


#
#
def Create_prefabs():
	'''

	'''

	prefabs_path = os.path.join(CRYENGINE_ASSETS_PATH, "prefabs")

	for prefabs_xml_path in CRY_PREFABS:
		path = os.path.join(prefabs_path, prefabs_xml_path) + ".xml"
		if (not os.path.isfile(path)): continue

		tree = ET.parse(path)
		root = tree.getroot()
		for prefab in root.iter('Prefab'):
			prefab.get("Name")
			prefab.get("Id")
			prefab.get("Library")

			print("Prefab: " + prefab.get("Name"))

			for cry_object in prefab.getchildren()[0].iter("Object"):
				# 
				p_type = cry_object.get("Type")
				cry_object.get("Layer")
				cry_object.get("Name")
				cry_object.get("Pos")
				cry_object.get("Rotate")
				cry_object.get("Scale")
				
				if (p_type == "Decal"):
					cry_object.get("Material")
				if (p_type == "Brush"):
					cry_object.get("Prefab")

				print("\tObject: " + cry_object.get("Name"))
		pass

		pass

	pass