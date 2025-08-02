from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Load both FAISS indexes
faiss_index_path_1 = "tools/output/jira_faiss_index"
faiss_index_path_2 = "tools/output/codebase_faiss_index"
vectorstore1 = FAISS.load_local(faiss_index_path_1, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
vectorstore2 = FAISS.load_local(faiss_index_path_2, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# Merge the second index into the first
vectorstore1.merge_from(vectorstore2)
vectorstore = vectorstore1

# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Custom system prompt
system_prompt = """
You are a helpful assistant. Use the provided context from the knowledge base to answer questions accurately.
If the answer is not in the context, than ask relevant clarifying questions to gather more information.
"""

# Initialize ChatOpenAI
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

# Create ConversationalRetrievalChain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
)

def chat_with_bot(user_input):
     # Include the system prompt and user input in the messages
     # Use the ConversationalRetrievalChain to handle the query
    response = response = qa_chain.invoke({
        "question": f"{system_prompt}\n\nUser Query: {user_input}"
    })
    return response["answer"]

if __name__ == "__main__":
    # print("Bot is ready. Type your message:")
    # results = vectorstore.similarity_search("TK-7959", k=3)
    # for result in results:
    #     print(result.page_content)
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer = chat_with_bot(user_input)
        print("Bot:", answer)