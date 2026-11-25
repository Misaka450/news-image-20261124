"""Verified story dataset for Tuesday 24 November 2026 (UTC).

Every entry is sourced strictly from FACTS.md. Region counts and total story
counts are computed programmatically by the renderer from STORIES.
"""

EDITION_DATE = "TUESDAY 24 NOVEMBER 2026"
EDITION_SHORT = "TUE 24 NOV 2026"
MASTHEAD_LEFT = "THE WORLD ON ONE PAGE"
MASTHEAD_CENTER = "GLOBAL PRINT EDITION · UTC"

REGION_ORDER = ["EU", "AP", "ME", "AM", "AF", "CL", "SE"]

REGION_LABELS = {
    "EU": "EUROPE & UKRAINE",
    "AP": "ASIA-PACIFIC",
    "ME": "MIDDLE EAST",
    "AM": "AMERICAS",
    "AF": "AFRICA",
    "CL": "CLIMATE & HEALTH",
    "SE": "SEAS & TRADE",
}

NUMBERS_STRIP = [
    {"value": "+9%", "label": "Taiex close (Kospi +7%)", "hot": True},
    {"value": "44", "label": "Injured, Zaporizhzhia", "hot": True},
    {"value": "11", "label": "Injured, Riyadh tower", "hot": True},
    {"value": "$41bn", "label": "Sanofi buys Insmed", "hot": False},
    {"value": "5.6", "label": "Nepal quake near Tibet", "hot": False},
    {"value": "1,700km", "label": "Libya USV strike (claim)", "hot": True},
]

UTC_CLOCK = [
    {"time": "01:32", "event": "M5.6 quake jolts E. Nepal (07:17 loc)"},
    {"time": "03:15", "event": "Russian jet drone 20km in Poland"},
    {"time": "07:52", "event": "Ulleung air-raid alert (3 min)"},
    {"time": "09:00", "event": "Tokyo reopens after 89.5h break"},
    {"time": "10:40", "event": "Two tankers ablaze in Hormuz"},
    {"time": "13:20", "event": "Jabalia water-well strike (UNRWA)"},
    {"time": "15:30", "event": "COP31 Antalya collapses, no deal"},
    {"time": "18:00", "event": "Nvidia reinstates Jensen Huang"},
]

LEAD_STORY = {
    "id": "nvidia_huang",
    "region": "AM",
    "kicker": "LEAD STORY · MARKETS & TECH · AMERICAS / ASIA-PACIFIC",
    "label": "Nvidia Reinstates Jensen Huang After 11 Days; Asia Markets Roar",
    "deck": (
        "Nvidia's board unanimously restores CEO Jensen Huang 11 days after he quit "
        "over an affairs scandal (Alice Huang / Megaspeed Int'l). Trump claims credit "
        "(\"I convinced them\"). Asian markets surge: Taiwan's Taiex closes +9%, "
        "Seoul's Kospi +7%, and Tokyo reopens after an 89.5h holiday."
    ),
    "source": "AP News, Reuters, NPR, HKFP, Clarin",
    "status": "CONFIRMED",
    "illustration": "candlesticks",
}

# 31 brief stories + 1 LEAD_STORY = 32 stories total across 7 regions.
# Region counts computed from [LEAD_STORY] + BRIEF_STORIES:
# EU: 5, AP: 5, ME: 5, AM: 5 (1 lead + 4 briefs), AF: 4, CL: 4, SE: 4 -> 32 total.
BRIEF_STORIES = [
    # --- TOP-RIGHT COL 3: SEAS & TRADE (top 2) ---
    {
        "id": "hormuz_tankers",
        "slot": "top_c3",
        "region": "SE",
        "label": "Two oil tankers hit mines, ablaze in Hormuz",
        "detail": "Vessels had US air escort; Iran's IRGC blames sea mines (cause: claim).",
        "source": "Express Tribune, Haaretz",
        "status": "CONFIRMED",
        "illustration": "tanker_fire",
    },
    {
        "id": "libya_usv",
        "slot": "top_c3",
        "region": "SE",
        "label": "Kyiv claims 1,700km Libya strike sank ship",
        "detail": "SBU says drone mothership launched 7 USVs that sank corvette Merkuriy in Benghazi.",
        "source": "Kyiv Post, Meduza",
        "status": "CLAIM",
        "illustration": "shipwreck",
    },
    # --- TOP-RIGHT COL 4: EUROPE & UKRAINE (top 2) ---
    {
        "id": "poland_drone",
        "slot": "top_c4",
        "region": "EU",
        "label": "Russian jet drone flies 20km into Poland",
        "detail": "Overnight 23-24 Nov incursion; Warsaw calls it deliberate; NATO sends AWACS.",
        "source": "Ukrainska Pravda, Kyiv Post",
        "status": "CONFIRMED",
        "illustration": "jet_drone",
    },
    {
        "id": "zaporizhzhia_hit",
        "slot": "top_c4",
        "region": "EU",
        "label": "Zaporizhzhia block hit: 2 dead, 44 hurt",
        "detail": "Russian strike tears five-storey building; separate FPV drone injures a woman.",
        "source": "Kyiv Independent, Meduza",
        "status": "CONFIRMED",
        "illustration": "split_building",
    },
    # --- LOWER COL 1: EUROPE & UKRAINE (3) + AMERICAS (4) ---
    {
        "id": "magyar_zelensky",
        "slot": "col1",
        "region": "EU",
        "label": "Hungary's Magyar meets Zelensky in Ukraine",
        "detail": "First Hungarian PM visit since 2015, in Zakarpattia; gas-supply deals agreed.",
        "source": "Ukrainska Pravda, Kyiv Indep.",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "germany_delta",
        "slot": "col1",
        "region": "EU",
        "label": "Germany to build drones & join Kyiv Delta",
        "detail": "Minister Pistorius pledges Ukraine drone output and first partner use of Delta.",
        "source": "Ukrainska Pravda, Kyiv Post",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "putin_refineries",
        "slot": "col1",
        "region": "EU",
        "label": "Putin protests Ukraine oil-refinery strikes",
        "detail": "Cites Trump request and vows retaliation; Kyiv's FM tells him to end the war.",
        "source": "Ukrainska Pravda",
        "status": "REPORTED",
        "illustration": None,
    },
    {
        "id": "trump_appeals",
        "slot": "col1",
        "region": "AM",
        "label": "Appeals court opens path to void verdict",
        "detail": "Federal panel gives Trump a legal route to erase his hush-money conviction.",
        "source": "AP News, Egypt Independent",
        "status": "CONFIRMED",
        "illustration": "scales",
    },
    {
        "id": "sanofi_insmed",
        "slot": "col1",
        "region": "AM",
        "label": "Sanofi agrees to buy Insmed for $41bn",
        "detail": "French drugmaker strikes $41bn takeover of US biopharma firm Insmed.",
        "source": "Reuters, Daily Sabah",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "house_1789_probe",
        "slot": "col1",
        "region": "AM",
        "label": "House Dems widen 1789 Capital access probe",
        "detail": "Rep. Raskin expands inquiry into Trump Jr.-linked fund and govt access.",
        "source": "AP News, The Hill, NPR",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "colombia_cartagena",
        "slot": "col1",
        "region": "AM",
        "label": "Colombia: Cartagena siege & car bomb",
        "detail": "Gunmen hold two dozen in supermarket; separate blast injures 25 elsewhere.",
        "source": "The Guardian, El Pais, Folha",
        "status": "CONFIRMED",
        "illustration": None,
    },
    # --- LOWER COL 2: ASIA-PACIFIC (5) + SEAS & TRADE (2) ---
    {
        "id": "shenzhou_pakistan",
        "slot": "col2",
        "region": "AP",
        "label": "Pakistan names Zeeshan Ali for Shenzhou-24",
        "detail": "First Pakistani astronaut & first foreign visitor to China's Tiangong station.",
        "source": "Dawn, Express Tribune",
        "status": "CONFIRMED",
        "illustration": "rocket_dock",
    },
    {
        "id": "nepal_quake",
        "slot": "col2",
        "region": "AP",
        "label": "M5.6 quake jolts eastern Nepal at 07:17",
        "detail": "Near Tibet border; felt in India, Bhutan and Bangladesh; no deaths reported.",
        "source": "Kathmandu Post, Himalayan Times",
        "status": "CONFIRMED",
        "illustration": "quake_ridge",
    },
    {
        "id": "ulleung_jets",
        "slot": "col2",
        "region": "AP",
        "label": "S. Korea scrambles jets; Ulleung alert",
        "detail": "Russian aircraft trigger 3-min 07:52 air-raid alert; no airspace breach.",
        "source": "Yonhap / SBS via Meduza",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "solomon_china",
        "slot": "col2",
        "region": "AP",
        "label": "Solomon Islands to end 2022 China pact",
        "detail": "Tells Beijing it will terminate security deal and seek an Australia treaty.",
        "source": "SMH, Daily Maverick",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "chen_jining_probe",
        "slot": "col2",
        "region": "AP",
        "label": "China probes Shanghai boss Chen Jining",
        "detail": "Fourth Politburo member to fall since 2025 in Beijing's anti-graft drive.",
        "source": "Reuters",
        "status": "REPORTED",
        "illustration": None,
    },
    {
        "id": "us_tariffs",
        "slot": "col2",
        "region": "SE",
        "label": "US finalising new tariffs on China & EU",
        "detail": "Washington prepares fresh duties targeting China, EU and a dozen nations.",
        "source": "El Pais, Folha",
        "status": "CONFIRMED",
        "illustration": "cargo_crate",
    },
    {
        "id": "iran_50_tankers",
        "slot": "col2",
        "region": "SE",
        "label": "WSJ: Iran eyed in threats on 50 tankers",
        "detail": "Suspected cyberattacks & bomb threats; US official says no evidence found.",
        "source": "Haaretz / WSJ",
        "status": "CLAIM",
        "illustration": None,
    },
    # --- LOWER COL 3: MIDDLE EAST (5) + CLIMATE & HEALTH (2) ---
    {
        "id": "riyadh_tower",
        "slot": "col3",
        "region": "ME",
        "label": "Houthi strike hits Riyadh tower; 11 hurt",
        "detail": "Second hit in a week on tallest financial tower (Saudi Civil Defence).",
        "source": "Daily Sabah, Asharq Al-Awsat",
        "status": "CONFIRMED",
        "illustration": "tower_burst",
    },
    {
        "id": "gaza_abu_nahl",
        "slot": "col3",
        "region": "ME",
        "label": "Gaza security chief killed in strike",
        "detail": "Israeli strike kills Mohamed Abu Nahl in Gaza City; Hamas claims war crime.",
        "source": "Palinfo, Al-Quds",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "jabalia_well",
        "slot": "col3",
        "region": "ME",
        "label": "UNRWA staffer killed at Jabalia well",
        "detail": "Strike on water well in northern Gaza camp leaves one dead and three hurt.",
        "source": "Al-Quds",
        "status": "REPORTED",
        "illustration": "water_well",
    },
    {
        "id": "eisenkot_knesset",
        "slot": "col3",
        "region": "ME",
        "label": "Eisenkot moves to repeal judicial laws",
        "detail": "Backed by 67 MKs; set to tell Pres. Herzog next week he formed a govt.",
        "source": "Jerusalem Post, Daily Sabah",
        "status": "CONFIRMED",
        "illustration": "parliament",
    },
    {
        "id": "idf_mosquito",
        "slot": "col3",
        "region": "ME",
        "label": "IDF probes 'Mosquito Protocol' shields",
        "detail": "Inquiry into Palestinians used as shields; Katz demands KAN pull report.",
        "source": "Haaretz, Jerusalem Post",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "england_heat",
        "slot": "col3",
        "region": "CL",
        "label": "England heat deaths hit record, up 76%",
        "detail": "Annual heat toll jumps 76% above previous national peak, Sky News reports.",
        "source": "Sky News",
        "status": "REPORTED",
        "illustration": None,
    },
    {
        "id": "oxfam_gaza_env",
        "slot": "col3",
        "region": "CL",
        "label": "Oxfam warns of Gaza soil & water crisis",
        "detail": "Cites long-term environmental catastrophe from polluted soil, water and air.",
        "source": "Al-Quds",
        "status": "REPORTED",
        "illustration": None,
    },
    # --- LOWER COL 4: CLIMATE & HEALTH (2) + AFRICA (4) ---
    {
        "id": "cop31_antalya",
        "slot": "col4",
        "region": "CL",
        "label": "COP31 in Antalya collapses without deal",
        "detail": "Longest COP (2 days over) ends as EU & ~100 states reject weak fossil text.",
        "source": "Reuters, France 24, The Hindu",
        "status": "CONFIRMED",
        "illustration": "gavel",
    },
    {
        "id": "un_women_violence",
        "slot": "col4",
        "region": "CL",
        "label": "UN: domestic violence kills ~5 women/hr",
        "detail": "Global UN figures show nearly five women killed every hour worldwide.",
        "source": "Folha / UN",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "ituri_ebola",
        "slot": "col4",
        "region": "AF",
        "label": "Ituri clashes trap DR Congo Ebola teams",
        "detail": "Fighting near hospital; WHO says toll far higher than official Bunia tallies.",
        "source": "UN News, Daily Sabah",
        "status": "CONFIRMED",
        "illustration": "medical_arc",
    },
    {
        "id": "senegal_afcon",
        "slot": "col4",
        "region": "AF",
        "label": "Senegal reinstated as 2025 AFCON winners",
        "detail": "CAS upholds Senegal's appeal to restore title; Morocco protests the ruling.",
        "source": "AllAfrica, Daily Nation",
        "status": "CONFIRMED",
        "illustration": "trophy",
    },
    {
        "id": "drc_plane_m23",
        "slot": "col4",
        "region": "AF",
        "label": "DR Congo plane missing; M23 claims hit",
        "detail": "Kinshasa reports aircraft missing; rebels claim shootdown; Uganda denies role.",
        "source": "BBC, AllAfrica",
        "status": "CONFIRMED",
        "illustration": None,
    },
    {
        "id": "ethiopia_alamata",
        "slot": "col4",
        "region": "AF",
        "label": "Amnesty flags Ethiopia Alamata shelling",
        "detail": "Rights group warns artillery strikes on Alamata may amount to war crimes.",
        "source": "Al-Quds",
        "status": "REPORTED",
        "illustration": None,
    },
]

ALL_STORIES = [LEAD_STORY] + BRIEF_STORIES

DATE_CHECK_EXCLUDED = [
    "Democrats win US House — reported 22-23 Nov",
    "COP31 rift began 22-23 Nov (final gavel Tue 24)",
    "Jensen Huang resignation — 11 days earlier (13 Nov)",
    "US loses measles-elimination status — prior week",
]

READERS_KEY = (
    "CONFIRMED = 2+ outlets or officials  ·  "
    "REPORTED = single credible desk  ·  "
    "CLAIM = one party's statement / state media"
)
