import streamlit as st
import openai
from datetime import datetime
from streamlit.components.v1 import html
import pandas as pd
import csv
import requests
from bs4 import BeautifulSoup



st.set_page_config(page_title="Brainlyne Essay Editor")


html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """

button = """
<script type="text/javascript" src="https://brainlyne.com" data-name="bmc-button" data-slug="nainiayoub" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Join Brainlyne" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
"""


with st.sidebar:
    st.markdown("""
    # About 
    Brainlyne Essay Support is a helper tool built and tuned to support with the generation of ideas for essays
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # How does it work
    Simply enter the topic of interest in the text field below and ideas will be generated.
    You can also download the essay as txt.
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    Made by Brainlyne
    """,
    unsafe_allow_html=True,
    )



input_text = None
if 'output' not in st.session_state:
    st.session_state['output'] = 0

if st.session_state['output'] <=2:
    st.markdown("""
    # Brainlyne Opportunity Analyzer
    """)
    input_text = st.text_input("Paste the website url", disabled=False, placeholder="Paste the opportunity's url, and let us do the magic!")
    st.session_state['output'] = st.session_state['output'] + 1
else:
    # input_text = st.text_input("Brainstorm ideas for", disabled=True)
    st.info("Thank you! Refresh for more brainstorming💡")
    st.markdown('''
    <style>
    .btn{
        display: inline-flex;
        -moz-box-align: center;
        align-items: center;
        -moz-box-pack: center;
        justify-content: center;
        font-weight: 400;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        margin: 0px;
        line-height: 1.6;
        color: #fff;
        background-color: #00acee;
        width: auto;
        user-select: none;
        border: 1px solid #00acee;
        }
    .btn:hover{
        color: #00acee;
        background-color: #fff;
    }
    </style>
    ''',
    unsafe_allow_html=True
    )

hide="""
<style>
footer{
	visibility: hidden;
    position: relative;
}
.viewerBadge_container__1QSob{
    visibility: hidden;
}
#MainMenu{
	visibility: hidden;
}
<style>
"""
st.markdown(hide, unsafe_allow_html=True)

html(button, height=70, width=220)
st.markdown(
    """
    <style>
        iframe[width="220"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if input_text:
    response = requests.get(input_text)

    soup = BeautifulSoup(response.content, 'html.parser')

# Extract the text content from the parsed HTML
    text_content = ''
    for p in soup.find_all('p'):
        text_content += p.text

    prompt = " Tell me what in a list what I should focus on if I want to be selected for this opportunity and examples of what I need to highlight "+str(text_content)
    if prompt:
        openai.api_key = st.secrets["openaiKey"]
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=1000)
        brainstorming_output = response['choices'][0]['text']
        today = datetime.today().strftime('%Y-%m-%d')
        topic = "Essay"+input_text+"\n@Date: "+str(today)+"\n"+brainstorming_output
        
        st.info(brainstorming_output)
        filename = "brainstorming_"+str(today)+".txt"
        btn = st.download_button(
            label="Download Recommendation",
            data=topic,
            file_name=filename
        )
        fields = [input_text, brainstorming_output, str(today)]
        # read local csv file
        r = pd.read_csv('./data/prompts.csv')
        if len(fields)!=0:
            with open('./data/prompts.csv', 'a', encoding='utf-8', newline='') as f:
                # write to csv file (append mode)
                writer = csv.writer(f, delimiter=',', lineterminator='\n')
                writer.writerow(fields)

        
        

        
