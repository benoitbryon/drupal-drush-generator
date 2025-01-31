########################
Drupal's Drush generator
########################
Install drush in your project's isolated environment
####################################################

Drush is THE Drupal-shell tool: http://drush.ws

This project provides helpers to install Drush in a project. It targets
installation in buildout environments, but it can be used to install drush
elsewhere.

Abstract
========

This project may be useful for people who like isolating projects in
directories: all stuff that belongs to a project is stored in one directory.

As an example, you can use something similar to the following directory
structure:

* www/ => Drupal's root (index.php, .htaccess...)
* etc/ => configuration files, such as Apache's VirtualHost definitions
* var/log => logs

To go further in isolation, let's add a "bin/" folder for shortcuts to "local"
commands:

* bin/apache2
* bin/mysql
* bin/php
* ...

Here comes the Drupal's Drush generator. Its goal is to generate a "local"
drush wrapper.

Where "local drush wrapper" means:

* it is located somewhere in your project deployment. At bin/drush by default.
* it preconfigures some drush options, so that all commands affect the project.
  Basically, it customizes drush options like --root, --include and --uri.

Advantages:

* install drush, drush make (and maybe other drush extensions) with one
  command. If you are not convinced yet, a continuous integration server may
  be.
* versions are under control. Don't break all your websites with a drush
  upgrade.
* package what is necessary to your project. You can package your project with
  drush. You actually don't package drush itself, but configuration.
* be reproductible. Your team will share the environment, and so the production
  server.
* configure drush only once. You don't have to pass options such as --root,
  --include and so on each time you use drush. Simply use bin/drush.
* contribute to drush and its extensions. Using a development version of drush
  is sometimes useful. But you certainly don't want to use an unstable version
  on all your websites. So keep development version in an isolated environment.

This tool may be used in conjunction with the following:

* a deployment tool (currently, Python's buildout)
* a template system to create directory structures, such as bin/, var/log...
  Currently, none is supported. Python's paster templates could be used.
* a shell-path tool, as Python-virtualenv's bin/activate. In order to run
  "drush" directly, instead of "path/to/drush", as if drush was installed
  system-wide.

Requirements
============

Currently, this tool is written in Python. So Python is required to generate
the drush script.
If you want it in PHP, BASH or whatever, fork and pull request! You are
welcome!

In order to be able to actually use the drush command, you need PHP's command
line interface!

The generated drush script is SH.

The demo project: with buildout
===============================

The demo/ folder in this projects can be used as an example and as a sandbox.
::

  cd demo/
  python bootstrap.py --distribute
  bin/buildout

You got a bin/drush command. Let's try it (PHP is required):
::

  bin/drush --version
  bin/drush make --version --no

Configuration
=============

buildout
--------

See demo/buildout.cfg for a sample buildout configuration.

bin-directory
  Directory in which install drush wrapper.
  Defaults to buildout's bin-directory, which itself defaults to "bin".

interpreter
  Filename of the wrapper.
  Defaults to part name.

directory
  Base directory. Used to determine default values for some other options:

  * drupal-root
  
  Defaults to buildout's directory.

url
  Full URL of the Drush archive (.tar.gz).
  Defaults to http://ftp.drupal.org/files/projects/drush-7.x-4.5.tar.gz

commands
  List of URL of additional drush commands to install. One per line.
  Defaults to:
  ::

    http://ftp.drupal.org/files/projects/drush_make-6.x-2.3.tar.gz

php
  Absolute path to php command line interface (CLI) to use.
  Defaults to empty string, which means that drush itself will try to guess the
  best php executable to use.
  Common practice could be to use some local ${buildout:bin-directory}/php
  wrapper, which could use a custom .ini file.

drupal-root
  Path to drupal root. See drush's --root option.
  Defaults to "www" folder relative to "directory" option.
  If you provide a "relative" path (not starting with a '/'), then the path
  will be relative to the "directory" option. If you provide an absolute path
  (such as /var/www), the "directory" option will not be used.

drupal-uri
  URI of the drupal site to use (only needed in multisite environments).
  See drush's --uri or -l option.
  Defaults to empty string which means default site.

drush-directory
  Location of drush on the filesystem. Drush will be downloaded and installed
  there.
  Defaults to "lib/drush" folder relative to "directory" option.

commands-directory
  Location where to install drush commands.
  See drush's "--include" option.
  Defaults to "lib/drush_commands" folder relative to "directory" option.

Standalone
----------

See etc/drush.cfg.sample for a sample standalone configuration.

With virtualenv
===============

You can install this tool in a virtual environment:
::

  virtualenv --no-site-packages --distribute env
  source env/bin/activate
  python setup.py install
  ls -al env/bin/drush_generator.py

Standalone usage
================

You can generate a drush script outside a buildout environment:
::

  drupal/drush/generator/bin/drush_generator.py
