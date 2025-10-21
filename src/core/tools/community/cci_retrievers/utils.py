import requests
import json
import os
from src.clients import LifespanClients
from src.core.cache.decorators import cache_user

from dotenv import load_dotenv
load_dotenv(override=True)


@cache_user("wbt_access", ttl=86400)
def get_wbt_access_types(user_login):
    
    """Returns a list of Web Based Training course_ids (named as curricula_ids in the synapse view) 
    that the user has completed.

    Args:
        user_email (str): email address of the user accessing the application

    Returns:
        List[str]: list of curricula_ids which the user has completed
    """

    # Get the SynapseClient from LifespanClients
    lifespan_clients = LifespanClients.get_instance()
    synapse_client = lifespan_clients.synapse

    wbt_table_name = os.getenv("OPENAI_SYNAPSE_WBT_TABLE")
    if not wbt_table_name:
        raise ValueError("OPENAI_SYNAPSE_WBT_TABLE must be provided in environment variables.")
    
    # Define your SQL query
    sql_query = f"""
        SELECT Course_id
        FROM {wbt_table_name} 
        WHERE user_login = '{user_login}'
    """
    # Execute the query using SynapseClient
    results = synapse_client.execute_query(sql_query)    

    # Process the results
    access_types = []
    
    for row in results:
        if row[0] is not None:  # Check if the course_id is not None
            access_types.append(row[0])

    return access_types

def get_asm_access_types(user_name):

    """Returns a list of functional locations that the user has access to, as queried from the ASM database.
    The ASM data is queried via an api endpoint by passing user credentials.
    The functional locations relate to Customer sites and geolocations which have customer confidential information.

    Args:
        user_name (str): user_name of the user accessing the application

    Returns:
        List[str]: list of functional_locations which the user has access to
    """

    user_info_endpoint = os.getenv("ASM_USERINFO_ENDPOINT")
    id_url = user_info_endpoint.format(user_name)
    api_key = os.getenv("ASM_API_KEY")

    headers = {"UserKey": api_key, "Accept": "application/json"}
    functional_locations = []

    # request for asm user_id
    try:
        response_id = requests.get(id_url, headers=headers)
        if response_id.status_code != 200:
            #  print("invalid username: {}".format(user_name))  # Need to log this to Azure app insights
            #  print(f"Request failed with status {response_id.status_code}, {response_id.text}")  # Need to log this to Azure app insights
            return functional_locations
    except Exception:
        return functional_locations

    user_data = response_id.json()
    user_id = user_data["asmuserid"]

    # request for users functional locations
    functional_locations_endpoint = os.getenv("ASM_FUNCTIONAL_LOCATIONS_ENDPOINT")
    url = functional_locations_endpoint.format(user_id)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Request failed with status {response.status_code}, {response.text}"
        )

    try:
        data = response.json()
        for data_dict in data:
            if "functional_location" in data_dict:
                for values in data_dict["functional_location"]:
                    functional_locations.append(values)
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Failed to decode JSON response")

    return functional_locations
