import json
import re
import io
import boto3
from flask import Response, Flask, render_template, request, redirect
from PIL import Image
from PIL.ExifTags import GPSTAGS

GPSInfo = 34853  # EXIF const

app = Flask(__name__)


def dec_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/lpr', methods=['POST'])
def upload():
    image = request.files['image']
    client = boto3.client('rekognition', region_name='us-east-1')
    buffer = image.read()
    #exif = Image.open(io.BytesIO(buffer))._getexif()
    lat = 1 #dec_from_dms(exif[GPSInfo][2], exif[GPSInfo][1])
    lng = 2 #dec_from_dms(exif[GPSInfo][4], exif[GPSInfo][3])

    response = client.detect_text(Image={'Bytes': buffer})
    for text in response['TextDetections']:
        txt = text['DetectedText']
        s = txt #''.join(re.findall('\d', txt))
        if len(s) < 8 and len(s) > 9:
            continue  # not a license plate
        return Response(mimetype='application/json',
                        response=json.dumps({'geo': (lat, lng),
                        'plate': s}), status=200)

    return Response(mimetype='application/json',
                    response="{'Error': 'No license plate found'}",
                    status=404)