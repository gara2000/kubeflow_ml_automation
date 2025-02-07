import requests
import json

url = "http://localhost:5000/predict"

with open("input.json", "r") as f:
    data  = json.load(f)
# data = {
#     "data": [0.5637305699481863, 0.8750257572635484, 0.7252368647717484, 0.19958953309389438, 0.9917898193760263, 
#              0.5319148936170208, 1.0, 0.0, 0.9500000000000002, 0.5791292328956462, 0.11594202898550723, 
#              0.8033439490445861, 0.9512195121951219]
# }
# print("data: ", data)

response = requests.post(url, json=data)

print(response.json())  # Print the model's response
