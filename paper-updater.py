#!/usr/bin/python3

import argparse
import re
import os
import json
import requests

base_download_url = "https://papermc.io/api/v1/paper/{}/latest/download"
base_version_url = "https://papermc.io/api/v1/paper/{}/latest"


class ServerBuild:
    def __init__(self, filepath, download_url, buildnum, size):
        self.filepath = filepath
        self.download_url = download_url
        self.buildnum = buildnum
        self.size = size


def cls():
    """Clears the terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def get_latest_server_build(paper_version):
    global base_download_url

    print('Checking for updates ...')

    download_url = base_download_url.format(paper_version)

    headers = requests.head(download_url)

    buildnum_pattern = r"^paper-{}-(.*).jar$".format(paper_version)

    build_data = json.loads(requests.get(base_version_url.format(paper_version)).text)
    latest_filename = 'paper-{}-{}.jar'.format(build_data['version'], build_data['build'])

    latest_download_size = int(headers.headers['Content-Length'])
    latest_buildnum = int(re.search(buildnum_pattern, latest_filename).group(1))

    # Find newest existing build jar in script dir
    current_buildnum = -1
    for filename in os.listdir(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))):
        if not re.match(buildnum_pattern, filename):
            # file is not a Paper jar file
            continue

        try:
            buildnum = int(re.search(buildnum_pattern, filename).group(1))
        except ValueError:
            continue

        if buildnum > current_buildnum:
            current_buildnum = buildnum

    if latest_buildnum <= current_buildnum:
        print('No updates are available (current build: {})'.format(current_buildnum))
        return None

    print('An update is available!')

    print('New Build:         {}'.format(latest_buildnum))
    if current_buildnum > -1:
        print('Installed Build:   {}'.format(current_buildnum))
    else:
        print('Installed Build:   No installed build was found')
    print('Download Size:     {}'.format(sizeof_fmt(latest_download_size)))

    return ServerBuild(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), latest_filename),
                       download_url, latest_buildnum, latest_download_size)


def download_update(server_build):
    print('Downloading update...')

    # Download and save jar
    jar = requests.get(server_build.download_url, allow_redirects=True)
    with open(server_build.filepath, 'wb') as file:
        file.write(jar.content)


def update_server_script(server_build, server_dir, start_script_name):
    jar_pattern = r"paper-(.*).jar"

    print('Updating server script...')

    start_script_path = os.path.join(server_dir, start_script_name)
    if not os.path.isfile(start_script_path):
        print("ERROR: Start script path '{}' cannot be found. Please update your server script manually.".format(
            start_script_path))
        return

    with open(start_script_path, 'r') as file:
        filedata = file.read()

    # replace Paper jar filename in script with the filename of the new jar
    filedata = re.sub(jar_pattern, os.path.basename(server_build.filepath), filedata)

    with open(start_script_path, 'w') as file:
        file.write(filedata)


def print_title(s):
    """Prints a nice looking title for menus, where 's' is a string consisting of the title text"""

    cls()
    print(s.upper())
    print("=" * len(s))
    print("")


def main():
    parser = argparse.ArgumentParser(description='Update your Paper server effortlessly.')

    parser.add_argument('--server-dir',
                        help='The full path to the directory where the server files reside.',
                        required=True)
    parser.add_argument('--minecraft-version',
                        help='The desired Minecraft version of the build to be downloaded.',
                        required=True)
    parser.add_argument('--start-script-name',
                        help='The name of the server start script that resides in the server dir, '
                             'including its file extension.',
                        default='start_noupdate.sh')

    args = parser.parse_args()

    server_build = get_latest_server_build(args.minecraft_version)
    if server_build is None:
        return

    download_update(server_build)
    update_server_script(server_build, args.server_dir, args.start_script_name)


main()
