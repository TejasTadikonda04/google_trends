import pandas as pd
import re
import os
import json
from datetime import datetime
from difflib import SequenceMatcher

def validate_dates(df, columns):
    for col in columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def clean_region_names(df):
    admin_words = [
        "County", "Province", "State of", "State", "Governorate",
        "Region", "Special Region", "District", "City", "Prefecture", "Oblast"
    ]
    admin_pattern = re.compile(r'\\b(?:' + '|'.join(re.escape(w) for w in admin_words) + r')\\b', re.IGNORECASE)
    df["region_name_cleaned"] = df["region_name"].apply(
        lambda x: re.sub(r"\\s+", "", admin_pattern.sub("", x)) if isinstance(x, str) else x
    )
    return df

def apply_manual_fixes(df):
    # === Step 2: Manual corrections (region_fix_map) ===
    region_fix_map = {
    "AutonomousofBuenosAires": "BuenosAires",
    "Federal": "DistritoFederal",
    "YukonTerritory": "Yukon",
    "Delhi": "NCTofDelhi",
    "Free": "FreeState",
    "Jeju-do": "Jeju",
    "Taoyuan": "Taiwan",
    "England": "NA",
    "Jonkoping": "Jönköping",
    "Bangkok": "BangkokMetropolis",
    # --- Austria ---
    "Carinthia": "Kärnten",
    "LowerAustria": "Niederösterreich",
    "UpperAustria": "Oberösterreich",
    "Styria": "Steiermark",
    "Vienna": "Wien",


    # --- Belgium ---
    "Flanders": "Vlaanderen",
    "Brussels": "Bruxelles",


    # --- Chile ---
    "XIRegión": "AyséndelGeneralIbañezdelCam",
    "O'Higgins": "LibertadorGeneralBernardoO'Hi",


    # --- Colombia ---
    "CaucaDepartment": "Cauca",
    "AmazonasDepartment": "Amazonas",
    "Bogota": "BogotáD.C.",
    "SantanderDepartment": "Santander",


    # --- Denmark ---
    "NorthDenmark": "Nordjylland",
    "CapitalofDenmark": "Hovedstaden",
    "CentralDenmark": "Midtjylland",
    "Zealand": "Sjælland",


    # --- Germany ---
    "LowerSaxony": "Niedersachsen",
    "Bavaria": "Bayern",
    "Saxony": "Sachsen",
    "NorthRhine-Westphalia": "Nordrhein-Westfalen",
    "Thuringia": "Thüringen",
    "Rhineland-Palatinate": "Rheinland-Pfalz",
    "Saxony-Anhalt": "Sachsen-Anhalt",


    # --- Israel ---
    "North": "HaZafon",
    "South": "HaDarom",
    "Center": "HaMerkaz",
    # --- Italy ---
    "Aosta": "Valled'Aosta",
    "Tuscany": "Toscana",
    "Sardinia": "Sardegna",
    "Trentino-AltoAdige/SouthTyrol": "Trentino-AltoAdige",


    # --- Malaysia ---
    "LabuanFederalTerritory": "Labuan",
    "FederalTerritoryofKualaLumpur": "KualaLumpur",
    "Malacca": "Melaka",
    "Penang": "PulauPinang",  # Correct match is Pulau Pinang, not Pahang


    # --- Netherlands ---
    "SouthHolland": "NA",
    "Friesland": "Fryslân",  # Flevoland is wrong match, actual is correct


    # --- Saudi Arabia ---
    "NorthernBorders": "AlḤudūdashShamāliyah",
    "Eastern": "AshSharqīyah",
    "Aseer": "'Asir",
    "Hail": "Ḥaʼil",
    "Riyadh": "ArRiyad",


     # --- Czech Republic ---
    "SouthBohemian": "Jihočeský",
    "CentralBohemian": "Středočeský",
    "SouthMoravian": "Jihomoravský",
    "ÚstínadLabem": "Ústecký",
    "HradecKrálové": "Královéhradecký",
    "Moravian-Silesian": "Moravskoslezský",
    "Zlin": "Zlínský",
    "Vysocina": "KrajVysočina",
    "KarlovyVary": "Karlovarský",
    "Plzeň": "Plzeňský",


    # --- Spain ---
    "BasqueCountry": "PaísVasco",
    "Navarre": "ComunidadForaldeNavarra",
    "ValencianCommunity": "ComunidadValenciana",
    "BalearicIslands": "IslasBaleares",
    "CanaryIslands": "IslasCanarias",
    "ofMurcia": "RegióndeMurcia",
    "Ceuta": "CeutayMelilla",
    "Melilla": "CeutayMelilla",
    "Asturias": "PrincipadodeAsturias",
    "Catalonia": "Cataluña",
    "CommunityofMadrid": "ComunidaddeMadrid",
    "Andalusia": "Andalucía",


    # --- Turkey ---
    "Ağrı": "Agri",
    "Afyonkarahisar": "Afyon",  # matched to Ankara, but Afyonkarahisar exists
    "Muş": "Mus",
    "Şırnak": "Sirnak",
    "Kahramanmaraş": "K.Maras",  # fix spelling to match your dataset
    "Kırıkkale": "Kirikkale",
    "Çankırı": "Cankiri",  # assuming the JSON doesn't have diacritics
    "Kırşehir": "Kirsehir",
    "Uşak": "Usak",
    "Şanlıurfa": "Sanliurfa",


        # --- Poland ---
    "WestPomeranianVoivodeship": "Zachodniopomorskie",
    "PomeranianVoivodeship": "Pomorskie",
    "SilesianVoivodeship": "Śląskie",
    "LowerSilesianVoivodeship": "Dolnośląskie",
    "Kuyavian-PomeranianVoivodeship": "Kujawsko-Pomorskie",
    "GreaterPolandVoivodeship": "Wielkopolskie",
    "LesserPolandVoivodeship": "Małopolskie",
    "MasovianVoivodeship": "Mazowieckie",
    "OpoleVoivodeship": "Opolskie",
    "ŁódźVoivodeship": "Łódzkie",
    "LublinVoivodeship": "Lubelskie",
    "Warmian-MasurianVoivodeship": "Warmińsko-Mazurskie",
    "LubuszVoivodeship": "Lubuskie",
    "PodlaskieVoivodeship": "Podlaskie",
    "PodkarpackieVoivodeship": "Podkarpackie",


    # --- Switzerland ---
    "CantonofUri": "Uri",
    "CantonofZug": "Zug",
    "Grisons": "Graubünden",  # 'Grisons' is French, but GeoJSON likely uses German
    "CantonofBern": "Bern",
    "CantonofJura": "Jura",
    "CantonofGlarus": "Glarus",
    "CantonofSchwyz": "Schwyz",
    "CantonofFribourg": "Fribourg",
    "CantonofObwalden": "Obwalden",
    "Geneva": "Genève",
    "CantonofNeuchâtel": "Neuchâtel",
    "CantonofSolothurn": "Solothurn",
    "CantonofSchaffhausen": "Schaffhausen",
    "AppenzellOuterRhodes": "AppenzellAusserrhoden",


        # --- Finland ---
    "Pirkanmaa": "WesternFinland",
    "Uusimaa": "SouthernFinland",
    "NorthKarelia": "EasternFinland",
    "Kymenlaakso": "SouthernFinland",
    "PäijänneTavastia": "SouthernFinland",
    "TavastiaProper": "SouthernFinland",
    "Satakunta": "WesternFinland",
    "Kainuu": "Oulu",
    "CentralOstrobothnia": "WesternFinland",
    "SouthKarelia": "SouthernFinland",
    "NorthernOstrobothnia": "Oulu",
    "Ostrobothnia": "WesternFinland",
    "NorthernSavonia": "EasternFinland",
    "SouthernOstrobothnia": "WesternFinland",
    "CentralFinland": "WesternFinland",
    "SouthernSavonia": "EasternFinland",


    # --- France ---
    "Languedoc-Roussillon": "Occitanie",
    "Picardy": "Hauts-de-France",
    "Limousin": "Nouvelle-Aquitaine",
    "Poitou-Charentes": "Nouvelle-Aquitaine",
    "Midi-Pyrénées": "Occitanie",
    "Champagne-Ardenne": "GrandEst",
    "Alsace": "GrandEst",
    "Burgundy": "Bourgogne-Franche-Comté",
    "Nord-Pas-de-Calais": "Hauts-de-France",
    "Auvergne": "Auvergne-Rhône-Alpes",
    "Lorraine": "GrandEst",
    "Brittany": "Bretagne",
    "LowerNormandy": "Normandie",
    "UpperNormandy": "Normandie",
    "Rhone-Alpes": "Auvergne-Rhône-Alpes",
    "Aquitaine": "Nouvelle-Aquitaine",
    "Corsica": "Corse",
    "Franche-Comté": "Bourgogne-Franche-Comté",


    "SOCCSKSARGEN": "SouthCotabato",        # Region XII
    "MIMAROPA": "Palawan",                  # Region IV-B
    "CordilleraAdministrative": "Ifugao",   # CAR
    "AutonomousinMuslimMindanao": "Maguindanao",  # ARMM (now BARMM)
    "CentralLuzon": "Pampanga",             # Region III
    "CentralVisayas": "Cebu",               # Region VII
    "WesternVisayas": "Iloilo",             # Region VI
    "Calabarzon": "Batangas",               # Region IV-A
    "Bicol": "Albay",                       # Region V
    "Davao": "DavaodelSur",                 # Region XI
    "Caraga": "AgusandelNorte",             # Region XIII
    "NorthernMindanao": "MisamisOriental",  # Region X
    "EasternVisayas": "Leyte",              # Region VIII
    "CagayanValley": "Cagayan",             # Region II
    "ZamboangaPeninsula": "ZamboangaSibugay",  # Region IX
    "MetroManila": "MetropolitanManila",


    "Luxor": "AlUqsur",
    "NewValley": "AlWadiAlJadid",
    "RedSea": "AlBahrAlAhmar",
    "Damietta": "Dumyat",
    "Suez": "AsSuways",
    "NorthSinai": "ShamalSina'",
    "SouthSinai": "JanubSina'",
    "Cairo": "AlQahirah",
    "Menia": "AlMinya",
    "Menofia": "AlMinufiyah",
    "Giza": "AlJizah",
    "ElBeheira": "AlBuhayrah",
    "Sohag": "Suhaj",
    "PortSaid": "BurSa`id",
    "KafrElSheikh": "KafrashShaykh",
    "Alexandria": "AlIskandariyah",
    "BeniSuef": "BaniSuwayf",
    "Dakahlia": "AdDaqahliyah",
    "Faiyum": "AlFayyum",
    "Assiut": "Asyut",
    "Qena": "Qina",
    "Ismailia": "AlIsma`iliyah",
    "Gharbia": "AlGharbiyah",


    "SpecialCapitalofJakarta": "JakartaRaya",
    "CentralJava": "JawaTengah",
    "EastJava": "JawaTimur",
    "WestJava": "JawaBarat",
    "RiauIslands": "KepulauanRiau",
    "SouthEastSulawesi": "SulawesiTenggara",
    "NorthSumatra": "SumateraUtara",
    "SouthSumatra": "SumateraSelatan",
    "CentralSulawesi": "SulawesiTengah",
    "WestSumatra": "SumateraBarat",
    "NorthSulawesi": "SulawesiUtara",
    "SouthSulawesi": "SulawesiSelatan",
    "WestSulawesi": "SulawesiBarat",
    "CentralKalimantan": "KalimantanTengah",
    "NorthKalimantan": "KalimantanUtara",
    "SouthKalimantan": "KalimantanSelatan",
    "EastKalimantan": "KalimantanTimur",
    "WestKalimantan": "KalimantanBarat",
    "NorthMaluku": "MalukuUtara",
    "WestPapua": "PapuaBarat",
    "EastNusaTenggara": "NusaTenggaraTimur",
    "WestNusaTenggara": "NusaTenggaraBarat",


    "Kyivs'ka": "KievCity",            # Kyiv Oblast
    "Sums'ka": "Sumy",
    "Rivnens'ka": "Rivne",
    "Volyns'ka": "Volyn",
    "Kyiv": "Kiev",                # The city of Kyiv (alternate name appears in GeoJSON)
    "Mykolaivs'ka": "Mykolayiv",
    "Cherkas'ka": "Cherkasy",
    "Khersons'ka": "Kherson",
    "Chernivets'ka": "Chernivtsi",
    "Zakarpats'ka": "Zakarpattia",


    "DaNang": "ĐàNẵng",
    "Hanoi": "HàNội",                      # Note: originally matched to HàGiang, should be HàNội
    "DakNong": "ĐắkNông",
    "BinhDinh": "BìnhĐịnh",
    "DienBien": "ĐiệnBiên",
    "HaiDuong": "HảiDương",
    "Haiphong": "HảiPhòng",
    "BinhDuong": "BìnhDương",
    "BinhPhuoc": "BìnhPhước",
    "CanTho": "CầnThơ",
    "HaTinh": "HàTĩnh",
    "PhuTho": "PhúThọ",
    "YenBai": "YênBái",
    "BaRia-VungTau": "BàRịa-VũngTàu",
    "BacLieu": "BạcLiêu",
    "DongNai": "ĐồngNai",
    "HoaBinh": "HoàBình",
    "HungYen": "HưngYên",
    "LangSon": "LạngSơn",
    "NamDinh": "NamĐịnh",
    "KhanhHoa": "KhánhHòa",
    "SocTrang": "SócTrăng",
    "ThaiBinh": "TháiBình",
    "ThuaThienHue": "ThừaThiênHuế",
    "VinhPhuc": "VĩnhPhúc",
    "BinhThuan": "BìnhThuận",
    "HoChiMinh": "HồChíMinh",
    "QuangBinh": "QuảngBình",
    "QuangNgai": "QuảngNgãi"

}

    df["region_name_final"] = df["region_name_cleaned"].apply(
        lambda x: region_fix_map.get(x, x)
    )
    return df

def perform_fuzzy_matching(df):
    iso3_mapping = {
        "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT", "Belgium": "BEL", "Brazil": "BRA",
        "Canada": "CAN", "Chile": "CHL", "Colombia": "COL", "Czech Republic": "CZE", "Denmark": "DNK",
        "Egypt": "EGY", "Finland": "FIN", "France": "FRA", "Germany": "DEU", "Hungary": "HUN",
        "India": "IND", "Indonesia": "IDN", "Israel": "ISR", "Italy": "ITA", "Japan": "JPN",
        "Malaysia": "MYS", "Mexico": "MEX", "Netherlands": "NLD", "New Zealand": "NZL",
        "Nigeria": "NGA", "Norway": "NOR", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
        "Romania": "ROU", "Saudi Arabia": "SAU", "South Africa": "ZAF", "South Korea": "KOR",
        "Spain": "ESP", "Sweden": "SWE", "Switzerland": "CHE", "Taiwan": "TWN", "Thailand": "THA",
        "Turkey": "TUR", "Ukraine": "UKR", "United Kingdom": "GBR", "Vietnam": "VNM"
    }
    def get_best_match(name, choices):
        best_match = max(choices, key=lambda x: SequenceMatcher(None, name, x).ratio())
        score = SequenceMatcher(None, name, best_match).ratio()
        return best_match, score

    poor_matches = []
    for country, iso3 in iso3_mapping.items():
        json_path = f"Downloads/Country_Regions/gadm41_{iso3}_1.json"
        if not os.path.exists(json_path):
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        geojson_regions = sorted(
            feature["properties"]["NAME_1"].replace(" ", "") for feature in geojson_data["features"]
        )

        country_regions = df[df["country_name"] == country]["region_name_final"].dropna().unique()
        for region in sorted(country_regions):
            if region is None:
                continue
            best_match, score = get_best_match(region, geojson_regions)
            if score < 0.80:
                poor_matches.append({
                    "country": country,
                    "region_in_dataset": region,
                    "geojson_best_match": best_match,
                    "similarity_score": round(score, 3)
                })

    poor_matches_df = pd.DataFrame(poor_matches)
    if not poor_matches_df.empty and "country" in poor_matches_df.columns:
        counts = poor_matches_df.groupby("country").size().reset_index(name="low_similarity_count")
        print(counts)
    else:
        print("No poor matches found or 'country' column missing.")
        
def clean_data(df):
    df = validate_dates(df, ['week', 'refresh_date'])
    df = clean_region_names(df)
    df = apply_manual_fixes(df)
    perform_fuzzy_matching(df)
    return df

if __name__ == "__main__":
    df = pd.read_csv("actualDataTeamProject.csv")
    df = clean_data(df)

    print("NaN values per column:\n", df.isna().sum())

    # Date validation details
    date_validation = {
        col: {
            'valid': df[col].notna().all(),
            'invalid_entries': df[df[col].isna()][col].tolist()
        }
        for col in ['week', 'refresh_date']
    }
    print(date_validation)

    # Country name/code mismatches
    country_reference = pd.DataFrame({
        'country_name': ['Brazil', 'Belgium', 'India', 'Japan', 'United Kingdom', 'Indonesia',
                         'Thailand', 'Norway', 'South Korea', 'Italy', 'Malaysia', 'Portugal',
                         'Netherlands', 'Poland', 'Vietnam', 'Mexico', 'Nigeria', 'South Africa',
                         'Austria', 'Chile', 'Finland', 'Philippines', 'Canada', 'Spain', 'Germany',
                         'Colombia', 'Argentina', 'Taiwan', 'Czech Republic', 'New Zealand', 'France',
                         'Switzerland', 'Ukraine', 'Australia', 'Sweden', 'Saudi Arabia', 'Turkey',
                         'Egypt', 'Romania', 'Hungary', 'Denmark', 'Israel'],
        'country_code': ['BR', 'BE', 'IN', 'JP', 'GB', 'ID', 'TH', 'NO', 'KR', 'IT', 'MY', 'PT', 'NL', 'PL',
                         'VN', 'MX', 'NG', 'ZA', 'AT', 'CL', 'FI', 'PH', 'CA', 'ES', 'DE', 'CO', 'AR', 'TW',
                         'CZ', 'NZ', 'FR', 'CH', 'UA', 'AU', 'SE', 'SA', 'TR', 'EG', 'RO', 'HU', 'DK', 'IL']
    })
    merged = df.merge(country_reference, on='country_name', how='left', suffixes=('', '_ref'))
    mismatches = merged[merged['country_code'] != merged['country_code_ref']]
    print("Mismatched rows:")
    print(mismatches[['country_name', 'country_code', 'country_code_ref']])

    df.to_csv("google_trends_cleaned.csv", index=False)
    print("Data cleaned and saved to google_trends_cleaned.csv")


