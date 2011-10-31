#!/usr/bin/env sh

# A drush wrapper for local project environment.
# Generated by %(generator)s on %(generation_time)s.

# Configuration
DRUSH_CMD="%(drush_cmd)s"
WWW_DIR="%(www_dir)s"
DRUPAL_URI="%(drupal_uri)s"
COMMAND_DIRS="%(command_dirs)s"
DRUSH_PHP="%(php)s"

# Drush wrapper
export DRUSH_PHP
$DRUSH_CMD --include=$COMMAND_DIRS --root=$WWW_DIR --uri=$DRUPAL_URI $@
