import json

from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes

def get_alternative_text(local_path:str):
    secrete = json.load(open('secrete.json'))
    API_KEY = secrete['API_KEY']
    END_POINT = secrete['END_POINT']
    client = ComputerVisionClient(END_POINT,API_KEY)
    respond = client.describe_image_in_stream(
        open(local_path,'rb'),
        raw=True
    )
    print(respond)
