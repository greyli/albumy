import json

from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes, VisualFeatureTypes


def get_alternative_text(local_path: str):
    secrete = json.load(open('albumy/blueprints/secrete.json'))
    API_KEY = secrete['API_KEY']
    END_POINT = secrete['END_POINT']
    client = ComputerVisionClient(END_POINT, CognitiveServicesCredentials(API_KEY))
    try:
        respond = client.describe_image_in_stream(
            open(local_path, 'rb'),
            raw=True
        )
        text = respond.output.captions[0].text
    except:
        print("Error occur when fetching alternating text from azure")

    return text
