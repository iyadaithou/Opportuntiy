import streamlit as st
import openai
import requests
from html.parser import HTMLParser
from multiprocessing import Process, Queue

st.set_page_config(page_title="Brainlyne Opportunity Analyzer")
openai.api_key = st.secrets["openaiKey"]

class MyHTMLParser(HTMLParser):
    def __init__(self, domain_url):
        super().__init__()
        self.domain_url = domain_url
        self.urls = []
        
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == "href" and self.domain_url in attr[1]:
                self.urls.append(attr[1])
                
    def get_urls(self):
        return self.urls

def get_all_pages(domain_url):
    response = requests.get(domain_url)
    parser = MyHTMLParser(domain_url)
    parser.feed(response.text)
    page_urls = parser.get_urls()
    return page_urls


def process_page(url, queue):
    response = requests.get(url)
    parser = MyHTMLParser(url)
    parser.feed(response.text)
    text_content = '\n'.join(parser.get_data())
    summary = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"What does this organization do? Which list of qualities will someone need to have to work here, get accepted, or join the team? Make it concise and very brief without losing relevant information. {text_content}",
        temperature=0.2,
        max_tokens=100,
        n=1,
        stop=None,
    )
    relevant_info = summary['choices'][0]['text']
    queue.put(relevant_info)


def process_pages(urls):
    queue = Queue()
    processes = []
    for url in urls:
        p = Process(target=process_page, args=(url, queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    return ' '.join(results)


def main():
    input_text = st.text_input("Paste the website url",
                               placeholder="Paste the opportunity's url, and let us do the magic!")
    if not input_text:
        return

    with st.spinner("Fetching and summarizing content. Please wait..."):
        list_of_urls = get_all_pages(str(input_text))
        relevant_info = process_pages(list_of_urls)
        prompt = "Avoid repetition and being too generic, and write in a clear style with an advising tone. First define what the website is about, then list the qualities or strengths I should focus on to be a good fit for this opportunity and get accepted, follow that by stories and examples of how to talk about those qualities. Also, please write a couple of paragraphs analyzing what they might be looking for. Make sure to refer to this as a program. Here is the text: " + relevant_info
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2000)
        brainstorming_output = relevant_info
        st.info(brainstorming_output)
if __name__ == '__main__':
    main()
