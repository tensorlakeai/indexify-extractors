import asyncio
import gzip
import io
from pathlib import Path
import tarfile
from docker import DockerClient, errors as docker_err
from .extractor_packager_utils import DockerfileTemplate, ExtractorPathWrapper, DynamicModuleLoader, async_docker_build
import docker
import logging
from jinja2 import Template
import importlib.resources as pkg_resources
import sys
import pathlib


class ExtractorPackager:
    """
    Manages the packaging of an extractor into a Docker image, including Dockerfile generation and tarball creation.

    Attributes:
        config: Configuration for the packager.
        docker_client (DockerClient): Client for interacting with Docker.
        logger (Logger): Logger for the packager.

    Methods:
        package: Orchestrates the packaging process, including Dockerfile generation, tarball creation, and Docker image building.
        _generate_dockerfile: Generates the Dockerfile content based on the configuration.
        _generate_compressed_tarball: Creates a compressed tarball containing the Dockerfile and any additional required files.
        _add_dev_dependencies: Adds development dependencies to the tarball if applicable.
    """

    def __init__(
        self,
        module_name: str,
        class_name: str,
        dockerfile_template_path: str = "../dockerfiles/Dockerfile.extractor",
        verbose: bool = False,
        dev: bool = False,
        gpu: bool = False,
    ):
        self.docker_client = DockerClient.from_env()
        self.logger = logging.getLogger(__name__)
        self.config = {
            "module_name": module_name,
            "class_name": class_name,
            "dockerfile_template_path": dockerfile_template_path,
            "verbose": verbose,
            "dev": dev,
            "gpu": gpu,
        }
        self.logger.debug(f"Config: {self.config}")

        self.extractor_path = ExtractorPathWrapper(
            self.config["module_name"], self.config["class_name"]
        ).validate()

        # try to load dynamically
        try:
            # change "." into "/"
            file_name = self.config["module_name"].replace(".", "/") + ".py"
            # join to the current working directory using path
            cwd = pathlib.Path.cwd()
            module_path = cwd.joinpath(file_name)
            self.logger.info(f"Loading module from {module_path}")

            module = DynamicModuleLoader.load_module_from_path(
                self.config["module_name"], module_path
            )
            self.extractor_module = module
        except Exception as e:
            self.logger.error(
                f"Failed to load extractor description for {self.extractor_path.format()} from {module_path}: {e}"
            )
            raise
        # get the class from the module
        extractor_cls = getattr(module, self.config["class_name"])

        # we don't need to initialize the class, just get the description
        self.extractor_description = {
            "name": extractor_cls.name,
            "version": extractor_cls.version,
            "system_dependencies": extractor_cls.system_dependencies,
            "python_dependencies": extractor_cls.python_dependencies,
        }
        assert (
            self.extractor_description["name"] is not None
        ), "Extractor.name must be defined"
        assert (
            self.extractor_description["version"] is not None
        ), "Extractor.version must be defined"

        # if dev, add the content of pyproject.toml - it's packaged in with resources
        if self.config.get("dev", False):
            self.dev_files = {}
            self._collect_dev_files()

    def _collect_dev_files(self):
        # Initialize the structure for package files
        self.dev_files = {
            "README.md": self._read_file_text(
                Path(__file__).parent.parent / "README.md"
            ),
            "pyproject.toml": self._read_file_text(
                Path(__file__).parent.parent / "pyproject.toml"
            ),
            "indexify_extractor_sdk": {"__files__": []},
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
            compressed_tar_stream = io.BytesIO(
                self._generate_compressed_tarball(dockerfile_content)
            )
        except Exception as e:
            self.logger.error(f"Failed to generate compressed tarball: {e}")
            raise

        self.logger.info(f"Building image {self.extractor_description['name']}...")
        self._build_image(self.extractor_description["name"], compressed_tar_stream)

    def _build_image(self, tag: str, fileobj: io.BytesIO):
        docker_client = docker.from_env()
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
                    pull=True,
                )
            )
            self.logger.info(f"Successfully built image {image.tags[0]}")
        except docker_err.BuildError as e:
            self.logger.error(
                f"Failed to build image {self.extractor_description.get('name')}: {e}"
            )
            raise
        except docker_err.APIError as e:
            self.logger.error(f"Docker API Error: {e}")
            raise

    def _generate_dockerfile(self) -> str:
        return (
            DockerfileTemplate(self.config["dockerfile_template_path"])
            .configure(
                extractor_path=self.extractor_path,
                system_dependencies=" ".join(
                    self.extractor_description["system_dependencies"]
                ),
                python_dependencies=" ".join(
                    self.extractor_description["python_dependencies"]
                ),
                additional_pip_flags=(
                    ""
                    if self.config["gpu"]
                    else "--extra-index-url https://download.pytorch.org/whl/cpu"
                ),
                dev=self.config.get("dev", False),
            )
            .render()
        )

    def _generate_compressed_tarball(self, dockerfile_content: str) -> bytes:
        """
        Generates a tarball containing the Dockerfile and any additional files needed for the extractor.
        """
        dockerfile_tar_buffer = io.BytesIO()
        with tarfile.open(
            fileobj=dockerfile_tar_buffer, mode="w|", format=tarfile.GNU_FORMAT
        ) as tar:
            dockerfile_info = tarfile.TarInfo("Dockerfile")
            dockerfile_info.mode = 0o755
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, fileobj=io.BytesIO(dockerfile_bytes))

            # add the module that is at self.extractor_module to the tar using the module name
            # the path should be the project root in <module_name>.py
            module_info = tarfile.TarInfo(self.extractor_path.file_name())
            module_bytes = pkg_resources.read_text(
                self.extractor_path.module_name, self.extractor_path.file_name()
            ).encode("utf-8")
            module_info.size = len(module_bytes)
            module_info.mode = 0o644
            tar.addfile(module_info, io.BytesIO(module_bytes))

            if self.config.get("dev", False):
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
                    file_content = pkg_resources.read_text(base_path, str(f)).encode(
                        "utf-8"
                    )
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

        self._add_files_from_dir(
            "indexify_extractor_sdk", "indexify_extractor_sdk", tar
        )

        # print the directory structure of the tar
        tar.list(verbose=True)

