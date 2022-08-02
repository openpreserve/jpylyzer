## Steps in preparing a jpylyzer release

### Before you start: Docker setup

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

### Before you start: tests setup

In order to run the automated tests you need to install a couple of Python modules:

1. pytest:
   ```
   pip install pytest
   ```

1. lxml:
   ```
   pip install lxml
   ```

---
TODO: the *TEST_DEPS* variable in [setup.py](./setup.py) also lists pre-commit, pylint and
pytest-coverage as test dependencies, but these are not used in any of the tests. It's not
entirely clear to me how *TEST_DEPS* works in the context of testing (since you typically
do this *before* installing any packages).
---

You also need the [jpylyzer-test-files](https://github.com/openpreserve/jpylyzer-test-files) corpus. 
The test script expects that the test files are located in a sibling directory to the jpylyzer 
source directory, e.g.:

```
        |-- jpylyzer/
home/ --|      
        |--jpylyzer-test-files/
```

Follow these steps:

1. In the terminal, go to the parent directory of the "jpylyzer" source directory. E.g., if the jpylyzer
   source directory is located in your home directory, first go to your home directory:
   ```
   cd ~
   ```
1. Then clone the repo:
   ```
   git clone https://github.com/openpreserve/jpylyzer-test-files.git
   ```

If you already have an (older) local copy of the test files, make sure it is up
to date:

1. Go to the test files directory:
   ```
   cd ~/jpylyzer-test-files
   ```
1. Update from the remote repo:
   ```
   git pull
   ```

### Jpylyzer release steps

1. Make necessary changes to the code.

1. Run the tests by issuing below command from the root of the jpylyzer repo:
   ```
   pytest
   ```

1. Update version number in *jpylyzer.py*.

1. In case of changes to command-line interface, update [jpylyzer.pod](debian/jpylyzer.pod) file in the *Debian* folder.

1. Create new entry in changelog using:
    ```
    dch -i
    ```
    then manually update the version number, and create list of changes. Also make sure the e-mail address is a valid e-mail address.

1. Update User Manual if necessary and export the Markdown file to HTML. See [instructions here](./doc).

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
    ./docker-package-pypi.sh
    ```
    You'll need a `.pypirc` in your home directory with suitable credentials to upload to the package via twine.
1. Build Windows binaries by running:
    ```
    ./docker-package-win.sh
    ```
1. Build Debian packages for Linux by running:
    ```
    ./docker-package.sh debian:stretch
    ```
1. Go to [*Releases*](https://github.com/openpreserve/jpylyzer/releases) and click on the *Draft a new release* button.

1. Click the *Choose a tag* button, and select the latest tag

1. Enter a release title, and a release decription

1. Upload Linux/Windows packages to the release by dragging them to the *Attach Binaries* field at the bottom.

1. Website: update *binVersion* in *_config.yml* (this updates the links to all packages to the correct version).

1. Website: write a short release note in the *_posts* directory.

1. Test website by running:
    ```
    jekyll serve
    ```
    or checkout [the following](https://github.com/Starefossen/docker-github-pages) to use a Docker container that reproduces authentic GitHub pages rendering.
1. Check website in browser at the following address:

    <http://127.0.0.1:4000/>

1. Commit changes to website and push to branch *gh-pages*.

1. Spread the word!
