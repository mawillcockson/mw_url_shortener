"""
Shows the version of Python3 included in Ubuntu 18.04

Relies on repology.org
"""
import json
from urllib.request import urlopen


def main() -> None:
    "Lists the versions of Python3 included in Ubuntu 18.04"
    with urlopen("https://repology.org/api/v1/project/python") as response:
        try:
            packages_text = response.read().decode("utf-8")
        finally:
            response.close()

    list_of_packages = json.loads(packages_text)
    ubuntu_18_04 = [
        package["version"]
        for package in list_of_packages
        if "ubuntu_18_04" in package["repo"].lower()
    ]
    print("\n".join(sorted(version for version in ubuntu_18_04 if version[0] == "3")))


if __name__ == "__main__":
    main()
