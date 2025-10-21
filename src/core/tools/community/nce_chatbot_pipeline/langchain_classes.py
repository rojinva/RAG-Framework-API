from langchain_community.utilities import SQLDatabase as BaseSQLDatabase
from typing import Optional, List
import logging
from langchain.memory import ConversationBufferMemory as BaseConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage


class SQLDatabase(BaseSQLDatabase):
    """
    This class takes the Langchain SQLDatabase class and overrides the
    get_table_info method to allow lazy loading of metadata tables.
    """

    def __init__(self, *args, **kwargs):
        super(SQLDatabase, self).__init__(*args, **kwargs)

    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        if table_names is None:
            return ""

        loaded_tables = self._metadata.tables

        tables_to_load = []

        for table_name in table_names:
            if table_name not in loaded_tables:
                tables_to_load.append(table_name)

        if len(tables_to_load) > 0:
            self._metadata.reflect(bind=self._engine, only=tables_to_load)

        return super().get_table_info(table_names)


class LazyReflectMetadata:
    def __init__(self):
        super().__init__()
        self._initial_reflect = True

    def reflect(
        self,
        bind=None,
        schema=True,
        views=False,
        only=None,
        extend_existing=False,
        autoload_replace=True,
        resolve_fks=True,
        **dialect_kwargs,
    ):
        if self._initial_reflect:
            logging.debug("Ignoring _initial_reflect due to initialization.")
            self._initial_reflect = False
        else:
            logging.debug("Calling reflect with tables=%s", only)
            return super().reflect(
                bind,
                schema,
                views,
                only,
                extend_existing,
                autoload_replace,
                resolve_fks,
                **dialect_kwargs,
            )


class ConversationBufferMemory(BaseConversationBufferMemory):
    def save_context(self, inputs, outputs) -> None:
        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        output_str = (
            output_str if isinstance(output_str, str) else str(output_str)
        )  # this line is the temp-fix
        self.chat_memory.add_messages(
            [HumanMessage(content=input_str), AIMessage(content=output_str)]
        )
