from io import StringIO
from flask import Flask, stream_with_context, request
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response
import simplekml
import io
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST','GET'])
def download():
	def generate():
		data = request.form['json']
		dataDicts = json.loads(data)
		coords = []
		kml = simplekml.Kml()
		for dataDict in dataDicts:
			for trace in dataDict['trace']:
				coords.append((trace['lat'],trace['lng']))
			for coord in coords:
				coords[coords.index(coord)] = (coord[1],) + (coord[0],) + (0,)
			fol = kml.newfolder()
			ls = fol.newlinestring(name="name")
			ls.coords = coords

		from bs4 import BeautifulSoup as bs4

		soup = bs4(kml.kml(), 'html.parser')
		coordinates = soup.findAll('coordinates')
		for coordinate in coordinates:
			coordinate.string = coordinate.text.replace(' ','\n      ')

		xml = soup.prettify("utf-8").decode("utf-8")
		f = io.StringIO(xml)
		for line in f:
			yield line.encode('utf-8').replace("linestring", "LineString").replace("placemark", "Placemark").replace("folder", "Folder").replace("document", "Document").decode('utf-8')

	# add a filename
	headers = Headers()
	headers.set('Content-Disposition', 'attachment', filename='log.kml')

	# stream the response as the data is generated
	return Response(
		stream_with_context(generate()),
		mimetype='text/xml', headers=headers
	)
