from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import email
from imapclient import IMAPClient
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import ToolMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

load_dotenv()

EMAIL_USER = os.getenv("IMAP_USER")
EMAIL_PASSWORD = os.getenv("IMAP_PASS")
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


@tool
def fetch_recent_emails(limit: int = 5) -> str:
    """Connects to the Gmail IMAP server using environment variables and selects the inbox."""

    try:
        with IMAPClient(IMAP_SERVER, port=IMAP_PORT, use_uid=True, ssl=True) as client:
            client.login(EMAIL_USER, EMAIL_PASSWORD)
            client.select_folder("INBOX", readonly=True)

            messages = client.search(["ALL"])
            recent_ids = messages[-limit:]
            response = client.fetch(recent_ids, ["RFC822"])

            results = []
            for id, data in response.items():
                raw_bytes = data[b"RFC822"]
                msg = email.message_from_bytes(raw_bytes)
                subject = msg["Subject"]
                sender = msg["From"]
                results.append(f"From: {sender} | Subject: {subject}")

            return "\n".join(results)

    except Exception as e:
        print(f"Failed to connect or authenticate: {e}")
        return None


model = ChatOllama(model="llama3.2")
model_with_tool = model.bind_tools([fetch_recent_emails])


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState):
    response = model_with_tool.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode([fetch_recent_emails])


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", tool_node)

graph_builder.set_entry_point("agent")
graph_builder.add_conditional_edges("agent", should_continue)
graph_builder.add_edge("tools", "agent")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

result = graph.invoke(
    {"messages": [HumanMessage(
        content="Summarize my latest emails in a friendly tone.")]},
    config,
)
print(result["messages"][-1].content)

config = {"configurable": {"thread_id": "2"}}
result = graph.invoke(
    {"messages": [HumanMessage(
        content="Which of those emails looks the most important?")]},
    config,
)
print(result["messages"][-1].content)


def main():
    print("Email Agent initialized.")


if __name__ == "__main__":
    main()
