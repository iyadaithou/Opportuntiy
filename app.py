import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import asyncio

st.set_page_config(page_title="Brainlyne Opportunity Analyzer")

openai.api_key = st.secrets["openaiKey"]
loop = asyncio.get_event_loop()

def get_all_pages(domain_url):
    response = requests.get(domain_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=lambda href: href and (domain_url in href))
    page_urls = [link.get("href") for link in links]
    return page_urls

async def process_page(url):
    response = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(response.content, "html.parser")
    text_content = ''.join(p.text for p in soup.find_all('p'))
    summary = await openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"What does this organization do? What list of qualities are required to work here, get accepted, or join the team? Make it concise without losing relevant information. {text_content}",
        temperature=0.2,
        max_tokens=100,
        n=1,
        stop=None,
    )
    relevant_info = summary['choices'][0]['text']
    return relevant_info

async def process_pages(urls):
    tasks = [asyncio.ensure_future(process_page(url)) for url in urls]
    results = await asyncio.gather(*tasks)
    return ' '.join(results)

if __name__ == '__main__':
    input_text = st.text_input("Paste the website url", placeholder="Paste the opportunity's URL")
    if input_text:
        list_of_urls = get_all_pages(input_text)
        relevant_info = loop.run_until_complete(process_pages(list_of_urls))
        prompt = f"Avoid repetition and being too generic. First, define what the website is about, then list the qualities or strengths that one needs to have to work here or join the team. Follow that with stories and examples of how to talk about those qualities. Also, please write a couple of paragraphs analyzing what they might be looking for. Make sure to refer to this as a program. Here is the text: {relevant_info}"
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2000)
        brainstorming_output = prompt
        st.info(brainstorming_output)
