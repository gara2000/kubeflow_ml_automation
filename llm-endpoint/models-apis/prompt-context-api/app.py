from flask import Flask, request, jsonify
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

app = Flask(__name__)

model_repo = os.getenv("MODEL_NAME", "tiiuae/Falcon3-1B-Instruct")

# Initialize HuggingFace endpoint
llm = HuggingFaceEndpoint(
    repo_id=model_repo,
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)

# Define prompt and output parser
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Please respond to the user's request only based on the given context."),
    ("user", "Question: {question}\nContext: {context}")
])
output_parser = StrOutputParser()

# Combine components into a chain
chain = prompt | llm | output_parser

@app.route('/generate', methods=['POST'])
def generate_response():
    # Get input data from the request
    data = request.json
    question = data.get('question')
    context = data.get('context')

    if not question or not context:
        return jsonify({"error": "Both 'question' and 'context' are required"}), 400

    # Invoke the chain with the provided question and context
    ai_response = chain.invoke({"question": question, "context": context})

    # Return the response as JSON
    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(debug=True)
