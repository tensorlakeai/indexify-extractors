import asyncio
import gzip
import io
from pathlib import Path
import tarfile
from docker import DockerClient, errors as docker_err
from .packager_utils import (
    DockerfileTemplate,
    ExtractorPathWrapper,
    DynamicModuleLoader,
    async_docker_build,
)
import docker
import logging
import importlib.resources as pkg_resources
import pathlib
from .base_extractor import EXTRACTORS_PATH


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
        verbose: bool = False,
        dev: bool = False,
        gpu: bool = False,
        tofile: bool = False,
    ):
        self.logger = logging.getLogger(__name__)
        self.config = {
            "module_name": module_name,
            "class_name": class_name,
            "verbose": verbose,
            "dev": dev,
            "gpu": gpu,
            "tofile": tofile,
        }
        self.logger.debug(f"Config: {self.config}")

        self.docker_client = DockerClient.from_env()

        self.extractor_path = ExtractorPathWrapper(
            self.config["module_name"], self.config["class_name"]
        ).validate()

        self.extractor_module = self._load_extractor_module()
        self.extractor_description = self._extract_validate_extractor_description()

        if self.config.get("dev", False):
            self.dev_files = self._collect_dev_files()

    def _load_extractor_module(self):
        """
        Dynamically loads the extractor module based on configuration.
        """
        file_name = self.config["module_name"].replace(".", "/") + ".py"
        cwd = pathlib.Path.cwd()
        module_path = cwd.joinpath(file_name)
        self.logger.info(f"Loading module from {module_path}")

        try:
            module = DynamicModuleLoader.load_module_from_path(
                self.config["module_name"], module_path
            )
            return module
        except Exception as e:
            self.logger.error(
                f"Failed to load extractor description for {self.extractor_path.format()} from {module_path}: {e}"
            )
            raise

    def _collect_dev_files(self) -> dict:
        # Initialize the structure for package files
        dev_files = {
            "README.md": self._read_file_text(
                Path(__file__).parent.parent / "README.md"
            ),
            "pyproject.toml": self._read_file_text(
                Path(__file__).parent.parent / "pyproject.toml"
            ),
            "indexify_extractor_sdk": {"__files__": []},
        }
        # Recursively add files from the package directory
        self._add_package_files(
            Path(__file__).parent, "indexify_extractor_sdk", dev_files
        )
        return dev_files

    def _read_file_text(self, path):
        # Utility function to read file text
        try:
            return path.read_text()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None

    def _add_package_files(self, package_path, package_name, acc: dict):
        # Recursively add files from a directory, maintaining structure
        # if the package name doesn't exist, create it
        if package_name not in acc:
            acc[package_name] = {"__files__": []}
        for item in package_path.iterdir():
            if item.is_dir():
                if item.name == "__pycache__":
                    continue  # Skip __pycache__
                # Initialize directory structure
                acc[package_name][item.name] = {"__files__": []}
                # Recurse into directory
                self._add_package_files(item, f"{package_name}.{item.name}", acc)
            elif item.suffix in {".py", ".pyi"}:
                # Add Python files to the list
                acc[package_name]["__files__"].append(str(item.name))

    def package(self):
        try:
            dockerfile_content = self._generate_dockerfile()
            self.logger.debug(dockerfile_content)
        except Exception as e:
            self.logger.error(f"Failed to generate Dockerfile: {e}")
            raise
        if self.config.get("tofile"):
            dockerfile_name = self.config.get('tofile')
            print(f"Saving dockerfile to {dockerfile_name}")
            f = open(dockerfile_name, 'w')
            f.write(dockerfile_content)
            f.close()
            return
        try:
            compressed_tar_stream = io.BytesIO(
                self._generate_compressed_tarball(dockerfile_content)
            )
        except Exception as e:
            self.logger.error(f"Failed to generate compressed tarball: {e}")
            raise

        self.logger.info(f"Building image {self.extractor_description['name']}...")
        try:
            self._build_image(self.extractor_description["name"], compressed_tar_stream)
        except Exception as e:
            self.logger.error(f"Failed to build image: {e}")

    def _extract_validate_extractor_description(self) -> dict:
        extractor_cls = getattr(self.extractor_module, self.config["class_name"])

        # we don't need to initialize the class, just get the description
        extractor_description = {
            "name": extractor_cls.name,
            "version": extractor_cls.version,
            "system_dependencies": extractor_cls.system_dependencies,
            "python_dependencies": self._get_python_dependencies(),
        }

        assert (
            extractor_description["name"] is not None
        ), "Extractor.name must be defined"
        assert (
            extractor_description["version"] is not None
        ), "Extractor.version must be defined"

        return extractor_description

    def _get_python_dependencies(self):
        # get module path
        module_path = pathlib.Path.cwd() / (
            self.config["module_name"].replace(".", "/") + ".py"
        )

        # check for requirements.txt
        requirements_path = module_path.joinpath(module_path.parent, "requirements.txt")
        if requirements_path.exists():
            with open(requirements_path, "r") as f:
                requirements = f.read()

            return [entry for entry in requirements.split("\n") if entry]

        # check for class dependencies
        extractor_cls = getattr(self.extractor_module, self.config["class_name"])
        if extractor_cls.python_dependencies:
            return extractor_cls.python_dependencies

        # no dependencies found
        return []

    def _build_image(self, tag: str, fileobj: io.BytesIO):
        try:
            image, _ = asyncio.run(
                async_docker_build(
                    self.docker_client,
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
        workdir = EXTRACTORS_PATH.split("/")[-1]
        return (
            DockerfileTemplate()
            .configure(
                workdir=workdir,
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

            parent_dir = pathlib.Path(self.extractor_path.file_name()).parent

            add_directory_to_tar(tar, parent_dir)

            if self.config.get("dev", False):
                self._add_dev_dependencies(tar)

            # if self.config.verbose, print the directory structure of the tar
            # using tar.list(verbose=True)
            if self.config["verbose"]:
                self.logger.debug("Tarball contents:")
                tar.list(verbose=True)

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


def add_directory_to_tar(tar_file: tarfile.TarFile, directory_path):
    import os

    """
    Add a directory to a tar file with path names relative to the parent directory.

    Parameters:
        directory_path (str): Path to the directory to be added to the tar file.
        tar_file_path (str): Path to the tar file.

    Returns:
        None
    """
    # Iterate over all files and subdirectories in the given directory
    print(f"Adding {directory_path} to tar file")
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, os.path.dirname(directory_path))
            print(f"Adding {file_path} to tar file with relative path {relative_path}")
            tar_file.add(file_path, arcname=relative_path)
