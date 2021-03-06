#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry file parser."""

import unittest

from plaso.parsers import winreg
# Register all plugins.
from plaso.parsers import winreg_plugins  # pylint: disable=unused-import

from tests import test_lib as shared_test_lib
from tests.parsers import test_lib


class WinRegistryParserTest(test_lib.ParserTestCase):
  """Tests for the Windows Registry file parser."""

  # pylint: disable=protected-access

  def _GetParserChains(self, event_objects):
    """Return a dict with a plugin count given a list of event objects."""
    parser_chains = {}
    for event_object in event_objects:
      parser_chain = getattr(event_object, u'parser', None)
      if not parser_chain:
        continue

      if parser_chain in parser_chains:
        parser_chains[parser_chain] += 1
      else:
        parser_chains[parser_chain] = 1

    return parser_chains

  def _PluginNameToParserChain(self, plugin_name):
    """Generate the correct parser chain for a given plugin."""
    return u'winreg/{0:s}'.format(plugin_name)

  def testEnablePlugins(self):
    """Tests the EnablePlugins function."""
    parser_object = winreg.WinRegistryParser()
    parser_object.EnablePlugins([u'appcompatcache'])

    self.assertIsNotNone(parser_object)
    self.assertIsNotNone(parser_object._default_plugin)
    self.assertNotEqual(parser_object._plugin_objects, [])
    self.assertEqual(len(parser_object._plugin_objects), 1)

  @shared_test_lib.skipUnlessHasTestFile([u'NTUSER.DAT'])
  def testParseNTUserDat(self):
    """Tests the Parse function on a NTUSER.DAT file."""
    parser_object = winreg.WinRegistryParser()
    storage_writer = self._ParseFile([u'NTUSER.DAT'], parser_object)

    parser_chains = self._GetParserChains(storage_writer.events)

    expected_parser_chain = self._PluginNameToParserChain(u'userassist')
    self.assertTrue(expected_parser_chain in parser_chains)

    self.assertEqual(parser_chains[expected_parser_chain], 14)

  @shared_test_lib.skipUnlessHasTestFile([u'ntuser.dat.LOG'])
  def testParseNoRootKey(self):
    """Test the parse function on a Registry file with no root key."""
    parser_object = winreg.WinRegistryParser()
    storage_writer = self._ParseFile([u'ntuser.dat.LOG'], parser_object)

    self.assertEqual(len(storage_writer.events), 0)

  @shared_test_lib.skipUnlessHasTestFile([u'SYSTEM'])
  def testParseSystem(self):
    """Tests the Parse function on a SYSTEM file."""
    parser_object = winreg.WinRegistryParser()
    storage_writer = self._ParseFile([u'SYSTEM'], parser_object)

    parser_chains = self._GetParserChains(storage_writer.events)

    # Check the existence of few known plugins, see if they
    # are being properly picked up and are parsed.
    plugin_names = [
        u'windows_usbstor_devices', u'windows_boot_execute',
        u'windows_services']
    for plugin in plugin_names:
      expected_parser_chain = self._PluginNameToParserChain(plugin)
      self.assertTrue(
          expected_parser_chain in parser_chains,
          u'Chain {0:s} not found in events.'.format(expected_parser_chain))

    # Check that the number of events produced by each plugin are correct.
    parser_chain = self._PluginNameToParserChain(u'windows_usbstor_devices')
    self.assertEqual(parser_chains.get(parser_chain, 0), 10)

    parser_chain = self._PluginNameToParserChain(u'windows_boot_execute')
    self.assertEqual(parser_chains.get(parser_chain, 0), 4)

    parser_chain = self._PluginNameToParserChain(u'windows_services')
    self.assertEqual(parser_chains.get(parser_chain, 0), 831)


if __name__ == '__main__':
  unittest.main()
