from enum import IntEnum, StrEnum

class ToolType(IntEnum):
    retriever_tool = 1
    non_retriever_tool = 2

class CitationType(IntEnum):
    structured = 1
    unstructured = 2
    pdf_unstructured = 3

class AzureOpenAIRegion(StrEnum):
    EastUS = "use"
    EastUS2 = "use2"
    WestUS = "usw"
    SouthCentralUS = "ussc"
    WestEurope = "euw"
    UKSouth = "uks"

class LLMFeature(StrEnum):
    STREAMING = "streaming"
    TEMPERATURE = "temperature"
    TOOL_CALLING = "tool_calling"
    REASONING = "reasoning"
    VISION = "vision"
    MAX_COMPLETION_TOKENS_PARAMETER = "max_completion_tokens_parameter"

class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    UNAUTHORIZED = "unauthorized"

class FileExtension(StrEnum):
    PDF = ".pdf"
    PPTX = ".pptx"
    PPT = ".ppt"
    XLSX = ".xlsx"
    XLS = ".xls"
    DOCX = ".docx"
    DOC = ".doc"
    CSV = ".csv"
    
class MinimumTools(StrEnum):
    all = "all"

class LamBotConfigAccessibiltiy(StrEnum):
    accessible = "accessible"
    non_accessible = "non-accessible"


# These mime types are in sync with the supported mime types for Assistant's API.
# https://platform.openai.com/docs/assistants/tools/code-interpreter#supported-files
class MimeType(StrEnum):
    WEBP = "image/webp"
    C = "text/x-c"
    CSharp = "text/x-csharp"
    CPlusPlus = "text/x-c++"
    CSV = "text/csv"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    HTML = "text/html"
    JAVA = "text/x-java"
    JSON = "application/json"
    MARKDOWN = "text/markdown"
    PDF = "application/pdf"
    PHP = "text/x-php"
    PPT = "application/vnd.ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PYTHON = "text/x-python"
    SCRIPT = "text/x-script.python"
    RUBY = "text/x-ruby"
    TEX = "text/x-tex"
    PLAIN = "text/plain"
    CSS = "text/css"
    JAVASCRIPT = "text/javascript"
    SHELL = "application/x-sh"
    TYPESCRIPT = "application/typescript"
    JPG = "image/jpg"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    PNG = "image/png"
    APPLICATION_X_TAR = "application/x-tar"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    APPLICATION_XML = "application/xml"
    TEXT_XML = "text/xml"
    APPLICATION_ZIP = "application/zip"

class IntakeItem(StrEnum):
   CONVERSATION_HISTORY = "conversation_history"
   FILE_ATTACHMENTS = "file_attachments"
   TOOL_KWARGS = "tool_kwargs"

class LanguageModelName(StrEnum):
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"
    GPT_4O_2 = "gpt-4o-2"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_32K = "gpt-4-32k"
    GPT_41 = "gpt-4.1"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41_NANO = "gpt-4.1-nano"
    GPT_5 = "gpt-5"
    GPT_5_CHAT = "gpt-5-chat"
    GPT_5_NANO = "gpt-5-nano"
    GPT_5_MINI = "gpt-5-mini"
    GPT_45_PREVIEW = "gpt-4.5-preview"
    O1 = "o1"
    O1_MINI = "o1-mini"
    O3 = "o3"
    O3_MINI = "o3-mini"
    O4_MINI = "o4-mini"
