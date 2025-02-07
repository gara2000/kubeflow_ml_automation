from flask import Flask, render_template, request, redirect, url_for
import requests  # For API requests to your AI model

app = Flask(__name__)

# Replace this URL with your AI model's endpoint
# MODEL_URL = "http://sklearn-model.kserve-test.172.18.255.200.nip.io/predict"
# MODEL_URL = "http://localhost:8080/predict"
# MODEL_URL = "http://sklearn-iris.kubeflow-user-example-com.svc.cluster.local/v1/models/sklearn-iris:predict"
# MODEL_URL = "http://sklearn-model.kubeflow-user-example-com.svc.cluster.local/predict"
MODEL_URL = "http://sklearn-inference.kubeflow-user-example-com.svc.cluster.local/v1/models/sklearn-inference:predict"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        print("Helloo!")
        print("Another hellooo!")
        x1 = request.form['x1']
        x2 = request.form['x2']
        x3 = request.form['x3']
        x4 = request.form['x4']
        # input_data = request.form['input_data']
        input_data = {"instances": [[0, 0, float(x1), float(x2), float(x3), float(x4)]]}
        
        print(input_data)
        headers = {"X-Frontend-Access": "true"}
        # Send the data to the AI model endpoint and get the prediction
        response = requests.post(MODEL_URL, json=input_data, headers=headers)
        print("posted request")
        print("repsonse json: ", response.json())
        prediction = response.json().get('predictions', 'Error: No prediction received')
        print("predcition: ", prediction)

        return redirect(url_for('result', result=prediction))
        # return redirect(url_for('result', result=response))
    
    return render_template('predict.html')

@app.route('/result')
def result():
    result = request.args.get('result', 'No result to display')
    return render_template('result.html', result=result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
