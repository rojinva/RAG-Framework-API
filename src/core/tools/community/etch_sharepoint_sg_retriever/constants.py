# Access for Account "A" data source (P0, P8a, P8c, P9, P27) is controlled by a common security group.
ETCH_SHAREPOINT_BASIC_ACCESS_SG_ID = "a90115ea-f1e7-4faa-ac50-28004a4771b4"     # lambots-retriever-etch

ETCH_SHAREPOINT_SITE_NAME_SG_ID_MAPPING = {
    "CEProcessCnFProject": "3f9645a3-9dcc-4be9-a18d-d8a70320d9ab",              # P0,27
    "IDTeam": ETCH_SHAREPOINT_BASIC_ACCESS_SG_ID,                               # P8a
    # Moved to P8c                                                              # P8b  
    "KnowledgeBotProject-referencearticlestxtbooks": ETCH_SHAREPOINT_BASIC_ACCESS_SG_ID,    # P8c
    "Cryo_Cell_EtchProgram-NewconceptsandHWtests": "bd8bafd3-0047-46f7-9aad-cd9888e3d19e",  # P9 ("Cryo_Cell_EtchProgram")
    "MicronCEProject": "3c7b15fd-7631-4c74-bbb4-c75133e2e108",                  # P2,5,7,11,26
    "3DDRAMTeam": "3655eea5-75eb-40dd-9653-8275939d33c9",                       # P3
    "SamsungCEProcessProject": "09c02b34-37fb-4697-8f2c-07d7bfd0ae99",          # P6,10,28,29,30,31
    "Hynix_DRAMProject": "e27d428d-e5c7-4920-ae57-00269529245d",                # P4,14
    "SKhDRAMTeamTeam": "8d7e5737-b9eb-485e-9ad8-9ef885f25dfd",                  # P12,23
    "SKhynix_ATProject": "dcd15202-4276-4277-be44-395456537bf2",                # P13
    "SKhNANDTeamTeam": "628c3503-19d9-4dea-8039-58de072b57d7",                  # P15
    "SKhProcessTeam": "3574b2fc-f121-4d8e-b55e-fc35c7480995",                   # P16
    "CE-SKh_KTCDemoTeam": "69e8324f-d3fd-4b80-8bbb-e84b3dd426c6",               # P17,18,19,20,21
    "SKhNewDRAMTeam": "57bbc381-7dc6-4329-b0ac-962369b37029",                   # P24,25
    # Personal SharePoint                                                       # P22
    "KIC-WDC_DETeam": "b4eb24ba-eb61-4f73-8029-e65ba6e4e75b",                   # P1
    "CEProductivitySenseiv2025Team": "a29bdf40-eaa5-4118-8d2c-ffbacffa6408",    # P32
}
