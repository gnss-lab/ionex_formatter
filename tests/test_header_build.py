import pytest
import hashlib
from . import conftest
from ionex_formatter.formatter import IonexFile, IonexMapType, HeaderConfig
from ionex_formatter.spatial import SpatialRange
from datetime import datetime, timedelta

description = [
"Global ionosphere maps for day 362, 2010 (28-12-2010)",       
"",                                                           
"",                                                            
"P1-P2 DCBs(UPC3-BRDC) 362 2010: Bias=  0.000 RMS= 0.851 [ns]",
"                                                            "
]

comment = [
    "TEC values in  0.1 TECUs; 9999 if no value available        ",
    "IGS GPS stations used in the computations:                  "
]

sites = [
    "019b", "ab02", "ab06", "ab09", "ab11", "ab12", "ab13", "ab25", "ab27", "ab33",
    "ab37", "ab41", "ab42", "ab44", "ab45", "ab49", "abmf", "abpo", "ac03", "ac12",
    "ac61", "acor", "acso", "acu5", "adis", "adks", "agmt", "ahid", "aira", "ajac",
    "alac", "albh", "alg3", "alic", "allg", "alon", "alrt", "alth", "amc2", "ankr",
    "antc", "arco", "areq", "arli", "artu", "aspa", "auck", "autf", "baie", "bake",
    "bald", "barh", "bcyi", "bdos", "bell", "bilb", "bjfs", "bla1", "bluf", "boav",
    "bogi", "bogt", "bomj", "brft", "brip", "brmu", "brst", "brus", "bshm", "bsmk",
    "bucu", "buri", "burn", "bysp", "bzrg", "cabl", "cagl", "call", "cand", "cant",
    "cas1", "casc", "cauq", "ccj2", "cedu", "cefe", "chan", "chat", "chiz", "chud",
    "chum", "chur", "cjtr", "ckis", "clrk", "cmbl", "cnmr", "coco", "cola", "copo",
    "cosa", "coyq", "crao", "crar", "crrl", "cuib", "cusv", "daej", "dane", "darw",
    "dav1", "devi", "dgar", "dgjg", "dksg", "drao", "dres", "dubo", "dubr", "dum1",
    "dupt", "ecsd", "eur2", "faa1", "falk", "fall", "fbyn", "flin", "flrs", "func",
    "g101", "g107", "g117", "g124", "g201", "g202", "ganp", "gisb", "glps", "glsv",
    "gmas", "gmma", "goav", "guao", "guat", "harb", "hdil", "helg", "her2", "hil1",
    "hilb", "hlfx", "hmbg", "hnlc", "hob2", "hobu", "hofn", "holm", "howe", "hrst",
    "hua2", "hueg", "hugo", "hvwy", "hyde", "ibiz", "iisc", "impz", "ineg", "invk",
    "iqal", "iqqe", "irkj", "isba", "ispa", "ista", "jct1", "joen", "karr", "kbug",
    "kely", "kerg", "khaj", "khar", "khlr", "kir0", "kiri", "kit3", "kouc", "kour",
    "ksnb", "kunm", "kuuj", "kvtx", "lamp", "lamt", "laut", "lhaz", "lpal", "lpgs",
    "lthw", "mac1", "majb", "mal2", "mana", "mar6", "mara", "marg", "maua", "maw1",
    "mchn", "mdvj", "meri", "mobs", "moiu", "morp", "mtbg", "nain", "nama", "naur",
    "neia", "nium", "nklg", "novm", "nril", "ntus", "nya1", "oax2", "ohi2", "onsa",
    "ouri", "p001", "p038", "p050", "palk", "park", "pece", "pets", "pimo", "pngm",
    "poal", "pohn", "qaar", "qaq1", "qiki", "rabt", "rbay", "rcm7", "reso", "reun",
    "reyk", "riga", "riob", "riop", "sa61", "saga", "sask", "savo", "sch2", "scor",
    "scrz", "sey1", "sg27", "shao", "smm1", "soda", "stj2", "sumk", "suth", "syog",
    "tash", "tehn", "tixg", "tong", "topl", "tow2", "trds", "tro1", "tuva", "ufpr",
    "ulab", "unbj", "vacs", "vanu", "vis0", "vlns", "whit", "whng", "whtm", "will",
    "wind", "wuhn", "xian", "xmis", "yakt", "yell", "yibl", "ykro", "ymer", "zeck"
]

class TestIonexHeaderBuild():

    @pytest.fixture
    def sample_header(self, data_dir):
        lines = []
        with open(data_dir / 'ionex_header.txt', 'r') as f:
            lines = f.readlines()
        return lines
    
    def test_header_validity(self, sample_header):
        assert len(sample_header) == 51
        md5_control = "a0dba3982a59e2b7c9456394a57b4761"
        md5_test = (hashlib.md5("".join(sample_header).encode())).hexdigest()
        assert md5_test == md5_control

    def test_version_set(self):
        formatter = IonexFile()
        formatter.set_version_type_gnss(version=1.0, map_type="I", gnss_type='GPS')
        expected  = ["     1.0            I                   " \
                     "GPS                 IONEX VERSION / TYPE"]
        assert formatter.header["IONEX VERSION / TYPE"] == expected

    def test_comment(self):
        formatter = IonexFile()
        formatter.add_comment(comment)
        formatter.add_comment(comment)
        expected  = [
            "TEC values in  0.1 TECUs; 9999 if no val"  
            "ue available        COMMENT             ", 
            "IGS GPS stations used in the computation" 
            "s:                  COMMENT             ",
            "TEC values in  0.1 TECUs; 9999 if no val"  
            "ue available        COMMENT             ", 
            "IGS GPS stations used in the computation" 
            "s:                  COMMENT             "
        ]
        assert formatter.header["COMMENT"] == expected

    def test_description(self):
        formatter = IonexFile()
        formatter.set_description(description)
        expected  = [
            "Global ionosphere maps for day 362, 2010"  
            " (28-12-2010)       DESCRIPTION         ", 
            "                                        "  
            "                    DESCRIPTION         ",
            "                                        "  
            "                    DESCRIPTION         ",
            "P1-P2 DCBs(UPC3-BRDC) 362 2010: Bias=  0" 
            ".000 RMS= 0.851 [ns]DESCRIPTION         ",
            "                                        " 
            "                    DESCRIPTION         "
    ]
        assert formatter.header["DESCRIPTION"] == expected

    def test_set_sites(self):
        formatter = IonexFile()
        formatter.set_sites(sites[:40])
        expected = [
            "019b ab02 ab06 ab09 ab11 ab12 ab13 ab25 " 
            "ab27 ab33 ab37 ab41 COMMENT             ",
            "ab42 ab44 ab45 ab49 abmf abpo ac03 ac12 "
            "ac61 acor acso acu5 COMMENT             ",
            "adis adks agmt ahid aira ajac alac albh "
            "alg3 alic allg alon COMMENT             ",
            "alrt alth amc2 ankr                     "
            "                    COMMENT             "

        ]
        assert formatter.header["COMMENT"] == expected

    def test_set_end_of_header(self):
        formatter = IonexFile()
        formatter.update_label("END OF HEADER", [])
        expected = [
            "                                        "
            "                    END OF HEADER       "
        ]
        assert formatter.header["END OF HEADER"] == expected
    
    def test_header_build(self, sample_header):
        _sample_header = []
        for line in sample_header:
            if line.endswith("\n"):
                _sample_header.append(line[:-1])
            else:
                _sample_header.append(line[:])
        formatter = IonexFile()
        formatter.set_version_type_gnss(version=1.0, map_type="I", gnss_type='GPS')
        formatter.update_label(
            "PGM / RUN BY / DATE",
            ["tecrms2ionex_4.awk", "UPC-IonSAT", "11/14/18  411UT"]
        )
        formatter.set_description(description)
        formatter.set_epoch_range(
            start=datetime(2010, 12, 28, 0, 0, 0),
            last=datetime(2010, 12, 28, 23, 59, 24)
        )
        formatter.update_label("INTERVAL", [900, ])
        formatter.update_label("# OF MAPS IN FILE", [97, ])
        formatter.update_label("MAPPING FUNCTION", ["COSZ", ])
        formatter.update_label("ELEVATION CUTOFF", [0, ])
        formatter.update_label("# OF STATIONS", [300, ])
        formatter.update_label("# OF SATELLITES", [32, ])
        formatter.update_label("BASE RADIUS", [6371.0, ])
        formatter.update_label("MAP DIMENSION", [2, ])
        formatter.set_spatial_grid(
            lat_range=SpatialRange(87.5, -87.5, -2.5), 
            lon_range=SpatialRange(-180, 180, 5),
            height_range=SpatialRange(450, 450, 0)
        )
        formatter.update_label("EXPONENT", [-1, ])
        formatter.add_comment(comment)
        formatter.set_sites(sites)
        formatter.update_label(
            "START OF AUX DATA", ["DIFFERENTIAL CODE BIASES", ]
        )
        formatter.update_label(
            "END OF AUX DATA", ["DIFFERENTIAL CODE BIASES", ]
        )
        formatter.update_label("END OF HEADER", [])
        order = [
            "IONEX VERSION / TYPE",
            "PGM / RUN BY / DATE",
            "DESCRIPTION",
            "EPOCH OF FIRST MAP",
            "EPOCH OF LAST MAP",
            "INTERVAL",
            "# OF MAPS IN FILE",
            "MAPPING FUNCTION",
            "ELEVATION CUTOFF",
            "# OF STATIONS",
            "# OF SATELLITES",
            "OBSERVABLES USED",
            "BASE RADIUS",
            "MAP DIMENSION",
            "HGT1 / HGT2 / DHGT",
            "LAT1 / LAT2 / DLAT",
            "LON1 / LON2 / DLON",
            "EXPONENT",
            "COMMENT",
            "START OF AUX DATA",
            "END OF AUX DATA",
            "END OF HEADER"
        ]
        formatter.set_header_order(order)
        ordered = [formatter.header[label] for label in formatter.line_order]
        header = list()
        for label_data in ordered:
            header.extend(label_data)
        for header_line, exp_line in zip(header, _sample_header):
            assert header_line == exp_line
        assert header == _sample_header
        assert len(header) == len(sample_header) 
        assert '\n'.join(header) == ''.join(sample_header)

    def test_header_lines_preparation(self, sample_header):
        _sample_header = []
        for line in sample_header:
            if line.endswith("\n"):
                _sample_header.append(line[:-1])
            else:
                _sample_header.append(line[:])
        formatter = IonexFile()
        order = [
            "IONEX VERSION / TYPE",
            "PGM / RUN BY / DATE",
            "DESCRIPTION",
            "EPOCH OF FIRST MAP",
            "EPOCH OF LAST MAP",
            "INTERVAL",
            "# OF MAPS IN FILE",
            "MAPPING FUNCTION",
            "ELEVATION CUTOFF",
            "# OF STATIONS",
            "# OF SATELLITES",
            "OBSERVABLES USED",
            "BASE RADIUS",
            "MAP DIMENSION",
            "HGT1 / HGT2 / DHGT",
            "LAT1 / LAT2 / DLAT",
            "LON1 / LON2 / DLON",
            "EXPONENT",
            "COMMENT",
            "START OF AUX DATA",
            "END OF AUX DATA",
            "END OF HEADER"
        ]
        header_config = HeaderConfig(
            map_type=IonexMapType.TEC,
            pgm = "tecrms2ionex_4.awk",
            run_by = "UPC-IonSAT",
            created_at = datetime(2018, 11, 14, 4, 11, 0),
            first_time = datetime(2010, 12, 28, 0, 0, 0),
            last_time = datetime(2010, 12, 28, 23, 59, 24),
            description = description,
            timestep = timedelta(seconds=900),
            number_of_maps=97,
            elevation_cutoff = 0,
            number_of_stations = 300,
            number_of_satellites = 32,
            sites_names = sites,
            version = "1.0",
            gnss_type = "GPS",
            mapping_function = "COSZ", 
            base_radius = 6371.0,
            latitude_range = SpatialRange(87.5, -87.5, -2.5),
            longitude_range = SpatialRange(-180, 180, 5),
            height_range = SpatialRange(450, 450, 0),
            exponent = -1,
            map_dimensions = 2,
            comment = comment,
            labels_order = order
        )
        header_lines = formatter.get_header_lines(header_config)
        for header_line, exp_line in zip(header_lines, _sample_header):
            assert header_line == exp_line
        assert header_lines == _sample_header
        assert len(header_lines) == len(sample_header) 
        assert '\n'.join(header_lines) == ''.join(sample_header)


            





