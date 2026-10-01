"""
Authoritative Geographic and Scenario Master Dataset for Suryanagar, India.
All geographic entities, road segments, shelters, and resource staging posts are defined here.
"""

SURYANAGAR_CENTER = {"lat": 16.5062, "lng": 80.6480, "name": "Suryanagar Municipal Corporation"}

SECTORS = [
    {"code": "SEC-1", "name": "Riverbank Lowland Ward", "lat": 16.5120, "lng": 80.6420, "risk": "High Flood Inundation"},
    {"code": "SEC-2", "name": "Coastal Fishermen Esplanade", "lat": 16.4950, "lng": 80.6650, "risk": "Cyclone Storm Surge"},
    {"code": "SEC-3", "name": "Old Town Heritage Bazaar", "lat": 16.5070, "lng": 80.6480, "risk": "Earthquake Masonry Collapse"},
    {"code": "SEC-4", "name": "Northern Ridge Pine Reserve", "lat": 16.5350, "lng": 80.6300, "risk": "Wildfire Hazard Corridor"},
    {"code": "SEC-5", "name": "Hillside Ghati Pass", "lat": 16.5250, "lng": 80.6150, "risk": "Landslide & Slope Failure"},
    {"code": "SEC-6", "name": "District Hospital & EOC Enclave", "lat": 16.5020, "lng": 80.6350, "risk": "Operational Core"},
    {"code": "SEC-7", "name": "Industrial Logistics Depot", "lat": 16.4850, "lng": 80.6200, "risk": "Staging & Supply Base"},
    {"code": "SEC-8", "name": "South Stadium Complex", "lat": 16.4800, "lng": 80.6550, "risk": "Mega Shelter Zone"}
]

ROAD_NETWORK = [
    {
        "code": "RS-01",
        "name": "Delta Embankment Arterial",
        "road_type": "ARTERIAL",
        "start_node": "SEC-1",
        "end_node": "SEC-3",
        "start_lat": 16.5120,
        "start_lng": 80.6420,
        "end_lat": 16.5070,
        "end_lng": 80.6480,
        "length_km": 2.4,
        "speed_limit_kmh": 40.0
    },
    {
        "code": "RS-02",
        "name": "Coastal Highway NH-216",
        "road_type": "HIGHWAY",
        "start_node": "SEC-2",
        "end_node": "SEC-8",
        "start_lat": 16.4950,
        "start_lng": 80.6650,
        "end_lat": 16.4800,
        "end_lng": 80.6550,
        "length_km": 3.8,
        "speed_limit_kmh": 65.0
    },
    {
        "code": "RS-03",
        "name": "Old Town Central Spine",
        "road_type": "LOCAL",
        "start_node": "SEC-3",
        "end_node": "SEC-6",
        "start_lat": 16.5070,
        "start_lng": 80.6480,
        "end_lat": 16.5020,
        "end_lng": 80.6350,
        "length_km": 1.9,
        "speed_limit_kmh": 35.0
    },
    {
        "code": "RS-04",
        "name": "Northern Ridge Spine",
        "road_type": "ARTERIAL",
        "start_node": "SEC-4",
        "end_node": "SEC-5",
        "start_lat": 16.5350,
        "start_lng": 80.6300,
        "end_lat": 16.5250,
        "end_lng": 80.6150,
        "length_km": 4.1,
        "speed_limit_kmh": 45.0
    },
    {
        "code": "RS-05",
        "name": "Ghat Mountain Pass Road",
        "road_type": "GHAT_ROAD",
        "start_node": "SEC-5",
        "end_node": "SEC-6",
        "start_lat": 16.5250,
        "start_lng": 80.6150,
        "end_lat": 16.5020,
        "end_lng": 80.6350,
        "length_km": 5.2,
        "speed_limit_kmh": 30.0
    },
    {
        "code": "RS-06",
        "name": "District Hospital Flyover Link",
        "road_type": "HIGHWAY",
        "start_node": "SEC-6",
        "end_node": "SEC-3",
        "start_lat": 16.5020,
        "start_lng": 80.6350,
        "end_lat": 16.5070,
        "end_lng": 80.6480,
        "length_km": 1.7,
        "speed_limit_kmh": 50.0
    },
    {
        "code": "RS-07",
        "name": "Industrial Freight Corridor",
        "road_type": "HIGHWAY",
        "start_node": "SEC-7",
        "end_node": "SEC-6",
        "start_lat": 16.4850,
        "start_lng": 80.6200,
        "end_lat": 16.5020,
        "end_lng": 80.6350,
        "length_km": 3.6,
        "speed_limit_kmh": 55.0
    },
    {
        "code": "RS-08",
        "name": "South Stadium Ring Bypass",
        "road_type": "ARTERIAL",
        "start_node": "SEC-8",
        "end_node": "SEC-3",
        "start_lat": 16.4800,
        "start_lng": 80.6550,
        "end_lat": 16.5070,
        "end_lng": 80.6480,
        "length_km": 4.5,
        "speed_limit_kmh": 50.0
    },
    {
        "code": "RS-09",
        "name": "River Bridge Causeway",
        "road_type": "BRIDGE",
        "start_node": "SEC-1",
        "end_node": "SEC-6",
        "start_lat": 16.5120,
        "start_lng": 80.6420,
        "end_lat": 16.5020,
        "end_lng": 80.6350,
        "length_km": 2.1,
        "speed_limit_kmh": 40.0
    },
    {
        "code": "RS-10",
        "name": "Western Bypass Expressway",
        "road_type": "HIGHWAY",
        "start_node": "SEC-7",
        "end_node": "SEC-5",
        "start_lat": 16.4850,
        "start_lng": 80.6200,
        "end_lat": 16.5250,
        "end_lng": 80.6150,
        "length_km": 6.8,
        "speed_limit_kmh": 70.0
    },
    {
        "code": "RS-11",
        "name": "Eastern Coastal Relief Route",
        "road_type": "ARTERIAL",
        "start_node": "SEC-2",
        "end_node": "SEC-3",
        "start_lat": 16.4950,
        "start_lng": 80.6650,
        "end_lat": 16.5070,
        "end_lng": 80.6480,
        "length_km": 3.2,
        "speed_limit_kmh": 45.0
    },
    {
        "code": "RS-12",
        "name": "Polytechnic Connector",
        "road_type": "LOCAL",
        "start_node": "SEC-6",
        "end_node": "SEC-8",
        "start_lat": 16.5020,
        "start_lng": 80.6350,
        "end_lat": 16.4800,
        "end_lng": 80.6550,
        "length_km": 4.0,
        "speed_limit_kmh": 45.0
    }
]

SHELTERS = [
    {
        "name": "Suryanagar South Stadium Mega Shelter",
        "code": "SH-01",
        "address": "Ring Road Sector 8, Suryanagar",
        "sector": "SEC-8",
        "lat": 16.4805,
        "lng": 80.6545,
        "total_capacity": 1200,
        "current_occupancy": 150,
        "status": "OPEN",
        "has_medical_facility": True,
        "has_power_backup": True,
        "food_days": 10,
        "water_liters": 45000,
        "contact_person": "Dr. R. K. Varma, Municipal Shelter Officer",
        "contact_phone": "+91-866-555-0111"
    },
    {
        "name": "Government Polytechnic Cyclone Shelter",
        "code": "SH-02",
        "address": "Coastal Bypass Sector 2, Suryanagar",
        "sector": "SEC-2",
        "lat": 16.4960,
        "lng": 80.6620,
        "total_capacity": 450,
        "current_occupancy": 320,
        "status": "OPEN",
        "has_medical_facility": True,
        "has_power_backup": True,
        "food_days": 5,
        "water_liters": 15000,
        "contact_person": "P. Lakshmi, Assistant Camp Officer",
        "contact_phone": "+91-866-555-0122"
    },
    {
        "name": "Suryanagar Central Community Hall",
        "code": "SH-03",
        "address": "Hospital Road Sector 6, Suryanagar",
        "sector": "SEC-6",
        "lat": 16.5030,
        "lng": 80.6340,
        "total_capacity": 300,
        "current_occupancy": 80,
        "status": "OPEN",
        "has_medical_facility": True,
        "has_power_backup": True,
        "food_days": 7,
        "water_liters": 12000,
        "contact_person": "M. Suresh, District Welfare Officer",
        "contact_phone": "+91-866-555-0133"
    },
    {
        "name": "North Hill School Evacuation Center",
        "code": "SH-04",
        "address": "Forest Ridge Road Sector 4, Suryanagar",
        "sector": "SEC-4",
        "lat": 16.5320,
        "lng": 80.6280,
        "total_capacity": 250,
        "current_occupancy": 30,
        "status": "OPEN",
        "has_medical_facility": False,
        "has_power_backup": True,
        "food_days": 4,
        "water_liters": 8000,
        "contact_person": "G. Rao, School Principal & Camp Incharge",
        "contact_phone": "+91-866-555-0144"
    }
]

INITIAL_RESOURCES = [
    # Ambulances
    {"name": "District Trauma Ambulance 108-A", "callsign": "AMB-01", "resource_type": "AMBULANCE", "capacity": 2, "base_station": "District Hospital Enclave", "lat": 16.5022, "lng": 80.6352, "speed_kmh": 60.0},
    {"name": "District Trauma Ambulance 108-B", "callsign": "AMB-02", "resource_type": "AMBULANCE", "capacity": 2, "base_station": "Old Town Health Post", "lat": 16.5065, "lng": 80.6475, "speed_kmh": 60.0},
    {"name": "Mobile ICU Ambulance 108-C", "callsign": "AMB-03", "resource_type": "AMBULANCE", "capacity": 1, "base_station": "South Stadium Relief Post", "lat": 16.4810, "lng": 80.6540, "speed_kmh": 55.0},
    
    # Rescue Boats
    {"name": "NDRF Inflatable Rescue Craft 1", "callsign": "BOAT-01", "resource_type": "RESCUE_BOAT", "capacity": 8, "base_station": "Riverbank Marine Police Station", "lat": 16.5115, "lng": 80.6415, "speed_kmh": 25.0},
    {"name": "SDRF Flood Rescue Zodiac 2", "callsign": "BOAT-02", "resource_type": "RESCUE_BOAT", "capacity": 6, "base_station": "Coastal Port Jetty", "lat": 16.4945, "lng": 80.6645, "speed_kmh": 30.0},
    
    # Rescue Teams (SDRF / NDRF)
    {"name": "SDRF Urban Search & Rescue Team Alpha", "callsign": "USAR-01", "resource_type": "RESCUE_TEAM", "capacity": 12, "base_station": "Central EOC Headquarters", "lat": 16.5025, "lng": 80.6358, "speed_kmh": 45.0},
    {"name": "NDRF High-Angle Rescue Team Bravo", "callsign": "USAR-02", "resource_type": "RESCUE_TEAM", "capacity": 10, "base_station": "Industrial Depot Staging", "lat": 16.4855, "lng": 80.6205, "speed_kmh": 50.0},
    
    # Fire Units
    {"name": "Central Fire Station Water Tender 1", "callsign": "FIRE-01", "resource_type": "FIRE_UNIT", "capacity": 5, "base_station": "Hospital Sector Fire Station", "lat": 16.5015, "lng": 80.6360, "speed_kmh": 50.0},
    {"name": "Industrial Fire Response Unit 2", "callsign": "FIRE-02", "resource_type": "FIRE_UNIT", "capacity": 6, "base_station": "Industrial Freight Base", "lat": 16.4845, "lng": 80.6195, "speed_kmh": 45.0},
    
    # Medical Teams
    {"name": "Rapid Medical Assessment Unit 1", "callsign": "MED-01", "resource_type": "MEDICAL_TEAM", "capacity": 4, "base_station": "District Civil Hospital", "lat": 16.5018, "lng": 80.6348, "speed_kmh": 50.0},
    {"name": "Field Trauma Surgical Unit 2", "callsign": "MED-02", "resource_type": "MOBILE_MEDICAL_UNIT", "capacity": 6, "base_station": "South Stadium Complex", "lat": 16.4802, "lng": 80.6552, "speed_kmh": 40.0},
    
    # Evacuation Buses & Relief
    {"name": "RTC Emergency Evacuation Bus E-101", "callsign": "BUS-01", "resource_type": "EVACUATION_BUS", "capacity": 45, "base_station": "Central Bus Depot", "lat": 16.5050, "lng": 80.6400, "speed_kmh": 45.0},
    {"name": "RTC Emergency Evacuation Bus E-102", "callsign": "BUS-02", "resource_type": "EVACUATION_BUS", "capacity": 45, "base_station": "Central Bus Depot", "lat": 16.5052, "lng": 80.6402, "speed_kmh": 45.0},
    {"name": "Civil Supplies Water Tanker WT-1", "callsign": "WT-01", "resource_type": "WATER_TANKER", "capacity": 10000, "base_station": "Industrial Logistics Depot", "lat": 16.4852, "lng": 80.6210, "speed_kmh": 40.0},
    {"name": "Emergency Diesel Generator Unit 500kVA", "callsign": "GEN-01", "resource_type": "GENERATOR", "capacity": 1, "base_station": "Electricity Board Substation", "lat": 16.4900, "lng": 80.6300, "speed_kmh": 35.0},
    {"name": "Disaster Relief Supply Truck R-1", "callsign": "TRUCK-01", "resource_type": "RELIEF_TRUCK", "capacity": 15, "base_station": "Industrial Logistics Depot", "lat": 16.4858, "lng": 80.6215, "speed_kmh": 45.0},
    {"name": "Indian Coast Guard Rescue Chopper CG-802", "callsign": "HELO-01", "resource_type": "HELICOPTER", "capacity": 6, "base_station": "Suryanagar Airfield Helipad", "lat": 16.4750, "lng": 80.6100, "speed_kmh": 180.0}
]

DISASTER_SCENARIOS = {
    "flood": {
        "name": "Riverine Inundation Flash Surge",
        "disaster_type": "flood",
        "description": "Upstream dam discharge combined with 180mm torrential rain causes Krishna Riverbank to breach embankments. Widespread low-lying residential flooding in Sector 1.",
        "weather_summary": "Torrential Downpour | 185mm rain | River Gauge 14.8m (Danger Mark 14.0m)",
        "wind_speed_kmh": 42.0,
        "rainfall_mm": 185.0,
        "initial_incidents": [
            {
                "title": "Submerged Residential Ward - 28 Citizens Stranded on Rooftops",
                "description": "Rapid water level rise of 1.6 meters in low-lying Krishna Nagar, Sector 1. Ground floors submerged, elderly citizens and infants require boat evacuation.",
                "disaster_type": "flood",
                "severity": "CRITICAL",
                "sector": "SEC-1",
                "address": "Krishna Nagar Ward 12, Sector 1",
                "lat": 16.5125,
                "lng": 80.6418,
                "affected_count": 28,
                "trapped_count": 28,
                "medical_critical_count": 4,
                "priority_score": 94.0,
                "triage_rationale": "High water levels rising 10cm/hr. Immediate life threat to elderly residents without vertical egress.",
                "reports": [
                    "URGENT: Water entered first floor at Krishna Nagar Ward 12. 15 people trapped on terrace. Please send rescue boats!",
                    "Ward 12, Krishna Nagar: Grandparents need urgent medical oxygen, water level waist high. Need boat right now.",
                    "Krishna Nagar 12 terrace: 28 persons total huddled on roof. Ground floor totally submerged."
                ]
            },
            {
                "title": "Elderly Care Home Isolation - Water Ingress into Basement Generator",
                "description": "Veda Elderly Care Sanctuary in Sector 1 experiencing perimeter wall breach. 14 senior citizens need assisted relocation.",
                "disaster_type": "flood",
                "severity": "HIGH",
                "sector": "SEC-1",
                "address": "Veda Senior Living, Embankment Road, Sector 1",
                "lat": 16.5140,
                "lng": 80.6435,
                "affected_count": 14,
                "trapped_count": 14,
                "medical_critical_count": 2,
                "priority_score": 88.0,
                "triage_rationale": "Vulnerable population with power failure imminent. Evacuation required before access road deepens.",
                "reports": [
                    "Veda Elderly Care home flooded. Basement power backup down. Need ambulance and evacuation bus."
                ]
            }
        ],
        "hazard_events": [
            {
                "tick": 3,
                "event_type": "ROAD_BLOCKAGE",
                "title": "Delta Embankment Arterial Submerged",
                "description": "Flash flooding overspills 60cm across RS-01 (Delta Embankment Arterial). Impassable for wheeled road vehicles.",
                "payload": {"segment_code": "RS-01", "status": "FLOODED", "water_depth_cm": 65, "passable_for_boat": True, "passable_for_high_clearance": False}
            },
            {
                "tick": 7,
                "event_type": "INCIDENT_SPAWN",
                "title": "Substation Failure & Power Grid Trip",
                "description": "Transformer submerged near Sector 1 margin. Local hospital generator backup engaged.",
                "payload": {"sector": "SEC-6", "severity": "MEDIUM", "affected_count": 120}
            }
        ]
    },
    
    "cyclone": {
        "name": "Very Severe Cyclonic Storm 'Varuna'",
        "disaster_type": "cyclone",
        "description": "Category 3 intensity cyclone making direct landfall near Suryanagar coastal esplanade. Sustained winds of 145 km/h with 2.5m storm surge inundation.",
        "weather_summary": "Sustained Winds 145 km/h | Gusts 165 km/h | Storm Surge 2.2m",
        "wind_speed_kmh": 145.0,
        "rainfall_mm": 120.0,
        "initial_incidents": [
            {
                "title": "Coastal Fishermen Colony Storm Surge Inundation",
                "description": "Storm surge has penetrated 400m inland at Sector 2 port settlement. Over 45 individuals in precarious tin-roof dwellings.",
                "disaster_type": "cyclone",
                "severity": "CRITICAL",
                "sector": "SEC-2",
                "address": "Fishermen Colony Jetty Sector 2",
                "lat": 16.4955,
                "lng": 80.6645,
                "affected_count": 45,
                "trapped_count": 35,
                "medical_critical_count": 6,
                "priority_score": 92.0,
                "triage_rationale": "Direct storm surge exposure with flying debris. Immediate mass evacuation to designated cyclone shelter required.",
                "reports": [
                    "Waves breaking over sea wall into colony houses. People gathered at temple terrace. Send high clearance transport!",
                    "Severe wind blew roofs off 10 huts in sector 2 jetty. Multiple laceration injuries."
                ]
            }
        ],
        "hazard_events": [
            {
                "tick": 2,
                "event_type": "ROAD_BLOCKAGE",
                "title": "Coastal Highway RS-02 Obstructed by High-Tension Pylons",
                "description": "Gale-force winds snapped 3 transmission towers across RS-02 Coastal Highway.",
                "payload": {"segment_code": "RS-02", "status": "DEBRIS_BLOCKED", "obstruction_details": "Fallen high tension electric poles across both lanes"}
            }
        ]
    },

    "earthquake": {
        "name": "Magnitude 6.4 Intraplate Seismic Event",
        "disaster_type": "earthquake",
        "description": "Shallow 10km depth earthquake causes widespread unreinforced masonry collapse across historic Old Town Sector 3. Secondary fires reported.",
        "weather_summary": "Clear Skies | Temperature 32C | Multiple Magnitude 4+ Aftershocks Expected",
        "wind_speed_kmh": 15.0,
        "rainfall_mm": 0.0,
        "initial_incidents": [
            {
                "title": "Multi-Story Commercial Arcade Collapse - Old Town",
                "description": "4-story heritage commercial building pancake collapse at Sector 3 Market Chowk. Estimated 18 persons trapped beneath debris slab.",
                "disaster_type": "earthquake",
                "severity": "CRITICAL",
                "sector": "SEC-3",
                "address": "Bazaar Chowk, Sector 3 Old Town",
                "lat": 16.5075,
                "lng": 80.6485,
                "affected_count": 35,
                "trapped_count": 18,
                "medical_critical_count": 9,
                "priority_score": 98.0,
                "triage_rationale": "Crush injuries and asphyxiation hazard. Immediate heavy USAR acoustic detection and extrication mandated.",
                "reports": [
                    "Bazaar arcade completely collapsed into street! People calling from underneath concrete slabs!",
                    "Sector 3 chowk collapsed. Dust everywhere. Gas smell reported, need fire tender and rescue squad immediately."
                ]
            }
        ],
        "hazard_events": [
            {
                "tick": 2,
                "event_type": "ROAD_BLOCKAGE",
                "title": "Old Town Central Spine RS-03 Blocked by Rubble",
                "description": "Masonry facade collapse across RS-03 has severed direct access between Old Town and District Hospital.",
                "payload": {"segment_code": "RS-03", "status": "DEBRIS_BLOCKED", "obstruction_details": "40 tonnes of reinforced concrete rubble obstructing carriageway"}
            }
        ]
    },

    "wildfire": {
        "name": "Northern Ridge Wildland-Urban Interface Firestorm",
        "disaster_type": "wildfire",
        "description": "Dry seasonal conditions and 55 km/h gusts push wildfire front along Northern Ridge towards residential Sector 4 outskirts.",
        "weather_summary": "Humidity 14% | Wind Gusts 55 km/h NE | Severe Smoke Plume Dispersion",
        "wind_speed_kmh": 55.0,
        "rainfall_mm": 0.0,
        "initial_incidents": [
            {
                "title": "Wildland Fire Approaching Ridge Outskirts Suburb",
                "description": "Fast-moving brush fire line within 600m of 30 homes at Sector 4 Ridge Margin. Heavy smoke inhalation risk.",
                "disaster_type": "wildfire",
                "severity": "CRITICAL",
                "sector": "SEC-4",
                "address": "Forest Margin Road, Sector 4",
                "lat": 16.5345,
                "lng": 80.6295,
                "affected_count": 60,
                "trapped_count": 12,
                "medical_critical_count": 3,
                "priority_score": 91.0,
                "triage_rationale": "Rapid flame advancement. Evacuation corridor must be protected with fire tenders and buses.",
                "reports": [
                    "Flames visible on ridge top, thick smoke blanketing north colony. People with asthma struggling to breathe.",
                    "Need fire engines and water tankers right away along forest edge!"
                ]
            }
        ],
        "hazard_events": [
            {
                "tick": 3,
                "event_type": "ROAD_BLOCKAGE",
                "title": "Northern Ridge Spine RS-04 Engulfed by Smoke and Fire Front",
                "description": "Dense smoke zero visibility and fire front crossing RS-04.",
                "payload": {"segment_code": "RS-04", "status": "FIRE_CORRIDOR", "obstruction_details": "Zero visibility, active burning branches across roadway"}
            }
        ]
    },

    "landslide": {
        "name": "Hillside Ghati Slope Failure & Road Severance",
        "disaster_type": "landslide",
        "description": "Saturated hillside shale yields at Km 4 of Ghat Road. 8,000 cubic meters of mud and rock detach, severing the pass and trapping vehicles.",
        "weather_summary": "Heavy Intermittent Rain | Slope Instability Warning | Saturated Mudflow",
        "wind_speed_kmh": 35.0,
        "rainfall_mm": 95.0,
        "initial_incidents": [
            {
                "title": "Passenger Minibus Trapped by Dual Debris Flow",
                "description": "A 22-passenger minibus and two private cars caught between two rockfalls on Ghat Pass Road Sector 5.",
                "disaster_type": "landslide",
                "severity": "CRITICAL",
                "sector": "SEC-5",
                "address": "Ghat Pass Bend 7, Sector 5",
                "lat": 16.5245,
                "lng": 80.6155,
                "affected_count": 26,
                "trapped_count": 26,
                "medical_critical_count": 5,
                "priority_score": 93.0,
                "triage_rationale": "High risk of secondary slope slide down valley gorge. Urgent rope rescue and earthmoving intervention.",
                "reports": [
                    "Tour bus trapped on hairpin bend 7 of ghat road. Boulders fallen in front and behind. Can't move!",
                    "Passengers injured from falling rocks shattering windows. Send NDRF rescue team and ambulances."
                ]
            }
        ],
        "hazard_events": [
            {
                "tick": 2,
                "event_type": "ROAD_BLOCKAGE",
                "title": "Ghat Mountain Pass RS-05 Blocked by Massive Rockfall",
                "description": "Entire roadway collapsed at hairpin bend 7 on RS-05. Road completely impassable.",
                "payload": {"segment_code": "RS-05", "status": "LANDSLIDE_BLOCKED", "obstruction_details": "Massive boulder slide and carriageway subsidence"}
            }
        ]
    }
}
