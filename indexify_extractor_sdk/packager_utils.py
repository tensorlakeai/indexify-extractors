import asyncio
import importlib
import json
import logging
import re
import sys
from typing import List
import docker
import concurrent.futures

from jinja2 import Template


class DockerfileTemplate:
    """
    Manages the rendering of Dockerfile templates using Jinja2.

    Methods:
        configure: Prepares the template with specific configuration parameters.
        render: Renders the Dockerfile template with the provided configuration.
    """

    def __init__(self):
        self.template = self._load_template()
        self.configuration_params = {}

    def configure(
        self,
        extractor_path: "ExtractorPathWrapper",
        system_dependencies: List[str],
        python_dependencies: List[str],
        additional_pip_flags: str = "",
        dev: bool = False,
    ) -> "DockerfileTemplate":
        self.configuration_params = {
            "extractor_path": extractor_path.format(),
            "module_name": extractor_path.module_name,
            "module_file_name": extractor_path.file_name(),
            "class_name": extractor_path.class_name,
            "system_dependencies": system_dependencies,
            "python_dependencies": python_dependencies,
            "additional_pip_flags": additional_pip_flags,
            "dev": dev,
        }
        return self

    def _load_template(self) -> Template:
        from importlib import resources as impresources
        from . import dockerfiles

        inp_file = impresources.files(dockerfiles) / "Dockerfile.extractor"
        try:
            with open(inp_file) as f:
                template_content = f.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Failed to load template: {e}")

        return Template(template_content)

    def render(self, **kwargs) -> str:
        return self.template.render(**self.configuration_params, **kwargs)


class ExtractorPathWrapper:
    """
    Wraps the extractor's module and class names, providing formatting utilities.

    Attributes:
        module_name (str): The name of the module.
        class_name (str): The name of the class.

    Methods:
        format: Returns a formatted string combining module and class names.
        file_name: Returns the Python file name for the module.
    """

    def __init__(self, module_name: str, class_name: str):
        # i.e. "colbertv2"
        self.module_name = module_name
        # i.e. "ColBERTv2Base"
        self.class_name = class_name

    def validate(self) -> "ExtractorPathWrapper":
        # nothing to do for now
        return self

    def format(self) -> str:
        return f"{self.module_name_local()}:{self.class_name}"

    def module_name_local(self) -> str:
        # only the file name portion of the module name, without path.to.module
        file_name = self.module_name.replace("-", "_")
        return file_name.split(".")[-1]

    def file_name(self) -> str:
        return self.module_name_local() + ".py"


class DynamicModuleLoader:
    @staticmethod
    def load_module_from_path(module_name: str, file_path: str):
        """
        Dynamically loads a module from a given file path.

        Parameters:
            module_name (str): The name to assign to the loaded module.
            file_path (str): The file path of the Python module to load.

        Returns:
            The loaded module object.
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


async def async_docker_build(client, **kwargs):
    """
    Asynchronously build a Docker image and stream build logs.

    Args:
        client: Docker client instance.
        **kwargs: Keyword arguments for the Docker build command.

    Returns:
        The Image object for the image that was built and a list of the build logs.

    Raises:
        docker.errors.BuildError if there is an error during the build.
    """
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # Run the Docker build process in a separate thread to avoid blocking
        resp = await loop.run_in_executor(pool, lambda: client.api.build(**kwargs))
        image_id = None
        build_logs = []

        streaming_log_handler = logging.StreamHandler(sys.stdout)
        streaming_log_handler.setLevel(logging.DEBUG)

        streaming_err_handler = logging.StreamHandler(sys.stderr)
        streaming_err_handler.setLevel(logging.ERROR)

        async for chunk in async_stream_logs(resp):
            build_logs.append(chunk)
            if "error" in chunk:
                streaming_err_handler.emit(
                    logging.LogRecord(
                        "docker",
                        logging.ERROR,
                        "docker",
                        0,
                        chunk["error"].strip(),
                        None,
                        None,
                    )
                )
                raise docker.errors.BuildError(chunk["error"], build_logs)
            if "stream" in chunk:
                streaming_log_handler.emit(
                    logging.LogRecord(
                        "docker",
                        logging.DEBUG,
                        "docker",
                        0,
                        chunk["stream"].strip(),
                        None,
                        None,
                    )
                )
                match = re.search(
                    r"(^Successfully built |sha256:)([0-9a-f]+)$", chunk["stream"]
                )
                if match:
                    image_id = match.group(2)

        if image_id:
            image = await loop.run_in_executor(
                pool, lambda: client.images.get(image_id)
            )
            return (image, build_logs)
        else:
            raise docker.errors.BuildError("Unknown error", build_logs)


async def async_stream_logs(resp):
    """
    Asynchronously stream Docker build logs.

    Args:
        resp: The response object from the Docker API build request.

    Yields:
        Decoded JSON objects from the build logs.
    """
    for line in resp:
        # a line can have multiple json objects, connected with \r\n
        for line in line.decode("utf-8").split("\r\n"):
            if line:
                yield json.loads(line)
