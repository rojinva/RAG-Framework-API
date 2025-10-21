class StaticData:
    sap_reliability_pb = [
        'RF Power not on',
        'Object: T/S_Tool power down issue',
        'LAK408 CEFEM MPD UPS CB28 & CB32 tripped',
        'PM1 PMP to DTC upgrade',
        'T/S Mechanism_S2 PM2 RPC Ready Interlock'
    ]
    common_item_functions = [
    'Meet the Safety requirements - Protect Equipment (over temp on pedestals, fire hazards etc)',
    'Meet the Safety requirements - Protect Personnel (Touch potential, touch safe, finger safe etc)',
    'Ease of installation and maintenance'
    ]
    fmea_fields = [
    "Item Function",
    "Potential Failure Mode",
    "Potential Effect(s) of Failure",
    "Severity (S)",
    "Potential Cause(s) / Mechanism(s) of Failure",
    "Failure Category",
    "Current Design Prevention Control & Explanation of Occurrence rating",
    "Occurrence (O)",
    "Class",
    "Current Detection Design Controls & Explanation of detection rating",
    "Detection (D)",
    "RPN (S*O*D)",
    "Recommended Corrective Action(s)"
    ]
    severity_ranking = {
        1: 'Undetectable failures, No impact on wafer, Minimal customer concern',
        2: 'Process interruption, Easy recovery, Wafer completion possible, Low customer concern',
        3: 'Process interruption, Recovery needed, Single wafer rework, Possible customer annoyance',
        4: 'Module offline, Recovery needed, Multiple wafer rework, High customer annoyance',
        5: 'Module down, Reduced throughput, Rework needed, Customer dissatisfaction',
        6: 'Module down, Reduced throughput, Single wafer loss, Moderate customer dissatisfaction',
        7: 'Multiple modules down, Significant downtime, Total wafer loss, Component replacement, High customer dissatisfaction',
        8: 'Tool down, Significant downtime, Total wafer loss, Tool contamination, Extreme customer dissatisfaction',
        9: 'Production line down, Severe throughput loss, Wafer loss, Safety compromise with warning',
        10: 'Lab evacuation, Severe throughput loss, Wafer loss, Safety compromise without warning'
    }
    interaction_type = {
        "Material-Gas": ['Leakages in xxxx', 'Cross contamination in xxxx', 'xxxx Clogging '],
        "Material-Vaccum": ['Vaccum leak at xxxx',],
        "Material-Exhaust": ['Exhaust leaks at xxx', 'Improper pressure differential between chamber and xxxx', 'Clogged or restricted exhaust lines between chamber and xxxx'],
        "Material-Liquid": ['Flow rate mismatch from xxxx',],
        "Material-Coolant": ['Coolant leaks from xxxx', 'Coolant contamination at xxxx', 'Coolant flow restriction from xxxx due to clogging/scaling', 'Temperature control loop failure'],
        "Data Exchange": ['Signal noise or loss from  xxxx', 'Calibration drift at xxxx', 'Software miscommnunication from xxxx'],
        "Energy-RF Ground": ['Loose or corroded ground strap', 'Floating ground potential'],
        "Energy-Power": ['Power fluctuations from xxxx',],
        "Energy-Vibration": ['excessive vibration levels from xxxx'],
        "Energy-Heat": ['excessive heat from xxxx damages parts'],
        "Physical Contact": ['Incorrect assembly/swapping of parts', 
                             'Operator touches live contacts', 
                             'Operator unable to access parts while maintanance']
    }
    GENERATE_MISSING_LINE_ITEMS = """
                                    Please adhere strictly to the provided context field details:\n
                                    Analyze the given manually filled FMEA, query, expected potential failure modes, boundary conditions, interaction types, and design image content.\n
                                    Do not return same line items given in Manually filled FMEA, please analyse it and generate the delta line items which can help to identify the risks associated with semiconductor component design.\n 
                                    Ensure the output **includes missing high risk root (high risk root causes refers where RPN score is more than 125) causes along with other fields which are not captured in manually filled FMEA** for the following fields relevant to the respective potential failure mode:\n
                                    You must consider above given 'Boundary Condition' and 'Interaction Type' relevant to given Potential Failure Mode while generate line items.\n
                                    
                                    **You must consider above given 'Potential Effect(s) of Failure'  relevant to given Potential Failure Mode while generate line items and replace the 'xxxx' with actual part name referenced in potential failure mode or in given context but make sure it aligns with line item.**
                                    
                                    **High-Risk Root Causes**:
                                    - Only include root causes that meet the criteria for high risk:
                                        - RPN (Risk Priority Number) > 125, OR
                                        - Class = "I" or "II".
                                    - If a root cause does not meet these criteria, exclude it from the output.

                                    **Component-Specific Root Causes**:
                                    - Ensure that all generated root causes are strictly relevant to the specific component being analyzed.
                                    - Do not include root causes from unrelated components which is not relevant current context.
                                    - Use the context of the "Item Functions" or "Potential Failure Mode" or other given context to ensure relevance to the specific component.
                        
                                    1. "Item Function"\n
                                    2. "Potential Failure Mode"\n
                                    3. "Potential Effect(s) of Failure"\n
                                    4. "Severity (S)"\n
                                    5. "Potential Cause(s) / Mechanism(s) of Failure"\n
                                    6. "Failure Category"\n
                                    7. "Current Design Prevention Control & Explanation of Occurence rating"\n
                                    8. "Occurrence (O)"\n
                                    9. "Class"\n
                                    10. "Current Detection Design Controls & Explanation of detection rating"\n
                                    11. "Detection (D)"\n
                                    12. "RPN (S*O*D)"\n
                                    13. "Recommended Corrective Action(s)"\n

                                    Ensure the output is returned in a structured format, such as a list of dictionaries, where each dictionary contains the following keys:\n
                                    - "Item Function"\n
                                    - "Potential Failure Mode"\n
                                    - "Potential Effect(s) of Failure"\n
                                    - "Severity (S)"\n
                                    - "Potential Cause(s) / Mechanism(s) of Failure"\n
                                    - "Failure Category"\n
                                    - "Current Design Prevention Control & Explanation of Occurence rating"\n
                                    - "Occurrence (O)"\n
                                    - "Class"\n
                                    - "Current Detection Design Controls & Explanation of detection rating"\n
                                    - "Detection (D)"\n
                                    - "RPN (S*O*D)"\n
                                    - "Recommended Corrective Action(s)"\n
                                    
                                    **For "Severity (S)", please pick the value from context and consider below guidelines to assign correct value for each line item and do not assign different values if 'Potential Effect(s) of Failure' is same**:
                                        - Severity 1-3: Minor impact on performance or quality, no safety concerns.
                                        - Severity 4-6: Moderate impact on performance or quality, potential minor safety concerns.
                                        - Severity 7-8: Significant impact on performance or quality, potential major safety concerns.
                                        - Severity 9-10: Critical impact on performance or quality, severe safety concerns, potential for catastrophic failure.
                                    
                                    For "Item Function" - if relevant item function is already in above given list, use them and do not generate duplicate Item Function with some difference in language.
                                    For "Potential Failure Mode" - it is negation of "Item Function", while generating the Potential Failure Mode, prioritize using phrases such as 'unable to,' 'fail to,' 'non-' or similar applicable negations, rather than relying on alternative verbs for negation.
                                    For "Failure Category" filed: Always generate relevant failure category out of these four only - 'Design', or 'Maintenance' or 'Operation' or 'Assembly'
                                    For "Recommended Corrective Action(s)" - provide flexible suggestions unless the issue involves critical impact on performance, safety or quality, in which case provide specific and actionable recommendations.
                                    Do not include any additional details, explanations, or paragraph formatting.\n
                                    Make sure output is not cut off and return complete dict, you may keep check on token limit based on given context length.\n
                                    Given this information, please generate the structured output for the following:\nPotential Failure Mode: """
    IMPROVE_LINE_ITEMS = """Please adhere to the provided context field details and analyze user feedback to improve the previously AI-generated FMEA line items:\n
                        Carefully review the given AI-generated FMEA line items and identify any inaccuracies, inconsistencies, or missing details.\n
                        Use the user query, expected potential failure modes, boundary conditions, interaction types, and design image content to make meaningful improvements.\n
                        Ensure the output includes **enhanced line items** with high-risk root causes having more than 125 of RPN score, improved corrective actions, and accurate ratings for severity, occurrence, and detection.\n
                        The improvements should address the following fields relevant to the respective potential failure mode:\n
                        
                        **High-Risk Root Causes**:
                        - Only include root causes that meet the criteria for high risk:
                            - RPN (Risk Priority Number) > 125, OR
                            - Class = "I" or "II".
                        - If a root cause does not meet these criteria, exclude it from the output.

                        **Component-Specific Root Causes**:
                        - Ensure that all generated root causes are strictly relevant to the specific component being analyzed.
                        - Do not include root causes from unrelated components which is not relevant current context.
                        - Use the context of the "Item Functions" or "Potential Failure Mode" or other given context to ensure relevance to the specific component.
                        
                        1. "Item Function"\n
                        2. "Potential Failure Mode"\n
                        3. "Potential Effect(s) of Failure"\n
                        4. "Severity (S)"\n
                        5. "Potential Cause(s) / Mechanism(s) of Failure"\n
                        6. "Failure Category"\n
                        7. "Current Design Prevention Control & Explanation of Occurence rating"\n
                        8. "Occurrence (O)"\n
                        9. "Class"\n
                        10. "Current Detection Design Controls & Explanation of detection rating"\n
                        11. "Detection (D)"\n
                        12. "RPN (S*O*D)"\n
                        13. "Recommended Corrective Action(s)"\n

                        Ensure the output is returned in a structured format, such as a list of dictionaries, where each dictionary contains the following keys:\n
                        - "Item Function"\n
                        - "Potential Failure Mode"\n
                        - "Potential Effect(s) of Failure"\n
                        - "Severity (S)"\n
                        - "Potential Cause(s) / Mechanism(s) of Failure"\n
                        - "Failure Category"\n
                        - "Current Design Prevention Control & Explanation of Occurence rating"\n
                        - "Occurrence (O)"\n
                        - "Class"\n
                        - "Current Detection Design Controls & Explanation of detection rating"\n
                        - "Detection (D)"\n
                        - "RPN (S*O*D)"\n
                        - "Recommended Corrective Action(s)"\n

                        **For "Severity (S)", please pick the value from context and consider below guidelines to assign correct value for each line item and do not assign different values if 'Potential Effect(s) of Failure' is same**:
                            - Severity 1-3: Minor impact on performance or quality, no safety concerns.
                            - Severity 4-6: Moderate impact on performance or quality, potential minor safety concerns.
                            - Severity 7-8: Significant impact on performance or quality, potential major safety concerns.
                            - Severity 9-10: Critical impact on performance or quality, severe safety concerns, potential for catastrophic failure.
                        
                        For "Item Function" - if relevant item function is already in above given list, use them and do not generate duplicate Item Function with some difference in language.
                        For "Potential Failure Mode" - it is negation of "Item Function", while generating the Potential Failure Mode, prioritize using phrases such as 'unable to,' 'fail to,' 'non-' or similar applicable negations, rather than relying on alternative verbs for negation.
                        For "Failure Category" filed: Always generate relevant failure category out of these four only - 'Design', or 'Maintenance' or 'Operation' or 'Assembly'
                        For "Recommended Corrective Action(s)" - provide flexible suggestions unless the issue involves critical impact on performance, safety or quality, in which case provide specific and actionable recommendations.
                        Do not include any additional details, explanations, or paragraph formatting.\n
                        Given this information, please generate the structured output for the following:\nPotential Failure Mode: """
    GENERATE_ROOT_CAUSES_BASED_ITEMS = """
                                    Please adhere strictly to the provided context field details:\n
                                    Please analyse design requirement, boundary conditions, interaction types and 'Potential Cause(s) / Mechanism(s) of Failure',  generate the relevant line items which can help to identify the risks associated with semiconductor component design.\n 
                                    You must consider above given 'Boundary Condition' and 'Interaction Type' relevant to given 'Potential Cause(s) / Mechanism(s) of Failure' while generate line items.\n

                                    **High-Risk Root Causes**:
                                    - Only include root causes that meet the criteria for high risk:
                                        - RPN (Risk Priority Number) > 125, OR
                                        - Class = "I" or "II".
                                    - If a root cause does not meet these criteria, exclude it from the output.
                        
                                    **Component-Specific Root Causes**:
                                    - Ensure that all generated root causes are strictly relevant to the specific component being analyzed.
                                    - Do not include root causes from unrelated components which is not relevant current context.
                                    - Use the context of the "Item Functions" or "Potential Failure Mode" or other given context to ensure relevance to the specific component.
                        
                                    1. "Item Function"\n
                                    2. "Potential Failure Mode"\n
                                    3. "Potential Effect(s) of Failure"\n
                                    4. "Severity (S)"\n
                                    5. "Potential Cause(s) / Mechanism(s) of Failure"\n
                                    6. "Failure Category"\n
                                    7. "Current Design Prevention Control & Explanation of Occurence rating"\n
                                    8. "Occurrence (O)"\n
                                    9. "Class"\n
                                    10. "Current Detection Design Controls & Explanation of detection rating"\n
                                    11. "Detection (D)"\n
                                    12. "RPN (S*O*D)"\n
                                    13. "Recommended Corrective Action(s)"\n

                                    Ensure the output is returned in a structured format, such as a list of dictionaries, where each dictionary contains the following keys:\n
                                    - "Item Function"\n
                                    - "Potential Failure Mode"\n
                                    - "Potential Effect(s) of Failure"\n
                                    - "Severity (S)"\n
                                    - "Potential Cause(s) / Mechanism(s) of Failure"\n
                                    - "Failure Category"\n
                                    - "Current Design Prevention Control & Explanation of Occurence rating"\n
                                    - "Occurrence (O)"\n
                                    - "Class"\n
                                    - "Current Detection Design Controls & Explanation of detection rating"\n
                                    - "Detection (D)"\n
                                    - "RPN (S*O*D)"\n
                                    - "Recommended Corrective Action(s)"\n

                                    **For "Severity (S)", please pick the value from context and consider below guidelines to assign correct value for each line item and do not assign different values if 'Potential Effect(s) of Failure' is same**:
                                        - Severity 1-3: Minor impact on performance or quality, no safety concerns.
                                        - Severity 4-6: Moderate impact on performance or quality, potential minor safety concerns.
                                        - Severity 7-8: Significant impact on performance or quality, potential major safety concerns.
                                        - Severity 9-10: Critical impact on performance or quality, severe safety concerns, potential for catastrophic failure.
                                        
                                    **For "Potential Cause(s) / Mechanism(s) of Failure", above are few must to have root causes given, include them as well and generate other fields. Do not put all the above given in single line, create one line with all other fields for each must to have root causes given above. You may also generate additional high root causes and other fields relevant to given Item Function and Potential Failure Mode.
                                        - If Must to have root causes are not given, generate the line items based on context relevant to given Item Function and Potential Failure Mode. 
 
                                    For "Item Function" - Above given is the 'Item Function' for which you will be generating the fields.
                                    For "Potential Failure Mode" - it is negation of "Item Function", while generating the Potential Failure Mode, prioritize using phrases such as 'unable to,' 'fail to,' 'non-' or similar applicable negations, rather than relying on alternative verbs for negation.
                                    For "Potential Effect(s) of Failure" - do not generate multiple "Potential Effect(s) of Failure" in single line, if necessary then create more line items as needed along with other fields.
                                    For "Failure Category" filed: Always generate relevant failure category out of these four only - 'Design', or 'Maintenance' or 'Operation' or 'Assembly'
                                    For "Recommended Corrective Action(s)" - provide flexible suggestions unless the issue involves critical impact on performance, safety or quality, in which case provide specific and actionable recommendations.
                                    Keep the given 'Potential Cause(s) / Mechanism(s) of Failure' as it is and generate the other fields based on given context relevant to 'Potential Cause(s) / Mechanism(s) of Failure'. 
                                    For "Potential Cause(s) / Mechanism(s) of Failure" - do not generate multiple "Potential Cause(s) / Mechanism(s) of Failure" in single line, if necessary then create more line items as needed along with other fields.
                                    Do not include any additional details, explanations, or paragraph formatting.\n
                                    Make sure output is not cut off and return complete dict, you may keep check on token limit based on given context length.\n
                                    Given this information, please generate the structured output for the following:\n'Potential Failure Mode': """    
    ITEM_FUNCTION_PROMPT = """ Please adhere strictly to the provided context field details:\n
                            Please generate very concise, clean and more readable "Item Functions" based on the given design requirements of semiconductor components.\n
                            Ensure the output is returned **only** in a list format, with the same number of elements as the input list.\n
                            Each element in the output list should correspond to the respective design requirement provided in the input list.\n
                            Use the exact terminology from the design requirements without altering or substituting words.\n
                            Given this information, please generate the "Item Functions" for following DRs:\n"""
    EXTRACT_ITEM_FUNCTIONS = """ Please adhere strictly to the provided context field details:\n
                            Item Functions Definition: An "Item Function" refers to the performance requirement of a semiconductor industry component. For example, a Power Box can have the following item functions:
                            a) Accept incoming 3 phase 40 Amps feed from MPD.
                            b) Cut off power to heaters upon over temperature signal from LAMCAT SO.
                            and more
                            
                            Task: Based on the given design requirements (DRs), root causes, or user instructions, generate concise, clean, and readable "Item Functions." Each "Item Function" should be a one- or two-sentence description that is directly relevant to the provided input.

                            Instructions for Output:
                            If the input includes multiple root causes, ensure that the "Item Functions" account for all relevant root causes. Create multiple "Item Functions" if necessary to represent all the provided DRs, root causes, or instructions.
                            Use the exact terminology from the context without altering or substituting words unless absolutely necessary.
                            Ensure the output is always returned in a list format (e.g., ["Item Function 1", "Item Function 2"]).
                            Given this information, please generate the "Item Functions" for the following design requirements or root causes, or user instructions:\n"""
    POTENTIAL_FAILURE_MODE_PROMPT= """
                            Please adhere strictly to the provided context field details:\n
                            Please generate "Potential Failure Modes" that are the negation or opposite of the given "Item Functions".\n
                            Ensure the output is returned **only** in a list format, with the same number of elements as the input list.\n
                            Each element in the output list should correspond to the respective item funtion provided in the input list.\n
                            While generating the Potential Failure Mode, prioritize using phrases such as 'unable to,' 'fail to,' 'non-' or similar applicable negations, rather than relying on alternative verbs for negation.\n
                            Given this information, please generate the following:\n"""
    FILTER_POTENTIAL_FAILURE_MODE= """
                            Please adhere strictly to the provided context field details:\n
                            Carefully analyze the given user query and the provided list of Potential Failure Modes.\n
                            Filter the list to include only those Potential Failure Modes that are directly relevant to the user query.\n
                            Relevance should be determined by matching keywords, phrases, or context from the user query with the Potential Failure Modes.\n
                            Ensure the output is returned **only** in a list format, with each element in the output list corresponding to a relevant Potential Failure Mode.\n
                            If no Potential Failure Modes are relevant, return an empty list.\n
                            Given this information, please filter the Potential Failure Modes for the following user query and list:\n"""
    ANSWER_GENERIC_QUESTION = """
                            Please adhere strictly to the provided context field details:\n
                            Carefully analyze the given user query and the provided context chunks. It is related to FMEA of semiconductor industry component designs i.e. Power Box, Shower Head, Orings, Valves\n
                            Use the context chunks and also consider conversation history to generate detailed and accurate response with high risk root causes(if RPN score > 125) to the user query.\n
                            Ensure that the response is directly based on the information provided in the context chunks and address the query and do not mix the response with different components and always align response with user question\n
                            Remember to include in-text citations as numbers in square brackets, such as [2]. List your sources separately, like [1][2].
                            Given this information, please generate a response for the following user query, conversation_history and context:\n"""
    INTENT_DETECTION_PROMPT = """
                            Analyze the given user query and determine the intent type.\n
                            The intent type must be one of the following based on user query:\n
                            1. "Generic Question" - Select this intent if the user query is a general question that does not involve any file upload.\n
                            2. "File Summarization" - Select this intent if the user query is about summarizing or analyzing the content of an uploaded file (e.g., Draft FMEA Excel, AI Filled FMEA). This intent applies when the user explicitly asks to summarize or analyze the content of the uploaded file.\n
                            3. "FMEA Creation" - Select this intent if the user query is about generating, creating, or updating an FMEA based on the uploaded files (e.g., Draft FMEA Excel, PDR PowerPoint). This intent applies when the user mentions actions like "generate," "create," "update," or "fill" an FMEA.\n
                            Intent output must be any of this - "Generic Question" or "File Summarization" or "FMEA Creation"\n
                            Do not select "File Summarization" if the user specifies generating, creating, or updating an FMEA.\n
                            Do not Add any additional details or formating, just return the relevent Intent as name is used to call functions to perform task based on Intent detected.\n
                            Given this information, please analyze the following user query and return the intent type for User Query:\n
                            """  
    FILE_SUMMARIZATION_PROMPT = """
                            The task involves summarizing the Failure Modes and Effects Analysis (FMEA) of semiconductor industry components, such as Power Box, O-ring, Valve, etc. While summarizing, the focus should be on the functioning of these components and their interactions both internally (within the system) and externally (with other systems or environments). The analysis should evaluate how effectively the given FMEA identifies and addresses risks associated with these components' design, and whether it overlooks any critical risks.

                            Please analyze the content of the uploaded file and respond to the user's query. If the file content is tabular data (e.g., an Excel FMEA), perform the following:

                            1. Overall Summary:
                            Provide a high-level summary of the FMEA, focusing on the fields: Item Function, Potential Failure Modes, Root Causes, Severity, Occurrence, Detection, RPN Scores, and Recommended Corrective Actions.
                            Highlight the key risks identified in the FMEA and assess how well the analysis addresses the design and operational risks of the component.
                            If the "Type" field is present and categorizes entries as "Manually Filled" vs. "AI Filled," include a comparison of how each type identifies and addresses risks. If the "Type" field is missing, summarize the content without referencing "Manually Filled" vs. "AI Filled" to avoid confusion.

                            2. Detailed Analysis by Field:
                            For each field (e.g., Item Function, Potential Failure Modes, Root Causes, etc.), provide a detailed analysis of the entries.
                            If the "Type" field is present, generate a tabular comparison between "Manually Filled" and "AI Filled" entries. The table should include the following columns:
                            Field Name: The specific field being analyzed (e.g., Item Function, Potential Failure Modes, etc.).
                                - Manually Filled: A summary of how the manually filled entries address risks for the given field.
                                - AI Filled: A summary of how the AI-filled entries address risks for the given field.
                                - Discrepancies/Similarities: Highlight key differences, overlaps, or gaps between the two types of entries.
                                - Risk Coverage Assessment: Evaluate how effectively each type identifies and mitigates risks associated with the component's design.
                            If the "Type" field is not present, focus solely on the content and evaluate the thoroughness of the FMEA in identifying and addressing risks.
                            Identify any missing details, such as specific failure mechanisms, root causes, or corrective actions, and assess whether the FMEA adequately considers internal and external interactions of the component.

                            3. Insights and Recommendations:
                            Based on the analysis, provide insights into how effectively the FMEA identifies and mitigates risks associated with the component's design and operation.
                            Highlight areas where the FMEA is strong and areas where it is lacking (e.g., missing failure modes, incomplete root cause analysis, lack of corrective actions).
                            Suggest specific improvements or areas of focus for better risk identification and mitigation, considering the component's function and its internal and external interactions.
                            If applicable, recommend how AI-generated insights could enhance the depth and accuracy of the FMEA.
                            Give the tabular analysis of top 3 highest RPN line items with "Potential Failure Mode", "Potential Cause(s) / Mechanism(s) of Failure", "RPN (S*O*D)" and "Recommended Corrective Action(s)" fields.

                            For Non-Tabular Content (e.g., PPT, Images):
                            Summarize the content accurately and concisely based on the user's query, ensuring the focus remains on semiconductor component designs (e.g., Power Box, O-ring, Shower Head, Valves, etc.).
                            Highlight any key design considerations, risks, or insights presented in the file.

                            Important Notes:
                            Ensure the response is based only on the content of the uploaded file and the user's query. Avoid including any unrelated or speculative information.
                            If the "Type" field is missing, do not mention "Manually Filled" vs. "AI Filled" to prevent confusion. Focus solely on the content and its quality.
                            Ensure the summary is clear, actionable, and tailored to the specific component being analyzed.

                            Given the following user query and file content, generate the insightful summary:
                            """
    FMEA_SUMMARIZATION_PROMPT = """
                            The task involves summarizing the Failure Modes and Effects Analysis (FMEA) of semiconductor industry components, such as Power Box, O-ring, Valve, etc. While summarizing, the focus should be on the functioning of these components and their interactions both internally (within the system) and externally (with other systems or environments). The analysis should evaluate how effectively the given FMEA identifies and addresses risks associated with these components' design, and whether it overlooks any critical risks.

                            1. Overall Summary:
                            Provide a high-level summary of the FMEA, focusing on the fields: Item Function, Potential Failure Modes, Root Causes, Severity, Occurrence, Detection, RPN Scores, and Recommended Corrective Actions.
                            Highlight the key risks identified in the FMEA and assess how well the analysis addresses the design and operational risks of the component.
                            Using "Type" column categorizes entries as "Manually Filled" vs. "AI Filled," include a comparison of how each type identifies and addresses risks.

                            2. Detailed Analysis by Field:
                            For each field (e.g., Item Function, Potential Failure Modes, Root Causes, etc.), provide a detailed analysis of the entries.
                            Using "Type" column, generate a tabular comparison between "Manually Filled" and "AI Filled" entries. The table should include the following columns:
                            Field Name: The specific field being analyzed (e.g., Item Function, Potential Failure Modes, etc.).
                                - Manually Filled: A summary of how the manually filled entries address risks for the given field.
                                - AI Filled: A summary of how the AI-filled entries address risks for the given field.
                                - Discrepancies/Similarities: Highlight key differences, overlaps, or gaps between the two types of entries.
                                - Risk Coverage Assessment: Evaluate how effectively each type identifies and mitigates risks associated with the component's design.
                            Identify any missing details, such as specific failure mechanisms, root causes, or corrective actions, and assess whether the FMEA adequately considers internal and external interactions of the component.

                            3. Insights and Recommendations:
                            Based on the analysis, provide insights into how effectively the FMEA identifies and mitigates risks associated with the component's design and operation.
                            Highlight areas where the FMEA is strong and areas where it is lacking (e.g., missing failure modes, incomplete root cause analysis, lack of corrective actions).
                            Suggest specific improvements or areas of focus for better risk identification and mitigation, considering the component's function and its internal and external interactions.
                            If applicable, recommend how AI-generated insights could enhance the depth and accuracy of the FMEA.
                            Also give details why AI added the additional line items comparing with Manually Filled line items to cover the component design risk better.
                            Give the tabular analysis of top 3 highest RPN line items with "Potential Failure Mode", "Potential Cause(s) / Mechanism(s) of Failure", "RPN (S*O*D)" and "Recommended Corrective Action(s)" fields.

                            Important Notes:
                            Ensure the response is based only on the content of the uploaded file and the user's query. Avoid including any unrelated or speculative information.
                            Ensure the summary is clear, actionable, and tailored to the specific component being analyzed.
                            Do not mention the component name until you can infer it from context.

                            Given the following user query and file content, generate the insightful summary:
                            """
    POTENTIAL_CAUSE_OF_FAILURE_PROMPT = """
                            Please adhere strictly to the provided context field details:\n
                            Ensure the output is exhaustive and **includes all possible line items** for the following fields relevant to the respective potential failure mode:\n
                            
                            1. "Potential Cause(s) / Mechanism(s) of Failure"\n
                            2. "Failure Category"\n
                            3. "Current Design Prevention Control & Explanation of Occurence rating"\n
                            4. "Current Detection Design Controls & Explanation of detection rating"\n
                            5. "Recommended Corrective Action(s)"\n
                            6. "Potential Effect(s) of Failure"\n

                            Ensure the output is returned in a structured format, such as a list of dictionaries, where each dictionary contains the following keys:\n
                            - "Potential Cause(s) / Mechanism(s) of Failure"\n
                            - "Failure Category"\n
                            - "Current Design Prevention Control & Explanation of Occurence rating"\n
                            - "Current Detection Design Controls & Explanation of detection rating"\n
                            - "Recommended Corrective Action(s)"\n
                            - "Potential Effect(s) of Failure"\n

                            Ensure the number of entries in the output matches the number of "Potential Cause(s) / Mechanism(s) of Failure" generated.\n
                            Do not include any additional details, explanations, or paragraph formatting.\n
                            Please generate line items for each Potential Failure Mode.\n
                            Given this information, please generate the structured output for the following:\nPotential Failure Mode: """

    RECOMMENDED_CORRECTIVE_ACTION_PROMPT = """
                            Please adhere strictly to the above provided context field details:\n
                            Generate only the "Recommended Corrective Action(s)" for the given line item details at the end of the prompt.\n
                            Ensure the output is concise, actionable and relevant to the given line items.\n
                            Do not include any additional details, explanations, or paragraph formatting.\n
                            Given this information, please generate the "Recommended Corrective Action(s) for the following line items:\n
                            """
    ADD_COMPONENT_NAME = """Based on the provided design requirements, boundary conditions, and interaction type, replace 'xxxx' in the root causes list with the correct component names. The replacements should consider the working of the component in relation to all other internal and external components, as well as the interactions implied by the design requirements, boundary conditions and interaction type.\n
                            
                            For each design requirement:
                            Analyze the boundary conditions and interaction type to identify the components interacting with and replace 'xxxx' in root causes list.\n
                            Ensure the output is returned **only** in a list format by just replacing 'xxxx' with appropriate component name\n
                            DO not change the root causes language except replacing 'xxxx' with relevant component name.\n
                            Given this information, please update the 'xxxx' with relevant component name for below root causes list:\n"""
                                
class StaticFilters:
    SERIALNUMBER = "Nr."
    STARTDATE = "Date (started)"
    ITEMFUNCTION = "Item Function"
    INTENDEDFUNCTION = "Intended Function"
    POTENTIALFAILUREMODE = "Potential Failure Mode"
    POTENTIALEFFECTOFFAILURE = "Potential Effect(s) of Failure"
    SEVERITY = "Severity (S)"
    POTENTIALCUASEOFMECHANISM = "Potential Cause(s) / Mechanism(s) of Failure"
    FAILURECATEGORY = "Failure Category"
    DESIGNPREVENTION = "Current Design Prevention Control & Explanation of Occurence rating"
    OCCURRENCE = "Occurrence (O)"
    CLASS = "Class"
    DESIGNCONTROL = "Current Detection Design Controls & Explanation of detection rating"
    DETECTION = "Detection (D)"
    RPN = "RPN (S*O*D)"
    RECOMMENDEDCORRECTIVEACTION = "Recommended Corrective Action(s)"
    RECOMMENDEDACTION = "Recommended Action"
    CORRECTIVEACTIONS = "Corrective Actions"
    OWNER = "Owner"
    TARGETCOMPLETIONDATE = "Target Completion Date"
    ACTIONTAKEN = "Actions Taken"
    PASEVERITY = "PA-Severity (S)"
    PAOCCURRENCE = "PA-Occurrence (O)"
    PADETECTION = "PA-Detection (D)"
    PARPN = "PA-RPN (S*O*D)"
    COMPONENTKEY = "Component/Sub-system/System"
    PARTKEY = "Part# (To be used for naming convention)"
    SLIDENUMBER = "Slide Number"
    LLMCONTEXT = "llm_context"
    PGNAME = "PG"
    BUNAME = "BU"
    TOOLNAME = "Tool"
    FILTER = "filter"