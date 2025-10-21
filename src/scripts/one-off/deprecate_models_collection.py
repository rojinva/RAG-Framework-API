import os
from pymongo import MongoClient, errors


# Get MongoDB endpoint from environment variable
mongo_db_endpoint = os.getenv('MONGO_DB_ENDPOINT')
mongo_db_name = os.getenv('MONGODB_DB_NAME', 'chat-ui')

try:
    print(f"Connecting to MongoDB at {mongo_db_endpoint}...")
    # Connect to MongoDB
    client = MongoClient(mongo_db_endpoint, serverSelectionTimeoutMS=5000)
    db = client[mongo_db_name]    # Collections
    lamBotConfig_collection = db['lambotConfigs']
    model_collection = db['models']

    # Iterate through all model documents
    for model in model_collection.find():
        lamBotConfigId = model.get('lamBotConfigId')
        if not lamBotConfigId:
            print(f"Skipping model with missing lamBotConfigId: {model.get('_id')}")
            continue

        # Find the corresponding lamBotConfig document
        lamBotConfig = lamBotConfig_collection.find_one({'id': lamBotConfigId})

        if lamBotConfig:
            # Move the 'name' field from model to lamBotConfig
            name = model.get('name')
            if name:
                try:
                    lamBotConfig_collection.update_one(
                        {'id': lamBotConfigId},
                        {'$set': {'name': name}}
                    )
                except errors.PyMongoError as e:
                    print(f"Error updating lamBotConfig {lamBotConfigId}: {e}")
            else:
                print(f"Model {model.get('_id')} missing 'name' field.")            # move the endpoints field from model to lamBotConfig
            endpoints = model.get('endpoints')
            if endpoints is not None:
                try:
                    lamBotConfig_collection.update_one(
                        {'id': lamBotConfigId},
                        {'$set': {'endpoints': endpoints}}
                    )
                except errors.PyMongoError as e:
                    print(f"Error updating endpoints for lamBotConfig {lamBotConfigId}: {e}")

            # Copy the 'chatPromptTemplate' field from model to lamBotConfig (do not remove from model)
            chat_prompt_template = model.get('chatPromptTemplate')
            if chat_prompt_template is not None:
                try:
                    lamBotConfig_collection.update_one(
                        {'id': lamBotConfigId},
                        {'$set': {'chatPromptTemplate': chat_prompt_template}}
                    )
                except errors.PyMongoError as e:
                    print(f"Error copying chatPromptTemplate for lamBotConfig {lamBotConfigId}: {e}")
            else:
                print(f"Model {model.get('_id')} missing 'chatPromptTemplate' field.")
            
            # Add uiComponents and promptExamples to lamBotConfig
            try:
                ui_components = model.get('uiComponents', [])
                prompt_examples = model.get('promptExamples', [])
                
                update_fields = {}
                if ui_components:
                    update_fields['uiComponents'] = ui_components
                if prompt_examples:
                    update_fields['promptExamples'] = prompt_examples
                
                if update_fields:
                    lamBotConfig_collection.update_one(
                        {'id': lamBotConfigId},
                        {'$set': update_fields}
                    )
            except errors.PyMongoError as e:
                print(f"Error updating uiComponents/promptExamples for lamBotConfig {lamBotConfigId}: {e}")
        else:
            print(f"lamBotConfig not found for id: {lamBotConfigId}")

    print("Migration completed successfully.")

except errors.ServerSelectionTimeoutError as err:
    print(f"Could not connect to MongoDB: {err}")
except Exception as e:
    print(f"Unexpected error: {e}")
