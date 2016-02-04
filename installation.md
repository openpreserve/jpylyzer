---
layout: page
title: Installation
---
{% include JB/setup %}

## Installation
The easiest option is to use the binary builds that exist for both *Windows*- and *Linux*-based systems. These are completely stand-alone, without any dependencies on other software (i.e. you don&#8217;t need *Python* to use them). 

## Windows
Download the Windows binaries using the link in the right-hand bar. Then extract the contents of the *ZIP* file to any directory you like. You should now be able to run *jpylyzer* from your command prompt. For example, assuming that you installed the contents  of the *ZIP* file to the directory *C:\jpylyzer\\*, type or paste the following line into a command prompt window:

{% highlight console %}
C:\jpylyzer\jpylyzer
{% endhighlight %}

This should give you the *jpylyzer* helper message.

## Running jpylyzer without typing the full path
Optionally, you may also want to add the full path of the jpylyzer installation directory to the Windows *Path* environment variable. Doing so allows you to run jpylyzer from any directory on your PC, without having to type the full path. In Windows 7 you can do this by selecting *settings* from the *Start* menu; then go to *control panel*/*system* and click on  *advanced system settings*. Then click on the *environment variables* button. Finally, locate the *Path* variable in the *system variables* window, click on *Edit* and add the full *jpylyzer* path (this requires local Administrator privileges). The settings take effect once you open a new command prompt.

## Linux
Debian packages of jpylyzer exist for *AMD6* and *i386* Linux architectures. To install, simply download the Debian package using the link in the right-hand bar, double-click on it and select *Install Package*. Alternatively you can also do this in the command terminal by typing:

{% highlight console %}
sudo dpkg -i jpylyzer_1.10.1_amd64.deb
{% endhighlight %}

In both cases you need to have superuser privileges.

## Python (any platform)
Instead of using the binary builds, you can also download *jpylyzer*&#8217;s source code to run *jpylyzer* as a [*Python*](http://www.python.org/) script. This should work on any platform, but note that this requires either *Python* 2.7 (earlier versions won&#8217;t work), or *Python* 3.2 or later (3.0 and 3.1 won&#8217;t work either!).



