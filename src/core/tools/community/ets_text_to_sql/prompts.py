reactive_metrics_field_description = """
{
  "Table": "gq.vw_RPT_Reactive_Metrics",
  "Alias": "REACTIVE_METRICS",
  "TableDescription": "Contains information related to ETS (Emergency Tracking System) events like injuries, illness, fires, property damage, chemical spills, or property damage.",
  "ImportantNotes": [
    "The following filters should be applied in most cases unless the user specifically specifies otherwise: EVENTSTATUS <> 'Deleted', ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null)",
    "When performing mathematical operations on INT type columns convert them to Floats first",
    "When Counting the number of Events unless the user specifies counting CAPAS, you should always use COUNT(DISTINCT [EVENTID])"
  ],
  "Columns": [
    {
      "ColumnName": "REACTIVEMETRICID",
      "DataType": "int",
      "ColumnDetails": "ID for the Reactive Metric",
      "Important Notes": "This isn't the Event ID, if the user asks about an event use EventID",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTID",
      "DataType": "int",
      "ColumnDetails": "The ID for the ETS Event",
      "Important Notes": "there can be more than one record with an event id. For example each CAPA gets a new line. When user requests count of ets events always use count of unique event ids instead of a raw count of rows",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTDATE",
      "DataType": "date",
      "ColumnDetails": "The date that the event happened on",
      "Important Notes": "Date format YYYY-MM-DD",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTTIME",
      "DataType": "time",
      "ColumnDetails": "The time that the event happened on",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "SUBMITTEDDATE",
      "DataType": "datetime",
      "ColumnDetails": "The date that the ETS record was submitted",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTSTATUS",
      "DataType": "varchar",
      "ColumnDetails": "The status of the ETS event. Important note: Unless the user specifically asks for 'Deleted' status ETS Events filter them out of Queries.",
      "Important Notes": "",
      "CategoricalValues": ["Deleted", "Not Submitted", "Submitted to EHS", "Closed", "Open"]
    },
    {
      "ColumnName": "EVENTTYPE",
      "DataType": "varchar",
      "ColumnDetails": "The type of ETS event",
      "Important Notes": "",
      "CategoricalValues": ["Chemical Release - Spill", "Odor", "Injury", "Property Damage/Business Impact", "Chemical Release - Air Emission", "Power Outage", "Regulatory Agency Inspection", "EHS Management System Audit", "Fire/Explosion", "Illness", "FLSS - Fire/HazMat Alarm", "Near Miss"]
    },
    {
      "ColumnName": "WORKMANSHIPQUALITY",
      "DataType": "varchar",
      "ColumnDetails": "Whether there was anything related to Workmanship Quality",
      "Important Notes": "",
      "CategoricalValues": ["Tool Damage", "Wafer Scrap", "Workmanship Near Miss"]
    },
    {
      "ColumnName": "EVENTDESCRIPTION",
      "DataType": "varchar",
      "ColumnDetails": "The is the description of the ETS event. It will include the details about what happened, during the event.",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "SBINCIDENTDESCRIPTION",
      "DataType": "varchar",
      "ColumnDetails": "Significant Behavioral Incident Type Description. An SBI happens when a significant behavioral action is responsible for the ets event. #",
      "Important Notes": "DO NOT USE this column based off a relevant value existing in the CategoricalValues field. This is only to be used when a user specifically uses the phrase "Significant Behavioral" ",
      "CategoricalValues": ["Failure to follow Pre-Task Planning", "Not Applicable", "Failure to follow Stop-Work", "LOTO", "PPE"]
    },
    {
      "ColumnName": "EVACUATION",
      "DataType": "varchar",
      "ColumnDetails": "Whether there was an evacuation and what type of evacuation for a given ETS event",
      "Important Notes": "",
      "CategoricalValues": ["Building Evacuation", "Area Evacuation", "None"]
    },
    {
      "ColumnName": "ERTMERTRESPONSE",
      "DataType": "varchar",
      "ColumnDetails": "Was there an ERT (Emergency Response Team) Response for the ETS event",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes"]
    },
    {
      "ColumnName": "MAJORSITEREGION",
      "DataType": "varchar",
      "ColumnDetails": "The Major site or Region where the ETS event happened",
      "Important Notes": "",
      "CategoricalValues": ["Korea", "Salzburg", "3.P.L - Inactive", "SE Asia", "Japan", "Malaysia MFG", "LMK", "Fremont", "N. America", "KTC", "Livermore", "", "Bristol - Inactive", "Taiwan", "Silfex - Inactive", "EMEA", "Villach", "India", "Tualatin", "Silfex, OH", "China", "San Jose - Inactive"]
    },
    {
      "ColumnName": "SPECIFICLOCATION",
      "DataType": "varchar",
      "ColumnDetails": "The specific location within a major site or Region that an ETS event happened",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CUSTOMERNAME",
      "DataType": "varchar",
      "ColumnDetails": "The customer name if any that was related to the ETS event",
      "Important Notes": "",
      "CategoricalValues": ["Intel Corporate", "NANYA", "Jiangsu Advanced Memory", "Advance Semiconductor Engineering", "Renesas Electronics Corp", "Fairchild Semiconductor", "Ichor Systems Ltd.", "Macronix", "Shenzhen Pensun Technology Co., Ltd.", "HuaHong Group", "Tsinghua Unigroup", "Wuhan Chuxing Technology", "Maxscend Microelectronics Company Ltd.", "Tower Semiconductor Ltd.", "Micron Technology", "SK Hynix", "Innotron Memory Co., Ltd", "Microchip", "SiEn (Qingdao) Integrated Circuits", "Canon", "PSMC", "Taiwan Semiconductor Manufacturing Corp. (TSMC)", "STMicroelectronics", "Hewlett Packard", "Texas Instruments", "RF360 Europe GmbH", "WaferTech LLC", "College of NSE", "NXP Semiconductors", "Semiconductor Manufacturing Internationa", "Infineon Technologies AG Neubiberg", "YMTC", "PolarFab", "Nissan", "Beijing Jidian", "Sony Corporation", "Cypress Semiconductor", "IMEC", "Honeywell", "Winbond", "Forehope Electronic (Ningbo) 300mm", "CEA LETI", "On Semiconductor", "Kioxia Corporation", "Robert Bosch GmbH", "UMC", "TDK Corporation", "Powertech Technology Inc. (PTI)", "Siliconware Precision Industries", "Lam Research", "Samsung", "EM Marin", "Hangzhou HFC Semiconductor", "Silex Microsystems", "Fujitsu Limited", "Avago Technologies Wireless (USA)", "Nexchip Semiconductor", "Changxin Jidian Memory Tech (CXJD)", "GLOBALFOUNDRIES", "X-Fab", "IBM", "Shanghai GTX Semiconductor", "Guangzhou Cansemi Technology Inc.", "LFoundry", "SMEC"]
    },
    {
      "ColumnName": "FABNAME",
      "DataType": "varchar",
      "ColumnDetails": "The Fab Name if any that was related to the ETS event",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "PRODUCTNAME",
      "DataType": "varchar",
      "ColumnDetails": "The Product Name if any that was related to the ETS event",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "WHY1",
      "DataType": "varchar",
      "ColumnDetails": "The '5 Whys' is a problem-solving technique that involves asking 'why' five times in succession to drill down into the root cause of a problem, rather than just addressing its symptoms. This is the first why",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "WHY2",
      "DataType": "varchar",
      "ColumnDetails": "The '5 Whys' is a problem-solving technique that involves asking 'why' five times in succession to drill down into the root cause of a problem, rather than just addressing its symptoms. This is the second why",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "WHY3",
      "DataType": "varchar",
      "ColumnDetails": "The '5 Whys' is a problem-solving technique that involves asking 'why' five times in succession to drill down into the root cause of a problem, rather than just addressing its symptoms. This is the third why",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "WHY4",
      "DataType": "varchar",
      "ColumnDetails": "The '5 Whys' is a problem-solving technique that involves asking 'why' five times in succession to drill down into the root cause of a problem, rather than just addressing its symptoms. This is the fourth why",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "WHY5",
      "DataType": "varchar",
      "ColumnDetails": "The '5 Whys' is a problem-solving technique that involves asking 'why' five times in succession to drill down into the root cause of a problem, rather than just addressing its symptoms. This is the fifth why",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CORRECTIVEPREVENTIVEACTION",
      "DataType": "varchar",
      "ColumnDetails": "This is the corrective action that will be applied as a result of the ETS incident to reduce likelihood of it happening again.",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "LASTMODIFIEDDATE",
      "DataType": "datetime",
      "ColumnDetails": "The date when the ETS record was last modified",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTCLASSIFICATION",
      "DataType": "varchar",
      "ColumnDetails": "This is the Classification of the event (the Tier level)",
      "Important Notes": "",
      "CategoricalValues": ["Tier 2", "Tier 1", "Tier 3", "Tier 4", "Tier 0"]
    },
    {
      "ColumnName": "CAPASTATUS",
      "DataType": "varchar",
      "ColumnDetails": "This is the status of the associated CAPA (Corrective and Preventive Action) for this ETS record. Important note: unless the user specifies retrieving 'Deleted' CAPASTATUS values, filter them out in the query",
      "Important Notes": "",
      "CategoricalValues": ["Closed", "Open", "Deleted"]
    },
    {
      "ColumnName": "CAPASNO",
      "DataType": "int",
      "ColumnDetails": "This is the CAPA serial number for the CAPA related to this ETS",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CAPACOMPLETEDDATE",
      "DataType": "datetime",
      "ColumnDetails": "When the CAPA was Completed if it was",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CAPAASSIGNEDDATE",
      "DataType": "datetime",
      "ColumnDetails": "When the CAPA was assigned if it was",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CAUSALFACTOR",
      "DataType": "varchar",
      "ColumnDetails": "The causal Factor related to the ETS event (What led to it happening). What the cause of this ETS event was.",
      "Important Notes": "",
      "CategoricalValues": ["Work Environment", "Process/Procedures", "Training/Skills", "Maintenance", "Management/Resources", "Mother Nature", "People/Behavior", "Machine/Equipment"]
    },
    {
      "ColumnName": "RESPONSIBLEMANAGER",
      "DataType": "varchar",
      "ColumnDetails": "The responsible manager Name for the ETS event: 'Lastname, Firstname'",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "INJURYCLASSIFICATION",
      "DataType": "varchar",
      "ColumnDetails": "The classification of the injury for this event (severity)",
      "Important Notes": "",
      "CategoricalValues": ["No Treatment", "Recordable", "First Aid", "Non-Lam Injury", "Recordable LWD"]
    },
    {
      "ColumnName": "INJURYTYPE",
      "DataType": "varchar",
      "ColumnDetails": "The type of injury for this event if there was an injury associated with the ETS event",
      "Important Notes": "",
      "CategoricalValues": ["Strain/Sprain", "Contusion/Bruise", "Fracture", "Rash/Irritation", "Abrasion/Scratch", "Chemical Exposure/Burn", "Thermo/Burn", "Electrical Shock/Burn", "Laceration/Cut", "Office MSD", "Other", "Personal Medical"]
    },
    {
      "ColumnName": "MODEOFINJURYDESCRIPTION",
      "DataType": "varchar",
      "ColumnDetails": "The mode in which the injury was inflicted",
      "Important Notes": "",
      "CategoricalValues": ["Caught in/Caught on", "Motor Vehicle Accident", "Fall from Height", "Contact with/Exposure to", "Strain/Sprain (Acute)", "Pinch/Crush", "Struck on (Bumped into object)", "Struck by (Hit by object)", "Repetitive Motion (Chronic)", "Other", "Personal Medical", "Slip/Trip/Fall (Fall on same level)"]
    },
    {
      "ColumnName": "BUSINESSGROUPNAME",
      "DataType": "varchar",
      "ColumnDetails": "Business group name",
      "Important Notes": "FunctionalGroup is a better pick for filtering on group. Only use Business Group if the User specifically asks for it.",
      "CategoricalValues": ["Deposition Business Unit",  "KR Samsung Account", "Regional Finance", "Dry Resist", "Admin", "Advanced Process Development", "Deposition Operations", "EPG Deputy GM", "JP MMJ Account", "Information Security", "Product Development", "GPG APAC/NA/EU BD", "CSBG North America", "Mechatronics Engineering", "Platform Products", "GCO - Global Customer Operations", "JP Customer Support Business Group", "Velocity Labs", "Product Marketing & Business Development", "Regional Operations - Global Foundries/NARO", "Regional Operations - Taiwan", "Deputy Head - GPG", "Global Information Systems", "Corporate Technology Development", "Enterprise Applic. Dev. & Integration", "SG RBO - Business Operations", "Aether Product Group", "Semiverse Solutions", "Deposition Engineering", "JP Toshiba Global Account", "Production", "Corp Tech Dev - Hardware", "Clean Division", "CSBG Engineering", "DE Memory HAR Technology", "Japan", "GPG Ops", "OCTO Staff", "Global Human Resources Business Partner", "Strategic Programs", "ALD / CVD Metals", "JP EHS", "Global Workplace Solutions", "Business Resilience & Security", "Corp Order Fulfillment & Prod Mgmt Ops", "Singapore", "Surface Integrity Group (SIG)", "Exec Staff", "China Regional Business Ops", "Enterprise Infrastructure & Cloud Services", "Selective Etch Productivity Group", "HRBPs", "Dielectric Deposition, PECVD/UVTP", "GF Malta Mgmt", "India Management", "DE Logic & Patterning Technology", "Silfex Manufacturing", "Corporate Business Operations", "Metrology Services", "Talent Acquisition", "Global Learning & Organizational Dev", "Innovative Productivity Solutions", "Advanced Technology Development", "Intel Global Account", "Korea Customer Operations", "Regional Operations - Micron", "SG APAC Reg (UMCi/SSMC/Regional/OSAT)", "Etch Engineering", "Global Logistics and SOPP", "KR Regional Operations", "Business Unit IT", "Engineering", "Global Logistics & SOPP", "Regional Operations - Korea", "Tua Pilot MFG & ENG", "Business Operations", "TW VP - TSMC Account Executive", "Global Customer Operations", "Metal Deposition, ECP/ELD", "SG CSBG", "Global Human Resources", "Chief Operating Officer", "Etch Emerging Tech & Knowledge Products", "Intellectual Property Law Group", "Metal Deposition, Packaging", "Lab Operations"]
    },
    {
      "ColumnName": "RCCACYCLEDAYS",
      "DataType": "int",
      "ColumnDetails": "How many days the RCCA (Root Cause Corrective Action) cycle took",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "ROOTCAUSE",
      "DataType": "varchar",
      "ColumnDetails": "The root cause for this ETS event",
      "Important Notes": "",
      "CategoricalValues": ["1-Work Environment", "4-Mother Nature", "5-Process/Procedures", "1-Mother Nature", "7-Work Environment", "3-Training/Skills", "1-Training/Skills", "4-Machine/Equipment", "2-Process/Procedures", "3-People/Behavior", "9-People/Behavior", "1-People/Behavior", "19-Process/Procedures", "2-Mother Nature", "5-Work Environment", "7-Training/Skills", "13-Work Environment", "6-People/Behavior", "4-People/Behavior", "2-Management/Resources", "4-Work Environment", "2-Machine/Equipment", "3-Process/Procedures", "4-Training/Skills", "2-Work Environment", "2-People/Behavior", "3-Work Environment", "3-Machine/Equipment", "5-Machine/Equipment"]
    },
    {
      "ColumnName": "CAPATARGETDATE",
      "DataType": "datetime",
      "ColumnDetails": "The target date for completion of the CAPA (Corrective and Preventive Action)",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "FUNCTIONALGROUP",
      "DataType": "varchar",
      "ColumnDetails": "The functional group or team assigned to this ETS",
      "Important Notes": "This is similar to business unit but has finer detail it represents the team underneath the business unit. When a user asks for how many ETS events did Logistics, or Pilot, or in a Lab. They are talking about Functional groups this field should come up a lot.",
      "CategoricalValues": ["Global Logistics", "Business Operations", "Deposition Program and Product Management", "GCO - Global Customer Operations", "Dielectric Etch Product Group", "Business Development", "Velocity Labs", "Physical Security", "Engineering Services", "Metrology Services", "Conductor Etch Process", "Regional Finance", "Aether Product Group", "Advanced Process Development", "Total Rewards", "Product Marketing", "Advanced Technology Integration", "Etch EI Technology", "Account mgmt", "Dielectrics Deposition", "SC Transformation", "Deposition Engineering", "Facilities Services", "Global End-User Technology and Services", "Production", "WETS - Clean", "Corp Controller", "CSBG Engineering", "DFS - Direct Field Service Mgmt", "Dielectric Etch", "Global Products Engineering", "Platform Hardware Engineering", "Process Development", "Etch Operations", "Global Logistics & SOPP", "GWS Bus Ops", "Lab Operations", "RTG - Regional Technical Group", "Chief Operating Officer", "Silfex Management", "Product Engineering", "Etch Product Group", "Enterprise Applications", "ALD / CVD Metals", "C&F Process Development", "Strategic Planning", "Information Security", "Software & Controls", "Admin", "Deposition Operations", "Business and Enterprise Solutions Team", "Global Workplace Solutions", "Product Safety", "Exec Staff", "C&F and Central Engineering", "HVM - Livermore", "Products & Services", "Semiverse Solutions Engineering", "Enterprise Infrastructure & Cloud Services", "Global University Engagement", "GIS India", "Sales Operations", "Etch Engineering", "Corporate Strategy", "Business Unit IT", "Deposition Product Marketing and Business Development", "Digital Workplace", "Conductor Etch Product Group", "Regional Operations - Intel", "Regional Operations - Japan", "Sales/Business Development", "Pilot Operations", "Business Development & Sales Operations", "Conductor Etch C&F", "Order Management", "CSBG - Customer Support Business Group", "Global Legal Services", "Global Environmental Health & Safety", "Order Fulfillment", "Etch Product Development", "Global Product Operations", "LMT", "Surface Integrity Group", "Global Quality", "Reliant", "Occupancy Planning/Real Estate", "Global Operations", "OCTO - Office Of The CTO", "PECVD", "Global Products Group", "Regional Operations - Europe", "Factory Operations", "Operations", "Regional HR", "GIO - Global Installed Base Operations", "Platform", "GPG Business Development and Product Marketing", "Korea Technology Center", "Product Ops"]
    },
    {
      "ColumnName": "INCCAPAS",
      "DataType": "int",
      "ColumnDetails": "Boolean Includes CAPAS",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "INCDESC",
      "DataType": "int",
      "ColumnDetails": "Boolean Includes Description of Event",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "INCGOV",
      "DataType": "int",
      "ColumnDetails": "Boolean Includes Governance",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "INCINV",
      "DataType": "int",
      "ColumnDetails": "Boolean Includes Investigation",
      "Important Notes": "",
      "CategoricalValues": ["1", "0"]
    },
    {
      "ColumnName": "INCWS",
      "DataType": "int",
      "ColumnDetails": "Boolean Includes Workmanship",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "CAPAOWNER",
      "DataType": "varchar",
      "ColumnDetails": "The owner of the CAPA (Corrective and Preventive Action): 'Lastname, Firstname'",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTCLOSEDDATE",
      "DataType": "date",
      "ColumnDetails": "The date when the ETS event was closed",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "EVENTCLOSEDTIMESTAMP",
      "DataType": "datetime",
      "ColumnDetails": "The time that the ETS event was closed",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "VPORGNAME",
      "DataType": "varchar",
      "ColumnDetails": "VP Organization assigned to this ETS",
      "Important Notes": "",
      "CategoricalValues": ["GRST - Global Resilience, Security & Transformation", "Japan", "Sales & Field Operations NA & Europe", "Strategic Programs", "Clean Product Line", "Global Human Resources", "Advanced Packaging", "Chief Operating Officer", "Advanced Technology Development", "Singapore", "Global Finance", "Corporate Development", "Corporate Strategy", "Business Development/ Sales Operations", "Global Operations", "Global Products Group", "Etch Product Group", "Global Products Engineering", "Deputy Head - GPG", "GCO - Global Customer Operations", "Global Information Systems", "China", "Global Quality", "CEO Staff", "Taiwan", "OCTO", "Deposition Product Group", "Legal", "Advanced Equipment & Process Control", "OCTO - Office Of The CTO", "CSBG - Customer Support Business Group", "Korea Corporate Office", "Pilot Operations"]
    },
    {
      "ColumnName": "EXCLUDEINCIDENTFROMBI",
      "DataType": "varchar",
      "ColumnDetails": "Whether or not to exclude this incident from BI reporting",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "ROOTCAUSEEXPLAINATION",
      "DataType": "varchar",
      "ColumnDetails": "This is the detailed explanation of the root cause of the ETS event",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "APPRENTICE",
      "DataType": "int",
      "ColumnDetails": "Boolean Apprentice Injured",
      "Important Notes": "",
      "CategoricalValues": ["1"]
    },
    {
      "ColumnName": "CONTRACTOR",
      "DataType": "int",
      "ColumnDetails": "Boolean Contractor Injured",
      "Important Notes": "",
      "CategoricalValues": ["1", "2"]
    },
    {
      "ColumnName": "EMPLOYEE",
      "DataType": "int",
      "ColumnDetails": "Boolean Full-Time Employee Injured",
      "Important Notes": "",
      "CategoricalValues": ["8", "1", "3", "4", "2"]
    },
    {
      "ColumnName": "INTERN",
      "DataType": "int",
      "ColumnDetails": "Boolean Intern Injured",
      "Important Notes": "",
      "CategoricalValues": ["1"]
    },
    {
      "ColumnName": "TEMPORARY",
      "DataType": "int",
      "ColumnDetails": "Boolean Temporary Worker Injured",
      "Important Notes": "",
      "CategoricalValues": ["4", "1", "3", "2"]
    },
    {
      "ColumnName": "CAPALEADTIME",
      "DataType": "int",
      "ColumnDetails": "Lead time for CAPA (Corrective and Preventive Action) Completion",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "QUARTER",
      "DataType": "varchar",
      "ColumnDetails": "Year and Quarter value for the event format example: 2024Q4, 2022Q1",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "SHIFT",
      "DataType": "varchar",
      "ColumnDetails": "The shift that this event occurred on",
      "Important Notes": "",
      "CategoricalValues": ["Day Shift", "Night Shift"]
    },
    {
      "ColumnName": "ETSLINK",
      "DataType": "varchar",
      "ColumnDetails": "URL Link to the ETS event",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "MONTHYEAR",
      "DataType": "nvarchar",
      "ColumnDetails": "Month and Year of the Event format example: Jan2016",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "MONTH",
      "DataType": "nvarchar",
      "ColumnDetails": "Month of the Event format example: Mar",
      "Important Notes": "",
      "CategoricalValues": ["Nov", "May", "Jun", "Feb", "Oct", "Aug", "Dec", "Sep", "Mar", "Apr", "Jan", "Jul"]
    },
    {
      "ColumnName": "CAPAAGING",
      "DataType": "int",
      "ColumnDetails": "How long the CAPA has been open for",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "ROOTCAUSE_NONUMBER",
      "DataType": "varchar",
      "ColumnDetails": "The category of the root cause in text. This rolls the root cause up into a categorical group",
      "Important Notes": "",
      "CategoricalValues": ["Machine/Equipment", "-Work Environment", "Work Environment", "Training/Skills", "Management/Resources", "Mother Nature", "Maintenance", "People/Behavior", "-Process/Procedures", "Process/Procedures"]
    },
    {
      "ColumnName": "CAPAOwnerBG",
      "DataType": "varchar",
      "ColumnDetails": "Business Group of the CAPA (Corrective and Preventive Action) owner",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "CAPAOwnerVpOrg",
      "DataType": "varchar",
      "ColumnDetails": "VP group of the CAPA (Corrective and Preventive Action) owner",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "ActionTakenToClose",
      "DataType": "varchar",
      "ColumnDetails": "The action that was taken in order to close this ETS event",
      "Important Notes": "",
      "CategoricalValues": null
    },
    {
      "ColumnName": "SUBMITTERNAME",
      "DataType": "varchar",
      "ColumnDetails": "Name of the person submitting the ETS event example form: 'Lastname, Firstname'",
      "Important Notes": "Names are formatted in the following way: 'Lastname, Firstname' ",
      "CategoricalValues": None
    },
    {
      "ColumnName": "REGULATORYVIOLATION",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event involve a Regulatory Violation",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes"]
    },
    {
      "ColumnName": "CAPAOWNERFG",
      "DataType": "varchar",
      "ColumnDetails": "The FG of the CAPA Owner",
      "Important Notes": "",
      "CategoricalValues": None
    },
    {
      "ColumnName": "LOCATIONBUILDINGNAME",
      "DataType": "varchar",
      "ColumnDetails": "The name of the Building involved in this ETS Event",
      "Important Notes": "",
      "CategoricalValues": ["CA03E Gottscho Lab", "CA10", "OR13 (Building L)", "CA06", "CA38 (Building 3940) - Inactive", "TWN-05-Hsinchu(No.17 & 19)", "KOR30 - Inactive", "OR12A (Building J)", "Building 9", "OR09 (Building E)", "Building 5", "KOR38 (Icheon)", "Building 1", "AZ-04 (Chandler)", "CA03", "CA04", "CA11", "CA05", "Warehouse - Inactive", "CHN37 (Dalian)", "CA41 (Building 3970) - Inactive", "NY03 - Inactive", "TWN-10-Houli", "IND05 (Bangalore Fairway Business Park)", "JPN41 (Kitakami)", "MAL01 (KHTP Business Center)", "OR03 (Hillsboro)", "CHN31 (Xian)", "CA30", "CA42 (Building 4000) - Inactive", "OR15 (Building Q)", "KOR27 - Inactive", "Production 1A - Inactive", "MYS03", "MYS04", "Kor34 (Yongin)", "JPN27(Yokkaichi)", "TWN-35-Longtan Lab(TTC 1.5)", "Building 10", "CHN49 (Wuhan)", "CA40 (Building 3960) - Inactive", "Plastic Workshop - Inactive", "OR12B (Building K)", "IND04 (Bangalore Kolar Rd)", "TWN12 - Inactive", "CHN79 (Qingdao)", "Production 1 - Inactive", "SIN01 - Inactive", "CHN28 - Inactive", "JPN32", "Production 3 - Inactive", "OR06 (Building B)", "Laboratory 3-4 - Inactive", "UK-01A (1230/1240) - Inactive", "CHN50 (Wuxi)", "ISR01 - Inactive", "OR16 (Building R)", "CHN32 - Inactive", "JPN22(Shin-Yokohama)", "NY05 - Inactive", "IRE03 (Cellbridge)", "CHN51 (Beijing Training Center)", "TWN23-Taichung", "CA09", "CA31", "TWN15-Tainan", "CA31 MFG Floor", "CA50", "OH01 (Silfex Eaton)", "NLD-01 (Solmates)", "MYS06 (ASW Selangor Malaysia)", "Building 17", "GER08 (Dresden)", "CA01", "JPN21(Oita)", "TWNX1-Hsinchu (TTC)", "CA07", "Building 2", "OR05 (Building A)", "TX11 (Austin)", "KOR47 (Hwaseong)", "KOR22 - Inactive", "Building 8", "IND01 (Bangalore Inner Ring Rd)", "Building 3", "KTC-1", "OR10 (Building F)", "Other", "Wildrose Warehouse ", "Building 13", "OR07 (Building C)", "TWN-17-Hsinchu(No. 7)", "TX05 - Inactive", "TWN24-Linko", "VA-02 (Manassas VA)", "OR14 (Building M)", "CA37 (Building 3930) - Inactive", "CHN4546 (Hefei)", "Building 6"]
    },
    {
      "ColumnName": "PREVENTABLEEVAC",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event involved a preventable Evacuation",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes", ""]
    },
    {
      "ColumnName": "SEVEREINJURIES",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event had severe injuries associated with it",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes", ""]
    },
    {
      "ColumnName": "SERIOUSNONINJURY",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event had a serious non-injury",
      "Important Notes": "",
      "CategoricalValues": ["", "No", "Yes"]
    },
    {
      "ColumnName": "LAMCAUSEDFABEVAC",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event involved a lamcaused evacuation of a Fab",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes", ""]
    },
    {
      "ColumnName": "LAMRESEARCHTOOLRELATED",
      "DataType": "varchar",
      "ColumnDetails": "Whether this ETS Event was related to a lam tool",
      "Important Notes": "",
      "CategoricalValues": ["No", "Yes"]
    },
    {
      "ColumnName": "TOOLLOCATION",
      "DataType": "varchar",
      "ColumnDetails": "The location of the lam tool if one was involved",
      "Important Notes": "",
      "CategoricalValues": ["Lam Factory/R&D", "Lam Customer", ""]
    },
    {
      "ColumnName": "CUSTOMERTEMPERATURE",
      "DataType": "varchar",
      "ColumnDetails": "The customer temperature classification representing how critical this ETS event is to a customer",
      "Important Notes": "",
      "CategoricalValues": ["Unknown", "Severe", "Mild", "Hot", "Warm"]
    },
    {
      "ColumnName": "FCID",
      "DataType": "varchar",
      "ColumnDetails": "The FCID Forecast Identification (unique id for a lam system) for the tool involved in the ETS event if any",
      "Important Notes": "",
      "CategoricalValues": None
    },
    {
      "ColumnName": "MODIFIEDPERSONNAME",
      "DataType": "varchar",
      "ColumnDetails": "The name ('Lastname, Firstname') of the person that last modified the ETS record",
      "Important Notes": "",
      "CategoricalValues": None
    },
    {
      "ColumnName": "ISFIELDREGION",
      "DataType": "bit",
      "ColumnDetails": "Whether this ETS Event involved a field region or not.",
      "Important Notes": "",
      "CategoricalValues": ["0", "1"]
    },
    {
      "ColumnName": "BODYPARTS",
      "DataType": "varchar",
      "ColumnDetails": "If there was an injury associated with this ETS Event, which body parts the injury was related to.",
      "Important Notes": "",
      "CategoricalValues": ["Forehead, Nose", "Face", "Head", "Left Knee", "Right Hand", "Lungs", "Right Wrist, Left Wrist", "Right Eye", "Back, Left Hip", "Right Hand, Left Leg, Left Knee", "Face, Back, Right Wrist, Left Wrist", "Right Ankle, Right Foot", "Abdomen, Lungs, Throat", "Chest, Back", "Face, Right Arm, Left Knee", "Right Shoulder, Left Wrist", "Head, Neck, Back, Pelvic Region, Left Leg", "Back, Right Wrist", "Right Knee", "Right Arm, Left Arm", "Right Ankle", "Right Foot, Left Foot", "Head, Right Shoulder, Right Hand", "Right Ankle, Left Ankle", "Right Arm, Right Wrist", "Back, Right Arm, Left Arm, Left Knee", "Neck, Right Shoulder", "Right Shoulder, Right Hip", "Left Shoulder, Left Foot", "Abdomen, Left Shoulder, Left Hip", "Left Arm, Right Wrist, Right Hand", "Right Knee, Left Ankle", "Left Arm, Left Leg", "Left Hand, Left Knee", "Back", "Left Leg", "Back, Abdomen", "Right Arm, Right Wrist, Right Hand", "Right Shoulder, Right Wrist", "Right Wrist, NA", "Left Leg, Right Knee", "Whole Body", "Neck, Back, Left Shoulder", "Face, Nose, Right Wrist, Left Knee", "Face, Right Eye, Mouth, NA", "Neck, Back, Right Shoulder", "Back, Left Shoulder", "Back, Right Ankle, Left Ankle", "Right Hand, NA", "Back, Right Hand, Right Hip", "Face, Right Wrist, Left Wrist", "Left Shoulder, Left Arm", "Left Hand, NA", "Head, Right Shoulder", "Right Hip, Right Knee, Right Ankle", "Right Knee, Left Knee, Right Ankle, Left Ankle, Right Foot, Left Foot", "Right Ankle, Left Ankle, Right Foot, Left Foot", "Back, Right Shoulder, Right Wrist, Right Hand", "Chest, Left Wrist, Left Hip, Right Knee, Left Knee", "Pelvic Region", "Right Hip, Left Hip", "Right Knee, Right Ankle", "Neck, Abdomen, Right Shoulder, Left Shoulder, Right Knee, Left Knee", "Nose", "Back, Right Shoulder, Left Shoulder, Right Arm, Left Arm, Right Hand, Left Hand", "Chest, Right Shoulder", "Right Leg, Right Knee, Left Knee", "Chest, Right Arm, Left Arm, Right Hip, Left Hip, Right Leg, Left Leg", "Left Hand", "Right Hand, Left Hand", "Left Shoulder", "Neck", "Neck, Right Shoulder, Left Shoulder", "Right Shoulder, Left Shoulder, Right Arm, Left Arm, Right Hand, Left Hand", "Right Eye, Right Foot", "Left Arm, Right Hand", "Nose, Right Arm", "Back, Right Knee", "Neck, Right Shoulder, Right Arm, Right Wrist", "Head, Back", "Right Wrist, Left Wrist, Right Knee, Left Knee", "Left Wrist", "NA", "Face, Right Eye, Left Eye", "Abdomen", "Left Foot", "Back, Right Shoulder", "Back, Right Leg", "Right Leg", "Right Leg, Left Leg, Right Knee, Left Knee", "Right Shoulder, Right Knee", "Right Shoulder, Left Shoulder, Right Wrist", "Left Shoulder, Left Wrist", "Right Shoulder, Right Arm, Right Knee", "Left Shoulder, Left Hip", "Left Arm, Left Hip, Left Leg", "Right Arm, Right Hand", "Neck, Right Shoulder, Right Arm, Right Hand", "Neck, Back, Right Shoulder, Left Shoulder, Right Arm, Left Arm, Right Hip, Left Hip"]
    },
    {
      "ColumnName": "COSTCENTERNAME",
      "DataType": "varchar",
      "ColumnDetails": "The name of the Cost Center assigned to the ETS Event",
      "Important Notes": "",
      "CategoricalValues": None
    }
  ]
}
"""

proactive_metrics_field_description = """
    {
    "Table": "gq.vw_RPT_Proactive_Metrics",
    "Alias": "PROACTIVE_METRICS",
    "TableDescription": "Contains information related to RMBWA (Risk Management by Walking Around) findings, and corrective actions.",
    "ImportantNotes": [
        "The following filters should be applied in most cases unless the user specifically specifies otherwise:",
        "RMBWASTATUS <> 'Deleted'",
        "When performing mathematical operations on INT type columns convert them to Floats first"
    ],
    "Columns": [
        {
        "ColumnName": "RMBWAEVENTID",
        "ColumnDetails": "This is the unique record id for each RMBWA (Risk Management by walking around) record. Important note: there can be more than one record with an event id. For example, each CAPA gets a new line. When user requests count of RMBWAs or events always use count of unique event ids instead of a raw count of rows.",
        "CategoricalValues": null,
        "DataType": "int"
        },
        {
        "ColumnName": "CAPA",
        "ColumnDetails": "The CAPA (Corrective and Preventive Action) for this particular RMBWA (Risk Management by walking around) record",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "CAPAOWNER",
        "ColumnDetails": "The owner for the CAPA (Corrective and Preventive Action) for this particular RMBWA (Risk Management by walking around) record",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "CAPASTATUS",
        "ColumnDetails": "The status for the CAPA (Corrective and Preventive Action) for this particular RMBWA (Risk Management by walking around) record. Important note: Unless the user specifically asks for \"Deleted\" CAPASTATUS filter them out in any query.",
        "CategoricalValues": ["Closed", "", "Deleted", "Open"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "CAPAASSIGNEDDATE",
        "ColumnDetails": "When the CAPA (Corrective and Preventive Action) was assigned to the owner",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "CAPACOMPLETEDDATE",
        "ColumnDetails": "The date that the CAPA (Corrective and Preventive Action) was completed",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "CONDUCTEDBY",
        "ColumnDetails": "The person or employee that conducted the RMBWA (Risk Management by walking around)",
        "CategoricalValues": null,
        "Important Notes": "Names are formatted in the following way: 'Lastname, Firstname' ",
        "DataType": "varchar"
        },
        {
        "ColumnName": "EHSRISKCATEGORY",
        "ColumnDetails": "The Risk Category observed by the person conducting the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Material Handling", "Elevated Work (> 4ft)", "Sharps Hazard", "Overhead Hazard", "Fire Hazard", "Process/Procedure", "Access/Egress", "Compress Gas Inactive", "PPE", "Stormwater", "Hazardous Energy (LOTO)", "Hand/Power Tool", "COVID-19 Other", "Slip/Trip/Fall", "Vehicle", "Biological", "Seismic", "Hazardous Waste", "Waste Water", "Other Inactive", "Life Safety System/Alarm", "Universal Waste", "Electrical Hazard (not-LOTO)", "Noise/Lighting", "Chemical Related", "Confined Space", "Housekeeping", "Equipment Discrepancy", "COVID-19 Social Distancing", "Ergo"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "RMBWADATE",
        "ColumnDetails": "The date that the RMBWA (Risk Management by walking around) was performed",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "RMBWASTATUS",
        "ColumnDetails": "The status of the RMBWA (Risk Management by walking around) record. Important note: Unless the user specifically asks for \"Deleted\" RMBWASTATUS filter them out in any query.",
        "CategoricalValues": ["Closed", "Open", "Deleted"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "FUNCTIONALGROUP",
        "ColumnDetails": "The functional group for the person that performed the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Sabre/ELD", "C&F and Central Engineering", "HRS", "Exec Staff", "Dielectric Etch Product Group", "FITS", "Semiconductor Process & Integration", "Global Workplace Solutions", "HVM - Livermore", "HVM - Korea", "HRBPs", "Dielectric Marketing", "Business Resilience & Security", "KAT/GPS", "Product Safety", "Business and Enterprise Solutions Team", "Etch Engineering", "LIGHT", "Sales Operations", "Investor Relations", "Product Materials Technology", "Corporate Strategy", "Digital Workplace", "Global Products Group Business Development and Product Marketing", "Deposition Product Marketing and Business Development", "GIS India", "Regional Operations - Micron", "Regional Operations - China", "Spares Ops", "Customer Interface (KAT/CTM)", "LMT", "Global Product Operations", "Reliant", "Surface Integrity Group", "Regional Product Support (RPS) - Corproate", "Global Quality", "Metryx", "Computational Process", "Supply Chain", "Logic Process", "Legal", "Striker Oxide", "Product Specialists", "Global Trade and Government Affairs", "ALD", "LFW - Low Fluorine Tungsten", "Shared Services", "ESC Technology", "Product Marketing and BD", "Deposition Product Group", "Robotics", "Memory", "Product Ops", "Semiverse Solutions Operations", "Regional Finance", "Engineering Services", "Gas Delivery Technology", "Product and Program Management", "Intellectual Property", "Asia Communications", "Deposition Program and Product Management", "Dry Resist", "Velocity Labs", "Semiverse Solutions Products", "CSBG Engineering", "WETS - Clean", "GIS Northwest", "ALD / CVD Metals", "Facilities Services", "HVM - Villach", "Production", "Deposition Engineering", "Global End-User Technology and Services", "C&F", "Products & Services", "Semiverse Solutions Engineering", "Strategic Programs", "Corp Controller", "Engineering Leadership Team", "BU Finance", "Advanced Technology Development", "Business Development", "Metrology Services", "Etch EI Technology", "Product Marketing", "India Management", "Advanced Technology Integration", "Engineering", "RTG - Regional Technical Group", "Regional Operations - Korea", "Etch Product Marketing and Business Development Org Unit", "Lab Operations", "GIS APAC", "HVM - Penang", "Clean Product Line", "Global Logistics & SOPP", "GWS Bus Ops", "Business Operations", "Etch Operations", "Global Human Resources"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "GOODCATCHTYPE",
        "ColumnDetails": "The type of \"Good Catch\" for the RMBWA (Risk Management by walking around). It's basically what category of finding from the RMBWA",
        "CategoricalValues": ["Quality", "EHS", "Security"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "QUARTER",
        "ColumnDetails": "The Quarter of the RMBWA (Risk Management by walking around), example value: 2023Q1, 2022Q4",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "ETSLINK",
        "ColumnDetails": "The URL link to the RMBWA (Risk Management by walking around)",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "MONTHYEAR",
        "ColumnDetails": "Month and Year of the RMBWA, format example: Jan2016",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "MONTH",
        "ColumnDetails": "Month of the RMBWA, format example: Mar",
        "CategoricalValues": ["Apr", "Jul", "Aug", "Mar", "Nov", "Dec", "Sep", "Jun", "Feb", "Jan", "Oct", "May"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "CAPALEADTIME",
        "ColumnDetails": "The lead time for CAPA (Corrective and Preventive Action) completion",
        "CategoricalValues": null,
        "DataType": "int"
        },
        {
        "ColumnName": "MAJORSITEORREGION",
        "ColumnDetails": "The major site or region where the RMBWA was performed",
        "CategoricalValues": ["SE Asia", "Salzburg", "Japan", "3.P.L - Inactive", "Fremont", "Livermore", "Bristol - Inactive", "Silfex - Inactive", "EMEA", "Tualatin", "India", "Batu Kawan", "Korea", "Malaysia MFG", "LMK", "N. America", "San Jose - Inactive", "China", "KTC", "", "Yongin", "Taiwan", "Villach"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "VPORGNAME",
        "ColumnDetails": "The VP Organization for the person conducting the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Singapore", "Business Development/ Sales Operations", "GRST - Global Resilience, Security & Transformation", "Advanced Technology Development", "OCTO - Office Of The CTO", "Global Products Group", "Strategic Programs", "Global Finance", "Corporate Development", "Global Operations", "Global Information Systems", "Corporate Communications", "GCO - Global Customer Operations", "Deputy Head - GPG", "Pilot Operations", "CSBG - Customer Support Business Group", "Korea Corporate Office", "Chief Financial Officer", "CEO Staff", "Global Quality", "Deposition Product Group", "Advanced Equipment & Process Control", "Legal", "Japan", "Sales & Field Operations NA & Europe", "Global Human Resources", "Chief Operating Officer", "Clean Product Line", "Advanced Packaging", "Global Products Engineering", "APAC Chairman", "Etch Product Group", "China", "10112961", "Taiwan", "OCTO"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "BUSINESSGROUPNAME",
        "ColumnDetails": "The business group for the person conducting the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Corporate Business Operations", "Global Logistics and SOPP", "Pilot Operations", "Dry Resist", "CSBG - Customer Support Business Group", "India Management", "KR Samsung Account", "Order Management", "Advanced Technology Development", "SG Field Process", "Regional Operations - Japan", "Regional Operations - Intel", "Sales/Business Development", "CH SMIC Account", "Regional Operations - Singapore/APCO", "NST SALES - ADMIN", "DE Logic & Patterning Technology", "Deposition Business Unit", "Advanced Technology Integration", "Global IT Operations", "JP Operations", "Corporate Financial Planning & Analysis", "Etch Product Group Marketing", "Dielectric Deposition, ALD/HDP/Flowable", "EPD and Engineering", "China", "Conductor Etch Logic Product Line", "Corp Marketing", "KR Customer Service Business Group", "Operations", "Talent Acquisition", "Technology", "Metrology Services", "Taiwan Technology Center", "Business Development", "GIS Business Operations", "Engineering", "Global Human Resources", "Regional Operations - Korea", "Etch Business Unit", "AEPC SW & Architecture", "Bevel", "Metal Deposition, ECP/ELD", "TW RBO 2", "Strategic Integrated Communications", "Regional Operations - China", "Sales & Field Operations Europe", "CEO Staff", "Global Product Operations", "Metryx", "Surface Integrity Group - SIG", "TW OSAT", "SG Memory", "Etch and Clean Software & Controls", "Surface Integrity Group", "Dry 2 -OEM & Services", "Process Analytics and Control Engineering", "FP&A", "Lab Operations", "CPG Spin Clean 'Systems Engineering", "Global Customer Operations", "Global Logistics & SOPP", "Product Group Marketing", "Direct Metals", "Reliant", "Global Quality", "CPG Supply Chain", "Corporate Quality", "Supply Chain", "Global Staffing & Mobility", "Deposition Product Group", "Legal", "Product Specialists", "Global Trade and Government Affairs", "ALD", "Tua Pilot MFG & ENG", "Electrical and Design Engineering", "Advanced Equipment & Process Control", "DPG Business Development and Marketing", "CSBG Spares", "AEPC Marketing", "Etch Emerging Tech & Knowledge Products", "SG CSBG", "Business Operations", "Metal Deposition, Packaging", "Japan Quality & Safety", "CPG Software", "RTG - Regional Technical Group", "KR OSAT", "Chief Operating Officer", "Albany Site Management &Technology", "TW VP - TSMC Account Executive", "Global Products Engineering", "Wet Processing", "DFS - Direct Field Service Mgmt", "Dielectric Etch", "KR Hynix Account", "Enterprise Applications", "Etch Product Group", "Account mgmt"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "LAMBUILDING",
        "ColumnDetails": "The lam building where the RMBWA (Risk Management by walking around) was conducted",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "INSPECTIONLOCATION",
        "ColumnDetails": "The specific area within a lam building or property where the RMBWA (Risk Management by walking around) was conducted",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "WHOCONDUCTEDRMBWA",
        "ColumnDetails": "The name of the person who conducted the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Individual Contributor", "Supervisor / Manager"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "SUBMITTEDBY",
        "ColumnDetails": "The name of the person that submitted the RMBWA (Risk Management by walking around)",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "MANAGER",
        "ColumnDetails": "The manager of the person that submitted the RMBWA (Risk Management by walking around)",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "DESCRIPTION",
        "ColumnDetails": "A description of the RMBWA (Risk Management by walking around) event, and the findings, or lack of findings while conducting the RMBWA",
        "CategoricalValues": null,
        "DataType": "varchar"
        },
        {
        "ColumnName": "CAPAOwnerVpOrg",
        "ColumnDetails": "The VP organization of the CAPA (Corrective and Preventive Action) owner",
        "CategoricalValues": ["GRST - Global Resilience, Security & Transformation", "Etch Product Group", "Global Finance", "Global Information Systems", "OCTO - Office Of The CTO", "GCO - Global Customer Operations", "Global Products Group", "Deposition Product Group", "Global Operations", "CSBG - Customer Support Business Group", "CEO Staff"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "CAPAOwnerBG",
        "ColumnDetails": "The business group for the CAPA (Corrective and Preventive Action) owner",
        "CategoricalValues": ["Information Security", "India Management", "Product Development", "Dry Resist", "Taiwan Technology Center", "Admin", "Regional Finance", "Global Treasury", "Global Tax", "Global Workplace Solutions", "Business Resilience & Security", "Exec Staff", "Enterprise Infrastructure & Cloud Services", "Regional Operations - Korea", "FP&A", "Global Logistics & SOPP", "Business Operations", "Global Human Resources", "Product Group Marketing", "Global Products Engineering", "Wet Processing", "Enterprise Applications", "Etch Product Group", "Dielectric Etch", "Aether Product Group", "Enterprise Analytics and Engineering", "FITS", "Business and Enterprise Solutions Team", "Etch Engineering", "Semiverse Solutions", "Regional Operations - Micron", "Global Products Group Business Development and Product Marketing", "Corporate Communications", "Business Unit IT", "Regional Operations - Global Foundries/NARO", "Global Information Systems", "Product Marketing & Business Development", "GCO - Global Customer Operations", "Integrated Technologies and Systems", "CSBG - Customer Support Business Group", "Order Management", "Regional Operations - Japan", "Regional Operations - Intel", "Regional Operations - Singapore/APCO", "Sales/Business Development", "Business Development & Sales Operations", "Corporate Planning & Transformation", "India Operations", "IT Service Delivery", "Regional Operations - China", "Metryx", "Surface Integrity Group", "Global Product Operations", "GIO - Global Installed Base Operations", "Korea Technology Center", "Computational Products", "Deposition Product Group", "ALD", "Legal", "Advanced Process Development", "ALD / CVD Metals", "OCTO Staff", "Production", "Deposition Engineering", "Integration modeling and services", "Global Operations", "PECVD", "Regional Operations - Europe", "OCTO - Office Of The CTO", "Spares/Logistics"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "Customer",
        "ColumnDetails": "The customer, if any, impacted by the RMBWA (Risk Management by walking around) event",
        "CategoricalValues": ["Renesas Electronics Corp", "Intel Corporate", "Fairchild Semiconductor", "NANYA", "Innostar Semiconductor - Shanghai", "Advance Semiconductor Engineering", "Jiangsu Advanced Memory", "Ningbo Semiconductor International Corp", "Advanced Micro Foundry Pte Ltd", "Hangzhou Silan", "United Test and Assembly Center (UTAC)", "A STAR Research Entities", "Murata Electronics", "Communication Systems Equipment", "Skyworks Solutions", "Epson", "Yamaha Semiconductor", "LUXSHARE ELECTRONIC (KUNSHAN)", "Facebook Technologies, LLC", "Zhejiang ICsprout Semiconductor", "TF AMD Micrelectronics (Penang) Sdn Bhd", "Ichor Systems Ltd.", "ESPROS", "General Dynamics", "VIshay", "Blackwatch International Corp", "Fuji Electric", "Murata Integrated Passive Solutions", "Shenzhen Pensun Technology Co., Ltd.", "Macronix", "Ningbo TRS Microelectronics", "ABB Power Grids Switzerland Ltd", "Seagate", "Microsemi Integrated Products", "U.C. Berkeley", "Dongguan Guangmao Technology Co., Ltd.", "Akoustis, Inc.", "Wuhan Chuxing Technology", "Maxscend Microelectronics Company Ltd.", "Huatian Group", "HuaHong Group", "Tower Semiconductor Ltd.", "Tsinghua Unigroup", "Japan Semiconductor", "IRay Technology Hefei", "Scientific and Manufacturing Complex", "Macom", "Kionix Inc", "Air Products Electronic Chemicals", "Advanced Wireless", "Rohm and Haas", "L-3 Communication", "Hunan Jiechuwei Semiconductor Technology", "SCS HighTech", "Microchip", "Micron Technology", "Medtronic", "Hiksvision", "SK Hynix", "DIODES Incorporated", "Innotron Memory Co., Ltd", "CSBG", "Winstek Semiconductor", "Cree Inc.", "SOITEC", "MIT Lincoln Labs", "Semefab Scotland Ltd.", "Jiangsu Changjiang Electronics Technolog", "Canon", "Analog Devices", "Runpeng semiconductor (Shenzhen) Co., LT", "PSMC", "Wuhan Xinxin Semi Mfg Co. Ltd", "Taiwan Semiconductor Research Inst NARL", "LumiLED", "ATX Semiconductor(Suzhou)", "Shanghai Simgui", "SiEn (Qingdao) Integrated Circuits", "Institute of Microelectronics", "Cabot Corporation", "Advance Technology Material Inc", "Taiwan Semiconductor Manufacturing Corp. (TSMC)", "Shanghai Advanced Research", "NXP Semiconductors", "Galaxycore Zhejiang Limited Corp", "Texas Instruments", "Beijing Oriental Science & Technology", "STMicroelectronics", "Hewlett Packard", "College of NSE", "International Semiconductor Products Pte", "Draper Labs", "RF360 Europe GmbH", "Skorpios Technologies", "Plessey Semiconductor", "Ji Guang Semiconductor (Shaoxing) Corp.", "M/A-Com", "Rohm", "Sensirion"],
        "DataType": "varchar"
        },
        {
        "ColumnName": "RMBWATime",
        "ColumnDetails": "The time that the RMBWA (Risk Management by walking around) was performed",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "CustomerFab",
        "ColumnDetails": "The Customer Fab that the RMBWA (Risk Management by walking around) was performed at if any",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EHSRiskSeverity",
        "ColumnDetails": "The risk severity of the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Major", "Minor", "Moderate"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "ProductRelated",
        "ColumnDetails": "Whether there was a Lam Product related to the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["No", "Yes"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "ProductLocation",
        "ColumnDetails": "The location of the lam product related to the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["0"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EHSCausalCategory",
        "ColumnDetails": "The Causal Category of the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Machine/Equipment", "Management/Resources", "Mother Nature", "People/Behavior", "Process/Procedures", "Training/Skills", "Work Environment"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EHSCausalFactor",
        "ColumnDetails": "The Causal Factors related to the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["PPE Available but Not Used", "Inadequate Warning System/Alarm", "Inattentive Behavior", "Defective Equipment/Tool", "Process inadequate", "Training Insufficient", "Inadequate Maintenance", "Failure to follow process/procedure", "Inclement weather or natural environmental hazards beyond control", "Lack of Training", "Inadequate Design", "Condition of Equipment", "Inadequate Preventive Maintenance", "Horseplay", "Procedure Not Developed", "Inadequate Illuminuation", "Procedure Insufficient", "PPE Unavailable/Inadequate", "Unable to Determine", "Failure to conduct adequate safety pass-down or communicate", "Lack of instructions/direction", "Workstation Layout Inadequate", "Fail to Follow Training", "Fatigue", "Necessary resources not available", "Improper Lifting/Pushing/Pulling", "Guard or Barrier Missing", "Age of Equipment"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "ProductName",
        "ColumnDetails": "The Product Name if there are any related to the RMBWA (Risk Management by walking around)",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "IsStopWorkRequired",
        "ColumnDetails": "Did someone have to stop work as a result of this RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["No", "Yes"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "RMBWAModifiedDate",
        "ColumnDetails": "The date in which the RMBWA was last modified",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "QualityRiskCategory",
        "ColumnDetails": "The risk category for the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Environment", "Hand tool or equipment", "Method - Procedure", "People/Behavior"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "QualityCausalFactor",
        "ColumnDetails": "If there was a related Quality Causal Category for the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["Negative Norms", "Lack of knowledge", "Tool not available", "Pressure", "Stress", "Lack of awareness", "Tool damaged or out of calibration", "Disorganized / messy jobsite", "Complacency", "Lack of resource", "Poor Team Work", "Lack of assertiveness", "Suspect items not segregated", "Poor lighting - difficult to see clearly", "Poor Communication", "Procedure not available at job site", "Inaccurate/incomplete or difficult to understand", "Fatigue", "Procedure not followed (violation)", "Incorrect tool being used", "Noisy - difficult to communicate", "Distraction"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "ShortTermContainment",
        "ColumnDetails": "The short term containment plan/action",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "FWORequired",
        "ColumnDetails": "Is a Work Order required as a result of the findings from this RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["No", "Yes"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "FWONumber",
        "ColumnDetails": "The number for the Work order if relevant",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationRequired",
        "ColumnDetails": "Is an escalation required for the RMBWA (Risk Management by walking around)",
        "CategoricalValues": ["", "No", "Yes"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "ActionTakenbyEscalationOwner",
        "ColumnDetails": "Actions if any that were taken by the escalation owner",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationStatus",
        "ColumnDetails": "The status of the escalation if any",
        "CategoricalValues": ["", "Closed", "Deleted", "Open"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationOwner",
        "ColumnDetails": "The name \"Lastname, Firstname\" of the escalation owner",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationOwnerVPOrg",
        "ColumnDetails": "The VP Org for the Escalation Owner",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationOwnerBG",
        "ColumnDetails": "The Business Group for the Escalation Owner",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationOwnerFG",
        "ColumnDetails": "The functional Group for the Escalation Owner",
        "CategoricalValues": null,
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "EscalationAssignedDate",
        "ColumnDetails": "The date on which the escalation if any was assigned",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "EscalationCompletedDate",
        "ColumnDetails": "The date on which the escalation if any was completed",
        "CategoricalValues": null,
        "DataType": "date"
        },
        {
        "ColumnName": "LocationBuildingName",
        "ColumnDetails": "The building name where the RMBWA was performed",
        "CategoricalValues": ["JPN41 (Kitakami)", "NY02 (Albany)", "CHN16 (Shanghai)", "CA10", "KOR38 (Icheon)", "CHN30 - Inactive", "OR10 (Building F)", "JPN22(Shin-Yokohama)", "JPN31(Hiroshima) - Inactive", "OR13 (Building L)", "TWN06 - Inactive", "FRA06 (Meylan)", "CA03", "KTC-1", "Production 3 - Inactive", "OR06 (Building B)", "Prototyping - Inactive", "KOR25 - Inactive", "TWN-05-Hsinchu(No.17 & 19)", "MAL01 (KHTP Business Center)", "Production 1A - Inactive", "GER08 (Dresden)", "CHN50 (Wuxi)", "NY07 (Fishkill)", "UT01 (Lehi)", "UK-01B (1255) - Inactive", "CA04", "NY04 - Inactive", "RK Fremont - Inactive", "Building 10", "ID02 (Boise) - Inactive", "MYS04", "JPN21(Oita)", "SIN02 (Woodlands)", "Building 1", "CA09", "RK Livermore - Inactive", "ITA01 (Agrate)", "AZ-05 (Phoenix)", "Kor34 (Yongin)", "Building 4", "TWN01-Hsinchu(No.22 & 24)", "CHN79 (Qingdao)", "CA03E Gottscho Lab", "RK Christy Fremont - Inactive", "JPN40 (Sakaemachi Building Hiroshima)", "OR12A (Building J)", "Other", "CHN48 (Huaian)", "CHN31 (Xian)", "CHN36 (Xiamen)", "Kor34 (Youngin)", "Building 3", "ID01 - Inactive", "KOR45 (Gyeon)", "Laboratory 3-4 - Inactive", "KOR30 - Inactive", "MYS03", "KOR37 (Hwaesong)", "CA32 MFG Floor", "OR08 (Building D)", "Production 1B - Inactive", "ISR01 - Inactive", "Building 9", "OR09 (Building E)", "NY03 - Inactive", "OR07 (Building C)", "UK-01A (1230/1240) - Inactive", "CHN44 (Nanjing)", "CHN28 - Inactive", "Building 13", "Production 1 - Inactive", "CA30", "CHN20 - Inactive", "Flushing Room - Inactive", "TX10 (Richardson)", "CA11", "KOR30 (Seongnam)", "JPN27(Yokkaichi)", "CA01", "TWN-26-Hsinchu(Gungdao 5 Rd)", "Building 6", "SIN01 - Inactive", "TWNX1-Hsinchu (TTC)", "CA08", "CHN41 (Beijing)", "TWN15-Tainan", "KOR33 (Osan)", "OR15 (Building Q)", "JPN36(Yamagata)", "Building 5", "WA04 - Inactive", "KOR24 - Inactive", "CHN35 - Inactive", "TWN24-Linko", "CHN43 - Inactive", "CA31 MFG Floor", "TWN-17-Hsinchu(No. 7)", "KOR39/44 (Osan Hanggyan Semi-tech)"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "PreviouslyReportedRMBWAFlag",
        "ColumnDetails": "Whether this RMBWA was reported before",
        "CategoricalValues": ["N", "Y"],
        "DataType": "nvarchar"
        },
        {
        "ColumnName": "PreviouslyReportedRMBWAID",
        "ColumnDetails": "The id of the related RMBWA",
        "CategoricalValues": null,
        "DataType": "int"
        },
        {
        "ColumnName": "IsFieldRegion",
        "ColumnDetails": "Did this RMBWA occur in the field",
        "CategoricalValues": ["0", "1"],
        "DataType": "bit"
        }
        ]
        }
        """

injured_body_part_field_description = """
    Table: gq.vw_Injured_Budy_Part
    Alias: INJURED_BODY_PART
    TableDescription: Contains information related to injuries in the workplace

    ColumnName: 
    - EVENTDATE
        Column Details: The Date that the injury occurred
        Categorical Values: None

    - EVENTID
        Column Details: The id for the event that caused the injury
        Categorical Values: None

    - EVENTTYPE
        Column Details: the type of event that caused the injury
        Categorical Values: ["Chemical Release - Air Emission", "Chemical Release - Spill", "EHS Management System Audit", "Fire/Explosion", "FLSS - Fire/HazMat Alarm", "Illness", "Injury", "Near Miss", "Odor", "Power Outage", "Property Damage/Business Impact", "Regulatory Agency Inspection"]

    - INJURYTYPE
        Column Details: The type of injury for this event
        Categorical Values: ["Abrasion/Scratch", "Chemical Exposure/Burn", "Contusion/Bruise", "Electrical Shock/Burn", "Fracture", "Laceration/Cut", "Office MSD", "Other", "Personal Medical", "Rash/Irritation", "Strain/Sprain", "Thermo/Burn"]

    - EVENTDESCRIPTION
        Column Details: the description of event that caused the injury
        Categorical Values: None

    - MAJORSITEREGION
        Column Details: The Major site or Region where the injury happened
        Categorical Values: ["SE Asia", "Fremont", "Livermore", "LMK", "N. America", "Japan", "Korea", "Villach", "Malaysia MFG", "EMEA", "Silfex - Inactive", "", "3.P.L - Inactive", "Tualatin", "Taiwan", "Silfex, OH", "Bristol - Inactive", "San Jose - Inactive", "KTC", "Salzburg", "India", "China"]

    - SPECIFICLOCATION
        Column Details: The specific location within a major site or Region. That an injury happened
        Categorical Values: None

    - BUSINESSGROUPNAME
        Column Details: The business group name involved with the injury
        Categorical Values: None

    - RESPONSIBLEMANAGER
        Column Details: The responsible manager Name for the employee that was injured
        Categorical Values: None

    - MODEOFINJURYDESCRIPTION
        Column Details: The text category of the mode of injury
        Categorical Values: ["Caught in/Caught on", "Contact with/Exposure to", "Fall from Height", "Motor Vehicle Accident", "Other", "Personal Medical", "Pinch/Crush", "Repetitive Motion (Chronic)", "Slip/Trip/Fall (Fall on same level)", "Strain/Sprain (Acute)", "Struck by (Hit by object)", "Struck on (Bumped into object)"]

    - EVENTCLASSIFICATION
        Column Details: The Tier classification of the event Tier n
        Categorical Values: ["Tier 0", "Tier 1", "Tier 2", "Tier 3", "Tier 4"]

    - INJURYCLASSIFICATION
        Column Details: The Classification of injury and whether it was recordable or not
        Categorical Values: ["First Aid", "No Treatment", "Non-Lam Injury", "Recordable", "Recordable LWD"]

    - BODYPART
        Column Details: The number value representing the body part that was injured
        Categorical Values: None

    - VPORGNAME
        Column Details: the vp organization of the injured person
        Categorical Values: None

    - FUNCTIONALGROUP
        Column Details: the functional group of the injured person
        Categorical Values: None

    - EVENTMONTH
        Column Details: The Month that the injury happened example value: Apr
        Categorical Values: ["Apr", "Jul", "Aug", "Mar", "Nov", "Dec", "Sep", "Jun", "Feb", "Jan", "Oct", "May"]

    - ETSLINK
        Column Details: The url link to the Injury record in ETS
        Categorical Values: None

    - CustomerName
        Column Details: The customer name if any that was related to the Injury
        Categorical Values: None
        """

reactive_metrics_sql_examples = """
[
    {
        input: "How many unique events occurred in 2022?",
        query: SELECT COUNT(DISTINCT EVENTID) AS UniqueEventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(EVENTDATE) = 2022 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What are the top three most common types of events?",
        query: SELECT TOP 3 EVENTTYPE, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY EVENTTYPE ORDER BY EventCount DESC;
    },
    {
        input: "What is the average time taken to close events in days?",
        query: SELECT AVG(DATEDIFF(DAY, EVENTDATE, EVENTCLOSEDDATE)) AS AvgCloseTime FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTCLOSEDDATE IS NOT NULL AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "How many events were classified as \"Tier 1\" and had a \"Closed\" status?",
        query: SELECT COUNT(DISTINCT EVENTID) AS Tier1ClosedEvents FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTCLASSIFICATION = 'Tier 1' AND EVENTSTATUS = 'Closed' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "Which region had the highest number of unique events?",
        query: SELECT TOP 1 MAJORSITEREGION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY MAJORSITEREGION ORDER BY EventCount DESC;
    },
    {
        input: "What is the distribution of injury classifications for events in 2021?",
        query: SELECT INJURYCLASSIFICATION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(EVENTDATE) = 2021 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY INJURYCLASSIFICATION;
    },
    {
        input: "How many events involved a \"Chemical Release - Spill\" and required an ERT response?",
        query: SELECT COUNT(DISTINCT EVENTID) AS ChemicalSpillERTEvents FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTTYPE = 'Chemical Release - Spill' AND ERTMERTRESPONSE = 'Yes' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is the average CAPA lead time for completed CAPAs?",
        query: SELECT AVG(CAPALEADTIME) AS AvgCAPALeadTime FROM gq.vw_RPT_Reactive_Metrics WHERE CAPASTATUS = 'Closed' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "How many events were submitted by each responsible manager in 2023?",
        query: SELECT RESPONSIBLEMANAGER, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(SUBMITTEDDATE) = 2023 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY RESPONSIBLEMANAGER;
    },
    {
        input: "What are the most common root causes of events that occurred during the night shift?",
        query: SELECT ROOTCAUSE_NONUMBER, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE SHIFT = 'Night Shift' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY ROOTCAUSE_NONUMBER ORDER BY EventCount DESC;
    },
    {
        input: "What is the total number of unique events that involved an evacuation?",
        query: SELECT COUNT(DISTINCT EVENTID) AS UniqueEvacuationEvents FROM gq.vw_RPT_Reactive_Metrics WHERE EVACUATION <> 'None' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "Which month had the highest number of unique events in 2022?",
        query: SELECT TOP 1 MONTH(EVENTDATE) AS EventMonth, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(EVENTDATE) = 2022 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY MONTH(EVENTDATE) ORDER BY EventCount DESC;
    },
    {
        input: "How many unique events were submitted but not yet closed?",
        query: SELECT COUNT(DISTINCT EVENTID) AS OpenSubmittedEvents FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTSTATUS = 'Submitted to EHS' AND EVENTCLOSEDDATE IS NULL AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is the average number of days between the event date and the submitted date?",
        query: SELECT AVG(DATEDIFF(DAY, EVENTDATE, SUBMITTEDDATE)) AS AvgDaysToSubmit FROM gq.vw_RPT_Reactive_Metrics WHERE SUBMITTEDDATE IS NOT NULL AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "How many unique events were classified under \"Injury\" and occurred in the \"N. America\" region?",
        query: SELECT COUNT(DISTINCT EVENTID) AS InjuryEventsInNA FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTTYPE = 'Injury' AND EVENTSTATUS <> 'Deleted' AND MAJORSITEREGION = 'N. America' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is the distribution of events by event classification for the year 2023?",
        query: SELECT EVENTCLASSIFICATION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(EVENTDATE) = 2023 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY EVENTCLASSIFICATION;
    },
    {
        input: "How many unique events had a CAPA status of \"Open\" and were related to \"Process/Procedures\"?",
        query: SELECT COUNT(DISTINCT EVENTID) AS OpenCAPAProcessEvents FROM gq.vw_RPT_Reactive_Metrics WHERE CAPASTATUS = 'Open' AND EVENTSTATUS <> 'Deleted' AND ROOTCAUSE_NONUMBER = 'Process/Procedures' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "Which specific location had the most unique events in 2021?",
        query: SELECT TOP 1 SPECIFICLOCATION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR(EVENTDATE) = 2021 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY SPECIFICLOCATION ORDER BY EventCount DESC;
    },
    {
        input: "How many unique events involved a \"Building Evacuation\" and occurred during the \"Day Shift\"?",
        query: SELECT COUNT(DISTINCT EVENTID) AS DayShiftBuildingEvacuations FROM gq.vw_RPT_Reactive_Metrics WHERE EVACUATION = 'Building Evacuation' AND SHIFT = 'Day Shift' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is the average RCCA cycle time for events that were classified as \"Tier 2\"?",
        query: SELECT AVG(RCCACYCLEDAYS) AS AvgRCCACycleTime FROM gq.vw_RPT_Reactive_Metrics WHERE EVENTCLASSIFICATION = 'Tier 2' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is my most frequent non-blank injury type for each month in 2023?",
        query: SELECT MONTH([EVENTDATE]) AS [Month], [INJURYTYPE], COUNT(DISTINCT EVENTID) AS [TypeCount] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE YEAR([EVENTDATE]) = 2023 AND [INJURYTYPE] IS NOT NULL AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY MONTH([EVENTDATE]), [INJURYTYPE] ORDER BY Month, [TypeCount] DESC;
    },
    {
        input: "How many incidents in 2023 related to LOTO?",
        query: SELECT TOP 10000 EVENTDESCRIPTION FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR([RMBWADATE]) = 2023 AND [EVENTDESCRIPTION] LIKE '%LOTO%' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "What is my most frequent injury type?",
        query: SELECT TOP 1 [INJURYTYPE], COUNT(DISTINCT EVENTID) AS [TypeCount] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE [INJURYTYPE] IS NOT NULL AND [INJURYTYPE] != '' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY [INJURYTYPE] ORDER BY [TypeCount] DESC;
    },
    {
        input: "how many recordable injuries occurred in 2022?",
        query: SELECT COUNT(DISTINCT [EVENTID]) AS RecordableInjuries2022 FROM gq.vw_RPT_Reactive_Metrics WHERE [INJURYCLASSIFICATION] in ('Recordable LWD', 'Recordable') AND YEAR([EVENTDATE]) = 2022 EVENTSTATUS <> 'Deleted' AND AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: "How many ETS events are excluded from reporting"
        query: SELECT COUNT(DISTINCT [EVENTID]) AS EXCLUDEDEVENTS FROM gq.vw_RPT_Reactive_Metrics WHERE EXCLUDEINCIDENTFROMBI = '1' EVENTSTATUS <> 'Deleted'
    },
    {
        input: "How many ETS events occurred or happened in the Field?"
        query: SELECT COUNT(DISTINCT [EVENTID]) AS EXCLUDEDEVENTS FROM gq.vw_RPT_Reactive_Metrics WHERE ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) AND LOWER([MAJORSITEREGION]) LIKE '%field%' EVENTSTATUS <> 'Deleted'
    },
        input: what are the top 10 root causes for slip trip fall ets events in 2022?
        query: SELECT TOP 10 [ROOTCAUSE] FROM gq.vw_RPT_Reactive_Metrics WHERE YEAR([EVENTDATE]) = 2022 AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) AND [MODEOFINJURYDESCRIPTION] = 'Slip/Trip/Fall (Fall on same level)' GROUP BY [ROOTCAUSE] ORDER BY COUNT(DISTINCT [EVENTID]) DESC;
    },
    {
        input: How many ETS events were submitted by each submitter?
        query: SELECT SUBMITTERNAME, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY SUBMITTERNAME;
    },
    {
        input: List all ETS events that occurred in the "CA03" building.
        query: SELECT * FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE LOCATIONBUILDINGNAME = 'CA03' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: Find the number of severe injuries reported in ETS events.
        query: SELECT COUNT(DISTINCT [EVENTID]) AS SevereInjuryCount FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE SEVEREINJURIES = 'Yes' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: Retrieve ETS events related to a lam tool.
        query: SELECT * FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE LAMRESEARCHTOOLRELATED = 'Yes' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: How many ETS events involved a preventable evacuation?
        query: SELECT COUNT(DISTINCT [EVENTID]) AS PreventableEvacCount FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE PREVENTABLEEVAC = 'Yes' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: Retrieve ETS events that occurred in a field region.
        query: SELECT * FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE ISFIELDREGION = 1 AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: List all ETS events with severe injuries and the body parts affected.
        query: SELECT EVENTID, SEVEREINJURIES, BODYPARTS FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE SEVEREINJURIES = 'Yes' AND EVENTSTATUS <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: How many serious injuries were there in 2022
        query: SELECT COUNT(DISTINCT [EVENTID]) AS SeriousInjuryCount FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE [SEVEREINJURIES] = 'Yes' AND YEAR([EVENTDATE]) = 2022 AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: provide detail on the ETS events related to vector extreme
        query: SELECT EVENTID, EVENTSTATUS, EVENTTYPE, PRODUCTNAME FROM gq.vw_RPT_Reactive_Metrics AS REACTIVE_METRICS WHERE [PRODUCTNAME] like '%Vector% %Extreme%' AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null);
    },
    {
        input: On average per year, how many incidents are related to chemical spills?
        query: SELECT YEAR([EVENTDATE]), [EVENTTYPE], AVG(CAST(COUNT(DISTINCT [EVENTID]) AS FLOAT)) OVER (PARTITION BY YEAR([EVENTDATE])) AS AvgIncidentsPerYear FROM gq.vw_RPT_Reactive_Metrics WHERE [EVENTTYPE] = 'Chemical Release - Spill' AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' or [EXCLUDEINCIDENTFROMBI] is null) GROUP BY [EVENTTYPE], YEAR([EVENTDATE]) Order BY YEAR([EVENTDATE]);
    },
    {
        input: "Which site has the most LOTO related incidents?",
        query:SELECT TOP 1 [MAJORSITEREGION] AS SITE FROM gq.vw_RPT_Reactive_Metrics WHERE [EVENTDESCRIPTION] LIKE '%LOTO%' AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL) GROUP BY [MAJORSITEREGION] ORDER BY COUNT(DISTINCT [EVENTID]) DESC
    },
    {
        input: "On average, how many incidents result in hospitalization per year?",
        query:"SELECT AVG(CAST([AnnualCount] AS FLOAT)) AS [AvgHospitalizationIncidentsPerYear] FROM (SELECT YEAR([EVENTDATE]) AS [Year], COUNT(DISTINCT [EVENTID]) AS [AnnualCount] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE  ( ([EVENTDESCRIPTION] LIKE '%hospitalization%' OR [EVENTDESCRIPTION] LIKE '%hospitalisation%' OR [EVENTDESCRIPTION] LIKE '%hospitalized%' OR [EVENTDESCRIPTION] LIKE '%hospitalised%' OR [EVENTDESCRIPTION] LIKE '%hospital%') OR ([SEVEREINJURIES] = 'Yes') OR ([EVENTTYPE] = 'Injury' AND [EVENTCLASSIFICATION] = 'Tier 3') ) AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL) GROUP BY YEAR([EVENTDATE])) AS AnnualCounts;"
    },
    {
        input: "Have any chemical exposure incidents resulted in hospitalization?",
        query: SELECT [EVENTDESCRIPTION], [SEVEREINJURIES], [INJURYTYPE], [EVENTCLASSIFICATION] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE ( ([EVENTDESCRIPTION] LIKE '%hospitalization%' OR [EVENTDESCRIPTION] LIKE '%hospitalisation%' OR [EVENTDESCRIPTION] LIKE '%hospitalized%' OR [EVENTDESCRIPTION] LIKE '%hospitalised%' OR [EVENTDESCRIPTION] LIKE '%hospital%') OR ([SEVEREINJURIES] = 'Yes') OR ([EVENTTYPE] = 'Injury' AND [EVENTCLASSIFICATION] = 'Tier 3')) AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL) AND [INJURYTYPE] = 'Chemical Exposure/Burn'
    },
    {
        input: "What percentage of injuries required medical treatment beyond first aid?",
        query: "SELECT (CAST(COUNT(DISTINCT CASE WHEN [INJURYCLASSIFICATION] IN ('Recordable', 'Recordable LWD') THEN [EVENTID] END) AS FLOAT) / CAST(COUNT(DISTINCT [EVENTID]) AS FLOAT)) * 100 AS [INJURYSEVERITY] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL) AND [EVENTTYPE] = 'Injury';"
    },
    {
        input: "What is the most common cause of evacuations?",
        query: "SELECT TOP 1 [CAUSALFACTOR], COUNT(DISTINCT [EVENTID]) AS EventCount FROM gq.vw_RPT_Reactive_Metrics  WHERE [EVACUATION] <> 'None' AND [CAUSALFACTOR] <> '' AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL) GROUP BY [CAUSALFACTOR]"
    },
    {
        input: "How many OSHA recordables in Tualatin Logistics in 2024",
        query: "SELECT COUNT(DISTINCT [EVENTID]) AS [OSHA_Recordables_Tualatin_GlobalLogistics_2024] FROM [gq].[vw_RPT_Reactive_Metrics] WHERE [INJURYCLASSIFICATION] IN ('Recordable', 'Recordable LWD') AND YEAR([EVENTDATE]) = 2024 AND [MAJORSITEREGION] = 'Tualatin' AND [FUNCTIONALGROUP] in('Global Logistics', 'Global Logistics and SOPP') AND [EVENTSTATUS] <> 'Deleted' AND ([EXCLUDEINCIDENTFROMBI] <> '1' OR [EXCLUDEINCIDENTFROMBI] IS NULL);"
    },
    ]
"""

proactive_metrics_sql_examples = """
    [
        {
            input: "How many unique RMBWA events were conducted in 2023?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS UniqueEvents FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR(RMBWADATE) = 2023 AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "What are the top 3 CAPA owners with the most open CAPAs?",
            query: SELECT TOP 3 CAPAOWNER, COUNT(*) AS OpenCAPACount FROM gq.vw_RPT_Proactive_Metrics WHERE CAPASTATUS = 'Open' AND RMBWASTATUS <> 'Deleted' GROUP BY CAPAOWNER ORDER BY OpenCAPACount DESC;
        },
        {
            input: "Find the average CAPA lead time for each EHS risk category.",
            query: SELECT EHSRISKCATEGORY, AVG(CAPALEADTIME) AS AvgLeadTime FROM gq.vw_RPT_Proactive_Metrics AND RMBWASTATUS <> 'Deleted' GROUP BY EHSRISKCATEGORY;
        },
        {
            input: "List all unique RMBWA events conducted by \"Alexander, Jason\".",
            query: SELECT DISTINCT RMBWAEVENTID FROM gq.vw_RPT_Proactive_Metrics WHERE CONDUCTEDBY = 'Alexander, Jason' AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "How many unique events have a status of 'Closed' and were conducted in the \"Fremont\" region?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS ClosedEvents FROM gq.vw_RPT_Proactive_Metrics WHERE RMBWASTATUS = 'Closed' AND MAJORSITEORREGION = 'Fremont';
        },
        {
            input: "What is the most common risk category observed in 2022?",
            query: SELECT TOP 1 EHSRISKCATEGORY, COUNT(DISTINCT RMBWAEVENTID) AS CategoryCount FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR(RMBWADATE) = 2022 AND RMBWASTATUS <> 'Deleted' GROUP BY EHSRISKCATEGORY ORDER BY CategoryCount DESC;
        },
        {
            input: "Identify the top 5 buildings with the most RMBWA events.",
            query: SELECT TOP 5 LAMBUILDING, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics  AND RMBWASTATUS <> 'Deleted' GROUP BY LAMBUILDING ORDER BY EventCount DESC;
        },
        {
            input: "How many unique RMBWA events have a \"Good Catch\" type of \"EHS\"?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS EHSEvents FROM gq.vw_RPT_Proactive_Metrics WHERE GOODCATCHTYPE = 'EHS' AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "Find the total number of CAPAs completed in 2021.",
            query: SELECT COUNT(*) AS CompletedCAPAs FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR(CAPACOMPLETEDDATE) = 2021 AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "What are the top 3 functional groups with the highest number of RMBWA events?",
            query: SELECT TOP 3 FUNCTIONALGROUP, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics WHERE RMBWASTATUS <> 'Deleted' GROUP BY FUNCTIONALGROUP ORDER BY EventCount DESC;
        },
        {
            input: "What is the average CAPA lead time for events conducted by \"Anderson, Richard\" in 2023?",
            query: SELECT AVG(CAPALEADTIME) AS AvgLeadTime FROM gq.vw_RPT_Proactive_Metrics WHERE CONDUCTEDBY = 'Anderson, Richard' AND YEAR(RMBWADATE) = 2023  AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "List the top 5 CAPA statuses with the most occurrences.",
            query: SELECT TOP 5 CAPASTATUS, COUNT(DISTINCT RMBWAEVENTID) AS StatusCount FROM gq.vw_RPT_Proactive_Metrics WHERE RMBWASTATUS <> 'Deleted' GROUP BY CAPASTATUS ORDER BY StatusCount DESC;
        },
        {
            input: "How many unique events have been submitted by \"Hong, Gary\" with a \"Closed\" status?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS ClosedEventsByGary FROM gq.vw_RPT_Proactive_Metrics WHERE SUBMITTEDBY = 'Hong, Gary' AND RMBWASTATUS = 'Closed';
        },
        {
            input: "Find the number of unique RMBWAs per quarter for the year 2022.",
            query: SELECT QUARTER, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR(RMBWADATE) = 2022 AND RMBWASTATUS <> 'Deleted' GROUP BY QUARTER ORDER BY QUARTER;
        },
        {
            input: "What is the most frequent inspection location for events with a \"Fire Hazard\" risk category?",
            query: SELECT TOP 1 INSPECTIONLOCATION, COUNT(DISTINCT RMBWAEVENTID) AS LocationCount FROM gq.vw_RPT_Proactive_Metrics WHERE EHSRISKCATEGORY = 'Fire Hazard' AND RMBWASTATUS <> 'Deleted' GROUP BY INSPECTIONLOCATION ORDER BY LocationCount DESC;
        },
        {
            input: "List all unique CAPA owners who have completed CAPAs in 2024.",
            query: SELECT DISTINCT CAPAOWNER FROM gq.vw_RPT_Proactive_Metrics WHERE YEAR(CAPACOMPLETEDDATE) = 2024 AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "How many unique events were conducted in the \"Japan\" region with a \"Quality\" good catch type?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS QualityEventsInJapan FROM gq.vw_RPT_Proactive_Metrics WHERE MAJORSITEORREGION = 'Japan' AND GOODCATCHTYPE = 'Quality' AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "Determine the average number of days between CAPA assigned and completed dates for \"Closed\" CAPAs.",
            query: SELECT AVG(DATEDIFF(day, CAPAASSIGNEDDATE, CAPACOMPLETEDDATE)) AS AvgDaysToComplete FROM gq.vw_RPT_Proactive_Metrics WHERE CAPASTATUS = 'Closed' AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "Identify the top 3 managers with the most RMBWA events submitted.",
            query: SELECT TOP 3 MANAGER, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics WHERE RMBWASTATUS <> 'Deleted' GROUP BY MANAGER ORDER BY EventCount DESC;
        },
        {
            input: "What is the total number of unique events that have a \"Deleted\" status?",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS DeletedEvents FROM gq.vw_RPT_Proactive_Metrics WHERE RMBWASTATUS = 'Deleted';
        },
        {
            input: "What are the most common "good catches"",
            query: SELECT TOP 1 GOODCATCHTYPE, COUNT(DISTINCT RMBWAEVENTID) AS CountOf FROM gq.vw_RPT_Proactive_Metrics WHERE GOODCATCHTYPE <> '' AND RMBWASTATUS <> 'Deleted' GROUP BY GOODCATCHTYPE ORDER BY CountOf DESC;
        },
        {
            input: "How many housekeeping good catches are there",
            query: SELECT COUNT(DISTINCT RMBWAEVENTID) AS NumberOfHousekeepingRMBWAs FROM gq.vw_RPT_Proactive_Metrics WHERE [EHSRISKCATEGORY] = 'housekeeping' AND RMBWASTATUS <> 'Deleted';
        },
        {
            input: "List all RMBWA events that required stop work in the month of May." ,
            query:  SELECT RMBWAEVENTID, RMBWADATE, IsStopWorkRequired FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND MONTH = 'May' AND IsStopWorkRequired = 'Yes';
        },
        {
            input: "How many RMBWA events were conducted by each VP Organization in Q1 2023?",
            query: SELECT VPORGNAME, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND QUARTER = '2023Q1' GROUP BY VPORGNAME;
        },
        {
            input: "How many RMBWA events were reported by each business group in April?",
            query: SELECT BUSINESSGROUPNAME, COUNT(DISTINCT RMBWAEVENTID) AS EventCount FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND MONTH = 'Apr' GROUP BY BUSINESSGROUPNAME;
        },
        {
            input:  "List all RMBWA events with a major EHS risk severity." ,
            query: SELECT RMBWAEVENTID, EHSRiskSeverity, RMBWADATE FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND EHSRiskSeverity = 'Major';
        },
        {
            input: "Find all RMBWA events where a Lam Product was related.",
            query: SELECT RMBWAEVENTID, ProductRelated, ProductName FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND ProductRelated = 'Yes';
        },
        {
            input: "Retrieve RMBWA events that required stop work.",
            query: SELECT RMBWAEVENTID, IsStopWorkRequired, RMBWADATE FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND IsStopWorkRequired = 'Yes';
        },
        {
            input: "List all RMBWA events with machine or equipment causal category.",
            query: SELECT RMBWAEVENTID, EHSCausalCategory, RMBWADATE FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND EHSCausalCategory = 'Machine/Equipment';
        },
        {
            input: "Find all RMBWA events that have been previously reported." ,
            query: SELECT RMBWAEVENTID, PreviouslyReportedRMBWAFlag, PreviouslyReportedRMBWAID FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND PreviouslyReportedRMBWAFlag = 'Y';
        },
        {
            input: "Retrieve all RMBWA events that occurred in the field.",
            query: SELECT RMBWAEVENTID, IsFieldRegion, RMBWADATE FROM gq.vw_RPT_Proactive_Metrics AS PROACTIVE_METRICS WHERE RMBWASTATUS <> 'Deleted' AND IsFieldRegion = 1;
        }

        ]
        """

injured_body_part_sql_examples = """
    [
        {
            input: "How many distinct injury events occurred in 2015?",
            query: SELECT COUNT(DISTINCT EVENTID) AS DistinctInjuryEvents FROM gq.vw_Injured_Budy_Part WHERE YEAR(EVENTDATE) = 2015;
        },
        {
            input: "What are the top 5 most common types of injuries?",
            query: SELECT TOP 5 INJURYTYPE, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY INJURYTYPE ORDER BY EventCount DESC;
        },
        {
            input: "Which major site region had the highest number of distinct injury events in 2020?",
            query: SELECT TOP 1 MAJORSITEREGION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE YEAR(EVENTDATE) = 2020 GROUP BY MAJORSITEREGION ORDER BY EventCount DESC;
        },
        {
            input: "How many distinct injury events were classified as \"Tier 1\"?",
            query: SELECT COUNT(DISTINCT EVENTID) AS Tier1Events FROM gq.vw_Injured_Budy_Part WHERE EVENTCLASSIFICATION = 'Tier 1';
        },
        {
            input: "What is the distribution of injury types by month for the year 2019?",
            query: SELECT EVENTMONTH, INJURYTYPE, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE YEAR(EVENTDATE) = 2019 GROUP BY EVENTMONTH, INJURYTYPE ORDER BY EVENTMONTH, EventCount DESC;
        },
        {
            input: "List the top 3 responsible managers with the most distinct injury events under their supervision.",
            query: SELECT TOP 3 RESPONSIBLEMANAGER, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY RESPONSIBLEMANAGER ORDER BY EventCount DESC;
        },
        {
            input: "How many distinct injury events involved chemical exposure or burns?",
            query: SELECT COUNT(DISTINCT EVENTID) AS ChemicalExposureEvents FROM gq.vw_Injured_Budy_Part WHERE INJURYTYPE = 'Chemical Exposure/Burn';
        },
        {
            input: "What are the top 5 specific locations with the highest number of distinct injury events?",
            query: SELECT TOP 5 SPECIFICLOCATION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY SPECIFICLOCATION ORDER BY EventCount DESC;
        },
        {
            input: "How many distinct injury events were reported by each business group in 2021?",
            query: SELECT BUSINESSGROUPNAME, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE YEAR(EVENTDATE) = 2021 GROUP BY BUSINESSGROUPNAME ORDER BY EventCount DESC;
        },
        {
            input: "Find the number of distinct injury events for each mode of injury description.",
            query: SELECT MODEOFINJURYDESCRIPTION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY MODEOFINJURYDESCRIPTION ORDER BY EventCount DESC;
        },
        {
            input: "What is the average number of distinct injury events per month in 2022?",
            query: SELECT AVG(MonthlyEvents) AS AvgMonthlyEvents FROM ( SELECT EVENTMONTH, COUNT(DISTINCT EVENTID) AS MonthlyEvents FROM gq.vw_Injured_Budy_Part WHERE YEAR(EVENTDATE) = 2022 GROUP BY EVENTMONTH ) AS MonthlyEventCounts;
        },
        {
            input: "Which event type had the highest number of distinct injury events in the \"N. America\" region?",
            query: SELECT TOP 1 EVENTTYPE, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE MAJORSITEREGION = 'N. America' GROUP BY EVENTTYPE ORDER BY EventCount DESC;
        },
        {
            input: "Identify the top 3 months with the highest number of  injury distinct \"Recordable\" injury events.",
            query: SELECT TOP 3 EVENTMONTH, COUNT(DISTINCT EVENTID) AS RecordableEvents FROM gq.vw_Injured_Budy_Part WHERE INJURYCLASSIFICATION = 'Recordable' GROUP BY EVENTMONTH ORDER BY RecordableEvents DESC;
        },
        {
            input: "How many distinct injury events were reported by the \"Global Operations\" VP organization?",
            query: SELECT COUNT(DISTINCT EVENTID) AS GlobalOperationsEvents FROM gq.vw_Injured_Budy_Part WHERE VPORGNAME = 'Global Operations';
        },
        {
            input: "What is the distribution of distinct injury events by body part for the \"Chemical Release - Spill\" event type?",
            query: SELECT BODYPART, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE EVENTTYPE = 'Chemical Release - Spill' GROUP BY BODYPART ORDER BY EventCount DESC;
        },
        {
            input: "Find the number of distinct injury events for each functional group in the \"EMEA\" region.",
            query: SELECT FUNCTIONALGROUP, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part WHERE MAJORSITEREGION = 'EMEA' GROUP BY FUNCTIONALGROUP ORDER BY EventCount DESC;
        },
        {
            input: "How many distinct injury events occurred in each tier classification?",
            query: SELECT EVENTCLASSIFICATION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY EVENTCLASSIFICATION ORDER BY EventCount DESC;
        },
        {
            input: "Which customer had the most distinct injury events associated with them?",
            query: SELECT TOP 1 CustomerName, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY CustomerName ORDER BY EventCount DESC;
        },
        {
            input: "Determine the number of distinct injury events by mode of injury for each major site region.",
            query: SELECT MAJORSITEREGION, MODEOFINJURYDESCRIPTION, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY MAJORSITEREGION, MODEOFINJURYDESCRIPTION ORDER BY MAJORSITEREGION, EventCount DESC;
        },
        {
            input: "What is the trend of distinct injury events over the years?",
            query: SELECT YEAR(EVENTDATE) AS EventYear, COUNT(DISTINCT EVENTID) AS EventCount FROM gq.vw_Injured_Budy_Part GROUP BY YEAR(EVENTDATE) ORDER BY EventYear;
        }]
        """

pipeline_tool_description = """
    - This is the tool that need to be used most of the time. It runs a pipeline to go fetch the information required to answer the user question about the ETS Event, RMBWA, or Injury
    """

pipeline_creator_prompt = """ 
    You are an assistant answering questions to the user based on a database that we have. The user might ask a question that only requires SQL query, 
    or they may ask a question that requires SQL query and an additional summarization postprocessing. The summarization step will be applied to one of the free-text columns 
    of the data resulting from the SQL query. Your job is to parse the question into two components as follows:
    - The SQL component that will be sent to a SQL agent and will be converted into a SQL code. 
    - The summarization component that indicates the column of the data that needs to be summarized based on the question. The question should include phrases such as "summarise" or "what are the common", etc. If there is no summarization
    needed return "". If the user ask to list, show, display, etc and the question does not include summazrization request then return "" for Summarization_Component.
    
    Only return the two components in a dictionary format with keys "SQL_Component" and "Summarization_Component"

    User: What is the total number of unique ETS events recorded? 
    Assistant: {{"SQL_Component": "Show me the total number of unique ETS events recorded?", "Summarization_Component": "EVENTID"}}

    User: How many events were submitted in each quarter? 
    Assistant: {{"SQL_Component": "Show the number of events submitted in each quarter?", "Summarization_Component": "QUARTER"}}

    User: What is the most common type of ETS event? 
    Assistant: {{"SQL_Component": "Show me the most common type of ETS event?", "Summarization_Component": "EVENTTYPE"}}

    User: How many ets events have been closed? 
    Assistant: {{"SQL_Component": "Show the number of events that have been closed?", "Summarization_Component": "EVENTSTATUS"}}

    User: What is the average lead time for CAPA completion? 
    Assistant: {{"SQL_Component": "Show me the average lead time for CAPA completion?", "Summarization_Component": "CAPALEADTIME"}}

    User: Which major site or region has the highest number of recorded injuries? 
    Assistant: {{"SQL_Component": "Show the major site or region with the highest number of recorded injuries?", "Summarization_Component": "MAJORSITEREGION"}}

    User: What is the distribution of injury classifications? 
    Assistant: {{"SQL_Component": "Show the distribution of injury classifications?", "Summarization_Component": "INJURYCLASSIFICATION"}}

    User: How many events involved a chemical release? 
    Assistant: {{"SQL_Component": "Show the number of events that involved a chemical release?", "Summarization_Component": "EVENTTYPE"}}

    User: What are the top three root causes for ETS events? 
    Assistant: {{"SQL_Component": "Show the top three root causes for ETS events?", "Summarization_Component": "ROOTCAUSE"}}

    User: How many events were conducted by each functional group? 
    Assistant: {{"SQL_Component": "Show the number of events conducted by each functional group?", "Summarization_Component": "FUNCTIONALGROUP"}}

    User: What is the trend of ETS events over the months in 2023? 
    Assistant: {{"SQL_Component": "Show the trend of ETS events over the months in 2023?", "Summarization_Component": "MONTHYEAR"}}

    User: Which injury type is most frequently reported? 
    Assistant: {{"SQL_Component": "Show the most frequently reported injury type?", "Summarization_Component": "INJURYTYPE"}}

    User: How many ETS events required an evacuation? 
    Assistant: {{"SQL_Component": "Show the number of ETS events that required an evacuation?", "Summarization_Component": "EVACUATION"}}

    User: What is the average RCCA cycle time for ETS events? 
    Assistant: {{"SQL_Component": "Show me the average RCCA cycle time for ETS events?", "Summarization_Component": "RCCACYCLEDAYS"}}

    User: Which cause is most associated with ETS events?
    Assistant: {{"SQL_Component": "Show the causal factor most associated with ETS events?", "Summarization_Component": "CAUSALFACTOR"}}

    User: please summarize the RMBWAs in Jan of 2022. Mention any patterns that you find.
    Assistant: {{"SQL_Component": "Show me the descriptions for RMBWAs that occurred in Jan of 2022", "Summarization_Component": "DESCRIPTION"}}

    User: {user_question}
    Assistant: 
    """

table_selection_system_message = """
    Return a list of the Aliases of all the SQL tables that might be relevant to the users question. Using the Meta data and examples below.
    The tables are:

    {tables}

    IMPORTANT: DO NOT SELECT Injured_Budy_Part

    Please include all relevant tables, even if you're not sure that they're needed. Do not return an empty list []. 
    General Rules:
    1) If the user asks anything related to ETS, Events, Injuries or Reactive 
    choose: ["REACTIVE_METRICS"]
    2) If the user asks anything related to RMBWA, Inspection, Risk categories or Proactive 
    choose: ["PROACTIVE_METRICS"] 

    Example: 
    User: How many ETS Events are there in 2021?
    Assistant: ["REACTIVE_METRICS"]
    User: How many distinct injury events were reported by the "Global Operations" VP organization?
    Assistant: ["REACTIVE_METRICS"]
    User: How many events involved a "Chemical Release - Spill" and required an ERT response?
    Assistant: ["REACTIVE_METRICS"]
    User: What is the most common risk category observed in 2022?
    Assistant: ["PROACTIVE_METRICS"]
    User: What is the most frequent inspection location for events with a "Fire Hazard" risk category?
    Assistant: ["PROACTIVE_METRICS"]
    User: Which major site region had the highest number of distinct injury events in 2020?
    Assistant: ["REACTIVE_METRICS"]
    User: How many unique ETS events were submitted but not yet closed?
    Assistant: ["REACTIVE_METRICS"]
    User: List all unique RMBWA events conducted by "John, Doe".
    Assistant: ["PROACTIVE_METRICS"]
    User: How many recordable injuries happened in 2022?
    Assistant: ["REACTIVE_METRICS"]
    User: how many serious injuries were there between 2020 and 2022?
    Assistant: ["REACTIVE_METRICS"]

    User: {user_question}
    Assistant: 
    """

filter_columns_prompt = """
    You are a tool that extracts the appropriate relevant columns from a users Question using the provided database MetaData:
    0. Return the table, tabledescription, Important Notes, set of columns, Column Details, Data Type, and Categorical values that are relevant for answering the question via SQL query
    1. Always include columns that are essential.
    2. Exclude columns that have an "Important Notes" field stating "DO NOT USE" unless the user explicitly requests them.
    3. For Categorical Values return all the values from the schema that might be relevant (if unsure include them anyways).
    4. Even if questions are near an edge case, always provide all possible options.
    5. Be concise, and not overly verbose in your response. 

    Question: {user_question}
    MetaData: {col_description}
    """

filter_examples_prompt = """
    Question: {user_question}\n
    examples:  {examples}
    ------IMPORTANT DO NOT DEVIATE-------
    1) Return the full set of input and query values from the above examples list that could be relevant for answering the above Question via a SQL query
    2) Only select from the above example list do not generate new examples.
    3) Only Return the relevant examples as a subset from the above examples and in the following format and NOTHING MORE:
    format example: 
            input: How many distinct injury events occurred in 2015?,
            query: SELECT COUNT(DISTINCT [EVENTID]) AS Fremont Evacuations FROM gq.vw_RPT_Reactive_Metrics WHERE [EVACUATION] <> 'None' AND [MAJORSITEREGION] = 'Fremont' AND [EVENTSTATUS] <> 'Deleted' AND [EXCLUDEINCIDENTFROMBI] <> '1';

            input: input 2
            query: query 2
    """

sql_gen_prompt = """
    You are a mssql expert. Given an input question, create a syntactically correct mssql query to run.
    This Query will be executed in an Azure Synapse DB using TSQL syntax so structure the query appropriately 


    These are the only tables that you may use: {table_info}.

    These are the fields and metadata that are relevant to the user's question:
    {col_desc}


    Below are examples of similar questions and their corresponding SQL queries Use these as known good examples of question sql pairs:
    {examples}

    ----------IMPORTANT DO NOT DEVIATE-----------------
    1) Do not return more than {top_k} rows.
    2) Add brackets around all field names.
    3) Only Generate a SQL Query using the above fields, metadata, and examples.
    4) Information from examples should be weighed more heavily than information from the metadata as those are known good question/query pairs.
    5) When doing mathematical operations on integer datatype fields convert them to float type first.
    6) Do not return with markdown. return the SQL query text and nothing else.
    ---------------------------

    Question: {input}
    """

sql_error_correction_prompt = """
    The following SQL Query was just run:
    {sql_query}

    It returned the following error:
    {error}

    Generate a new SQL Query that will execute correctly.

    Using the following context and examples:
    Relevant Columns:
    {columns}

    Relevant Examples:
    {examples}

    RESPOND WITH THE SQL QUERY ONLY DO NOT RETURN ANYTHING ELSE NO MATTER WHAT."""

summarization_map_template = """
    A user has asked a question: {user_question}. 
    To answer this question, you need to summarize the following items: (The items are separated by '==TicketEnd==') 

    {content}

    Summary:
    """

summarization_reduce_template = """

    A user has asked {user_question}. Summarize the following items with repect to to this question:
    
    {doc_summaries}
    
    Consolidate the response in the form of bullet points wherever possible. Avoid having more than 10 total bullet points under each heading.
    Keep your summary word limit less than 1000 words.
    Summary:
    """

####### Needs work still ######

agent_prefix = """
    You are a chatbot agent, assisting users with some questions they ask. The question user asks can be answered using a single tool you have (full_pipeline). 
    Here are your instructions:
    1. Receive user question. 
    2. Decide to run the full_pipeline tool with the user question updated with the conversation history or ask follow-up question in following cases:
    - If the user specifies "event" without specifying what type of event they should clarify which of the following Types of events: ETS, RMBWA, Injury
"""
###########

sql_explainer_prompt = """
    You are an assistant helping the user understanding a SQL query. 
    Summarize the query into the following sections: tables, joins, fields by table, any aggregation (avg, count, etc), filters, grouping, and overall summary.
    Examples
    User: SELECT TOP 3 EVENTMONTH, COUNT(DISTINCT EVENTID) AS RecordableEvents FROM gq.vw_Injured_Budy_Part WHERE INJURYCLASSIFICATION = 'Recordable' GROUP BY EVENTMONTH ORDER BY RecordableEvents DESC;
    Assistant: 
    #### Tables:
    - gq.vw_Injured_Budy_Part 
    #### Joins:
    - Type: None
    - Condition: None
    #### Fields by Table:
    - gq.vw_Injured_Budy_Part: EVENTMONTH, EVENTID 
    #### Aggregation:
    - DISTINCT: The query uses DISTINCT to ensure that only unique values of gq.vw_Injured_Budy_Part.EVENTID are selected.
    #### Filters:
    - INJURYCLASSIFICATION = 'Recordable'
    #### Grouping:
    - gq.vw_Injured_Budy_Part.EVENTMONTH
    #### Ordering:
    -  Decending order by gq.vw_Injured_Budy_Part.RecordableEvents
    #### Overall Summary:
    The query retrieves the top 3 months with the highest number of distinct recordable events from the gq.vw_Injured_Budy_Part table. It filters the data to include only those events classified as 'Recordable', groups the results by month, and orders them in descending order based on the number of distinct events per month.


    User: {sql_code}
    Assistant: 
"""

output_prep_prompt = """
    You are part of a chatbot preparing the final output to answer the user input question. 
    Your task is to create a coherent and contextually appropriate response based on the provided input and output. 

    Instructions:
    1. Analyze the input message to understand the user's intent and context.
    2. The output is in the format of a Python dictionary. Extract the relevant information from that dictionary based on the user input.
    3. Generate a response based on the provided output.

    Example:

    User Input:
    "How many ETS events happened in 2022?"

    Output:
    {{"": 4748}}

    Response:
    There were 4748 ETS Events with With Event Dates in 2022.

    User Input:
    {0}

    Output:
    {1}

    Response:
"""

ambiguity_checker_prompt = """
    You are an assistant that checks if the user's query is ambiguous or if there is enough information to generate a SQL query to answer it based on the provided metadata.

    Here is your workflow:
    1. Determine if the question is clear and if you can generate a SQL query using the metadata below.
    2. Clear and answerable means that each part of the user's question clearly corresponds to a column and/or categorical value in the meta data below while respecting the important notes for each column.
    3. If there is no clear set of columns, filters, and/or example values to answer the user's question, respond with exactly the following JSON object:
    {{
    "Ambiguous": true,
    "Reason": "Clearly explain why the question is ambiguous or unanswerable based on the metadata provided. Include suggestions if there are columns that might be close to what the user is looking for."
    }}
    4. If the question is clear and answerable, respond with exactly the following JSON object:
    {{
    "Ambiguous": false,
    "Reason": ""
    }}

    User Question: {user_question}

    Meta Data Context: {context}

    ----------IMPORTANT: DO NOT DEVIATE-------------
    Respond with only the JSON object and nothing else.
    ------------------------------------------------------
"""

# General prompt constants (renamed by function)
prompts = {
    "REACTIVE_METRICS_FIELDS": ("ETS_REACTIVE_METRICS_FIELDS", reactive_metrics_field_description),
    "PROACTIVE_METRICS_FIELDS": ("ETS_PROACTIVE_METRICS_FIELDS", proactive_metrics_field_description),
    "INJURED_BODY_PART_FIELDS": ("ETS_INJURED_BODY_PART_FIELDS", injured_body_part_field_description),
    "REACTIVE_METRICS_EXAMPLES": ("ETS_REACTIVE_METRICS_EXAMPLES", reactive_metrics_sql_examples),
    "PROACTIVE_METRICS_EXAMPLES": ("ETS_PROACTIVE_METRICS_EXAMPLES", proactive_metrics_sql_examples),
    "INJURED_BODY_PART_EXAMPLES": ("ETS_INJURED_BODY_PART_EXAMPLES", injured_body_part_sql_examples),
    "FILTER_COLUMNS_PROMPT": ("ETS_FILTER_COLUMNS_PROMPT", filter_columns_prompt),
    "FILTER_EXAMPLES_PROMPT": ("ETS_FILTER_EXAMPLES_PROMPT", filter_examples_prompt),
    "SQL_GEN_PROMPT": ("ETS_SQL_GEN_PROMPT", sql_gen_prompt),
    "SQL_ERROR_CORRECTION_PROMPT": ("ETS_SQL_ERROR_CORRECTION_PROMPT", sql_error_correction_prompt),
    "SUMMARIZATION_REDUCE_TEMPLATE": ("ETS_SUMMARIZATION_REDUCE_TEMPLATE", summarization_reduce_template),
    "TABLE_SELECTION_PROMPT": ("ETS_TABLE_SELECTION_PROMPT", table_selection_system_message),
    "SUMMARIZATION_MAP_TEMPLATE": ("ETS_SUMMARIZATION_MAP_TEMPLATE", summarization_map_template),
    "PIPELINE_CREATOR_PROMPT": ("ETS_PIPELINE_CREATOR_PROMPT", pipeline_creator_prompt),
    "PIPELINE_TOOL_DESCRIPTION": ("ETS_PIPELINE_TOOL_DESCRIPTION", pipeline_tool_description),
    "SQL_EXPLAINER_PROMPT": ("ETS_SQL_EXPLAINER_PROMPT", sql_explainer_prompt),
    "AMBIGUITY_CHECKER_PROMPT": ("ETS_AMBIGUITY_CHECKER_PROMPT", ambiguity_checker_prompt)
}

