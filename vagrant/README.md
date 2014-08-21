# Building jpylyzer packages

This page describes how to build Debian packages for jpylyzer. By using virtual machines for the build process, we can easily create packages for a variety of platforms without the risk of accidentally messing up the host machine in the process. It also means that the platform of the host machine doesn't matter.

**Note:** the instructions below always result in a jpylyzer build that is based on the source code in the *remote* Github repo at <https://github.com/openplanets/jpylyzer/>, *not* on the local code!

##Step 1: install virtualisation software

* Install [VirtualBox](https://www.virtualbox.org/)
* Install VirtualBox Extension Pack (download link [here](https://www.virtualbox.org/))
* Install [Vagrant](https://www.vagrantup.com/)

## Step 2: go to Vagrant directory that corresponds with target platform

These are all under the directory `vagrant` in the jpylyzer repo. As an example we'll assume here that our target platform is Ubuntu 12.04 LTS (64 bit). This corresponds to the *precise64* Vagrant box (see [this link](https://vagrantcloud.com/discover/popular) for an overview of publicly available Vagrant boxes), so we'll enter:

    cd jpylyzer/vagrant/precise64

<!--

## Step 3: check if vagrant box already exists

Enter following command:

    vagrant box list

and look for the line:

    precise64 (virtualbox)

amongst the listed boxes. (On a linux box `vagrant box list | grep precise64` can be used to thin the output if necessary.) If the box is included in the output, go to step 5. If not, first go to step 4.

## Step 4: initialise vagrant box

Enter:

    vagrant box add precise64 http://files.vagrantup.com/precise64.box

This may take a couple of minutes to complete.

-->

## Step 3: start the virtual machine

Enter:

    vagrant up

If this is the first time you've run the command it will provision the virtual machine, that is install the appropriate software that is needed for building the package. This is achieved by running the bootstrap.sh shell script. This may take a while, so please be patient.
 

## Step 4: connect to the virtual machine and go to shared directory

Enter:

    vagrant ssh

Then while in the shell:

    cd /vagrant

## Step 5: build the package

Enter:

    ./buildjpylyzer.sh

If all goes well the package is now built; all files can be found in working directory (`jpylyzer/vagrant/precise64`).

## Step 6: disconnect and shut down virtual machine

    logout
    vagrant halt

All done!

