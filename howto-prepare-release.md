## Steps in preparing a jpylyzer release

### Before you start

Some steps in the jpylyzer release process use Docker. In order to run Docker as a non-root user, it is helpful to create a Unix *docker* group. Steps (see also the more detailed discussion [here](https://docs.docker.com/install/linux/linux-postinstall/)):

1. Create the *docker* group:
    ```
    sudo groupadd docker
    ```
1. Add the current user to the group:
    ```
    sudo usermod -aG docker $USER
    ```
1. Then log out and then log back in for the changes to take effect, or run the following command:
    ```
    newgrp docker
    ```
1. Verify that everything works by running the following test:
    ```
    docker run hello-world
    ```
### Jpylyzer release steps

1. Make necessary changes to the code.

1. Update version number in *jpylyzer.py*.

1. In case of changes to command-line interface, update [jpylyzer.pod](debian/jpylyzer.pod) file in the *Debian* folder.

1. Create new entry in changelog using:
    ```
    dch -i
    ```
    then manually update the version number, and create list of changes. Also make sure the e-mail address is a valid e-mail address.

1. Update  User Manual if necessary and export the Markdown file to HTML. See [instructions here](./doc).

1. Commit all changes and push to the *master* branch.

1. Add tag:
    ```
    git tag -a 1.x.x -m "release that fixes everything"
    ```
1. Push tags:
    ```
    git push --tags
    ```
1. Create and upload PyPi packages by running:
    ```
    sudo ./package-pypi.sh
    ```
1. Build Windows binaries by running:
    ```
    ./docker-package-win.sh debian:stretch
    ```
1. Build Debian packages for Linux by running:
    ```
    ./docker-package.sh debian:stretch
    ```
1. Go to [*Latest Release*](https://github.com/openpreserve/jpylyzer/releases/latest) and click on the *Edit* button.

1. Upload Linux/Windows packages to the release by dragging them to the *Attach Binaries* field at the bottom.

1. Website: update *binVersion* in *_config.yml* (this updates the links to all packages to the correct version).

1. Website: write a short release note in the *_posts* directory.

1. Test website by running:
    ```
    jekyll serve
    ```
1. Check website in browser at the following address:

    <http://127.0.0.1:4000/>

1. Commit changes to website and push to branch *gh-pages*.

1. Spread the word!
