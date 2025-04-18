import json
import os
import subprocess

from setuptools import Command
from setuptools.command.bdist_egg import bdist_egg
from setuptools.command.sdist import sdist as base_sdist

from wagtail import __semver__


class assets_mixin:
    def compile_assets(self):
        try:
            subprocess.check_call(["npm", "run", "build"])
        except (OSError, subprocess.CalledProcessError) as e:
            print("Error compiling assets: " + str(e))  # noqa: T201
            raise SystemExit(1)

    def publish_assets(self):
        try:
            subprocess.check_call(["npm", "publish", "client"])
        except (OSError, subprocess.CalledProcessError) as e:
            print("Error publishing front-end assets: " + str(e))  # noqa: T201
            raise SystemExit(1)

    def bump_client_version(self):
        """
        Writes the current Wagtail version number into package.json
        """
        path = os.path.join(".", "client", "package.json")

        try:
            with open(path, "r") as f:
                package = json.loads(f.read())
        except ValueError as e:
            print("Unable to read " + path + " " + e)  # noqa: T201
            raise SystemExit(1)

        package["version"] = __semver__

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(json.dumps(package, indent=2, ensure_ascii=False)))
        except OSError as e:
            print(  # noqa: T201
                "Error setting the version for front-end assets: " + str(e)
            )
            raise SystemExit(1)


class assets(Command, assets_mixin):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.bump_client_version()
        self.compile_assets()
        self.publish_assets()


class sdist(base_sdist, assets_mixin):
    def run(self):
        self.compile_assets()
        base_sdist.run(self)


class check_bdist_egg(bdist_egg):
    # If this file does not exist, warn the user to compile the assets
    sentinel_dir = "wagtail/wagtailadmin/static/"

    def run(self):
        bdist_egg.run(self)
        if not os.path.isdir(self.sentinel_dir):
            print(  # noqa: T201
                "\n".join(
                    [
                        "************************************************************",
                        "The front end assets for Wagtail are missing.",
                        "To generate the assets, please refer to the documentation in",
                        "docs/contributing/developing.md",
                        "************************************************************",
                    ]
                )
            )
