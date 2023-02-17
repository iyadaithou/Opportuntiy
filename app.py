import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import asyncio

st.set_page_config(page_title="Brainlyne Opportunity Analyzer")
openai.api_key = st.secrets["openaiKey"]

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def get_all_pages(domain_url):
    # Parse the domain URL to extract the subdomain
    # Send a GET request to the domain URL and extract its content
    response = requests.get(domain_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the links on the page that point to the same domain or subdomain
    links = soup.find_all("a", href=lambda href: href and (domain_url in href))

    # Extract the URLs of all the pages on the same domain or subdomain
    page_urls = [link.get("href") for link in links]

    return page_urls

async def process_page(url):
    response = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract the text content from the parsed HTML
    text_content = ''
    for p in soup.find_all('p'):
        text_content += p.text
        
    # Use OpenAI to summarize the text content
    summary = await openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"What does this organization do? which list of qualities will someone need to have to work here, get accepted, or join the team; Make it concise and very brief without losing relevant information {text_content}",
        temperature=0.2,
        max_tokens=100,
        n=1,
        stop=None,
    )
    
    # Extract relevant information from the summary
    relevant_info = summary['choices'][0]['text']
    return relevant_info

async def process_pages(urls):
    tasks = []
    for url in urls:
        tasks.append(asyncio.ensure_future(process_page(url)))
    results = await asyncio.gather(*tasks)
    return ' '.join(results)

async def main(urls):
    relevant_info = await process_pages(urls)
    return relevant_info

def run_app():
    input_text = st.text_input("Paste the website url", disabled=False, placeholder="Paste the opportunity's url, and let us do the magic!")
    if input_text:
        listofurls= get_all_pages(input_text)
        relevant_info= loop.run_until_complete(main(listofurls))
        #prompt = "Avoid repeition and being too generic, and write in a clear style with an advising tone. First define what the website is about, then list the qualities or strengths I should focus on to be good fit for this opportunity and get accepted, follow that by stories and example of how to talk about those qualities. Also, please write a couple of paragraphs analyzing what they might be looking for. Make sure to refer to this as a program. Here is the text "+relevant_info    
        prompt = relevant_info    

        if prompt:
            response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2000)
            brainstorming_output = prompt
            st.info(brainstorming_output)

if __name__ == '__main__':
    run_app()
