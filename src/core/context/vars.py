import contextvars

# Create a context variable to store the access_token
access_token_var = contextvars.ContextVar("access_token", default=None)
user_email_var = contextvars.ContextVar("user_email", default=None)

# this is the MS Graph Object ID for the user (not the LamBots user id in Mongo)
ms_user_object_id_var = contextvars.ContextVar("ms_user_object_id", default=None)
