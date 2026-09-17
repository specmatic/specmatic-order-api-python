import os
import sys
import threading
from pathlib import Path
from wsgiref.simple_server import make_server

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from api import app, database
from definitions import PROJECT_ROOT_PATH

APPLICATION_HOST = "0.0.0.0"
APPLICATION_PORT = 5001


def stream_container_logs(container: DockerContainer, name=None):
    def _stream():
        for line in container.get_wrapped_container().logs(stream=True, follow=True):
            text = line.decode(errors="ignore").rstrip()
            prefix = f"[{name}] " if name else ""
            print(f"{prefix}{text}", flush=True)

    thread = threading.Thread(target=_stream, daemon=True)
    thread.start()
    return thread


@pytest.fixture(scope="module")
def api_service():
    database.reset()
    server = make_server(APPLICATION_HOST, APPLICATION_PORT, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture(scope="module")
def test_container():
    container = DockerContainer("specmatic/specmatic")
    host_user = f"{os.getuid()}:{os.getgid()}" if hasattr(os, "getuid") and hasattr(os, "getgid") else None
    for name, value in os.environ.items():
        container.with_env(name, value)

    container = (
        container
        .with_command(["test"])
        .with_volume_mapping(str(Path.home() / ".specmatic"), "/specmatic", mode="ro")
        .with_env("SPECMATIC_LICENSE_PATH", "/specmatic/specmatic-license.txt")
        .with_env("JAVA_OPTS", "-Dspecmatic.logging.level=trace -Dspecmatic.logging.stdout.enabled=true")
        .with_env("APP_URL", f"http://host.docker.internal:{APPLICATION_PORT}")
        .with_volume_mapping(str(PROJECT_ROOT_PATH), "/usr/src/app", mode="rw")
        .with_env("GIT_DISCOVERY_ACROSS_FILESYSTEM", "1")
        .with_kwargs(
            extra_hosts={"host.docker.internal": "host-gateway"},
            working_dir="/usr/src/app",
            **({"user": host_user} if host_user else {}),
        )
        .waiting_for(LogMessageWaitStrategy("Tests run:").with_startup_timeout(120))
    )
    thread = None
    try:
        container.start()
        thread = stream_container_logs(container, name="specmatic-test")
        yield container
    finally:
        try:
            container.stop()
        finally:
            if thread is not None:
                thread.join(timeout=10)


@pytest.mark.skipif(
    os.environ.get("CI") == "true" and not sys.platform.startswith("linux"),
    reason="Run only on Linux CI; all platforms allowed locally",
)
def test_contract(api_service, test_container):
    stdout, stderr = test_container.get_logs()
    stdout = stdout.decode("utf-8", errors="replace")
    stderr = stderr.decode("utf-8", errors="replace")
    logs = f"Contract test container logs:\n{stdout}\n{stderr}"
    assert "Failures: 0" in stdout, logs
