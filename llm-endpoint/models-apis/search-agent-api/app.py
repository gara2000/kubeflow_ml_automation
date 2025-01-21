from flask import Flask, request, jsonify
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import os

app = Flask(__name__)

model_repo = os.getenv("MODEL_NAME", "HuggingFaceH4/zephyr-7b-beta")

def get_chat_model(repo_id):
  llm = HuggingFaceEndpoint(
      repo_id=repo_id,
      task="text-generation",
      max_new_tokens=512,
      do_sample=False,
      repetition_penalty=1.03,
  )
  
  chat_model = ChatHuggingFace(llm=llm)
  return chat_model

search = TavilySearchResults(max_results=2)
tools = [search]
model = get_chat_model(model_repo)
agent_executor = create_react_agent(model, tools)

@app.route('/generate', methods=['POST'])
def generate_response():
    # Get input data from the request
    data = request.json
    question = data.get('question')
    context = data.get('context')

    if not question or not context:
        return jsonify({"error": "Both 'question' and 'context' are required"}), 400

    message = f"Question: {question} \nContext: {context}"
    response = agent_executor.invoke({"messages": [HumanMessage(content=message)]})

    # Parse the response to extract useful data
    extracted_data = {
        "human_message": next(
            (msg.content for msg in response["messages"] if isinstance(msg, HumanMessage)), None
        ),
        "ai_response": next(
            (msg.content for msg in response["messages"] if isinstance(msg, AIMessage)), None
        ),
        "tool_results": []
    }

    # If there are tool results, add them to the response
    for msg in response["messages"]:
        if isinstance(msg, ToolMessage):
            print("msg artifact: ", msg.artifact)
            if msg.artifact:
                extracted_data["tool_results"].append({
                    "tool_name": msg.name,
                    "query": msg.artifact.get('query'),
                    "results": [
                        {
                            "title": result.get("title"),
                            "url": result.get("url"),
                            "content": result.get("content")
                        } for result in msg.artifact.get("results", [])
                    ],
                    "response_time": msg.artifact.get("response_time")
                })

    return jsonify(extracted_data)
    # response["messages"]

    # Return the response as JSON
    # return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
