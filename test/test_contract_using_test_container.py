import threading
from pathlib import Path
from wsgiref.simple_server import make_server

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from api import app, database

APPLICATION_HOST = "host.docker.internal"
APPLICATION_PORT = 5001
HTTP_STUB_PORT = 8080


def stream_container_logs(container: DockerContainer, name=None):
    def _stream():
        for line in container.get_wrapped_container().logs(stream=True, follow=True):
            text = line.decode(errors="ignore").rstrip()
            prefix = f"[{name}] " if name else ""
            print(f"{prefix}{text}")

    thread = threading.Thread(target=_stream, daemon=True)
    thread.start()
    return thread


@pytest.fixture(scope="module")
def api_service():
    database.reset()
    server = make_server("0.0.0.0", APPLICATION_PORT, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    yield
    server.shutdown()
    thread.join()


@pytest.fixture(scope="module")
def test_container():
    specmatic_yaml_path = Path("specmatic.yaml").resolve()
    build_reports_path = Path("build/reports/specmatic").resolve()
    container = (
        DockerContainer("specmatic/specmatic")
        .with_command(["test", f"--host={APPLICATION_HOST}", f"--port={APPLICATION_PORT}"])
        .with_env("SPECMATIC_GENERATIVE_TESTS", "true")
        .with_volume_mapping(specmatic_yaml_path, "/usr/src/app/specmatic.yaml", mode="ro")
        .with_volume_mapping(build_reports_path, "/usr/src/app/build/reports/specmatic", mode="rw")
        .waiting_for(LogMessageWaitStrategy("Tests run:"))
    )
    container.start()
    stream_container_logs(container, name="specmatic-test")
    yield container
    container.stop()


def test_contract(api_service, test_container):
    stdout, stderr = test_container.get_logs()
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")
    if stderr or "Failures: 0" not in stdout:
        raise AssertionError(f"Contract tests failed; container logs:\n{stdout}\n{stderr}")  # noqa: EM102
