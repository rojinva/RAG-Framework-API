class AzureChatOpenAIClientWrapper:
    def __init__(self, wrapped_class):
        """
        Wrapper class used to inspect actual HTTP request and response sent to Azure OpenAI chat completion.

        Reference: https://github.com/langchain-ai/langchain/discussions/6511
        """
        self.wrapped_class = wrapped_class

    def __getattr__(self, attr):
        original_func = getattr(self.wrapped_class, attr)

        def wrapper(*args, **kwargs):
            print(f"Calling function: {attr}")
            print(f"Arguments: {args}, {kwargs}")
            result = original_func(*args, **kwargs)
            print(f"Response: {result}")
            return result

        return wrapper
