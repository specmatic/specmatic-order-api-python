import os
import threading
from wsgiref.simple_server import make_server

import pytest
from specmatic.core.specmatic import Specmatic

from api import app, database
from definitions import PROJECT_ROOT


class TestContract:
    pass


database.reset()
server = make_server("127.0.0.1", 0, app)
port = server.server_port
os.environ["APP_URL"] = f"http://127.0.0.1:{port}"
thread = threading.Thread(target=server.serve_forever)
thread.start()

try:
    (
        Specmatic(PROJECT_ROOT)
        .test_with_api_coverage_for_flask_app(TestContract, app)
        .run()
    )
finally:
    server.shutdown()
    thread.join()

if __name__ == "__main__":
    pytest.main()
