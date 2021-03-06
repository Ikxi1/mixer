import unittest

import bpy
from bpy import data as D  # noqa
from bpy import types as T  # noqa
from mixer.blender_data.json_codec import Codec
from mixer.blender_data.proxy import BpyBlendProxy, BpyIDProxy, BpyStructProxy
from mixer.blender_data.tests.utils import register_bl_equals

from mixer.blender_data.filter import safe_context
from mixer.blender_data.diff import BpyBlendDiff


class TestWorld(unittest.TestCase):
    def setUp(self):
        self.bpy_data_proxy = BpyBlendProxy()
        self.diff = BpyBlendDiff()
        bpy.data.worlds[0].name = "World"
        register_bl_equals(self, safe_context)

    def test_world(self):
        world = bpy.data.worlds[0]
        world.use_nodes = True
        self.assertGreaterEqual(len(world.node_tree.nodes), 2)

        self.diff.diff(self.bpy_data_proxy, safe_context)
        sent_ids = {}
        sent_ids.update({("worlds", world.name): world})

        changeset = self.bpy_data_proxy.update(self.diff, safe_context)
        updates = changeset.creations
        # avoid clash on restore
        world.name = world.name + "_bak"

        codec = Codec()
        for update in updates:
            key = (update.collection_name, update.data("name"))
            sent_id = sent_ids.get(key)
            if sent_id is None:
                continue

            encoded = codec.encode(update)
            # sender side
            #######################
            # receiver side
            decoded = codec.decode(encoded)
            created = self.bpy_data_proxy.update_datablock(decoded)
            self.assertEqual(created, sent_id)

    def test_non_existing(self):
        world = bpy.data.worlds[0]

        self.diff.diff(self.bpy_data_proxy, safe_context)
        sent_ids = {}
        sent_ids.update({("worlds", world.name): world})

        changeset = self.bpy_data_proxy.update(self.diff, safe_context)
        creations = changeset.creations
        # avoid clash on restore
        world.name = world.name + "_bak"

        codec = Codec()
        for update in creations:
            key = (update.collection_name, update.data("name"))
            sent_id = sent_ids.get(key)
            if sent_id is None:
                continue

            # create a property on the send proxy and test that is does not fail on the receiver
            # property on ID
            update._data["does_not_exist_property"] = ""
            update._data["does_not_exist_struct"] = BpyStructProxy()
            update._data["does_not_exist_ID"] = BpyIDProxy()

            encoded = codec.encode(update)
            # sender side
            #######################
            # receiver side
            decoded = codec.decode(encoded)
            created = self.bpy_data_proxy.update_datablock(decoded)
            self.assertEqual(created, sent_id)
