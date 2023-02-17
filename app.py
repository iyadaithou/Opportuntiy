import streamlit as st
import openai
import requests
from html.parser import HTMLParser
from multiprocessing import Pool

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


def process_page(url,relevant_info):
    response = requests.get(url)
    parser = MyHTMLParser(url)
    parser.feed(response.text)
    text_content = "\n".join(parser.get_data())
    summary = openai.Completion.create(
        engine="text-davinci-003",
        prompt="does this information: "+text_content+"  \n help  to improve response to what hat is the program? is it a school? summer institue, a company? or what exactly, and what are the qualities or strengths I should focus on to be a good fit for this opportunity and get accepted. \n \n Here is the current information "+ relevant_info+" rewite a new response if it will provide clearer answer to the question, if not keep it unchanged ",
        temperature=0.1,
        max_tokens=450,
        n=1,
        stop=None,
    )
    relevant_info = summary["choices"][0]["text"]
    return relevant_info


def process_pages(urls):
    relevant_info = ""
    for url in urls:
        new_relevant_info = process_page(url,relevant_info)
        if new_relevant_info:
            relevant_info = new_relevant_info
    return relevant_info


def main():
    input_text = st.text_input(
        "Paste the website url",
        placeholder="Paste the opportunity's url, and let us do the magic!",
    )
    if not input_text:
        return

    with st.spinner("Fetching and summarizing content. Please wait..."):
        list_of_urls = MyHTMLParser(input_text).get_urls()
        relevant_info = process_pages(list_of_urls[:5])
        prompt = (
            "Avoid repetition and being generic, and write in a clear style with an advising tone. First gives the name of the program, then waht is the program? is it a school? summer institue, a company? or what exactly, then list the qualities or strengths I should focus on to be a good fit for this specifc program;  follow that by stories and examples of how to talk about those qualities. Also, please write a couple of paragraphs analyzing what they might be looking for. Make sure to refer to this as a program "
            + relevant_info
        )
        response = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, temperature=0.1, max_tokens=2000
        )
        brainstorming_output = response["choices"][0]["text"]
        st.info(brainstorming_output)


if __name__ == "__main__":
    main()
