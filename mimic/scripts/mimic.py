#!usr/bin/env python

"""
The main module.
"""

try:
    import pymel.core as pm

    MAYA_IS_RUNNING = True
except ImportError:  # Maya is not running
    pm = None
    MAYA_IS_RUNNING = False
import os

import general_utils
import mimic_config
import mimic_ui

reload(general_utils)
reload(mimic_config)
reload(mimic_ui)


def load_mimic_plugins(plugin_file_names):
    """
    Loads required python plugins into Maya from a directory.
    These are Dependency Graph and Command plugins that should be loaded into
    Maya's plugin manager
    :param plugin_file_names: List of required plug-ins 
    :return:
    """
    # Check to see if each plug-in is loaded
    for script in plugin_file_names:
        # If the plug-in is not loaded:
        if not pm.pluginInfo(script, query=True, loaded=True):
            try:
                # Try loading it (and turn on autoload)
                pm.loadPlugin(script)
                pm.pluginInfo(script, autoload=True)
                print '{} Plug-in loaded'.format(script)
                continue
            except Exception as e:
                pm.warning('Could not load plugin {}: {}'.format(script, e))
        # If it's already loaded:
        print '{} Plug-in already loaded'.format(script)


def confirm_requirements_exist():
    """
    Confirm that the directories required for Mimic to run do, in fact, exist.
    Confirm that the rigs directory contains something. Confirm that files, such
    as LICENSE and mimic.mod, exist.
    :return:
    """
    # Check required directories
    requirements = [
        'rigs',
        'plug-ins',
        'shelves',
        'scripts',
        'LICENSE.md',
        'mimic.mod',
    ]
    dir_mimic = general_utils.get_mimic_dir()
    for requirement in requirements:
        if '.' in requirement:  # not a directory (.md, .mod)
            parent = os.path.abspath(os.path.join(dir_mimic, os.pardir))
            path = '{}/{}'.format(parent, requirement)
        else:
            path = '{}/{}'.format(dir_mimic, requirement)
        try:  # Check that directories all exist; if not, raise exception!
            assert os.path.exists(path)
        except AssertionError:
            if 'LICENSE.md' in path:  # Missing license!
                # Don't block Mimic from running
                print "Warning: We noticed that you don't have a copy of our LICENSE! " \
                      "Download the latest release from our GitHub repository!"
            else:
                # Full stop, Mimic won't work correctly!
                raise Exception("Exception: We noticed that you're missing a requirement! "
                                "Download the latest release from our GitHub repository! "
                                + requirement)
        try:  # Check that the rigs directory has robots; if not, print warning!
            if requirement == 'rigs':
                items = os.listdir(path)
                subdir_paths = [os.path.join(path, item) for item in items]
                assert any(os.path.isdir(subdir_path) for subdir_path in subdir_paths)
                for subdir_path in subdir_paths:
                    try:
                        print subdir_path
                        items = os.listdir(subdir_path)
                        print items
                        assert any('.ma' in item for item in items)
                        continue
                    except OSError:  # not a directory (.md)
                        pass
        except AssertionError:
            # Don't block Mimic from running
            print "Warning: We noticed that you don't have any robot rigs! " \
                  "Download the latest rigs from out GitHub repository " \
                  "and add them to mimic/rigs!"


def run():
    """
    Check that mimic is all there, loaded, and then create the Mimic UI.
    :return:
    """
    # Perform preliminary checks
    confirm_requirements_exist()
    load_mimic_plugins(mimic_config.REQUIRED_PLUGINS)
    # Build the UI itself
    mimic_ui.build_mimic_ui()
