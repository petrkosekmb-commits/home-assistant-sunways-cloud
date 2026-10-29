"""Execute production function bodies with offline HA boundary doubles."""
import ast
import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock

ROOT = Path(__file__).resolve().parents[1] / 'custom_components/sunways'

def function(file, name, context, owner=None):
    tree = ast.parse((ROOT / file).read_text(encoding='utf-8'))
    nodes = tree.body if owner is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner).body
    node = next(n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), node], type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(ROOT / file), 'exec'), context)
    return context[name]

class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_device_failure_clears_stale_values(self):
        class LoginFailed(Exception): pass
        class ApiFailed(Exception): pass
        run = function('coordinator.py', '_async_update_devices', dict(asyncio=asyncio, LoginFailed=LoginFailed,
            SunwaysClientException=ApiFailed, ConfigEntryAuthFailed=RuntimeError, _LOGGER=logging.getLogger('test')),
            'SunwaysDataUpdateCoordinator')
        owner = NS(_device_list=[{'id': 'synthetic'}], client=NS(get_device_info=AsyncMock(side_effect=TimeoutError())),
                   data={'devices': [{'sensors': {'temperature': 99}}]})
        self.assertEqual(await run(owner), [])

    async def test_late_devices_added_once_and_listener_removed_on_unload(self):
        listeners = []
        unregister = Mock()
        coordinator = NS(data={'devices': []}, async_add_listener=lambda callback: (listeners.append(callback), unregister)[1])
        entry = NS(runtime_data=NS(coordinator=coordinator), async_on_unload=Mock())
        added = []
        run = function('sensor.py', 'async_setup_entry', dict(DESCRIPTIONS=[],
            DEVICE_DESCRIPTIONS=[NS(key='frequency')], callback=lambda f: f,
            SunwaysSensor=Mock(), SunwaysDeviceSensor=lambda c,e,d,s: (d['id'],s.key)))
        await run(None, entry, added.extend)
        self.assertEqual(added, [])
        coordinator.data = {'devices': [{'id': 'synthetic', 'sensors': {'frequency': 50}}]}
        listeners[0]()
        listeners[0]()
        self.assertEqual(added, [('synthetic', 'frequency')])
        entry.async_on_unload.assert_called_once_with(unregister)

    async def test_reauth_removes_old_initial_token(self):
        client = NS(get_stations=AsyncMock(return_value=[]))
        factory = Mock(return_value=client)
        run = function('config_flow.py', 'async_step_reauth_confirm', dict(create_sunways_client=factory,
            CONF_INITIAL_TOKEN='initial_token'), 'SunwaysConfigFlow')
        entry = object()
        owner = NS(_data={'initial_token': 'synthetic-old', 'station_id': '1'}, hass=None,
                   _get_reauth_entry=lambda: entry, async_update_reload_and_abort=Mock(return_value='ok'))
        self.assertEqual(await run(owner, {'password': 'synthetic-new'}), 'ok')
        data = factory.call_args.args[1]
        self.assertNotIn('initial_token', data)
        self.assertEqual(data['station_id'], '1')
        owner.async_update_reload_and_abort.assert_called_once_with(entry, data=data)
