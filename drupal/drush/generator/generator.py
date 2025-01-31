"""Helper to download and install Drush in a project's environment."""

import ConfigParser
from datetime import datetime
import logging
from optparse import OptionParser
import os
import re
import subprocess
import sys


class DrushInstaller(object):
    logger_id = 'drupal-drush-generator'
    
    def __init__(self):
        # Generator name
        self.generator_id = 'DrushInstaller class'
        # Logging
        self.logger = logging.getLogger(self.logger_id)
        # Created paths
        self.created_paths = []
        # Defaults (conventions)
        self.base_dir = os.getcwd()
        lib_dir = 'lib'
        self.drush_url = 'http://ftp.drupal.org/files/projects/drush-7.x-4.5.tar.gz'
        self.drush_dir = os.path.join(lib_dir, 'drush')
        self.drush_local_commands = os.path.join(lib_dir, 'drush_commands')
        self.drush_command_dirs = [self.drush_local_commands]
        self.drush_commands = [
            'http://ftp.drupal.org/files/projects/drush_make-6.x-2.3.tar.gz',
        ]
        self.drush_wrapper = os.path.join('bin', 'drush')
        self.tmp_dir = os.path.join('var', 'tmp')
        self.www_dir = 'www'
        self.php = ''  # By default, provide an empty value to drush so that
                       # drush searches for the adequate PHP by itself.
        self.drupal_uri = ''
    
    def __call__(self):
        """Main command callback."""
        self.configure()
        if self.is_drush_installed():
            self.logger.info('Drush is already installed. Skipping installation')
        else:
            self.logger.info("Installing drush in %s", self.drush_dir)
            self.install_drush()
            self.logger.info("Done")
        self.install_drush_commands()
        self.generate_drush_wrapper()

    def configure(self):
        """Read configuration from arguments and/or configuration files"""
        if not self.base_dir:
            raise Exception('undefined base dir')
        
        # Resolve paths
        if not self.is_absolute_path(self.base_dir):
            self.base_dir = os.path.abspath(self.base_dir)
        for key in ('drush_dir', 'drush_wrapper', 'drush_local_commands',
                    'tmp_dir', 'www_dir'):
            setattr(self, key, self.configure_path(getattr(self, key)))

        # Parse drush_command_dirs
        if isinstance(self.drush_command_dirs, basestring):
            self.drush_command_dirs = re.sub(r'\s+', ' ', self.drush_command_dirs).strip(' ')
            self.drush_command_dirs = self.drush_command_dirs.split(' ')
        # Resolve paths
        tmp = []
        for path in self.drush_command_dirs:
            path = self.configure_path(path)
            if not path in tmp:
                tmp.append(path)
        self.drush_command_dirs = tmp

        # Parse drush_commands
        if isinstance(self.drush_commands, basestring):
            self.drush_commands = re.sub(r'\s+', ' ', self.drush_commands).strip(' ')
            self.drush_commands = self.drush_commands.split(' ')
            # TODO: parse drush_commands URLs: they can be URLs or paths

    def is_absolute_path(self, path):
        """Returns True if the given path is absolute, False if relative."""
        return path.startswith(os.path.sep)
    
    def configure_path(self, path):
        if self.is_absolute_path(path):
            parsed_path = path
        else:
            parsed_path = os.path.join(self.base_dir, path)
        parsed_path = os.path.normpath(parsed_path)
        return parsed_path
    
    def mkdir(self, path):
        """Create a directory."""
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise Exception('%s is not a directory' % path)

    def is_drush_installed(self):
        """Returns True if drush has already been installed."""
        return os.path.exists(self.drush_dir)
    
    def install_drush(self):
        """Download and install drush."""
        self.mkdir(self.tmp_dir)
        self.mkdir(self.drush_dir)
        self.created_paths.append(self.drush_dir)
        tmp_archive = os.path.join(self.tmp_dir, 'drush.tar.gz')
        subprocess.call(["wget", self.drush_url, "-O", tmp_archive])
        subprocess.call(['tar',
                         '-xzf',
                         tmp_archive,
                         '-C',
                         os.path.dirname(self.drush_dir)])
        os.remove(tmp_archive)

    def install_drush_commands(self):
        self.mkdir(self.drush_local_commands)
        self.created_paths.append(self.drush_local_commands)
        for url in self.drush_commands:
            self.install_drush_command(url)
    
    def install_drush_command(self, url):
        """Download and install a drush command."""
        self.logger.info("Installing %s", url)
        self.mkdir(self.tmp_dir)
        tmp_archive = os.path.join(self.tmp_dir, 'drush_command.tar.gz')
        subprocess.call(["wget",
                         url,
                         "-O",
                         tmp_archive])
        subprocess.call(['tar',
                         '-xzf',
                         tmp_archive,
                         '-C',
                         self.drush_local_commands])
        os.remove(tmp_archive)
        self.logger.info('Done')
    
    def generate_drush_wrapper(self):
        """Generate drush wrapper."""
        self.logger.info('Generating bin/drush command')
        template_filename = os.path.join(
            os.path.normpath(os.path.abspath(os.path.dirname(__file__))),
            'templates',
            'drush_wrapper.sh'
            )
        with open(template_filename) as f:
            script_content = f.read()
        script_content = script_content % {
            'drush_cmd': os.path.join(self.drush_dir, 'drush'),
            'www_dir': self.www_dir,
            'command_dirs': ':'.join(self.drush_command_dirs),  # WARNING: the ":" separator may fail on Windows
            'php': self.php,
            'drupal_uri': self.drupal_uri,
            'generator': self.generator_id,
            'generation_time': datetime.now().isoformat(),
        }

        with open(self.drush_wrapper, 'w') as f:
            f.write(script_content)
        os.chmod(self.drush_wrapper, 0755)
        self.logger.info('Done')
        self.created_paths.append(self.drush_wrapper)


class DrushInstallerCommand(object):
    def __init__(self, argv=[]):
        self.argv = argv
        self.config_file = None
    
    def __call__(self):
        """Main command callback."""
        self.installer = DrushInstaller()
        self.configure()
        self.installer()
                
        
    def configure(self):
        """Read configuration from arguments and/or configuration files"""
        parser = OptionParser()
        parser.add_option("-c", "--config-file", action="store",
                          type='string', dest="config_file",
                          help="Path to configuration file.")
        parser.add_option("--base-dir", action="store",
                          type='string', dest="base_dir",
                          help="Base directory for project environment.")
        
        (options, args) = parser.parse_args(self.argv)

        # Read configuration file
        config_file = options.config_file or self.config_file
        if config_file and os.path.exists(config_file):
            config = ConfigParser.ConfigParser()
            config_section = 'drush'
            with open(config_file) as fp:
                config.readfp(fp)
            if not config.has_section(config_section):
                raise Exception('Config file has no [%s] section' % config_section)
        else:
            if options.config_file:
                raise Exception('Unable to open configuration file %s' % config_file)
            config = None
        
        # base_dir
        self.installer.base_dir = options.base_dir or \
                        (config and config.has_option(config_section, 'base-dir') and config.get(config_section, 'base-dir')) or \
                        self.installer.base_dir
        
        if not self.installer.base_dir:
            raise Exception('undefined base dir. Use the --base-dir option.')
        
        # Other options
        for key in ('drush_dir', 'drush_url', 'drush_wrapper',
                    'drush_local_commands', 'drush_command_dirs',
                    'drush_commands', 'tmp_dir', 'www_dir'):
            setattr(self.installer, key, (config and config.has_option(config_section, key) and config.get(config_section, key)) or \
                    getattr(self, key))
