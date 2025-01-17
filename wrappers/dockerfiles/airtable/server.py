from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime, json
from urllib.parse import urlparse, parse_qs
import airtablemock

hostName = "0.0.0.0"
serverPort = 8086
base_id = 'baseID'
test_table = 'table-foo'
test_view = 'view-bar'

# This is a client for the base "baseID", it will not access the real
# Airtable service but only the mock one which keeps data in RAM.
client = airtablemock.Airtable(base_id, 'apiKey')

class AirtableMockServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path)
        [_, base_id, table_id] = path.path.split('/')
        views = parse_qs(path.query).get('view')
        view = views[0] if views else None

        records = client.get(table_id, view=view)
        if records is None:
            self.send_response(404)
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        for rec in records['records']:
            rec['createdTime'] = datetime.datetime.now().isoformat()

        self.wfile.write(bytes(json.dumps(records), "utf-8"))
        return


if __name__ == "__main__":
    # Populate a test table
    client.create(test_table, {'field1': 1, 'field2': 'two', 'field3': '2023-07-19T06:39:15.000Z'})
    client.create(test_table, {'field1': 2, 'field2': 'three', 'field3': '2023-07-20T06:39:15.000Z'})

    # Create a test view
    airtablemock.create_view(base_id, test_table, test_view, 'field2 = "three"')

    # Create web server
    webServer = HTTPServer((hostName, serverPort), AirtableMockServer)
    print("Airtable Mock Server started at http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
