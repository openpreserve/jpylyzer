# How to build the Windows binaries


## Prerequisites

The windows packaging is now Docker based. In order to run Docker as a non-root user, it is helpful to create a Unix *docker* group. Steps (see also the more detailed discussion [here](https://docs.docker.com/install/linux/linux-postinstall/)):

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
## Building the binaries

In your console window, go to the root of the jpylyzer directory. Then run:
    ```
    ./docker-package-win.sh
    ```
The (zipped) binaries can be found in the `dist` directory.
