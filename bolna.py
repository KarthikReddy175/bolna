import streamlit as st
from openai import OpenAI
import re
# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Streamlit application
st.title("BOLNA")

# User input
user_input = st.text_input("Enter your question:", "What is my laptop not turning on?")

# Prompt to emphasize specificity and citations
prompt = (
    f"Answer the following question related to Lenovo Laptop in a very specific manner, "
    f"providing the exact cause and the solution of the customer's problems; Do not elaborate a lot "
    f"unless specifically asked in the user query. Provide nearby locations for Service centres respectively as the user might deem necessary, "
    f"included with links. Act as a complete helpful assistant:\n\n{user_input}"
)

# Button to submit the input and get the response
if st.button("Get Genes and Citations"):
    completion = client.chat.completions.create(
        model="meta/llama-3.1-405b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content

    # Display the response as plain text
    st.write("Response")
    st.write(response)

    # Extract and format citations
    citations = re.findall(r'\[(.*?)\]\((.*?)\)', response)
    if citations:
        st.write("Citations:")
        for text, link in citations:
            st.write(f"[{text}]({link})")
