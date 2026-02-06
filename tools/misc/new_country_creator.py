




## PARAMETERS:
tag = "AVA"
color = "129 25 82 "
loc_name = "Avari Tribes"


def replace_in_file(filepath, search, replace):
    # Read in the file
    with open(filepath, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(search, replace)

    # Write the file out again
    with open(filepath, 'w') as file:
        file.write(filedata)


base_path = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr'

replace_in_file(
    base_path+r'\common\country_tags\lotr_00_countries.txt',
    "# $NEW_COUNTRY_TOKENHELPER_TAG",
    f"{tag} = \"countries/{loc_name}.txt\"\n# $NEW_COUNTRY_TOKENHELPER_TAG"
)

c_content = """
graphical_culture = commonwealth_gfx
graphical_culture_2d = southamerican_2d

color = { 255  204  204 }"""

with open(base_path+f"/common/countries/{loc_name}.txt", "w") as f:
  f.write(c_content)


col_content = tag + " = {\n\tcolor = rgb { "+color+" }\n\tcolor_ui = rgb { "+color+" }\n}"

replace_in_file(
    base_path+r'\common\countries\colors.txt',
    "# $NEW_COUNTRY_TOKENHELPER_COLORS",
    col_content+"\n# $NEW_COUNTRY_TOKENHELPER_COLORS"
)

# loc_name
loc_names_content = """ $TAG$_belligerent:0 "$NAME$"
 $TAG$_belligerent_DEF:0 "$NAME$"
 $TAG$_cooperative:0 "$NAME$"
 $TAG$_cooperative_DEF:0 "$NAME$"
 $TAG$_unaligned:0 "$NAME$"
 $TAG$_unaligned_DEF:0 "$NAME$"
 $TAG$_revolutionary:0 "$NAME$"
 $TAG$_revolutionary_DEF:0 "$NAME$"
 $TAG$_belligerent_ADJ:0 "$NAME$"
 $TAG$_cooperative_ADJ:0 "$NAME$"
 $TAG$_unaligned_ADJ:0 "$NAME$"
 $TAG$_revolutionary_ADJ:0 "$NAME$"
 $TAG$:0 "$NAME$"
 $TAG$_DEF:0 "$NAME$"
 $TAG$_ADJ:0 "$NAME$"
 ##############################
# $NEW_COUNTRY_TOKENHELPER_LOCNAMES"""
loc_names_content = loc_names_content.replace("$TAG$", tag)
loc_names_content = loc_names_content.replace("$NAME$", loc_name)
replace_in_file(
    base_path+r'\localisation\english\countries_l_english.yml',
    "# $NEW_COUNTRY_TOKENHELPER_LOCNAMES",
    loc_names_content
)


# unit_models_copy
unit_models_content = """entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_infantry_entity"
}

entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_infantry_2_entity"
}

entity = {
	clone = "lotr_cavalry_unit_entity"
	name = "$TAG$_light_cavalry_entity"
}

entity = {
	clone = "lotr_cavalry_unit_entity"
	name = "$TAG$_chariot_entity"
}

entity = {
	clone = "lotr_cavalry_unit_entity"
	name = "$TAG$_heavy_cavalry_entity"
}

entity = {
	clone = "lotr_catapult_unit_entity"
	name = "$TAG$_catapult_entity"
}

entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_motorized_entity"
}

entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_mechanized_entity"
}

entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_anti_tank_entity"
}

entity = {
	clone = "lotr_generic_infantry_entity"
	name = "$TAG$_artillery_entity"
}


# $NEW_COUNTRY_TOKENHELPER_UNIT_MODELS"""

unit_models_content = unit_models_content.replace("$TAG$", tag)
replace_in_file(
    base_path+r'\gfx\entities\lotr_units_infantry.asset',
    "# $NEW_COUNTRY_TOKENHELPER_UNIT_MODELS",
    unit_models_content
)



# names
names_content = """#### $NAME$
$TAG$ = {
	male = {
		names = {
			Harbrand Thorwulf Jornard Mornrek Aldwald Alngeir Rodgils Sigvar Bothvith Fridbar Grimstyr Heormund Treorek Galkarl Valohd Hrothrath Heorbald Jornald Arangeir Frothac Sigtan Skoltorn Jartar Hrothrek Alnric Lorsel Stigmoth Otwar Iskin Grimkar Lorbold Eranwine Dagvar Erndhor Nardrek Forngrim Nardvith Magwulf Ferhame Skolrath Widhelm Skolhame Rathhere Randvith Barard Valdstin Sigfast Daghar Waldgár Forngrim Mothac Wulwine Galkald Hartwar Magald Neddan Walddan Barvar Sigkar Jarric Rodbert Thorard Magrand Lydald Igor Ernoric Vulgeir Galgils Grimvir Baldor Jaldam Richelm Fridor Jarnbar Otric Wulthorn Lortar Ordvar Eranbold Fridsel Glumwald Norhyrde Harsorn Jornangar Stigwald Fridac Othkin Randmód Alnbold Raegrek Iwor Valbar Lorvith Glumkin Borgdac Harbert Isfast Hrothhame Fridond Gluthfast
		  }
	}
	female = {
		names = {
			Ulwyn Lyna Venwyn Ulvindira Lifnwyn Jenhild Birntyn Fastbwyn Grimla WaentinaSigwyn Olaeya Gerthbwyn Aervild Solhild Ovinrlin Aernwyn Ulvinbwyn Ovinowyn GaildoraOviwyn Raenrin Ranbyn Iorfyn Kayvild Bruniaen Waenhelda Diswed Magbina Melfirth Kayhild Lifrun Gudrlin Ilinwyn Gudhild Kayaen Odowyn Ethara Rilgarth Velbyn Dyrwinne Ulvintyn Gaillin Hrimla Brerloth Unalaug Sigwed Ethlaug Ingihild Rhonfirth Ranrlin Kyndis Kaynis Aernwyn Waenwyn Salwild Brunia Dinfirth Hallwyn Iorrin Raenwyn Fynvild Odvera Fastowyn Gelava Katda Kathtyn Hunanda Rilginny Katrun Beorngun Brunielde Eyhelda Lifrlin Dyraen Ingieith Treolin Iorhild Berahild Raenwyn Iswyn Dislaug Grimwyn Amalanda Arinewyn Hallaeya Rileva Ethbwyn Magnwyn Jerntira Berangun Dyrhild Jilwed Oddora Gelaen Kynwyn Velnis Iorwyn Domdora Kayhera Ethda Winthrith Hallhild Isrisa Rangifu Berahild Ranvera Gailwyn Beranhelda Harfast Ovivor Beornelde Linwyn Leotwyn Mageva Bognwyn Isvyn Norbi Isowyn Velfrida
		}
	}
	surnames = { "" }
	callsigns = { }
}
# $NEW_COUNTRY_TOKENHELPER_NAMES"""
names_content = names_content.replace("$TAG$", tag)
names_content = names_content.replace("$NAME$", loc_name)
replace_in_file(
    base_path+r'\common\names\00_names.txt',
    "# $NEW_COUNTRY_TOKENHELPER_NAMES",
    names_content
)
