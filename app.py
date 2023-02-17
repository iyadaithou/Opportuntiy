import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import asyncio

st.set_page_config(page_title="Brainlyne Opportunity Analyzer")

openai.api_key = st.secrets["openaiKey"]

input_text = None
if 'output' not in st.session_state:
    st.session_state['output'] = 0

if st.session_state['output'] <=2:
    st.markdown("""
    # Brainlyne Opportunity Analyzer
    """)
    input_text = st.text_input("Paste the website url", disabled=False, placeholder="Paste the opportunity's url, and let us do the magic!")
    st.session_state['output'] = st.session_state['output'] + 1

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
    text_content = ''
    for p in soup.find_all('p'):
        text_content += p.text
    summary = await openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"What does this organization do? Which list of qualities will someone need to have to work here, get accepted, or join the team? Make it concise and very brief without losing relevant information. {text_content}",
        temperature=0.2,
        max_tokens=100,
        n=1,
        stop=None,
    )
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

if input_text:
    list_of_urls = get_all_pages(input_text)
    relevant_info = loop.run_until_complete(main(list_of_urls))
    prompt = f"Avoid repetition and being too generic, and write in a clear style with an advising tone. First, define what the website is about, then list the qualities or strengths I should focus on to be a good fit for this opportunity and get accepted. Follow that by stories and examples of how to talk about those qualities. Also, please write a couple of paragraphs analyzing what they might be looking for. Make sure to refer to this as a program. Here is the text: {relevant_info}"    
    if prompt:
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2000)
        brainstorming_output = response['choices'][0]['text']
        st.info(brainstorming_output)
