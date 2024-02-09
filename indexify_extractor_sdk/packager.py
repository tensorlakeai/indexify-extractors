import asyncio
import gzip
import io
import json
import os
from pathlib import Path
import re
import tarfile
from docker import DockerClient, errors as docker_err
import docker
import logging
from pydantic_settings import BaseSettings
from typing import Dict, Any, List
from jinja2 import Template
from .base_extractor import ExtractorWrapper
import importlib.resources as pkg_resources
import importlib.util
import sys

class ExtractorPackagerConfig(BaseSettings):
    """
    Configuration settings for the extractor packager using Pydantic for environment management.

    Attributes:
        module_name (str): The name of the module where the extractor is defined.
        class_name (str): The name of the extractor class.
        dockerfile_template_path (str): Path to the Dockerfile Jinja2 template. Defaults to "Dockerfile.extractor".
        verbose (bool): Enables verbose logging if set to True. Defaults to False.
        dev (bool): Indicates if the package is being prepared for development. This affects dependency inclusion. Defaults to False.
        gpu (bool): Indicates if the package requires GPU support. Affects how Python dependencies are installed. Defaults to False.
    """
    module_name: str
    class_name: str

    dockerfile_template_path: str = "../dockerfiles/Dockerfile.extractor"
    verbose: bool = False
    dev: bool = False
    gpu: bool = False

    # Example of using Field to customize env variable names
    # some_other_config: str = Field(default="default_value", env="SOME_OTHER_CONFIG")

    class Config:
        # Tells Pydantic to read from environment variables as well
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"


class DockerfileTemplate:
    """
    Manages the rendering of Dockerfile templates using Jinja2.

    Attributes:
        template_path (str): The file path to the Jinja2 template for the Dockerfile.

    Methods:
        configure: Prepares the template with specific configuration parameters.
        render: Renders the Dockerfile template with the provided configuration.
    """
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = None
        self._load_template()
        self.configuration_params = {}

    def configure(self, extractor_path: "ExtractorPathWrapper", system_dependencies: List[str], python_dependencies: List[str], additional_pip_flags: str = "", dev: bool = False) -> "DockerfileTemplate":
        self.configuration_params = {
            "extractor_path": extractor_path.format(),
            "module_name": extractor_path.module_name,
            "class_name": extractor_path.class_name,
            "system_dependencies": system_dependencies,
            "python_dependencies": python_dependencies,
            "additional_pip_flags": additional_pip_flags,
            "dev": dev
        }
        return self

    def _load_template(self):
        try:
            template_content = pkg_resources.read_text("dockerfiles", "Dockerfile.extractor")
            self.template = Template(template_content)
            return
        except Exception as e:
            # print an error then try loading from the file system
            print(f"Error loading template {self.template_path} from package: {e}")
            print("Loading from file system...")
        
        try:
            with open(self.template_path, "r") as f:
                self.template = Template(f.read())
        except Exception as e:
            raise Exception(f"Failed to load template: {e}")

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
        return f"{self.module_name}:{self.class_name}"

    def file_name(self) -> str:
        return f"{self.module_name}.py"

class ExtractorPackager:
    """
    Manages the packaging of an extractor into a Docker image, including Dockerfile generation and tarball creation.

    Attributes:
        config (ExtractorPackagerConfig): Configuration for the packager.
        docker_client (DockerClient): Client for interacting with Docker.
        logger (Logger): Logger for the packager.

    Methods:
        package: Orchestrates the packaging process, including Dockerfile generation, tarball creation, and Docker image building.
        _generate_dockerfile: Generates the Dockerfile content based on the configuration.
        _generate_compressed_tarball: Creates a compressed tarball containing the Dockerfile and any additional required files.
        _add_dev_dependencies: Adds development dependencies to the tarball if applicable.
    """

    def __init__(self, config: ExtractorPackagerConfig = None):
        # use default config if not provided
        self.config = config if config else ExtractorPackagerConfig()
        self.docker_client = DockerClient.from_env()
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Config: {self.config}")
    
        self.extractor_path = ExtractorPathWrapper(config.module_name, config.class_name).validate()

        # try to load dynamically
        try:
            # change "." into "/"
            file_name = config.module_name.replace(".", "/") + ".py"
            # join to the current working directory using path
            import pathlib
            cwd = pathlib.Path.cwd()
            module_path = cwd.joinpath(file_name)
            self.logger.info(f"Loading module from {module_path}")

            module = DynamicModuleLoader.load_module_from_path(config.module_name, module_path)
        except Exception as e:
            self.logger.error(f"Failed to load extractor description for {config.module_name}:{config.class_name} from {module_path}: {e}")
            raise
        # get the class from the module
        extractor_cls = getattr(module, config.class_name)

        # we don't need to initialize the class, just get the description
        self.extractor_description = {
            "name": extractor_cls.name,
            "version": extractor_cls.version,
            "system_dependencies": extractor_cls.system_dependencies,
            "python_dependencies": extractor_cls.python_dependencies,
        }
        assert self.extractor_description["name"] is not None, "Extractor.name must be defined"
        assert self.extractor_description["version"] is not None, "Extractor.version must be defined"
        self.logger.debug(self.extractor_description)
        
        # if dev, add the content of pyproject.toml - it's packaged in with resources
        if self.config.dev:    
            self.dev_files = {}
            if self.config.dev:
                self._collect_dev_files()

    def _collect_dev_files(self):
        # Initialize the structure for package files
        self.dev_files = {
            "README.md": self._read_file_text(Path(__file__).parent.parent / "README.md"),
            "pyproject.toml": self._read_file_text(Path(__file__).parent.parent / "pyproject.toml"),
            "indexify_extractor_sdk": {"__files__": []}
        }
        # Recursively add files from the package directory
        self._add_package_files(Path(__file__).parent, "indexify_extractor_sdk")

    def _read_file_text(self, path):
        # Utility function to read file text
        try:
            return path.read_text()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None

    def _add_package_files(self, package_path, package_name):
        # Recursively add files from a directory, maintaining structure
        # if the package name doesn't exist, create it
        if package_name not in self.dev_files:
            self.dev_files[package_name] = {"__files__": []}
        for item in package_path.iterdir():
            if item.is_dir():
                if item.name == "__pycache__":
                    continue  # Skip __pycache__
                # Initialize directory structure
                self.dev_files[package_name][item.name] = {"__files__": []}
                # Recurse into directory
                self._add_package_files(item, f"{package_name}.{item.name}")
            elif item.suffix in {".py", ".pyi"}:
                # Add Python files to the list
                rel_path = item.relative_to(package_path.parent)
                self.dev_files[package_name]["__files__"].append(str(item.name))

    def package(self):
        try:
            dockerfile_content = self._generate_dockerfile()
            self.logger.debug(dockerfile_content)
        except Exception as e:
            self.logger.error(f"Failed to generate Dockerfile: {e}")
            raise

        try:
            compressed_tar_stream = io.BytesIO(self._generate_compressed_tarball(dockerfile_content))
        except Exception as e:
            self.logger.error(f"Failed to generate compressed tarball: {e}")
            raise

        self.logger.info(f"Building image {self.extractor_description['name']}...")
        self.logger.info(f"Results aren't streamed, so this may take a while.")
        self._build_image(self.extractor_description["name"], compressed_tar_stream)

    
    def _build_image(self, tag: str, fileobj: io.BytesIO):
        docker_client = docker.from_env()
        # create a docker log handler that just prints to stdout
        # create a docker err handler that just prints to stderr
        docker_stdout_handler = logging.StreamHandler(sys.stdout)
        docker_stdout_handler.setLevel(logging.DEBUG)

        docker_stderr_handler = logging.StreamHandler(sys.stderr)
        docker_stderr_handler.setLevel(logging.ERROR)
        try:
            image, build_log = asyncio.run(
                async_docker_build(
                    docker_client,
                    tag=tag,
                    fileobj=fileobj,
                    custom_context=True,
                    encoding="gzip",
                    rm=True,
                    forcerm=True,
                    pull=True
                )
            )
            # )
            # image, build_log = docker_client.images.build(
            #     tag=tag,
            #     fileobj=fileobj,
            #     custom_context=True,
            #     encoding="gzip",
            #     rm=True,
            #     forcerm=True,
            #     pull=True
            # )

            # for chunk in build_log:
            #     if "stream" in chunk:
            #         docker_stdout_handler.emit(logging.LogRecord("docker", logging.INFO, "docker", 0, chunk["stream"].strip(), None, None))
            #     elif "error" in chunk:
            #         docker_stderr_handler.emit(logging.LogRecord("docker", logging.ERROR, "docker", 0, chunk["error"].strip(), None, None))
            
            self.logger.info(f"Successfully built image {image.tags[0]}")
        
        except docker_err.BuildError as e:
            self.logger.error(f"Failed to build image {self.extractor_description.get('name')}: {e}")
            # docker gives you the result_stream
            for chunk in e.build_log:
                if "stream" in chunk:
                    docker_stdout_handler.emit(logging.LogRecord("docker", logging.INFO, "docker", 0, chunk["stream"].strip(), None, None))
                elif "error" in chunk:
                    docker_stderr_handler.emit(logging.LogRecord("docker", logging.ERROR, "docker", 0, chunk["error"].strip(), None, None))
            raise

        except docker_err.APIError as e:
            self.logger.error(f"Docker API Error: {e}")
            raise

    def _generate_dockerfile(self) -> str:
        return DockerfileTemplate(self.config.dockerfile_template_path).configure(
            extractor_path=self.extractor_path,
            system_dependencies=" ".join(self.extractor_description["system_dependencies"]),
            python_dependencies=" ".join(self.extractor_description["python_dependencies"]),
            additional_pip_flags="" if self.config.gpu else "--extra-index-url https://download.pytorch.org/whl/cpu",
            dev=self.config.dev
        ).render()
    
    def _generate_compressed_tarball(self, dockerfile_content: str) -> bytes:
        """
        Generates a tarball containing the Dockerfile and any additional files needed for the extractor.
        """
        dockerfile_tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=dockerfile_tar_buffer, mode="w|", format=tarfile.GNU_FORMAT) as tar:
            dockerfile_info = tarfile.TarInfo("Dockerfile")
            dockerfile_info.mode = 0o755
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, fileobj=io.BytesIO(dockerfile_bytes))
            if self.config.dev:
                self._add_dev_dependencies(tar)
        
        dockerfile_tar_buffer.seek(0)
        compressed_data_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=compressed_data_buffer, mode="wb") as gz:
            gz.write(dockerfile_tar_buffer.getvalue())

        compressed_data_buffer.seek(0)
        return compressed_data_buffer.getvalue()

    # Function to recursively add files from a directory
    def _add_files_from_dir(self, base_path, base_tar_path, tar):
        for file_name, content in self.dev_files[base_path].items():
            if file_name == "__files__":
                for f in content:
                    file_path = Path(base_path) / f
                    file_info = tarfile.TarInfo(name=str(Path(base_tar_path) / f))
                    file_content = pkg_resources.read_text(base_path, str(f)).encode("utf-8")
                    file_info.size = len(file_content)
                    file_info.mode = 0o644  # Regular file permissions
                    tar.addfile(file_info, io.BytesIO(file_content))
            else:
                # It's a directory, add it and its contents
                dir_tar_path = str(Path(base_tar_path) / file_name)
                dir_info = tarfile.TarInfo(name=dir_tar_path)
                dir_info.type = tarfile.DIRTYPE
                dir_info.mode = 0o755  # Directory permissions
                tar.addfile(dir_info)
                self._add_files_from_dir(f"{base_path}.{file_name}", dir_tar_path, tar)

    def _add_dev_dependencies(self, tar: tarfile.TarFile):
        # Add the pyproject.toml file
        pyproject_content = self.dev_files["pyproject.toml"].encode("utf-8")
        pyproject_info = tarfile.TarInfo(name="pyproject.toml")
        pyproject_info.size = len(pyproject_content)
        pyproject_info.mode = 0o644  # Regular file permissions
        tar.addfile(pyproject_info, io.BytesIO(pyproject_content))

        # Add the README.md file
        readme_content = self.dev_files["README.md"].encode("utf-8")
        readme_info = tarfile.TarInfo(name="README.md")
        readme_info.size = len(readme_content)
        readme_info.mode = 0o644
        tar.addfile(readme_info, io.BytesIO(readme_content))
        
        self._add_files_from_dir("indexify_extractor_sdk", "indexify_extractor_sdk", tar)

        # print the directory structure of the tar
        tar.list(verbose=True)

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
    
import concurrent.futures

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
            if 'error' in chunk:
                streaming_err_handler.emit(logging.LogRecord("docker", logging.ERROR, "docker", 0, chunk["error"].strip(), None, None))
                raise docker.errors.BuildError(chunk['error'], build_logs)
            if 'stream' in chunk:
                streaming_log_handler.emit(logging.LogRecord("docker", logging.DEBUG, "docker", 0, chunk["stream"].strip(), None, None))
                match = re.search(
                    r'(^Successfully built |sha256:)([0-9a-f]+)$',
                    chunk['stream']
                )
                if match:
                    image_id = match.group(2)

        if image_id:
            image = await loop.run_in_executor(pool, lambda: client.images.get(image_id))
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
        for line in line.decode('utf-8').split("\r\n"):
            if line:
                yield json.loads(line)