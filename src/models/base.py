from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from typing import List


class ConfiguredBaseModel(BaseModel):
    """
    A Pydantic BaseModel with a custom configuration that supports both camelCase and snake_case naming conventions.

    This model allows for flexible initialization and retrieval of field names, making it easier to work with different naming conventions in your data.
    """

    class Config:
        """
        Configuration for the ConfiguredBaseModel.

        Attributes:
            alias_generator (callable): A function to generate aliases for fields. Uses camelCase.
            populate_by_name (bool): Whether an aliased field may be populated by its name as given by the model attribute, as well as the alias.
        """

        alias_generator = to_camel

        # When set to True:
        # You can initialize the model using either the field names or their aliases.
        # This is useful when you want to support both camelCase and snake_case naming conventions.

        # When set to False:
        # You can only initialize the model using the field aliases.
        # This enforces a strict naming convention for input data.
        populate_by_name = True

    def get_field_names(self, by_alias: bool = False) -> List:
        """
        Retrieve the field names of the model.

        Args:
            by_alias (bool): If True, returns the field aliases instead of the field names.

        Returns:
            list: A list of field names or aliases.
        """
        if by_alias:
            return [field.alias for field in self.model_fields.values()]
        return list(self.model_fields.keys())
