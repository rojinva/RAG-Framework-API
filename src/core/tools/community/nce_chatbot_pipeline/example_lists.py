from .constants import IQMS_NCE_LIVE, RPT_IQMS_8D_GRID, VW_IPLM_PROBLEM_REPORT, VW_OAI_ESCALATION_TICKETS

nce_live_field_description = """
Table gq.IQMS_NCE_LIVE has the following columns:
- "ABC_Description": High level product grouping (with values "Transport Module", "Etch Dielectric", "CVD", "Etch Conductor Poly", "Electrofill", "Product Upgrade", etc). This grouping would be the next level below Product Group. After this level product starts to break into product family.
- "Begin_Guarantee": Begin Guarantee is the warranty start date.
- "Commit_Date_Impact": This field is essentially a flag that indicates whether the NCE is likely to have significant impact to the commit date communicated to the customer with values "Major Commit date missed", "None", "Minor Commit date missed", or "". 
- "Removed_Part_Family": This field represents the part family of the part that failed on the NCe. It is also referred to as the "removed part" or "commodity type". Examples are "RF, Generator", "Valves", "Cables and Harnesses", "Controllers", "PCB", "Filter", etc. Always search this field with sql LIKE operator. 
- "Customer_Group": This bins Customer Names into groups for the company's most common customers since a Customer can have multiple names and accounts.  The values include: "UMC", "YMTC", "SK Hynix", "Kioxia", "SEC", "Micron", "ROW", "ST Micro", "TSMC" and "Intel".  SEC may also be referred to as Samsung.  "ROW" stands for Rest Of World and is the grouping for all other Customers not grouped here.  Higher fidelity mapping is in the NCe "Customer_Name" field
- "Customer_Name": specifies who owns the tool being worked on. Always search this field with sql LIKE operator. 
- "Customer_Temperature_Impact": This field indicates how sensitive the customer is relative to NCEs, with values "Mild", "Unknown", "", "Warm", "Not visible to customer", "Hot", "Severe", "Section Supervisor"
- "Date_Current_State": Date of the current state of the NCe. 
- "Date_Opened": is the generated data and time of the NCe record
- "Description": provides a narrative on what went wrong and is specific to the NCe
- "Escape_Description": Additional text regarding what is going wrong with the part associated with the failure. Often times there is some history explained in the field with along with dates. 
- "Escape_Notification_Type": Also referred to as Serivce Notification Type comes from SAP. Z4 and Z5 represent install NCes, Z3 represent non-install NCes and Z1 are for NCes for direc part orders not tied to Lam serviced tools
- "Escape_Title": This field is related to the other escape fields it is essentially a summarized version of the other escape description fields:  Escape and Description.
- "Fab_Name": This is the customer site where the tool is operating.
- "FCID": This is a string describing the identification number of the tool. Synonymous term is FID. This identification number is often used as the basis for normalizing NCE counts as in NCE per FID (or FCID because it is synonymous). FID level is a frequent level of analysis.
- "Field_Owner": This is the Field Service Engineer who is responsible for the FID / FCID number tool at the customer fab.
- "FQM_Owner": FQM is the next level up from FSE. Functional Quality Managers manage Field Service Engineers.
- "Functional_Location": This is a code associated with the customer and the fab. Infrequently used field, primary levels of use as Customer and Fab Name. This field essentially combines them into a single system code.
- "Geo_Region_Member": represents the geographical region associated with the NCe, the values include: "KOREA", "FAR EAST", "TAIWAN", "CENTRAL EUROPE", "CENTRAL", "WEST", "MALAYSIA", "JAPAN", "EAST COAST", "NORTHERN EUROPE", "SOUTHERN EUROPE", "CHINA" or ""
- "Management_Region": represents the management geo region, the values include: "KOREA", "N. AMERICA", "TAIWAN", "CHINA", "JAPAN", "", "EUROPE", "SEA".
- "IBASE_Sales_Order": Sales order number identifying the contract in the ibase system
- "IBASE_Serial_Number": Serial number of the tool used in the ibase system
- "IBFAB_Description": Similar to functional location this filed is another description of where the FID operated geographically.
- "Impact": Impact can be set to Safety, Critical, Medium or Low and is based on the impact to the customer
- "Installation_Team_Lead": This is the name of the FSE who is leading the team installing the FID at the customer site.
- "Investigation_Group": represents the investigation group assigned to the NCe. If no investigation group is assigned the value is "". Other values are "Supplier", "Etch Product Group", "Logistics/Warehouse", "Dep Product Group", "Field Service", "BOM Configuration", "Engineering", "Manufacturing", "Manufacturing - Tualatin", "Manufacturing - Livermore", "Global Ops Order Fulfillment", "Global Ops Config Eng", "Global Products Engineering", "Pilot", "Reliant PG (CSBG)", "Sales Ops", "Clean Product Group", "Product Group/Engineering", "Manufacturing - Silfex", etc. 
- "Investigation_Required": Yes/no field related to the impact field. Safety and critical usually require investigation which is a formal process to understand the NCE on a more detailed basis. The process to investigate is the 8D process.
- "iQMS_ID": serves as the quality management system record key and it represents an NCe ID in this table
- "LPR_Type": This is a code for the type of LPR with values "PM", "UPG", "ATM", "OTHER", etc. 
- "Material_Cost": represents the total cost of parts
- "Model_Number_Group": This is the model number group field
- "MRBe_Comments_Log": This field holds comments from the MRBe log this time stamps the free text entered for the MRBes.
- "MyLam_System": This is a product type field containing a product name. When people ask for product type this is one of the fields that should be utilized, but not the only one.
- "NCeFrequency": This field should be utilized whenever part failure frequency questions are asked. It represents the count of NCEs with the same damage code and part number at the time of the NCE creation.
- "NCe_Log": will contain time-stamped free text inputs from iQMS users providing context and information on the NCe that is not captured elsewhere in the record
- "NCe_Risk_Assessment_Level": The NCe Risk Assessment Level, denoted as NCe_Risk_Assessment_Level, is essentially the output of a function that calculates based on frequency and cost to Lam and includes other factors, and it highlights the impact of this NCe to Lam, with lower numbers representing higher impact to Lam; notably, Risk Assessment Level 1 would be the worst for Lam.
- "Nonconformance_Type": This is a field that denoted it is an NCE. it does not really provide much explanatory value.
- "Notification_Number": The Notification Number is assigned by SAP. In the NCe table, this represents the key for the parent Quality Escape of the given NCe. If an Escalation Solver ticket is opened for the NCe's parent Quality Escape, the TicketID in Escalation Solver will match the Notification Number and can be used as a key for table joins
- "Object_Type": Object type
- "Opportunity_Type_Desc": This field denotes the kind of sales opportunity associated with the NCE. PG system opportunity vs CSBG system opportunity vs Eval system opportunity are the kinds of opportunities that are included in this field.
- "Ordered_Part_Description": this field holds the codes and descriptions of the parts that were ordered associated with resolution of this nce. 
- "Org_Group": This is another product type level. It is a mid-level grouping of product types. When users are interested in product types but getting too low level or too many product types in the results this field would likely be a sensible grouping level for product type.
- "Original_Service_Order_Number": Original Service Order Number also call Service Order or SO is assigned by SAP. A Service Order will have one to many notification numbers. Tools are installed with a single service order, but may have many service orders for warranty or other contract work
- "Originator": This is the person who initiated the NCE
- "Part_CE": Part CE with values "Yes" or "No"
- "Part_Cost": This is the material cost of the part associated with the nce.
- "Part_Critical_Classification": Part Critical Classification (with values "NC", "C1, "C4", "C8", "CV", etc)
- "Part_Description": This is a text description in abbreviated code form that describes the part associated with the NCE. It is linked to the part_number as in every part_description has an associated part_number
- "Part_Fail_Date": This is the fail date for the part number. It is infrequently populated.
- "Part_Number": specifies the part number being replaced in an attempt to fix the tool
- "Part_Product_Family": specifies the type of tool being worked on (e.g., "ETCH 2300", "VECTOR EXTREME", "ETCH 2300R", "SABRE", "VECTOR EXCEL", "ETCH SENSE.I", "SPIN CLEAN", "ALTUS", "DEP HANDLER", "DIRECT METALS", etc)
- "Part_Quantity": Part Quantity specifies the number of parts that failed and are being ordered. This can be an integer 1 or higher
- "Product_Group_Classification": specifies the Product Group responsible for the tool (e.g. 'ETCH', 'DEPOSITION', 'CLEAN', etc)
- "Product_Group": This is a mid-high level product grouping field. It is closer to product family than product type. (some values are: 'FLEXHXP', 'SABRE', 'KIYO-GX', 'TM', 'UPGRADE', 'VANTEX', 'KIYO-FXE', 'STRATA', etc)
- "Product_Type": This field represents the product type associated with the NCE. This should be the first level of grouping when users ask for product level results. (some values are: '2300 ETCH', 'VECTOR', 'SABRE', 'L-SERIES', 'CONCEPT 3', 'CONCEPT 3 2300', etc.)  
- "Purchase_Make": specifies whether Lam manufactures the part or purchases it directly from a vendor (with values "MAKE" or "PURCHASE")
- "QPL_Owner": QPL Owner is the Quality Product Lead assigned to the NCe. QPLs are generally aligned to geographic regions
- "RAM_Number": RAM number is a tracking number used by reverse logistics to ship the return of a part. Not all NCes have part returns or RAMs, but there can be only one RAM per part
- "RAM_Status_Date": RAM Status Date is the last time the RAM status was updated
- "RAM_Status_Description": RAM status specifies what is currently happening on the part return 
    (e.g. "RAM COMPLETED", "IN QUARANTINE", "SCRAPPED - PART THROWN AWAY", "RAM ISSUED", "RAM ITEM DELETED", "IN TRANSIT TO REPAIRING PLANT", "ISSUED TO ENGINEERING", etc)
- "RAM_Type": RAM Type (with values: "", "WR", "CUSTRETURN", "DEFECTZFSE", "FA_ONLY", "OTHER/QDR", or "NCE")
- "RTV_Requestor": RTV requestor is the person who requested the part be returned to vendor
- "Safety_Impact": Safety Impact is answered by the FSE and is part of the Impact calculation. The NCe can be classified with the following values ("Safety incident", "Safety Risk/Near Miss" or "No")
- "Sales_Order_Line_No": This specifies the portion of the contract that the Service Order for this NCe is being performed on. It will be an integer.
- "Sales_Order_No": Sales Order Number is an integer key assigned by SAP for the work Lam is contracted to do
- "SAP_Damage_Code_Group": is a categorical description of the broad category of damage for the part. Values for the damage code group include: 
    -- "OOBQ": Out of Box Quality issue where the part fails to function upon arrival or install 
    -- "PERF": Performance issue where the part worked for a period of time, but failed early than it should have 
    -- "SWPR": Software Problem that can be fixed without a part order 
    -- "MATORD": is a non-quality defect"
- "SAP_Damage_Code"": SAP_Damage_Code"" specifies the type of damage. Values include: 
    -- "WRNG": Wrong | Part number does not match expected part 
    -- "MSPT": Missing | Part missing from shipment 
    -- "OVS": Overstock | More parts shipped than structured or requested  
    -- "SPEC": Spec | Part received does not match drawing (Lam spec) 
    -- "DMG": Damaged | Part arrived damaged 
    -- "PLBL": Part Label | Part has incorrect label 
    -- "DOI": Dead on Install | Part does not work upon initial installation (Lam spec) 
    -- "ELF": Early Life Failure | Part failed within 90 days of installation  
    -- "RAM": Reliability and Maintenance | Part fails at inconsistent intervals (beyond 90 days)  
    -- "INST": Software installation issues (< 2 weeks after SW upgrade) 
    -- "SWDF": Software defect 
    -- "USER": User error related to software 
    -- "CANC": Cancelled | Part order canceled or duplicate NCe identified 
    -- "COMB": Combined | Additional parts damaged due to other part defects OR Parts missing or wrong from a non-FRU Kit/Assembly 
    -- "DIAG": Diagnostics | When ordering parts for troubleshooting ONLY 
    -- "DUPL": Duplicate | Duplicate entry 
    -- "CSPC": Customer Statistical Process Control | Meets Lam spec, does not meet customer SPC/FDC limits 
    -- "HNDL": Handling | Part damaged after arrival 
    -- "LOST": Lost | Part lost during install 
    -- "PRVM": Preventative Maintenance | One-time use, or when ordering supplemental parts needed to support replacement of another quality issues (e.g., O-rings / VCR gasket on Valve Failure) 
    -- "UPGR": Upgrade | Parts ordered for upgrade or enhancement 
    -- "ZNOL": Not listed | Does not fit any other Damage Code 
    -- "ZORD": Wrong part ordered | Incorrect part ordered by account team "
- "SAP_Mandatory_Return": SAP Mandatory Return specifies if this part must be returned due to scarcity or other reasons for Lam, with values "Yes, or "No"
- "Serial_Number": This is the serial number of the part associated with the NCE
- "Supplier_Name": represents the Vendor of the part, who supplied the part.
- "Symptom_Detail": This is a failure grouping. It is different from the damage codes but there is overlap between concepts in DIAG for example. In essence this field describes the symptom that cause the NCE. Electrical, mechanical, communication, leaks, etc are all kinds for additional symptoms that can be identified in this field.
- "Symptom": This is the highest level of failure types. Examples include functional failures, MATORDs, Missing, etc. It is closely associated to damage code group but includes some other descriptive alternatives
- "System_Description_Group": This is another product type description but not the most useful. This field should be utilized infrequently because the grouping level is about the lowest level if it is actually populated. More useful would be using this field in tandem with a higher level product type field. 
- "System_Description": This is another product type field. It is very detailed and like system_description_group is very low level so grouping at this level will only work when it is a very specific question. It is a concatenated field of various grouping levels. 
- "Title": This is a very high level summary of the failure description.
- "Total_Nce_Cost": represents the total cost of parts and estimated labor costs incurred for this NCe
- "Triage_SPOC_Owner": This is the single point of contact for triaging the NCE
- "Type_of_Activity": specifies type of the work being performed by the engineers (e.g. "INSTL", "WARR", "EVAL", "STRTUP", "VARSPR", etc)
- "Warranty_End": This is the date of the end of the warranty period. After this point Lam is not responsible for covering the cost of tool failures.
- "ZFSE_Norm": specifies whether the removed part is "ZFSE", "NORM" or ""
- "Actual_Ship_Date": Actual Ship Date also referred to as ASD. This represents the date the tool shipped to the customer
- "Actual_Ship_Fiscal_Quarter_Text": This represents the fiscal quarter of Actual ship date. For example, Quarter 1 through 4 of 2021 are represented by The values are "QMar'21", "QJun'21", "QSep'21", and "QDec'21" respectively.. 
- "Installation_Complete_Calendar_Quarter_Text": This is the fiscal quarter the tool installation was completed for the customer. For example, Quarter 1 through 4 of 2024 are represented by The values are "QMar'24", "QJun'24", "QSep'24", and "QDec'24" respectively. 
- "Date_Opened_Fisc_Qtr_Text": Fiscal quarter when the NCe was opened. For example, Quarter 1 through 4 of 2022 are represented by The values are "QMar'22", "QJun'22", "QSep'22", and "QDec'22" respectively. 
- "Date_Closed": Date the NCe was closed
"""

eight_d_field_description = """
Table gq.RPT_IQMS_8D_Grid has the following columns:
- "8D_Priority": represents the level of importance for the investigation ranging from Priority 1 to Priority 4. The lower the number, the higher the priority
- "Preventive_Action_Summary_Implemented": remains null while preventive actions are in process for an 8D and then set to "Yes" if completed or "No" if not completed
- "Corrective_Action_Action_Implemented": remains null while corrective actions are in process for an 8D and then set to "Yes" if completed or "No" if not completed
- "Corrective_Action_Summary_CA_Description_G": free text summarizing the corrective action
- "Corrective_Action_Implementation_Date": corrective action implementation date
- "Containment_Grid_Conta_Action_Item_G": free text summarizing the containment action description
- "Containment_Grid_Conta_AI_Comp_On_G": remains blank until the containment action is completed and then is populated with the date the containment action was completed
- "Containment_Grid_Cont_AI_Owner_First_Name": This is the first name of the owner of the containment action item this person is responsible for implementation
- "Containment_Grid_Cont_AI_Owner_Last_Name": This is the last name of the owner of the containment action item this person is responsible for implementation
- "Containment_Grid_Conta_Item_Commit_On": Date of commitment for containment item
- "Corrective_Action_Summary_Corrective_Action_Owner_G_First": First name of the owner of the implementation of the corrective action
- "Corrective_Action_Summary_Corrective_Action_Owner_G_Last": Last name of the owner of the implementation of the corrective action
- "Current_State": specifies the current state of the record with values. If a record is closed, the state will start with "Closed - "
- "D5_Completed_by_QCO_Date": this is the date that d5 was completed
- "D6_Validated_Date": date that the d6 step was validated
- "Date_Opened": date that the case was opened in the system
- "Date_Opened_Fiscal_Qtr_Text": The fiscal quarter associated with Date_Opened. The format is typically "QJun'19", "QMar'20", etc. 
- "FQM_Owner": This is the FQM assigned to the case
- "Impact": Impact field records the effects or consequences of the observed symptoms the system.
- "Corrective_Action_Summary_Implementation_Commit_Date_G": date committed for implementation corrective action
- "Preventive_Action_Summary_Implementation_Date": date of implementation of the corrective action
- "Investigation_Group_Detail": This is what is being investigated or the responsible group for the investigation. The values include: "N/A", "", "001 - Main", "031 - Upper Chamber", "023 - PM Test", "032 - Lower Chamber", "SFS", "Mechatronics Engineering", "Part Supplier", "Mfg Engineering", "008 - Enclosure", "033 - Chamber Test", "Remote Factory", "Conductor", "Product Management", "Dielectric", "03002 Decon", "Engineering", "Manufacturing", "?", etc.
- "Investigation_Group": This is the assigned functional group within Lam Research that is leading the investigation. Example values include: "Supplier", "Manufacturing", "Dep Product Group", "Etch Product Group", "Global Products Engineering", "Warehouse", "Manufacturing - Tualatin", "Logistics/Warehouse", "Manufacturing - LMM", "Reliant PG (CSBG)", "Clean Product Group", "Manufacturing - Livermore", "Pilot", "Manufacturing - Villach", "Manufacturing - Silfex", "CFT", "Resupply", "Product Group/Engineering", "Manufacturing - LMK", "Order Fulfillment", etc.
- "iQMS_ID": serves as the quality management system record key and it represents an ID in this table
- "Preventive_Action_Summary_PA_Description": free text summarizing the preventive action
- "Parent_ID": is equivalent to "iqms_id" field in GQ.IQMS_NCE_LIVE and the key to join that table
- "Part_Number": Part number associated with the NCE that has triggered the 8D investigation
- "Part_Description": Part description associated with the NCE that has triggered the 8D investigation
- "Preventive_Action_Summary_First_Name": First name of owner of the preventative action assigned
- "Preventive_Action_Summary_Last_Name": Last name of owner of the preventative action assigned
- "QPL_Owner": This is the QPL assigned to the case
- "Root_Cause_Summary_Seq_No": identification number of the assigned root cause
- "Reason_CA_Not_Implemented": text field explaining reasoning for no implementation of the corrective action
- "Preventive_Action_Summary_Reason_not_Implemented": text field explaining why the corrective action was not implemented
- "8D_Record_Owner": This is the owner of the 8D entry
- "Root_Cause_Category_1_G": represents categorical binning of the root cause
- "Root_Cause_Category_2_G": root cause subcategorya
- "Root_Cause_Category_3_G": root cause subcategory.
- "Root_Cause_Description_G": free text summarizing the root cause description
- "Team_Member_Grid_Team_Member_G_First_Name": First Name of Team member assigned to the 8d
- "Team_Member_Grid_Team_Member_G_Last_Name": Last Name of Team member assigned to the 8d
- "Team_Member_Grid_Team_Member_Business_Unit_G": team member's assigned business unit
- "Team_Member_Count": Number of Team Members assigned for the 8D
- "Team_Member_Grid_Team_Member_Role_G": the functional role of the team member assigned
- "Team_Member_Grid_Team_Member_Functional_Role_G": That team member's role on the team
- "Title": title is a brief description of the 8D case, basically a short overview of the problem and/or symptom under investigation
- "8D_Finding_Details": This is the next level down of the 8D finding.  Example: for workmanship 8d finding, there can be many finidng details like negative practice, accidental damage, assembly error, etc.
- "8D_Finding": This is the summary result of the 8D assigning the fault to some process grouping like Workmanship, configuration, facitlities, etc.
- "D3_Summary": This is the summary of the D3 step which is to Develop interim containment plan; implement and verify interim actions
- "D4_Commit_Date": Date of the d4 step
- "D4_Summary": Summarization of the 8D step to Determine, identify, and verify root causes and escape points
- "D5_Due_Date": due date for the d5 step.
- "D5_Summary": Summarization of the 8D step to Choose and verify permanent corrections (PCs) for problem/nonconformity
- "D6_Actual_Implementation_Date": date of implementation of the d6 step which is to implement and validate corrective actions
- "D6_Summary": Summarization of the 8D step to Implement and validate corrective actions
- "D7_Implemented_Date": date preventative measures were implemented
- "D7_Summary": Summarization of the 8D step to Take preventive measure
- "Description": description field is a longer version of the title field.  It relays important text information about the case under investigation.  Users generally use this field to give an overview of the problem underinvestigation,
- "Final_Problem_Statement": Problem statement resulting from completion of the 8D
- "First_Why": Summary of the first why in the 8d investigation process
- "FQM_Approved_8D_Date": Date that the fqm approved the 8D
- "Initial_Problem_Statement": Initial problem statement is the starting point for the 8D investigation.
- "Originator:First_Name": indicates the frist name of the person who opened the case in the system
- "Originator:Last_Name": indicates the last name of the person who opened the case in the system
- "QPL_Approved_8D_Date": Date that the QPL approved the 8D
- "Quality_Risk_Level": This is the risk level associated with the case.  Can be risk level 1 through 4 or mandatory critical.  Risk level 1 is high, 4 is low and mandatory critical is a different scale which has to be addressed as top priority.
- "Related_Records": These are other cases that are related to the same part that have been conducted in the past.
- "Responsible_Group": Group responsible for the 8D
- "Submittd_to_Close_w_no_RC_Date": This is a date field for submitted to close without an RC date
- "Supplier_8D_First_Pass_Yield": First pass yield value for the part
- "Supplier_Code": This is a numeric code used to identify the supplier
- "Supplier_Name": Supplier of the part under investigation.
- "Symptom_Detail": this is a detailed explanation of the symptom field. The difference between this field and the symptom field is the level of detail provided.  More detailed in this field.
- "Symptom": symptom field is the primary issue under investigation.  It is an observable sign or indication that there is an issue or malfunction within the system.
- "D6_Completed_Date": Date of the D6 step completion
- "D6_Completed_Date_Fiscal_Qtr_Text": Quarter of the D6 step completion
- "8D_Closed_Date": Date 8D Closed
- "8D_Closed_Fiscal_Qtr_Text": Quarter the 8D Closed
"""

es_field_description = """
Table es.vw_oai_EscalationTickets has the following columns:
- "ESCustomerID": Escalation Solver Customer Identifier code
- "EquipmentID": Refers to a unique numerical identifier for the equipment/product. Used in SAP.
- "EquipmentStatusID": EquipmentStatusID": An ID with values (T0, T1, T2, or T3) specifies the tier status of the equipment. For example, EquipmentStatusID="T1" shows tier 1 escalation tools. It may also be referred to as "Type", 'Tier", "EquipmentStatus" 
- "EqParentID": Refers to a unique numerical identifier for the higher level equipment a module would report into. Used in SAP.
- "WaferSize": Describes the size of the wafer/product with values "125MM", "450MM", "150MM", "200MM", or "300MM"
- "ModuleType": Type of module with values U, T, S, or M
- "PlatformType": Platform related to the product (e.g. DEPOSITION, ETCH, CLEAN, ADVANCED SERVICES, UPGR, etc)
- "ObjectType": Type of tool (e.g. 2300FEOL, VECTOR, SABRE, SPINBEOL, ALTUS, 2300BEOL, SPEED, ALLIANCE, SPINFEOL, GAMMA, etc)
- "ABCIndicator": Describes nature of the equipment/system (e.g. V, T, K, P, L, D, W, M, etc)
- "ModelNo": Model Number of the product (e.g. "Q STRATA", "XPR", "STRIKER OXIDE FE", "VER METAL PM", "MAX", "STRIKER CARBIDE CK", "DV28", "EXELAN FLEX FL PM", etc)
- "MyLamSystem": System Name (e.g. "EOS", "MACH IV", "VECTOR EXPRESS", "DV-PRIME", "VECTOR", "2300E4 TRANSPORT MODULE", "SABRE EXTREME", "2300E6 TRANSPORT MODULE", "SABRE 3D", "WTS-MAX", "SABRE NEXT", "KIYO GX")
- "TopLevelSystem": Refers to the highest level system a module reports into (e.g. "VECTOR EXTREME", "EOS", "VECTOR EXPRESS", "VECTOR", "DV-PRIME", "STRIKER", "C3 ALTUS MAX", "C3 ALTUS", "VECTOR STRATA", "UPGRADE", "SABRE EXTREME", "SABRE NEXT", "2300 KIYO GX", etc)
- "SymptomID": Unique numeric identifier for Symptom of a problem
- "ParentID": Describes the parent child relationship to SymptomID
- "Symptom": Brief explanation of the symptom needed to perform a fishbone analysis (e.g. "PC - Random - No Pattern", "Defects Out of Specification", "PC - Edge - Clocked Positions", "Software Defect Observed", "PC - Showerhead Patterns", etc)
- "Description": Symptom Description
- "isLeaf": If equals true, indicates this is the ultimate child or symptom. If equals false, indicates it is part of the larger symptom or parent.
- "HierarchyLevel": A number that indicates the level of the tree the symptom is located on. If isLeaf is true, this value will be greater than 0. If isLeaf is false, this value will be 0.
- "Hierarchy": Indicates a specific section of the symptom tree that can be queried
- "IsCategory": Indicates a specific category of symptom or group of symptoms
- "TicketID": Unique numerical identifier for a particular problem ticket raised, this field is used to join the table to nce live through the field Notification_Number
- "BU": Business Unit (e.g. "PECVD", "2300 Conductor Etch", "Spin Clean", "Electrofill", "2300 Dielectric Etch", "Direct Metals", "Gapfill", "SCE / Alliance", "ALD", etc)
- "ProblemStatement": Short Description of the Problem as entered by the user
- "Resolution": Description of the resolution to a certain problem statement or ticket
- "ESBUID": Unique identifier for business unit in SAP
- "IsActive": Flag to identify whether a BU is active in SAP with values equal to true or false
- "Hypothesis": Contains only confirmed hypotheses for given problem/symptoms in ES. These may also be considered as root causes 
(e.g. "Software Bug", "Chamber Conditioning Insufficient", "No Confirmed Hypothesis - Problem Not Recurring / Unresolved", 
"Component Failure - Module/Platform/System/Equipment/CTC/QNX Controller", "Component failure - IOC / EIOC / SIOC / HDSIOC", "Showerhead Failed - Contamination, Cable / Wiring - Failure", etc)
- "OpenDate": the date the ticket opened. 
- "ClosedDate": the date the ticket closed.
- "open_fisc_qtr_text": the fiscal quarter associated with Open Date. The format is typically "QJun'19", "QMar'20", etc. 
- "closed_fisc_qtr_text": the fiscal quarter associated with closed date. The format is typically "QSep'21", "QDec'22", etc.
"""

iplm_field_description = """
Table eng.vw_IPLMProblemReport has the following columns:
- "name": Problem Report (PR) number, the unique identifier of the rows in iplm table
- "state": Lifecycle state of the PR, one of the values of "Closed", "Confirmed", "In Work", "Cancelled", "In Review", "Create", "Test", "Develop", or "Safety Review" 
- "title": Summary of the problem - to be viewed in conjunction with the details
- "problem_description": Textual description of the problem
- "priority": Urgency of the PR, (one of the values of "Normal", "Urgent", "Line Down", "Safety", "Medium")
- "originator": Name of person raising PR in first instance
- "fcid_number": FCID number, sometimes referred to as FID
- "escalation_number": PR created as a result of an escalation - ES TicketID
- "deviation_or_waiver_required": If a waiver or deviation is needed for a PR the value is "Yes", otherwise "No"
- "requestor_organization": Originator's organization (e.g. Supply Chain, Product Group, Manufacturing, Pilot, etc)
- "reason": Reason code assigned to the PR 
    (e.g. "Software Change Request", "Supplier Mfg Process Change", "BOM/Spec Error", "Cannot Build Part to Print", "Supplier Request for Deviation", "Obsolete Component", "Critical Part Change", "Product Design", etc)
- "suggested_solution": Text entry from originator - need not be the final solution for the PR
- "benefit": It describes the benefit that will be accrued if issue underlying the PR is addressed. 
- "customer": Customer affected by PR
- "solution_type": Set of values assigned when solution is being executed 
    (e.g. "ECR", "Monitoring", "See Comments", "Supplier Deviation/Waiver", "Change Order", "Supplier Change Authorization", "Address with Future Design", "ECN", "PCN", etc)
- "cause_code": Assessed cause determined for the PR 
    (e.g., "Supplier Capability", "Z_Miscellaneous", "Obsolescence", "Drafting", "BOM", "Producibility Improvement", "Z_Business Process Tracking", "Mechanical Design", "Software", "Electrical Design", etc)
- "root_cause_corrective_action": Textual description for corrective action taken to resolve the PR
- "disposition": Disposition on the PR with values equal to "Confirmed", "Reject" or "Defer"
- "injury": Injury flag with values "Yes" or "No" or ""
- "business_unit_name": business unit (BU) Name (e.g. "CSBG BU", "Conductor", "PECVD", "Dielectric", "Direct Metal", "Electrofill", "Clean BU", "Platform-EPG", "Multi-BU Dep", "ALD", etc)
- "primary_product_affected_name": Primary product affected by the PR 
    (e.g. "2300 Conductor - Poly", "Multi-BU: DEP", "2300 Dielectric - FX / GXE / HX", "EOS", "ALTUS/ALTUS Max", "Platform Products - Etch/Clean", "Sabre 3D", "CSBG: Conductor - Reliant", "VECTOR Express", "Sabre", etc)
- "secondary_product_affected_name": Secondary product affected by the PR
- "product_group": Prod group associated with the PR (e.g., GOPS, Dep, GPE, Etch, CSBG, Clean, etc)
- "department": User's department based on who is acting on the PR (e.g., "SQAD", "ENG-Software (Dep)", "Software - 2300 Infrastructure", "SMG", "ENG-Etch-Con", "Eng-CSBG", "Manufacturing", "Product Management - CSBG", etc) 
- "department_category": Hierarchy of department (one level above Department) (e.g., "SQAD - Supplier CIP", "SMT - Ramp Approved - Supplier Capacity addition/expansion/relocation", "ENG - Drafting Mechanical", etc)
- "po_number": Purchase Order number where relevant
- "likelihood": Likelihood of problem recurrence, the values are: 
        -- "Unlikely - No more than once in 10 years"
        -- "Possible - More than once in 5 years, but no more than once per year"
        -- "Likely - More than once per year, but no more than five times in a year"
        -- "Frequent - More than five times in a year"
        -- "Rare - More than once in 10 years, but no more than once in 5 years"
- "end_item": Top level assembly part number (e.g. EI-CVD-C3-SOLA, etc)
- "part_name": Part number related to the PR, this field is used to join eng.vw_IPLMProblemReport table to gq.IQMS_NCE_LIVE table using Part_Number field.
- "actual_completion_date": date the PR was completed. 
- "submitted_date": date the PR was submitted.
- "completion_fisc_qtr_text": the fiscal quarter associated with completion data. The format is typically "QJun'19", "QMar'20", etc.
- "submitted_fisc_qtr_text": the fiscal quarter associated with submitted date. The format is typically "QSep'21", "QDec'22", etc.
"""

field_description = {
    IQMS_NCE_LIVE : nce_live_field_description,
    RPT_IQMS_8D_GRID: eight_d_field_description,
    VW_OAI_ESCALATION_TICKETS: es_field_description,
    VW_IPLM_PROBLEM_REPORT: iplm_field_description,
}


sql_loaded_prefix = """
You are a mssql expert. Given an input question, create a syntactically correct mssql query to run. Do not use LIMIT clause, use TOP instead. Unless otherwise specified, do not return more than {top_k} rows.
Only use the following tables: {table_info}.
{col_desc} 
Add the brackets for all field names.

Below are a number of examples of questions and their corresponding SQL queries:"""

loaded_examples = {
    IQMS_NCE_LIVE : [
        {
            "input": "How many NCEs are in 2023?",
            "query": "SELECT COUNT(*) FROM gq.IQMS_NCE_LIVE where YEAR([Date_Opened])=2023;",
        },
        {
            "input": "Show the top 10 customer groups with highest number of NCes?",
            "query": "SELECT TOP 10 [Customer_Name], COUNT(*) as [Number_of_Records] FROM gq.IQMS_NCE_LIVE GROUP BY [Customer_Name] ORDER BY COUNT(*) DESC",
        },
        {
            "input": "What percentage of NCEs in 2022 have investigation group assigned?",
            "query": "SELECT (CAST((SELECT COUNT(*) FROM gq.IQMS_NCE_LIVE WHERE [Investigation_Group]!='' and YEAR([Date_Opend])=2022) AS FLOAT) / CAST((SELECT COUNT(*) FROM gq.IQMS_NCE_LIVE WHERE YEAR([Date_Opened])=2022) AS FLOAT)) * 100 AS [Percentage]",
        },
        {
            "input": "Are NCE per fid increasing or decreasing during 2023?",
            "query": """WITH NCE_Per_FID AS (SELECT [FID], COUNT([iQMS_ID]) as [NCE_Count], MONTH([Date_Opened]) as [Month] FROM gq.IQMS_NCE_LIVE WHERE 
YEAR([Date_Opened]) = 2023 GROUP BY [FID], MONTH([Date_Opened])) SELECT [Month], AVG([NCE_Count]) as [Average_NCE_Per_FID]
FROM NCE_Per_FID GROUP BY [Month] ORDER BY [Month]
""",
        },
        {
            "input": "How many warranties ended in QDec 2023?",
            "query": "SELECT COUNT(*) count FROM gq.IQMS_NCE_LIVE WHERE YEAR([Warranty_End]) = 2023 AND DATEPART(QUARTER, [Warranty_End]) = 4",
        },
        {
            "input": "are oobq problems increasing or decreasing and by how much on a monthly basis over the last 12 months",
            "query": "SELECT YEAR([Date_Opened]) as [Year], MONTH([Date_Opened]) as [Month], COUNT(*) as [Count] FROM gq.IQMS_NCE_LIVE WHERE [SAP_Damage_Code_Group] = 'OOBQ' AND [Date_Opened] >= DATEADD(MONTH, -12, GETDATE()) GROUP BY YEAR([Date_Opened]), MONTH([Date_Opened]) ORDER BY [Year], [Month]",
        },
        {
            "input": "show the number of nces per fiscal quarters of open date of 2023",
            "query": "SELECT [Date_Opened_Fisc_Qtr], COUNT(*) as Number_of_Records FROM gq.IQMS_NCE_LIVE WHERE [Date_Opened_Fisc_Qtr] LIKE '2023%' GROUP BY [Date_Opened_Fisc_Qtr] ORDER BY [Date_Opened_Fisc_Qtr]",
        },
        {
            "input": "How many FIDs were install complete for BU Deposition?",
            "query": "SELECT COUNT(DISTINCT [FCID]) FROM gq.IQMS_NCE_LIVE WHERE [Escape_Notification_Type] IN ('Z4', 'Z5') AND [Product_Group_Classification] = 'DEPOSITION'",
        },
    ],
    RPT_IQMS_8D_GRID: [
        {
            "input": "How many 8ds were there in 2022?",
            "query": "SELECT COUNT(DISTINCT grid.[iqms_id]) FROM gq.RPT_IQMS_8D_Grid WHERE YEAR([Date_Opened])=2022;",
        },
        {
            "input": "Show the top 8d root cause categories for product group 'ETCH'?",
            "query": """SELECT grid.[Root_Cause_Category_1_G], COUNT(*) FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE nce.[Product_Group_Classification]='ETCH' GROUP BY grid.[Root_Cause_Category_1_G] ORDER BY COUNT(*) DESC;""",
        },
        {
            "input": "How many 8D were opened on Low Impact NCes",
            "query": """SELECT COUNT(DISTINCT grid.[iqms_id]) FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE nce.[Impact]='Low' """,
        },
        {
            "input": "How many 8Ds are currently running?",
            "query": """SELECT COUNT(DISTINCT grid.[iqms_id]) FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE grid.[Current_State] NOT LIKE 'Closed - %'; """,
        },
        {
            "input": "How many 8Ds belong to Samsung?",
            "query": """SELECT COUNT(DISTINCT grid.[iqms_id]) FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE UPPER(nce.[Customer_Name]) LIKE '%SAMSUNG%'; """,
        },
        {
            "input": "List the Root Causes for 8Ds for NCes in Warranty on Sabre tools",
            "query": "SELECT DISTINCT grid.[Root_Cause_Description_G] FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID[] = nce.[iQMS_ID] WHERE nce.[Warranty_Status]='Warranty' AND nce.[Product_Type] LIKE '%Sabre%';",
        },
        {
            "input": "List Preventive actions on parts that cost over $1,000?",
            "query": "SELECT DISTINCT grid.[Preventive_Action_Summary_PA_Description] FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE nce.[Material_Cost] > 1000;",
        },
        {
            "input": "show me the root cause values for 8d iqms id 2477427",
            "query": "SELECT grid.[Root_Cause_Description_G] FROM gq.RPT_IQMS_8D_Grid grid WHERE grid.[iQMS_ID] = 2477427",
        },
        {
            "input": "List corrective actions for DOI on Dep products for 8D closed in the past 4 quarters",
            "query": "SELECT grid.[Corrective_Action_Summary_CA_Description_G] FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.[Parent_ID] = nce.[iQMS_ID] WHERE nce.[SAP_Damage_Code] = 'DOI' AND nce.[Product_Group_Classification] = 'DEPOSITION' AND nce.[Date_Closed] >= DATEADD(QUARTER, -4, GETDATE())",
        },
        {
            "input": "List containment actions for 8Ds assigned to Dep product group",
            "query": "SELECT grid.[Containment_Grid_Conta_Action_Item_G] FROM gq.RPT_IQMS_8D_Grid WHERE Investigation_Group = 'Dep Product Group'",
        },
    ],
    VW_OAI_ESCALATION_TICKETS : [
        {
            "input": "Are there currently any investigations running on part 685-097330-006?",
            "query": """SELECT count(*) FROM es.vw_oai_EscalationTickets esc LEFT JOIN gq.IQMS_NCE_LIVE nce ON CAST(esc.[TicketID] as varchar) =
SUBSTRING([Notification_Number], PATINDEX('%[^0]%', [Notification_Number]+'.'), LEN([Notification_Number])) WHERE nce.[Part_Number]='685-097330-006'""",
        },
        {
            "input": "List all open Tier 1 Escalations on tools being installed for Intel",
            "query": """SELECT count(*) FROM es.vw_oai_EscalationTickets esc LEFT JOIN gq.IQMS_NCE_LIVE nce ON CAST(esc.[TicketID] as varchar) =
SUBSTRING([Notification_Number], PATINDEX('%[^0]%', [Notification_Number]+'.'), LEN([Notification_Number])) WHERE esc.[EquipmentStatusID]='T1' AND UPPER(nce.[Customer_Name]) LIKE '%INTEL% AND nce.[Escape_Notification_Type] IN ('Z4', 'Z5')
            """,
        },
        {
            "input": "How many NCes in 2023 resulted in escalations?",
            "query": """SELECT COUNT(DISTINCT iQMS_ID) m FROM gq.IQMS_NCE_LIVE nce INNER JOIN es.vw_oai_EscalationTickets esc ON CAST(esc.[TicketID] as varchar) = SUBSTRING(nce.[Notification_Number], PATINDEX('%[^0]%', nce.[Notification_Number]+'.'), LEN(nce.[Notification_Number])) WHERE YEAR(nce.[Date_Opened])=2023""",
        },
        {
            "input": "How many NCES on part 27-442905-00 in the last two years have related escalation solver ticket?",
            "query": "SELECT COUNT(*) FROM gq.IQMS_NCE_LIVE nce INNER JOIN es.vw_oai_EscalationTickets esc ON CAST(esc.[TicketID] as varchar) = SUBSTRING(nce.[Notification_Number], PATINDEX('%[^0]%', nce.[Notification_Number]+'.'), LEN(nce.[Notification_Number])) WHERE nce.[Part_Number]='27-442905-00' AND nce.[Date_Opened] >= DATEADD(YEAR, -2, GETDATE())",
        },
    ],
    VW_IPLM_PROBLEM_REPORT : [
        {
            "input": "List all problem report descriptions",
            "query": "SELECT [problem_description] FROM eng.vw_IPLMProblemReport",
        },
        {
            "input": "How many PR are running on part 826-802391-164",
            "query": "SELECT count(*) FROM eng.vw_IPLMProblemReport WHERE part_name='826-802391-164'",
        },
        {
            "input": "How many PR are running on part 826-802391-164",
            "query": "SELECT count(*) FROM eng.vw_IPLMProblemReport WHERE part_name='826-802391-164'",
        },
        {
            "input": "List the root cause corrective actions from iplm data for MATORD",
            "query": "SELECT DISTINCT iplm.[root_cause_corrective_action] FROM eng.vw_IPLMProblemReport iplm INNER JOIN gq.IQMS_NCE_LIVE nce ON iplm.[part_name]=nce.[Part_Number] WHERE nce.[SAP_Damage_Code_Group] = 'MATORD'",
        },
    ],
}


summarization_reduce_template = """A user has asked {user_question}. Summarize the following items with repect to to this question:
 
{doc_summaries}
 
Consolidate the response in the form of bullet points wherever possible. Avoid having more than 10 total bullet points under each heading.
Keep your summary word limit between 150-200 words.
Summary:"""


summarization_map_template = """A user has asked a question: {user_question}. 
To answer this question, you need to summarize the following items: (The items are separated by '==TicketEnd==') 

{content}

Summary:
"""

summarization_map_template = """

Write a concise summary of the given content:

```{content}```

Summary:
"""

acs_vs_sql_prompt = """You are an assistant helping the users to classify if they should use ACS or SQL resources. 
- If the user clearly asks to use ACS, return 'ACS'.
- otherwise, return 'SQL'.
- Please provide only a single word mentioning 'ACS' or 'SQL'.

User: What are the unique iqms ids for 8ds in 2022?
Thought: there is no ACS ask from user. 
Assitant: SQL
User: Display all problems that include the word generator in the past year
Thought: there is no ACS ask from user. 
Assistant: SQL 
User: Use ACS to answer: what are the iplm report with problem description containing shower in 2023?
Thought: The user asked to use ACS. 
Assistant: ACS
User: {}
Thought: """

table_selection_system_message = """Return a list of the names of all the SQL tables that might be relevant to the user question. 
The tables are:

gq.IQMS_NCE_LIVE: {nce_live_columns}
gq.RPT_IQMS_8D_Grid: {grid_columns}
es.vw_oai_EscalationTickets: {es_columns},
eng.vw_IPLMProblemReport: {iplm_columns}

Please include all relevant tables, even if you're not sure that they're needed. Do not return an empty list []. 
Example: 
User: How many nce are there in 2021?
Assistant: ["gq.IQMS_NCE_LIVE"]
User: List all corrective actions made on part 123333 and the dates they completed D6?
Assistant: ["gq.IQMS_NCE_LIVE", "gq.RPT_IQMS_8D_Grid"]
User: Are there currently any investigations running on part 685-097330-006?
Assistant: ["es.vw_oai_EscalationTickets", "gq.IQMS_NCE_LIVE"]
User: Summarize the Description from escalation solver data?
Assistant: ["es.vw_oai_EscalationTickets"]
User: Summarize the NCe Description in 2023?
Assistant: ["gq.IQMS_NCE_LIVE"]
User: Summarize the Description from iplm problem report data?
Assistant: ["eng.vw_IPLMProblemReport"]
User: Summarize the benefits from iplm data?
Assistant: ["eng.vw_IPLMProblemReport"]
User: What are the most common root cause corrective actions in iplm data?
Assistant: ["eng.vw_IPLMProblemReport"]
User: Summarize the 8d root causes in 2022?
Assistant: ["gq.RPT_IQMS_8D_Grid"]
User: What is the current state of iQMS ID 2393405
Assistant: ["gq.RPT_IQMS_8D_Grid"]
User: {user_question}
Assistant: 
"""


pipeline_creator_prompt = """ You are an assistant answering questions to the user based on a database that we have. The user might ask a question that only requires SQL query, 
or they may ask a question that requires SQL query and an additional summarization postprocessing. The summarization step will be applied to one of the free-text columns 
of the data resulting from the SQL query. Your job is to parse the question into two components as follows:
- The SQL component that will be sent to a SQL agent and will be converted into a SQL code. 
- The summarization component that indicates the column of the data that needs to be summarized based on the question. The question should include phrases such as "summarise" or "what are the common", etc. If there is no summarization
needed return "". If the user ask to list, show, display, etc and the question does not include summazrization request then return "" for Summarization_Component.
 
Only return the two components in a dictionary format with keys "SQL_Component" and "Summarization_Component"

User: What is the count of NCes in 2022?
Assistant: {{"SQL_Component": "What is the count of NCes in 2022", "Summarization_Component": ""}}

User: What are the common NCe issues for damage code WRNG?
Assistant: {{"SQL_Component": "Show me the Description for all records for damage code WRNG?", "Summarization_Component": "Description"}}

User: Show the top 10 customer groups with highest number of NCes?
Assistant: {{"SQL_Component": "Show the top 10 customer groups with highest number of NCes?", "Summarization_Component": ""}}

User: Summarize the 8d root causes in 2022?
Assistant: {{"SQL_Component": "Show me the 8d root causes in 2022?", "Summarization_Component": "Root_Cause_Description_G"}}

User: List the Root Causes for 8Ds for NCes in Warranty on Sabre tools?
Assistant: {{"SQL_Component": "List the Root Causes for 8Ds for NCes in Warranty on Sabre tools?", "Summarization_Component": ""}} 

User: Show me the summary of NCEs with ETCH in QMarch 2022?
Assistant: {{"SQL_Component": "List Decription for ETCH in first quarter of 2022?", "Summarization_Component": "Description"}} 

User: Summarize the NCEs in 2022?
Assistant: {{"SQL_Component": "Show me the NCE Description for all records in 2022?", "Summarization_Component": "Description"}}

User: What are the most common root cause corrective actions in iplm data?
Assistant: {{"SQL_Component": "Show me the root_cause_corrective_actions for iplm problem reports", "Summarization_Component": "root_cause_corrective_action"}}

User: Summarize the problem descriptions on NCes for 839-102001-136?
Assistant: {{"SQL_Component": "List all descriptions from NCe table for part 839-102001-136", "Summarization_Component": "Description"}}

User: Find the top 5 most costly parts that failed in QSep 2024?
Assistant: {{"SQL_Component": "List 5 most costly parts that failed in third quarter of 2024", "Summarization_Component": ""}}

User: What were the most common NCE problems experienced in product types like vantex in qSep 2023 in NCE table?
Assistant: {{"SQL_Component": "List the description for product types like vantex in the 3rd qaurter of 2023 in NCE table?", "Summarization_Component": "Description"}}

User: What were the most common part numbers responsible for install nces in qMar 2024
Assistant: {{"SQL_Component": "List the part numbers with highest count for 1st qaurter of 2024 install nces?", "Summarization_Component": ""}}

User: For perf problems in etch systems in qJun 2023 what are the most common types of NCE failures in problem description?
Assistant: {{"SQL_Component": "List description for PERF for ETCH systems for 2nd qaurter of 2023 form NCE table?", "Summarization_Component": "Description"}}


User: What are the top 5 most costly parts that failed date in qMarch 2024?
Assistant: {{"SQL_Component": "What are the top 5 most costly parts that failed date in 1st quarter of 2024?", "Summarization_Component": ""}}

User: for the 5 most costly parts categorize problems in the description field?
Assistant: {{"SQL_Component": "Show Description from the nce data where part number belongs to the 5 most costly parts", "Summarization_Component": "Description"}}

User: {user_question}
Assistant: 
"""


acs_query_creator = """
# Objective:
Convert the user's query into relevant keywords for querying the Azure Cognitive Search (ACS) index, ensuring the following criteria are met:

- Identify and extract keywords from the user's query that can be used to search in the ACS index.
- Spelling and Phrasing: Correct any spelling mistakes and standardize variations in phrasing to improve search accuracy.
- Return only meaningful and relevant keywords, avoiding any that are irrelevant or prone to errors.
- Exclude keywords related to product groups, departments, or any filter-related information.
- Do not include years, timestamps, or dates as keywords.
- Do not include table or database names such as: nce, 8d, iplm, iqms, escalation solver, gq.
- Exclude generic words from the user input such as: records, issue, problem, descriptions, common, summary, value, field.
- Utilize fuzzy search capabilities to handle spelling errors and variations.
- The user's intention may include some SQL components. These SQL expressions will be executed separately and should not be included in the keywords.

# Output:
Return only the search query keywords as a comma-separated list, nothing else.

# Examples:

User: "show me the count of nce issues related to valve per customer in product group ETCH"
Assistant: valve
User: "can you give me a list of iqms ids that are affected by the valve leakage problem"
Assistant: valve, leakage
User: "show me the summary of the 2023 dc problem from the deposition"
Assistant: leakage
User: "I would like to show the sum of cost of generator issues per customer in 2023 for Intel"
Assistant: generator
User: List the issues with valve in the field problem description in iplm data
Assistant: valve
User: "{0}"
Assistant:
"""


agent_prefix = """You are a chatbot agent, assisting users with some questions they ask. The question user asks can be answered using a single tool you have (full_pipeline). 
Here is your instruction:
1. Receive user question. 
2. Decide to run the full_pipeline tool with the user question updated with the conversation history or ask follow-up question in following cases:
- If the user specifies "product" they should clarify which of the following fields: 
nce: Part_Product_Family, Product_Group_Classification, Product_Group, Product_Type, System_Description_Group, System_Description, ABC_Description, MyLam_System, Org_Group
iplm: primary_product_affected_name, secondary_product_affected_name, product_group
- If the user ask about a year or date or quarter such as QMarch, QMar, QSep, QJun, QDec, they should clarify which of the date columns listed below: 
nce: Date_Current_State, Date_Opened, Part_Fail_Date, RAM_Status_Date, Warranty_End, Actual_Ship_Date, Date_Opened_Fisc_Qtr, Date_Closed
8d: Corrective_Action_Implementation_Date, Containment_Grid_Conta_Item_Commit_On, D5_Completed_by_QCO_Date, D6_Validated_Date, Date_Opened, Date_Opened_Fiscal_Qtr_Text, Corrective_Action_Summary_Implementation_Commit_Date_G, Preventive_Action_Summary_Implementation_Date
es: OpenDate, ClosedDate, open_fisc_qtr_text, closed_fisc_qtr_text
iplm: actual_completion_date, submitted_date
- If the user ask about failure mode, they should clarify failure mode in which of the below fields: 
nce: Description, Nce Log, SAP Damage Code, Symptom Detail
8d: Root Cause Description or Root Cause Category (levels 1 - 3).  
es: Description, Problem Statement, Hypothesis 
iplm: Problem Description, Reason, Cause Code, Root Cause Corrective Action.
3. If the user mentions part, run the tool with the user question updated with the conversation history.
"""


pipeline_tool_description = """
- This is the tool that need to be used most of the time. It runs a pipeline to go fetch the information required to answer the user question about the iqms, iplm, or escaltion solver data. """


sql_explainer_prompt = """You are an assistant helping the user understanding a SQL query. 
Summarize the query into the following sections: tables, joins, fields by table, any aggregation (avg, count, etc), filters, grouping, and overall summary.
Examples
User: SELECT DISTINCT grid.Preventive_Action_Summary_PA_Description FROM gq.RPT_IQMS_8D_Grid grid LEFT JOIN gq.IQMS_NCE_LIVE nce ON grid.Parent_ID = nce.iQMS_ID WHERE nce.Material_Cost > 1000;
Assistant: 
#### Tables:
 - gq.RPT_IQMS_8D_Grid (aliased as grid)
 - gq.IQMS_NCE_LIVE (aliased as nce)
#### Joins:
 - Type: LEFT JOIN
 - Condition: grid.Parent_ID = nce.iQMS_ID
#### Fields by Table:
 - gq.RPT_IQMS_8D_Grid (aliased as grid): Preventive_Action_Summary_PA_Description
 - gq.IQMS_NCE_LIVE (aliased as nce): iQMS_ID, Material_Cost
#### Aggregation:
 - DISTINCT: The query uses DISTINCT to ensure that only unique values of grid.Preventive_Action_Summary_PA_Description are selected.
#### Filters:
 - nce.Material_Cost > 1000
#### Grouping:
 - did not exist. 
#### Overall Summary:
This query selects unique descriptions of preventive actions from the gq.RPT_IQMS_8D_Grid table, where the corresponding material cost in the gq.IQMS_NCE_LIVE table is greater than 1000. The tables are joined on the Parent_ID field from grid and the iQMS_ID field from nce.


User: {0}
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
"How many 8ds with Date Opened in 2022?"

Output:
{{"": 4748}}

Response:
There were 4748 8ds with Date Opened in 2022.

User Input:
{0}

Output:
{1}

Response:
"""

ambiguity_checker_prompt = """
You are an assistant checking if the user input is ambiguous or it contains enough information. 
1. Receive user question.
2. Check against the following ambiguities and list all ambiguous items.  
- Product: If the user specifies "product" but not any of the specific fields: Part Product Family, Product Group Classification, Product Group, Product Type, Primary Product Affected, Secondary Product Affected, System_Description_Group, System_Description, ABC_Description.
- Date: If the user asks about a year or date or quarter such as QMarch, QMar, QSep, QJun, QDec, but has not clarified which of the date columns listed below: 
    -- nce: Date_Current_State, Date_Opened, Part_Fail_Date, RAM_Status_Date, Warranty_End, Actual_Ship_Date, Date_Opened_Fisc_Qtr, Date_Closed
    -- 8d: Corrective_Action_Implementation_Date, Containment_Grid_Conta_Item_Commit_On, D5_Completed_by_QCO_Date, D6_Validated_Date, Date_Opened, Date_Opened_Fiscal_Qtr_Text, Corrective_Action_Summary_Implementation_Commit_Date_G, Preventive_Action_Summary_Implementation_Date
    -- es: OpenDate, ClosedDate, open_fisc_qtr_text, closed_fisc_qtr_text
    -- iplm: actual_completion_date", submitted_date"
- Failure: If the user asks about failure or failure mode, they should clarify failure mode in which of the below fields: 
    -- nce: Description, Nce_Log, SAP_Damage_Code, Symptom_Detail
    -- 8d: Root Cause Description or Root Cause Category (levels 1 - 3).  
    -- es: Description, Problem Statement, Hypothesis 
    -- iplm: Problem Description, Reason, Cause Code, Root Cause Corrective Action.
3. If there is no ambiguity, return "No ambiguity"

Example:
User: What are the unique iqms ids for 8ds in 2022?
Thought: The user asked about year but did not clarify which fields to filter for 2022. There is an ambigity regarding date.
Assistant: Date
User: What are the unique iqms ids for 8ds in 2022?
Thought: The user asked about year but did not clarify which fields to filter for 2022. There is an ambigity regarding date.
Assistant: Date
User: What failures are there on parts ending in -136 in the last year?
Thought: The user asked about last year but did not clarify what field to use for year. The user aslo asked about failures and there is an ambiguity there as well. 
Assistant: Date, Failure
User: Show me the nce count per product group?
Thought: The user asked about product group and it is clear that we can use produt group field. There is no other ambiguity in the question.  
Assistant: No ambiguity
User: {}
Thought:
"""



acs_index_names_mapping = {
  IQMS_NCE_LIVE : "index-oai-nce-live", 
  RPT_IQMS_8D_GRID : "index-oai-rpt-8d-grid",
  VW_IPLM_PROBLEM_REPORT : "index-oai-iplm-problem-report",
  VW_OAI_ESCALATION_TICKETS : "index-oai-escalation-tickets"
}

index_key_date_column_mapping = {
    acs_index_names_mapping[IQMS_NCE_LIVE]: {
        "key": "iQMS_ID",
        "acs_key":"iQMS_ID",
        "date": "Date_Opened"
    },
    acs_index_names_mapping[RPT_IQMS_8D_GRID]: {
        "key" : "ACS_Key",
        "acs_key": "ACS_Key",      
        "date" : "DWH_Update_Date"
    },
    acs_index_names_mapping[VW_IPLM_PROBLEM_REPORT]: {
        "key" : "ACS_Key",
        "acs_key": "ACS_Key",           
        "date" : "SUBMITTED_DATE"
    },
    acs_index_names_mapping[VW_OAI_ESCALATION_TICKETS]: {
        "key": "ACS_Key",
        "acs_key": "ACS_Key",
        "date": "OpenDate"
  }
}



nce_live_index_description = f"""
ACS index {acs_index_names_mapping[IQMS_NCE_LIVE]} has the following fields:
- "ABC_Description": High level product grouping (with values "Transport Module", "Etch Dielectric", "CVD", "Etch Conductor Poly", "Electrofill", "Product Upgrade", etc). This grouping would be the next level below Product Group. After this level product starts to break into product family.
- "Begin_Guarantee": Begin Guarantee is the warranty start date.
- "Commit_Date_Impact": This field is essentially a flag that indicates whether the NCE is likely to have significant impact to the commit date communicated to the customer with values "Major Commit date missed", "None", "Minor Commit date missed", or "". 
- "Removed_Part_Family": This field represents the part family of the part that failed on the NCe. It is also referred to as the "removed part" or "commodity type". Examples are "RF, Generator", "Valves", "Cables and Harnesses", "Controllers", "PCB", "Filter", etc. Always search this field with sql LIKE operator. 
- "Customer_Group": This bins Customer Names into groups for the company's most common customers since a Customer can have multiple names and accounts. The values include: "UMC", "YMTC", "SK Hynix", "Kioxia", "SEC", "Micron", "ROW", "ST Micro", "TSMC" and "Intel". SEC may also be referred to as Samsung. "ROW" stands for Rest Of World and is the grouping for all other Customers not grouped here. Higher fidelity mapping is in the NCe "Customer_Name" field
- "Customer_Name": specifies who owns the tool being worked on
- "Customer_Temperature_Impact": This field indicates how sensitive the customer is relative to NCEs, with values "Mild", "Unknown", "", "Warm", "Not visible to customer", "Hot", "Severe", "Section Supervisor"
- "Date_Current_State": Date of the current state of the NCe. 
- "Date_Opened": is the generated data and time of the NCe record
- "Description": provides a narrative on what went wrong and is specific to the NCe
- "Escape_Description": Additional text regarding what is going wrong with the part associated with the failure. Often times there is some history explained in the field with along with dates. 
- "Escape_Notification_Type": Also referred to as Serivce Notification Type comes from SAP. Z4 and Z5 represent install NCes, Z3 represent non-install NCes and Z1 are for NCes for direc part orders not tied to Lam serviced tools
- "Escape_Title": This field is related to the other escape fields it is essentially a summarized version of the other escape description fields:  Escape and Description.
- "Fab_Name": This is the customer site where the tool is operating.
- "FCID": This is a string describing the identification number of the tool. Synonymous term is FID. This identification number is often used as the basis for normalizing NCE counts as in NCE per FID (or FCID because it is synonymous). FID level is a frequent level of analysis.
- "Field_Owner": This is the Field Service Engineer who is responsible for the FID / FCID number tool at the customer fab.
- "FQM_Owner": FQM is the next level up from FSE. Functional Quality Managers manage Field Service Engineers.
- "Functional_Location": This is a code associated with the customer and the fab. Infrequently used field, primary levels of use as Customer and Fab Name. This field essentially combines them into a single system code.
- "Geo_Region_Member": represents the geographical region associated with the NCe, the values include: "KOREA", "FAR EAST", "TAIWAN", "CENTRAL EUROPE", "CENTRAL", "WEST", "MALAYSIA", "JAPAN", "EAST COAST", "NORTHERN EUROPE", "SOUTHERN EUROPE", "CHINA" or ""
- "Management_Region": represents the management geo region, the values include: "KOREA", "N. AMERICA", "TAIWAN", "CHINA", "JAPAN", "", "EUROPE", "SEA".
- "IBASE_Sales_Order": Sales order number identifying the contract in the ibase system
- "IBASE_Serial_Number": Serial number of the tool used in the ibase system
- "IBFAB_Description": Similar to functional location this filed is another description of where the FID operated geographically.
- "Impact": Impact can be set to Safety, Critical, Medium or Low and is based on the impact to the customer
- "Installation_Team_Lead": This is the name of the FSE who is leading the team installing the FID at the customer site.
- "Investigation_Group": represents the investigation group assigned to the NCe. If no investigation group is assigned the value is "". Other values are "Supplier", "Etch Product Group", "Logistics/Warehouse", "Dep Product Group", "Field Service", "BOM Configuration", "Engineering", "Manufacturing", "Manufacturing - Tualatin", "Manufacturing - Livermore", "Global Ops Order Fulfillment", "Global Ops Config Eng", "Global Products Engineering", "Pilot", "Reliant PG (CSBG)", "Sales Ops", "Clean Product Group", "Product Group/Engineering", "Manufacturing - Silfex", etc. 
- "Investigation_Required": Yes/no field related to the impact field. Safety and critical usually require investigation which is a formal process to understand the NCE on a more detailed basis. The process to investigate is the 8D process.
- "iQMS_ID": serves as the quality management system record key and it represents an NCe ID in this table
- "LPR_Type": This is a code for the type of LPR with values "PM", "UPG", "ATM", "OTHER", etc. 
- "Material_Cost": represents the total cost of parts
- "Model_Number_Group": This is the model number group field
- "MRBe_Comments_Log": This field holds comments from the MRBe log this time stamps the free text entered for the MRBes.
- "MyLam_System": This is a product type field containing a product name. When people ask for product type this is one of the fields that should be utilized, but not the only one.
- "NCeFrequency": This field should be utilized whenever part failure frequency questions are asked. It represents the count of NCEs with the same damage code and part number at the time of the NCE creation.
- "NCe_Log": will contain time-stamped free text inputs from iQMS users providing context and information on the NCe that is not captured elsewhere in the record
- "NCe_Risk_Assessment_Level": The NCe Risk Assessment Level, denoted as NCe_Risk_Assessment_Level, is essentially the output of a function that calculates based on frequency and cost to Lam and includes other factors, and it highlights the impact of this NCe to Lam, with lower numbers representing higher impact to Lam; notably, Risk Assessment Level 1 would be the worst for Lam.
- "Nonconformance_Type": This is a field that denoted it is an NCE. it does not really provide much explanatory value.
- "Notification_Number": The Notification Number is assigned by SAP. In the NCe table, this represents the key for the parent Quality Escape of the given NCe. If an Escalation Solver ticket is opened for the NCe's parent Quality Escape, the TicketID in Escalation Solver will match the Notification Number and can be used as a key for table joins
- "Object_Type": Object type
- "Opportunity_Type_Desc": This field denotes the kind of sales opportunity associated with the NCE. PG system opportunity vs CSBG system opportunity vs Eval system opportunity are the kinds of opportunities that are included in this field.
- "Ordered_Part_Description": this field holds the codes and descriptions of the parts that were ordered associated with resolution of this nce. 
- "Org_Group": This is another product type level. It is a mid-level grouping of product types. When users are interested in product types but getting too low level or too many product types in the results this field would likely be a sensible grouping level for product type.
- "Original_Service_Order_Number": Original Service Order Number also call Service Order or SO is assigned by SAP. A Service Order will have one to many notification numbers. Tools are installed with a single service order, but may have many service orders for warranty or other contract work
- "Originator": This is the person who initiated the NCE
- "Part_CE": Part CE with values "Yes" or "No"
- "Part_Cost": This is the material cost of the part associated with the nce.
- "Part_Critical_Classification": Part Critical Classification (e.g. "NC", "C1, "C4", etc)
- "Part_Description": This is a text description in abbreviated code form that describes the part associated with the NCE. It is linked to the part_number as in every part_description has an associated part_number
- "Part_Fail_Date": This is the fail date for the part number. It is infrequently populated.
- "Part_Number": specifies the part number being replaced in an attempt to fix the tool
- "Part_Product_Family": specifies the type of tool being worked on
- "Part_Quantity": Part Quantity specifies the number of parts that failed and are being ordered. This can be an integer 1 or higher
- "Product_Group_Classification": specifies the Product Group responsible for the tool (e.g. 'ETCH', 'DEPOSITION', 'CLEAN', etc)
- "Product_Group": This is a mid-high level product grouping field. It is closer to product family than product type. (some values are: 'FLEXHXP', 'SABRE', 'KIYO-GX', 'TM', 'UPGRADE', 'VANTEX', 'KIYO-FXE', 'STRATA', etc)
- "Product_Type": This field represents the product type associated with the NCE. This should be the first level of grouping when users ask for product level results.  
- "Purchase_Make": specifies whether Lam manufactures the part or purchases it directly from a vendor (with values "MAKE" or "PURCHASE")
- "QPL_Owner": QPL Owner is the Quality Product Lead assigned to the NCe. QPLs are generally aligned to geographic regions
- "RAM_Number": RAM number is a tracking number used by reverse logistics to ship the return of a part. Not all NCes have part returns or RAMs, but there can be only one RAM per part
- "RAM_Status_Date": RAM Status Date is the last time the RAM status was updated
- "RAM_Status_Description": RAM status specifies what is currently happening on the part return 
    (e.g. "RAM COMPLETED", "IN QUARANTINE", "SCRAPPED - PART THROWN AWAY", "RAM ISSUED", "RAM ITEM DELETED", "IN TRANSIT TO REPAIRING PLANT", "ISSUED TO ENGINEERING", etc)
- "RAM_Type": RAM Type (with values: "", "WR", "CUSTRETURN", "DEFECTZFSE", "FA_ONLY", "OTHER/QDR", or "NCE")
- "RTV_Requestor": RTV requestor is the person who requested the part be returned to vendor
- "Safety_Impact": Safety Impact is answered by the FSE and is part of the Impact calculation. The NCe can be classified with the following values ("Safety incident", "Safety Risk/Near Miss" or "No")
- "Sales_Order_Line_No": This specifies the portion of the contract that the Service Order for this NCe is being performed on. It will be an integer.
- "Sales_Order_No": Sales Order Number is an integer key assigned by SAP for the work Lam is contracted to do
- "SAP_Damage_Code_Group": is a categorical description of the broad category of damage for the part. Values for the damage code group include: 
    -- "OOBQ": Out of Box Quality issue where the part fails to function upon arrival or install 
    -- "PERF": Performance issue where the part worked for a period of time, but failed early than it should have 
    -- "SWPR": Software Problem that can be fixed without a part order 
    -- "MATORD": is a non-quality defect"
- "SAP_Damage_Code"": SAP_Damage_Code"" specifies the type of damage. Values include: 
    -- "WRNG": Wrong | Part number does not match expected part 
    -- "MSPT": Missing | Part missing from shipment 
    -- "OVS": Overstock | More parts shipped than structured or requested  
    -- "SPEC": Spec | Part received does not match drawing (Lam spec) 
    -- "DMG": Damaged | Part arrived damaged 
    -- "PLBL": Part Label | Part has incorrect label 
    -- "DOI": Dead on Install | Part does not work upon initial installation (Lam spec) 
    -- "ELF": Early Life Failure | Part failed within 90 days of installation  
    -- "RAM": Reliability and Maintenance | Part fails at inconsistent intervals (beyond 90 days)  
    -- "INST": Software installation issues (< 2 weeks after SW upgrade) 
    -- "SWDF": Software defect 
    -- "USER": User error related to software 
    -- "CANC": Cancelled | Part order canceled or duplicate NCe identified 
    -- "COMB": Combined | Additional parts damaged due to other part defects OR Parts missing or wrong from a non-FRU Kit/Assembly 
    -- "DIAG": Diagnostics | When ordering parts for troubleshooting ONLY 
    -- "DUPL": Duplicate | Duplicate entry 
    -- "CSPC": Customer Statistical Process Control | Meets Lam spec, does not meet customer SPC/FDC limits 
    -- "HNDL": Handling | Part damaged after arrival 
    -- "LOST": Lost | Part lost during install 
    -- "PRVM": Preventative Maintenance | One-time use, or when ordering supplemental parts needed to support replacement of another quality issues (e.g., O-rings / VCR gasket on Valve Failure) 
    -- "UPGR": Upgrade | Parts ordered for upgrade or enhancement 
    -- "ZNOL": Not listed | Does not fit any other Damage Code 
    -- "ZORD": Wrong part ordered | Incorrect part ordered by account team "
- "SAP_Mandatory_Return": SAP Mandatory Return specifies if this part must be returned due to scarcity or other reasons for Lam, with values "Yes, or "No"
- "Serial_Number": This is the serial number of the part associated with the NCE
- "Supplier_Name": represents the Vendor of the part, who supplied the part.
- "Symptom_Detail": This is a failure grouping. It is different from the damage codes but there is overlap between concepts in DIAG for example. In essence this field describes the symptom that cause the NCE. Electrical, mechanical, communication, leaks, etc are all kinds for additional symptoms that can be identified in this field.
- "Symptom": This is the highest level of failure types. Examples include functional failures, MATORDs, Missing, etc. It is closely associated to damage code group but includes some other descriptive alternatives
- "System_Description_Group": This is another product type description but not the most useful. This field should be utilized infrequently because the grouping level is about the lowest level if it is actually populated. More useful would be using this field in tandem with a higher level product type field. 
- "System_Description": This is another product type field. It is very detailed and like system_description_group is very low level so grouping at this level will only work when it is a very specific question. It is a concatenated field of various grouping levels. 
- "Title": This is a very high level summary of the failure description.
- "Total_Nce_Cost": represents the total cost of parts and estimated labor costs incurred for this NCe
- "Triage_SPOC_Owner": This is the single point of contact for triaging the NCE
- "Type_of_Activity": specifies type of the work being performed by the engineers (e.g. "INSTL", "WARR", "EVAL", "STRTUP", "VARSPR", etc)
- "Warranty_End": This is the date of the end of the warranty period. After this point Lam is not responsible for covering the cost of tool failures.
- "ZFSE_Norm": specifies whether the removed part is "ZFSE", "NORM" or ""
- "Actual_Ship_Date": Actual Ship Date also referred to as ASD. This represents the date the tool shipped to the customer
- "Actual_Ship_Fiscal_Quarter_Text": This represents the fiscal quarter of Actual ship date. The format is typically "QDec'19", "QSep'20", etc. 
- "Installation_Complete_Calendar_Quarter_Text": This is the fiscal quarter the tool installation was completed for the customer. The format is typically "QDec'19", "QSep'20", etc. 
- "Date_Opened_Fisc_Qtr_Text": Fiscal quarter when the NCe was opened. The format is typically "QDec'19", "QSep'20", etc. 
- "Date_Closed": Date the NCe was closed
"""
eight_d_index_description = f"""
ACS index {acs_index_names_mapping[RPT_IQMS_8D_GRID]} has the following fields:
- "D_Priority": represents the level of importance for the investigation ranging from Priority 1 to Priority 4. The lower the number, the higher the priority
- "Preventive_Action_Summary_Implemented": remains null while preventive actions are in process for an 8D and then set to "Yes" if completed or "No" if not completed
- "Corrective_Action_Action_Implemented": remains null while corrective actions are in process for an 8D and then set to "Yes" if completed or "No" if not completed
- "Corrective_Action_Summary_CA_Description_G": free text summarizing the corrective action
- "Corrective_Action_Implementation_Date": corrective action implementation date
- "Containment_Grid_Conta_Action_Item_G": free text summarizing the containment action description
- "Containment_Grid_Conta_AI_Comp_On_G": remains blank until the containment action is completed and then is populated with the date the containment action was completed
- "Containment_Grid_Cont_AI_Owner_First_Name": This is the first name of the owner of the containment action item this person is responsible for implementation
- "Containment_Grid_Cont_AI_Owner_Last_Name": This is the last name of the owner of the containment action item this person is responsible for implementation
- "Containment_Grid_Conta_Item_Commit_On": Date of commitment for containment item
- "Corrective_Action_Summary_Corrective_Action_Owner_G_First": First name of the owner of the implementation of the corrective action
- "Corrective_Action_Summary_Corrective_Action_Owner_G_Last": Last name of the owner of the implementation of the corrective action
- "Current_State": specifies the current state of the record with values. If a record is closed, the state will start with "Closed - "
- "D5_Completed_by_QCO_Date": this is the date that d5 was completed
- "D6_Validated_Date": date that the d6 step was validated
- "Date_Opened": date that the case was opened in the system
- "Date_Opened_Fiscal_Qtr_Text": The fiscal quarter associated with Date_Opened. The format is typically "QJun'19", "QMar'20", etc. 
- "FQM_Owner": This is the FQM assigned to the case
- "Impact": Impact field records the effects or consequences of the observed symptoms the system.
- "Corrective_Action_Summary_Implementation_Commit_Date_G": date committed for implementation corrective action
- "Preventive_Action_Summary_Implementation_Date": date of implementation of the corrective action
- "Investigation_Group_Detail": This is what is being investigated or the responsible group for the investigation. The values include: "N/A", "", "001 - Main", "031 - Upper Chamber", "023 - PM Test", "032 - Lower Chamber", "SFS", "Mechatronics Engineering", "Part Supplier", "Mfg Engineering", "008 - Enclosure", "033 - Chamber Test", "Remote Factory", "Conductor", "Product Management", "Dielectric", "03002 Decon", "Engineering", "Manufacturing", "?", etc.
- "Investigation_Group": This is the assigned functional group within Lam Research that is leading the investigation. Example values include: "Supplier", "Manufacturing", "Dep Product Group", "Etch Product Group", "Global Products Engineering", "Warehouse", "Manufacturing - Tualatin", "Logistics/Warehouse", "Manufacturing - LMM", "Reliant PG (CSBG)", "Clean Product Group", "Manufacturing - Livermore", "Pilot", "Manufacturing - Villach", "Manufacturing - Silfex", "CFT", "Resupply", "Product Group/Engineering", "Manufacturing - LMK", "Order Fulfillment", etc.
- "iQMS_ID": serves as the quality management system record key and it represents an ID in this table
- "Preventive_Action_Summary_PA_Description": free text summarizing the preventive action
- "Parent_ID": is equivalent to "iqms_id" field in GQ.IQMS_NCE_LIVE and the key to join that table
- "Part_Number": Part number associated with the NCE that has triggered the 8D investigation
- "Part_Description": Part description associated with the NCE that has triggered the 8D investigation
- "Preventive_Action_Summary_First_Name": First name of owner of the preventative action assigned
- "Preventive_Action_Summary_Last_Name": Last name of owner of the preventative action assigned
- "QPL_Owner": This is the QPL assigned to the case
- "Root_Cause_Summary_Seq_No": identification number of the assigned root cause
- "Reason_CA_Not_Implemented": text field explaining reasoning for no implementation of the corrective action
- "Preventive_Action_Summary_Reason_not_Implemented": text field explaining why the corrective action was not implemented
- "D_Record_Owner": This is the owner of the 8D entry
- "Root_Cause_Category_1_G": represents categorical binning of the root cause
- "Root_Cause_Category_2_G": root cause subcategory.
- "Root_Cause_Category_3_G": root cause subcategory.
- "Root_Cause_Description_G": free text summarizing the root cause description
- "Team_Member_Grid_Team_Member_G_First_Name": First Name of Team member assigned to the 8d
- "Team_Member_Grid_Team_Member_G_Last_Name": Last Name of Team member assigned to the 8d
- "Team_Member_Grid_Team_Member_Business_Unit_G": team member's assigned business unit
- "Team_Member_Count": Number of Team Members assigned for the 8D
- "Team_Member_Grid_Team_Member_Role_G": the functional role of the team member assigned
- "Team_Member_Grid_Team_Member_Functional_Role_G": That team member's role on the team
- "Title": title is a brief description of the 8D case, basically a short overview of the problem and/or symptom under investigation
- "D_Finding_Details": This is the next level down of the 8D finding.  Example: for workmanship 8d finding, there can be many finidng details like negative practice, accidental damage, assembly error, etc.
- "D_Finding": This is the summary result of the 8D assigning the fault to some process grouping like Workmanship, configuration, facitlities, etc.
- "D3_Summary": This is the summary of the D3 step which is to Develop interim containment plan; implement and verify interim actions
- "D4_Commit_Date": Date of the d4 step
- "D4_Summary": Summarization of the 8D step to Determine, identify, and verify root causes and escape points
- "D5_Due_Date": due date for the d5 step.
- "D5_Summary": Summarization of the 8D step to Choose and verify permanent corrections (PCs) for problem/nonconformity
- "D6_Actual_Implementation_Date": date of implementation of the d6 step which is to implement and validate corrective actions
- "D6_Summary": Summarization of the 8D step to Implement and validate corrective actions
- "D7_Implemented_Date": date preventative measures were implemented
- "D7_Summary": Summarization of the 8D step to Take preventive measure
- "Description": description field is a longer version of the title field.  It relays important text information about the case under investigation.  Users generally use this field to give an overview of the problem underinvestigation,
- "Final_Problem_Statement": Problem statement resulting from completion of the 8D
- "First_Why": Summary of the first why in the 8d investigation process
- "FQM_Approved_8D_Date": Date that the fqm approved the 8D
- "Initial_Problem_Statement": Initial problem statement is the starting point for the 8D investigation.
- "Originator:First_Name": indicates the frist name of the person who opened the case in the system
- "Originator:Last_Name": indicates the last name of the person who opened the case in the system
- "QPL_Approved_8D_Date": Date that the QPL approved the 8D
- "Quality_Risk_Level": This is the risk level associated with the case.  Can be risk level 1 through 4 or mandatory critical.  Risk level 1 is high, 4 is low and mandatory critical is a different scale which has to be addressed as top priority.
- "Related_Records": These are other cases that are related to the same part that have been conducted in the past.
- "Responsible_Group": Group responsible for the 8D
- "Submittd_to_Close_w_no_RC_Date": This is a date field for submitted to close without an RC date
- "Supplier_8D_First_Pass_Yield": First pass yield value for the part
- "Supplier_Code": This is a numeric code used to identify the supplier
- "Supplier_Name": Supplier of the part under investigation.
- "Symptom_Detail": this is a detailed explanation of the symptom field. The difference between this field and the symptom field is the level of detail provided.  More detailed in this field.
- "Symptom": symptom field is the primary issue under investigation.  It is an observable sign or indication that there is an issue or malfunction within the system.
- "D6_Completed_Date": Date of the D6 step completion
- "D6_Completed_Date_Fiscal_Qtr_Text": Quarter of the D6 step completion
- "D_Closed_Date": Date 8D Closed
- "D_Closed_Fiscal_Qtr_Text": Quarter the 8D Closed
"""

escalationsolver_index_description = f"""
ACS index {acs_index_names_mapping[VW_OAI_ESCALATION_TICKETS]} has the following fields:
- "ESCustomerID": Escalation Solver Customer Identifier code
- "EquipmentID": Refers to a unique numerical identifier for the equipment/product. Used in SAP.
- "EquipmentStatusID": EquipmentStatusID": An ID with values (T0, T1, T2, or T3) specifies the tier status of the equipment. For example, EquipmentStatusID="T1" shows tier 1 escalation tools. It may also be referred to as "Type", 'Tier", "EquipmentStatus" 
- "EqParentID": Refers to a unique numerical identifier for the higher level equipment a module would report into. Used in SAP.
- "WaferSize": Describes the size of the wafer/product with values "125MM", "450MM", "150MM", "200MM", or "300MM"
- "ModuleType": Type of module with values U, T, S, or M
- "PlatformType": Platform related to the product (e.g. DEPOSITION, ETCH, CLEAN, ADVANCED SERVICES, UPGR, etc)
- "ObjectType": Type of tool (e.g. 2300FEOL, VECTOR, SABRE, SPINBEOL, ALTUS, 2300BEOL, SPEED, ALLIANCE, SPINFEOL, GAMMA, etc)
- "ABCIndicator": Describes nature of the equipment/system (e.g. V, T, K, P, L, D, W, M, etc)
- "ModelNo": Model Number of the product (e.g. "Q STRATA", "XPR", "STRIKER OXIDE FE", "VER METAL PM", "MAX", "STRIKER CARBIDE CK", "DV28", "EXELAN FLEX FL PM", etc)
- "MyLamSystem": System Name (e.g. "EOS", "MACH IV", "VECTOR EXPRESS", "DV-PRIME", "VECTOR", "2300E4 TRANSPORT MODULE", "SABRE EXTREME", "2300E6 TRANSPORT MODULE", "SABRE 3D", "WTS-MAX", "SABRE NEXT", "KIYO GX")
- "TopLevelSystem": Refers to the highest level system a module reports into (e.g. "VECTOR EXTREME", "EOS", "VECTOR EXPRESS", "VECTOR", "DV-PRIME", "STRIKER", "C3 ALTUS MAX", "C3 ALTUS", "VECTOR STRATA", "UPGRADE", "SABRE EXTREME", "SABRE NEXT", "2300 KIYO GX", etc)
- "SymptomID": Unique numeric identifier for Symptom of a problem
- "ParentID": Describes the parent child relationship to SymptomID
- "Symptom": Brief explanation of the symptom needed to perform a fishbone analysis (e.g. "PC - Random - No Pattern", "Defects Out of Specification", "PC - Edge - Clocked Positions", "Software Defect Observed", "PC - Showerhead Patterns", etc)
- "Description": Symptom Description
- "isLeaf": If equals true, indicates this is the ultimate child or symptom. If equals false, indicates it is part of the larger symptom or parent.
- "HierarchyLevel": A number that indicates the level of the tree the symptom is located on. If isLeaf is true, this value will be greater than 0. If isLeaf is false, this value will be 0.
- "Hierarchy": Indicates a specific section of the symptom tree that can be queried
- "IsCategory": Indicates a specific category of symptom or group of symptoms
- "TicketID": Unique numerical identifier for a particular problem ticket raised, this field is used to join the table to nce live through the field Notification_Number
- "BU": Business Unit (e.g. "PECVD", "2300 Conductor Etch", "Spin Clean", "Electrofill", "2300 Dielectric Etch", "Direct Metals", "Gapfill", "SCE / Alliance", "ALD", etc)
- "ProblemStatement": Short Description of the Problem as entered by the user
- "Resolution": Description of the resolution to a certain problem statement or ticket
- "ESBUID": Unique identifier for business unit in SAP
- "IsActive": Flag to identify whether a BU is active in SAP with values equal to true or false
- "Hypothesis": Contains only confirmed hypotheses for given problem/symptoms in ES. These may also be considered as root causes 
(e.g. "Software Bug", "Chamber Conditioning Insufficient", "No Confirmed Hypothesis - Problem Not Recurring / Unresolved", 
"Component Failure - Module/Platform/System/Equipment/CTC/QNX Controller", "Component failure - IOC / EIOC / SIOC / HDSIOC", "Showerhead Failed - Contamination, Cable / Wiring - Failure", etc)
- "OpenDate": the date the ticket opened. 
- "ClosedDate": the date the ticket closed.
- "open_fisc_qtr_text": the fiscal quarter associated with Open Date. The format is typically "QJun'19", "QMar'20", etc. 
- "closed_fisc_qtr_text": the fiscal quarter associated with closed date. The format is typically "QSep'21", "QDec'22", etc.
"""

problemreports_index_description = f"""
ACS index {acs_index_names_mapping[VW_IPLM_PROBLEM_REPORT]} has the following fields:
- "name": Problem Report (PR) number, the unique identifier of the rows in iplm table
- "state": Lifecycle state of the PR, one of the values of "Closed", "Confirmed", "In Work", "Cancelled", "In Review", "Create", "Test", "Develop", or "Safety Review" 
- "title": Summary of the problem - to be viewed in conjunction with the details
- "problem_description": Textual description of the problem
- "priority": Urgency of the PR, (one of the values of "Normal", "Urgent", "Line Down", "Safety", "Medium")
- "originator": Name of person raising PR in first instance
- "fcid_number": FCID number, sometimes referred to as FID
- "escalation_number": PR created as a result of an escalation - ES TicketID
- "deviation_or_waiver_required": If a waiver or deviation is needed for a PR the value is "Yes", otherwise "No"
- "requestor_organization": Originator's organization (e.g. Supply Chain, Product Group, Manufacturing, Pilot, etc)
- "reason": Reason code assigned to the PR 
    (e.g. "Software Change Request", "Supplier Mfg Process Change", "BOM/Spec Error", "Cannot Build Part to Print", "Supplier Request for Deviation", "Obsolete Component", "Critical Part Change", "Product Design", etc)
- "suggested_solution": Text entry from originator - need not be the final solution for the PR
- "benefit": It describes the benefit that will be accrued if issue underlying the PR is addressed. 
- "customer": Customer affected by PR
- "solution_type": Set of values assigned when solution is being executed 
    (e.g. "ECR", "Monitoring", "See Comments", "Supplier Deviation/Waiver", "Change Order", "Supplier Change Authorization", "Address with Future Design", "ECN", "PCN", etc)
- "cause_code": Assessed cause determined for the PR 
    (e.g., "Supplier Capability", "Z_Miscellaneous", "Obsolescence", "Drafting", "BOM", "Producibility Improvement", "Z_Business Process Tracking", "Mechanical Design", "Software", "Electrical Design", etc)
- "root_cause_corrective_action": Textual description for corrective action taken to resolve the PR
- "disposition": Disposition on the PR with values equal to "Confirmed", "Reject" or "Defer"
- "injury": Injury flag with values "Yes" or "No" or ""
- "business_unit_name": business unit (BU) Name (e.g. "CSBG BU", "Conductor", "PECVD", "Dielectric", "Direct Metal", "Electrofill", "Clean BU", "Platform-EPG", "Multi-BU Dep", "ALD", etc)
- "primary_product_affected_name": Primary product affected by the PR 
    (e.g. "2300 Conductor - Poly", "Multi-BU: DEP", "2300 Dielectric - FX / GXE / HX", "EOS", "ALTUS/ALTUS Max", "Platform Products - Etch/Clean", "Sabre 3D", "CSBG: Conductor - Reliant", "VECTOR Express", "Sabre", etc)
- "secondary_product_affected_name": Secondary product affected by the PR
- "product_group": Prod group associated with the PR (e.g., GOPS, Dep, GPE, Etch, CSBG, Clean, etc)
- "department": User's department based on who is acting on the PR (e.g., "SQAD", "ENG-Software (Dep)", "Software - 2300 Infrastructure", "SMG", "ENG-Etch-Con", "Eng-CSBG", "Manufacturing", "Product Management - CSBG", etc) 
- "department_category": Hierarchy of department (one level above Department) (e.g., "SQAD - Supplier CIP", "SMT - Ramp Approved - Supplier Capacity addition/expansion/relocation", "ENG - Drafting Mechanical", etc)
- "po_number": Purchase Order number where relevant
- "likelihood": Likelihood of problem recurrence, the values are: 
        -- "Unlikely - No more than once in 10 years"
        -- "Possible - More than once in 5 years, but no more than once per year"
        -- "Likely - More than once per year, but no more than five times in a year"
        -- "Frequent - More than five times in a year"
        -- "Rare - More than once in 10 years, but no more than once in 5 years"
- "end_item": Top level assembly part number (e.g. EI-CVD-C3-SOLA, etc)
- "part_name": Part number related to the PR, this field is used to join eng.vw_IPLMProblemReport table to gq.IQMS_NCE_LIVE table using Part_Number field.
- "actual_completion_date": date the PR was completed. 
- "submitted_date": date the PR was submitted.
- "completion_fisc_qtr_text": the fiscal quarter associated with completion data. The format is typically "QJun'19", "QMar'20", etc.
- "submitted_fisc_qtr_text": the fiscal quarter associated with submitted date. The format is typically "QSep'21", "QDec'22", etc.
"""

index_description = {
    acs_index_names_mapping[IQMS_NCE_LIVE]: nce_live_index_description,
    acs_index_names_mapping[RPT_IQMS_8D_GRID]: eight_d_index_description,
    acs_index_names_mapping[VW_IPLM_PROBLEM_REPORT]: problemreports_index_description,
    acs_index_names_mapping[VW_OAI_ESCALATION_TICKETS]: escalationsolver_index_description
    }


acs_query_index_select = """Return the name of an ACS index that is relevant to the user question. 
The indexes are:

(nce data) {0}: {4}
(8d grid data) {1}: {5}
(iplm data) {2}: {6}
(escalation solver or es data) {3}: {7}

Please include only the relevant index, even if you're not sure that they're needed. Do not return an empty string. 
Return only one index name as string, nothing else.
User: find nce records with shower in problem description?
Assistant: {0}
User: find me the iplm reports with 
Assistant: {2}
User: {8}
Assistant: 
"""



acs_query_fields = """You are an assistant answering questions to the user based on the following Azure Cognitive Search (ACS) index that you have:  

{1}

- Your job is to identify the Lucene query syntax parameters based on user input to query the index above. 
- Only return the search body as a json object with keys "search", "filter", "select", "queryType", and "searchMode".
- "search" can be on multiple fields. Always use fuzzy search. If the search tefrm is plural, search for single form of it. Avoid searching for generic words such as problem, issue, etc. 
- "filter" use this only to filter for numeric values or dates, the date columns are saved in the index as Edm.String. If needed, use today's date as {2}. Do not include the search fields what is identified as filter. 
- For date filters do not use "substringof()" operator, only use "le" or "ge" operators. All date fields are in the format of yyyy-MM-dd. For instance, to filter submitted_date = 2023, use "submitted_date ge '2023-01-01' and submitted_date le '2023-12-31' "
- "select" represents the list of columns that needs to be retrieved as part of the user questions from the index definition. This list should include all the search fields and the fields used for filtering. 
- Always use "queryType": "full" and "searchMode": "all".
- The fields names are case-sensitive, use them exactly as described. 

User: show me the issues related to valve for ETCH in NCE description
Assistant: {{"search": "Description:valve~, "filter": "Product_Group_Classification eq 'ETCH'", "select": "Description, Product_Group", "queryType": "full", "searchMode": "all"}}
User: use acs, show me the iplm records with power issues in Root Cause Corrective Action for customer name = Intel
Assistant: {{"search": "ROOT_CAUSE_CORRECTIVE_ACTION_STR:power~ AND CUSTOMER:Intel~", "select": "ROOT_CAUSE_CORRECTIVE_ACTION_STR, CUSTOMER", "queryType": "full", "searchMode": "all"}}
User: {0}
Assistant: 
"""