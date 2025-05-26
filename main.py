from trafilatura.spider import focused_crawler
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import json

# Schema classes
class Employee(BaseModel):
    name: str = Field(description="REQUIRED: The name of the person.")
    title: str = Field(None, description="The title of the person.")
    position: str = Field(None, description="The position of the person.")
    location: str = Field(None, description="The location of the person.")

class WebsiteSummary(BaseModel):
    title: str = Field(description="REQUIRED: The title of the website to summarize.")
    summary: str = Field(description="REQUIRED: The summary of the website's content.")
    company_name: str = Field(description="REQUIRED: The name of the company.")
    industry: str = Field(None, description="The industry that this company is in.")
    employees: List[Employee] = Field([], description="Any employees identified in the website.")
    value_proposition: str = Field(None, description="The value proposition of the company.")
    competition: List[str] = Field(None, description="Competing firms to the company.")

# Fetch and extract plain text from a webpage
def fetch_and_extract_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except requests.RequestException as e:
        print(f"Error fetching or parsing {url}: {e}")
        return ''

# Summarization class
class Summarize:
    def __init__(self):
        self.__apikey = ''
        self.llm = ChatOpenAI(
            openai_api_key=self.__apikey,
            model_name='gpt-3.5-turbo',
            temperature=0.1,
            max_tokens=4000
        )

    def summarize_webpage(self, text: str, chain_type: Literal["stuff", "refine", "map_reduce"]) -> str:
        try:
            if not text or len(text) < 30:
                return "No text to summarize"

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=1000)
            chunks = text_splitter.create_documents([text])

            map_custom_prompt = '''
            Summarize the following text in a clear and concise way:
            TEXT:`{text}`
            Brief Summary:
            '''
            map_prompt_template = PromptTemplate(input_variables=['text'], template=map_custom_prompt)

            combine_custom_prompt = '''
            Generate a summary of the following text that includes the following elements in json format:

            * A title that accurately reflects the content of the text.
            * The summary of the website's content in string.
            * The company_name in string
            * The industry that this company is in
            * extract list of all employee like team member ,directors,advisors details about there names ,position, make sure you are not summarize the members and not generate AI employee list.
            * The value preposition of the company
            * Information about competing firms may include details about their products, pricing strategies,  market share, customer base, marketing approaches, and any other factors that impact their competitiveness in the industry
            Text:`{text}`
            '''
            combine_prompt_template = PromptTemplate(input_variables=['text'], template=combine_custom_prompt)

            if chain_type == "map_reduce":
                summary_chain = load_summarize_chain(
                    llm=self.llm,
                    chain_type=chain_type,
                    verbose=True,
                    map_prompt=map_prompt_template,
                    combine_prompt=combine_prompt_template,
                )
            else:
                summary_chain = load_summarize_chain(
                    llm=self.llm,
                    chain_type=chain_type,
                    verbose=True
                )

            summary = summary_chain.invoke(chunks)
            data = json.loads(summary['output_text'])
            return data

        except Exception as e:
            raise e

# Extract all internal website links
def get_all_website_links(url):
    urls = set()
    domain_name = urlparse(url).netloc

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return urls

    soup = BeautifulSoup(response.text, "html.parser")

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if len(urls) >= 9:
            break
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if href in urls:
            continue
        if domain_name not in href:
            continue
        urls.add(href)

    return urls

# Main execution function
def main(start_url):
    combined_text = ''
    urls = get_all_website_links(start_url)

    for url in urls:
        print(url)
        text_content = fetch_and_extract_text(url)
        combined_text += ' ' + text_content

    print(combined_text)

    summary = Summarize()
    summarization_method = "map_reduce"
    summarize_text_data = summary.summarize_webpage(combined_text, chain_type=summarization_method)

    print("-----------------------------------------------------")
    print(summarize_text_data['title'])

    print("-----------------------------------------------------")
    website_summary = WebsiteSummary(**summarize_text_data)
    print(website_summary)

    print("-----------------------------------------------------")
    print(website_summary.employees)

if __name__ == "__main__":
    main_url = "https://dolphinstudios.co/"
    main(main_url)
