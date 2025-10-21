import re
import asyncio
import warnings
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import logging
from .openai_config import llm_4o, llm_4o_mini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


warnings.filterwarnings("ignore")


class Summarizer:
    def __init__(
        self,
        df,
        col_list,
        summary_prompt_reduce,
        summary_prompt_map,
        question,
        chunk_size=45000,
        chunk_overlap=0,
        chunk_split_type="rec_character",
        character_lim=15,
        word_lim=0,
        row_lim=0,
        concurrent_runs=10,
        gpt_mod="gpt-4o",
    ):
        self.df = df.copy()
        self.question = question
        self.col_list = col_list
        self.gpt_mod = gpt_mod
        self.summary_prompt_reduce = summary_prompt_reduce
        self.summary_prompt_map = summary_prompt_map
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_split_type = chunk_split_type
        self.character_lim = character_lim
        self.word_lim = word_lim
        self.row_lim = row_lim
        self.concurrent_runs = concurrent_runs

    def text_cleanup(self, line_inp):
        ### Removing Timestamp
        line_inp = line_inp.replace("\n", " ")
        line_inp = re.sub(" +", " ", line_inp)
        pat = re.compile(r"\d{2}[-/]\d{2}[-/]\d{4} \d{2}:\d{2}:\d{2} PST ")
        pat2 = re.compile(r"\d{2,4}\.\d{1,2}\.\d{1,2}")  ## Optimize
        line = re.sub(pat, "", line_inp)
        line = re.sub(pat2, "", line)
        return line.lower()

    def initialize_azure_client(self):
        if self.gpt_mod == "gpt-4o":
            llm_ = llm_4o
        else:
            llm_ = llm_4o_mini
        return llm_

    def get_docs(self, text_inp, chunk_size, chunk_overlap, split_type="character"):
        docs = [Document(page_content=text_inp)]
        if split_type == "token":
            splitter = TokenTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
        elif split_type == "character":
            splitter = CharacterTextSplitter(
                separator="==TicketEnd=="
            ).from_tiktoken_encoder(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )  ##(separator='\n\n')
        else:
            splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base",
                separators=["==TicketEnd=="],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        split_docs = splitter.split_documents(docs)
        return split_docs

    def mr_framework(self, docs_inp, llm_inp):

        # Map Chain
        map_template = self.summary_prompt_map

        map_prompt = PromptTemplate.from_template(map_template)

        map_chain = LLMChain(prompt=map_prompt, llm=llm_inp)

        # Reduce Chain
        reduce_template = self.summary_prompt_reduce

        reduce_prompt = PromptTemplate.from_template(reduce_template)
        reduce_chain = LLMChain(prompt=reduce_prompt, llm=llm_inp)
        stuff_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="doc_summaries"
        )

        reduce_chain = ReduceDocumentsChain(
            combine_documents_chain=stuff_chain,
        )

        # Map Reduce Chain
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            document_variable_name="content",
            reduce_documents_chain=reduce_chain,
        )
        summary = map_reduce_chain.run(docs_inp)
        return summary

    def get_summary(self):

        logging.info("There are {} rows before filtering.".format(self.df.shape[0]))

        self.df["Desc_Cleaned"] = self.df[self.col_list].apply(
            lambda x: self.text_cleanup(str(x))
        )

        df_filtered = self.df[self.df["Desc_Cleaned"] != ""]

        logging.info("There are {} rows in filtered data".format(df_filtered.shape[0]))

        logging.info("Creating chunks for data")
        t_str = (" ==TicketEnd== ").join(
            [text.strip() for text in df_filtered["Desc_Cleaned"].values]
        )
        split_docs = self.get_docs(
            t_str,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            split_type=self.chunk_split_type,
        )
        logging.info("No. of documents after chunking: {}".format(len(split_docs)))
        logging.info("Initialize LLM instance")
        llm = self.initialize_azure_client()
        summary = self.mr_framework(split_docs, llm)

        return summary

    async def amr_framework(self, docs_inp, llm_inp):
        concurrent_runs = self.concurrent_runs
        semaphore = asyncio.Semaphore(concurrent_runs)
        logging.info("No. of concurrent runs : {}".format(concurrent_runs))
        async with semaphore:
            # Map Chain
            map_template = self.summary_prompt_map
            map_prompt = PromptTemplate.from_template(map_template)

            map_chain = LLMChain(prompt=map_prompt, llm=llm_inp)

            # Reduce Chain
            reduce_template = self.summary_prompt_reduce

            reduce_prompt = PromptTemplate.from_template(reduce_template)
            reduce_chain = LLMChain(prompt=reduce_prompt, llm=llm_inp)
            stuff_chain = StuffDocumentsChain(
                llm_chain=reduce_chain, document_variable_name="doc_summaries"
            )

            reduce_chain = ReduceDocumentsChain(
                combine_documents_chain=stuff_chain,
            )

            # Map Reduce Chain
            map_reduce_chain = MapReduceDocumentsChain(
                llm_chain=map_chain,
                document_variable_name="content",
                reduce_documents_chain=reduce_chain,
            )

            summary = await map_reduce_chain.arun(docs_inp)
            return summary

    async def aget_summary(self):

        df_filtered = self.df.copy()

        logging.info("There are {} rows".format(df_filtered[self.col_list].shape[0]))
        logging.info("Cleaning the columns: {}".format(self.col_list))
        df_filtered["Desc_Cleaned"] = df_filtered["Description"].apply(
            lambda x: self.text_cleanup(x)
        )

        logging.info("There are {} rows in filtered data.".format(df_filtered.shape[0]))

        logging.info("Creating chunks for data")
        t_str = (" ==TicketEnd== ").join(
            [text.strip() for text in df_filtered["Desc_Cleaned"].values]
        )
        split_docs = self.get_docs(
            t_str,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            split_type=self.chunk_split_type,
        )
        logging.info("No. of documents after chunking: {}".format(len(split_docs)))

        logging.info("Initialize LLM instance")
    
        llm = self.initialize_azure_client()

        output_summary = await self.amr_framework(split_docs, llm)

        return output_summary
