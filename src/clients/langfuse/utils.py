import warnings
from typing import Dict, List, Any
from langchain_core.messages.ai import AIMessageChunk, AIMessage
from langchain_core.messages.system import SystemMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.agents import AgentFinish
from copy import deepcopy

class TraceSanitizer:
    """
    A class used to mask sensitive data in various traces.

    Attributes:
    ----------
    mask_string : str
        The string used to replace sensitive data.
    """

    def __init__(self, mask_string="Masked"):
        """
        Initializes the TraceSanitizer with a specified mask string.

        Args:
            mask_string (str): The string used to replace sensitive data.
        """
        self.mask_string = mask_string

    def _mask_dict(self, data: Dict) -> Dict:
        """
        Masks sensitive data in a dictionary.

        Args:
            data (Dict): The dictionary containing data to be masked.

        Returns:
            Dict: The dictionary with masked data.
        """
        if "input" in data:
            data["input"] = self.mask_string
        if "output" in data:
            data["output"] = self.mask_string
        if "role" in data and data["role"] != "system":
            data["content"] = self.mask_string
        if "messages" in data:
            for message in data["messages"]:
                if isinstance(message, AIMessage):
                    message.content = self.mask_string
        return data

    def _mask_ai_message_chunk(self, data: AIMessageChunk) -> AIMessageChunk:
        """
        Masks sensitive data in an AIMessageChunk.

        Args:
            data (AIMessageChunk): The AIMessageChunk containing data to be masked.

        Returns:
            AIMessageChunk: The AIMessageChunk with masked data.
        """
        data.content = self.mask_string
        return data

    def _mask_agent_finish(self, data: AgentFinish) -> AgentFinish:
        """
        Masks sensitive data in an AgentFinish.

        Args:
            data (AgentFinish): The AgentFinish containing data to be masked.

        Returns:
            AgentFinish: The AgentFinish with masked data.
        """
        data.log = self.mask_string
        if "output" in data.return_values:
            data.return_values["output"] = self.mask_string
        if "messages" in data.return_values:
            for message in data.return_values["messages"]:
                if isinstance(message, AIMessage):
                    message.content = self.mask_string
        return data

    def _mask_chat_prompt_value(self, data: ChatPromptValue) -> ChatPromptValue:
        """
        Masks sensitive data in a ChatPromptValue.

        Args:
            data (ChatPromptValue): The ChatPromptValue containing data to be masked.

        Returns:
            ChatPromptValue: The ChatPromptValue with masked data.
        """
        for message in data.messages:
            if not isinstance(message, SystemMessage):
                message.content = self.mask_string
        return data

    def _mask_list(self, data: List[Dict]) -> List[Dict]:
        """
        Masks sensitive data in a list of dictionaries.

        Args:
            data (List[Dict]): The list containing dictionaries with data to be masked.

        Returns:
            List[Dict]: The list with masked data.
        """
        for message_dict in data:
            if "role" in message_dict and message_dict["role"] != "system":
                message_dict["content"] = self.mask_string
        return data

    def mask(self, data: Any) -> Any:
        """
        Masks sensitive data in various data structures.

        Args:
            data (Any): The data to be masked.

        Returns:
            Any: The data with masked content.

        Raises:
            UserWarning: If the data type is not supported.
        """
        _data = deepcopy(data)
        if isinstance(_data, Dict):
            return self._mask_dict(_data)
        elif isinstance(_data, AIMessageChunk):
            return self._mask_ai_message_chunk(_data)
        elif isinstance(_data, AgentFinish):
            return self._mask_agent_finish(_data)
        elif isinstance(_data, ChatPromptValue):
            return self._mask_chat_prompt_value(_data)
        elif isinstance(_data, List):
            return self._mask_list(_data)
        else:
            warnings.warn(f"Alert!! Unknown data type: {type(_data)}. Known types are Dict, AIMessageChunk, AgentFinish, ChatPromptValue, or list. Data will not be masked.", UserWarning)
            return _data
