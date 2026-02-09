import os
import threading
from wsgiref.simple_server import make_server

import pytest
from specmatic.core.specmatic import Specmatic

from api import app, database
from definitions import ROOT_DIR

os.environ["SPECMATIC_GENERATIVE_TESTS"] = "true"
os.environ["FILTER"] = "PATH!='/internal/metrics'"
os.environ["APP_URL"] = "http://127.0.0.1:5001"


class TestContract:
    pass


database.reset()
server = make_server("127.0.0.1", 0, app)
port = server.server_port
os.environ["APP_URL"] = f"http://127.0.0.1:{port}"
thread = threading.Thread(target=server.serve_forever)
thread.start()

try:
    Specmatic().with_project_root(ROOT_DIR).test_with_api_coverage_for_flask_app(
        TestContract, app, test_host="127.0.0.1", test_port=port
    ).run()
finally:
    server.shutdown()
    thread.join()

if __name__ == "__main__":
    pytest.main()
