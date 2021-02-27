# Paper-Updater Beta
Update your Minecraft Paper server effortlessly. **This script has not been tested enough to be considered stable, use it at your own risk.**

## Prerequisites
### Operating System
This script is designed for Linux and has not been tested on, nor designed for, other operating systems.

### System packages
**Debian/Ubuntu: Run <code>sudo apt update</code> once then install with <code>sudo apt install \<package\></code>**
- python3
- python3-pip
- git

### Python packages
**Install with <code>pip3 install \<package\></code> while signed in to the user that is running your Minecraft server**
- requests

## Downloading
1. Sign in to a user with sudo privileges.
2. Install the required system packages according to the instructions above.
3. Switch to the user owning the Minecraft server(s) by using <code>sudo su - \<user\></code>
4. Install the required Python packages according to the instructions above.
5. Navigate to a parent directory of your Minecraft server(s), preferably your home directory (<code>cd ~</code>)
6. Run <code>git clone https://github.com/steel9/Paper-Updater.git</code>

## Usage
- To update your server, sign in to the user owning the Minecraft server, <code>cd</code> to the script directory and run <code>./paper-updater.py --server-dir \<your-server-dir\> --minecraft-version \<desired-minecraft-server-version\></code>, where **server-dir** is the directory containing your server JAR file, scripts, whitelist, worlds etc, and **minecraft-version** the Minecraft version you want your server to use. The script will download the latest build available for the specified Minecraft version.
- Update this updater script by running <code>git pull</code> after <code>cd</code>:ing to the script directory. This is useful if the script for some reason stops working. Keep in mind that the script syntax/arguments _might_ change after an update, so make sure you verify that everything is working afterwards.
- You may call the updater from within your server start script for automatic server updates (as long as the server also automatically restarts). See **Usage in scripts** below.
- For more information about syntax and arguments, run <code>./paper-updater.py -h</code>

## Usage in scripts
We recommend that you use 2 scripts for your Paper server - one that runs Paper-Updater and another one that starts Paper and is called by the first script. Two scripts are recommended as Paper-Updater will modify the server starting script to point to the new Paper JAR file. **Example:**

### start.sh
<code>#!/bin/sh</code>\
<code>python3 \~/Paper-Updater/paper-updater.py --server-dir "~/servers/My-Vanilla-Server" --minecraft-version 1.16.5</code>\
<code>sh ./start_noupdate.sh</code>

### start_noupdate.sh
<code>#!/bin/sh</code>\
<code>java -Xmx4G -jar paper-1.16.5-123.jar</code>

If you name **start_noupdate.sh** something else, you need to specify the argument <code>--start-script-name \<your-start-script-name\></code> when calling Paper-Updater (including its file extension).
