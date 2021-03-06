import unittest
import os
from .helpers.ptrack_helpers import ProbackupTest, ProbackupException
import subprocess
from sys import exit


module_name = 'delete'


class DeleteTest(ProbackupTest, unittest.TestCase):

    # @unittest.skip("skip")
    # @unittest.expectedFailure
    def test_delete_full_backups(self):
        """delete full backups"""
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # full backup
        self.backup_node(backup_dir, 'node', node)

        pgbench = node.pgbench(
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(backup_dir, 'node', node)

        pgbench = node.pgbench(
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pgbench.wait()
        pgbench.stdout.close()

        self.backup_node(backup_dir, 'node', node)

        show_backups = self.show_pb(backup_dir, 'node')
        id_1 = show_backups[0]['id']
        id_2 = show_backups[1]['id']
        id_3 = show_backups[2]['id']
        self.delete_pb(backup_dir, 'node', id_2)
        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(show_backups[0]['id'], id_1)
        self.assertEqual(show_backups[1]['id'], id_3)

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    # @unittest.expectedFailure
    def test_del_instance_archive(self):
        """delete full backups"""
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # full backup
        self.backup_node(backup_dir, 'node', node)

        # full backup
        self.backup_node(backup_dir, 'node', node)

        # restore
        node.cleanup()
        self.restore_node(backup_dir, 'node', node)
        node.slow_start()

        # Delete instance
        self.del_instance(backup_dir, 'node')

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    # @unittest.expectedFailure
    def test_delete_archive_mix_compress_and_non_compressed_segments(self):
        """stub"""

    # @unittest.skip("skip")
    def test_delete_increment_page(self):
        """delete increment and all after him"""
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # full backup mode
        self.backup_node(backup_dir, 'node', node)
        # page backup mode
        self.backup_node(backup_dir, 'node', node, backup_type="page")
        # page backup mode
        self.backup_node(backup_dir, 'node', node, backup_type="page")
        # full backup mode
        self.backup_node(backup_dir, 'node', node)

        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(len(show_backups), 4)

        # delete first page backup
        self.delete_pb(backup_dir, 'node', show_backups[1]['id'])

        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(len(show_backups), 2)

        self.assertEqual(show_backups[0]['backup-mode'], "FULL")
        self.assertEqual(show_backups[0]['status'], "OK")
        self.assertEqual(show_backups[1]['backup-mode'], "FULL")
        self.assertEqual(show_backups[1]['status'], "OK")

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_increment_ptrack(self):
        """delete increment and all after him"""
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'],
            pg_options={'ptrack_enable': 'on'})

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # full backup mode
        self.backup_node(backup_dir, 'node', node)
        # ptrack backup mode
        self.backup_node(backup_dir, 'node', node, backup_type="ptrack")
        # ptrack backup mode
        self.backup_node(backup_dir, 'node', node, backup_type="ptrack")
        # full backup mode
        self.backup_node(backup_dir, 'node', node)

        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(len(show_backups), 4)

        # delete first page backup
        self.delete_pb(backup_dir, 'node', show_backups[1]['id'])

        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(len(show_backups), 2)

        self.assertEqual(show_backups[0]['backup-mode'], "FULL")
        self.assertEqual(show_backups[0]['status'], "OK")
        self.assertEqual(show_backups[1]['backup-mode'], "FULL")
        self.assertEqual(show_backups[1]['status'], "OK")

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_orphaned_wal_segments(self):
        """
        make archive node, make three full backups,
        delete second backup without --wal option,
        then delete orphaned wals via --wal option
        """
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        node.safe_psql(
            "postgres",
            "create table t_heap as select 1 as id, md5(i::text) as text, md5(repeat(i::text,10))::tsvector as tsvector from generate_series(0,10000) i")
        # first full backup
        backup_1_id = self.backup_node(backup_dir, 'node', node)
        # second full backup
        backup_2_id = self.backup_node(backup_dir, 'node', node)
        # third full backup
        backup_3_id = self.backup_node(backup_dir, 'node', node)
        node.stop()

        # Check wals
        wals_dir = os.path.join(backup_dir, 'wal', 'node')
        wals = [f for f in os.listdir(wals_dir) if os.path.isfile(os.path.join(wals_dir, f)) and not f.endswith('.backup')]
        original_wal_quantity = len(wals)

        # delete second full backup
        self.delete_pb(backup_dir, 'node', backup_2_id)
        # check wal quantity
        self.validate_pb(backup_dir)
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_1_id)['status'], "OK")
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_3_id)['status'], "OK")
        # try to delete wals for second backup
        self.delete_pb(backup_dir, 'node', options=['--wal'])
        # check wal quantity
        self.validate_pb(backup_dir)
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_1_id)['status'], "OK")
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_3_id)['status'], "OK")

        # delete first full backup
        self.delete_pb(backup_dir, 'node', backup_1_id)
        self.validate_pb(backup_dir)
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_3_id)['status'], "OK")

        result = self.delete_pb(backup_dir, 'node', options=['--wal'])
        # delete useless wals
        self.assertTrue('INFO: removed min WAL segment' in result
            and 'INFO: removed max WAL segment' in result)
        self.validate_pb(backup_dir)
        self.assertEqual(self.show_pb(backup_dir, 'node', backup_3_id)['status'], "OK")

        # Check quantity, it should be lower than original
        wals = [f for f in os.listdir(wals_dir) if os.path.isfile(os.path.join(wals_dir, f)) and not f.endswith('.backup')]
        self.assertTrue(original_wal_quantity > len(wals), "Number of wals not changed after 'delete --wal' which is illegal")

        # Delete last backup
        self.delete_pb(backup_dir, 'node', backup_3_id, options=['--wal'])
        wals = [f for f in os.listdir(wals_dir) if os.path.isfile(os.path.join(wals_dir, f)) and not f.endswith('.backup')]
        self.assertEqual (0, len(wals), "Number of wals should be equal to 0")

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_wal_between_multiple_timelines(self):
        """
                    /-------B1--
        A1----------------A2----

        delete A1 backup, check that WAL segments on [A1, A2) and
        [A1, B1) are deleted and backups B1 and A2 keep
        their WAL
        """
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        A1 = self.backup_node(backup_dir, 'node', node)

        # load some data to node
        node.pgbench_init(scale=3)

        node2 = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node2'))
        node2.cleanup()

        self.restore_node(backup_dir, 'node', node2)
        node2.append_conf(
            'postgresql.auto.conf', "port = {0}".format(node2.port))
        node2.slow_start()

        # load some more data to node
        node.pgbench_init(scale=3)

        # take A2
        A2 = self.backup_node(backup_dir, 'node', node)

        # load some more data to node2
        node2.pgbench_init(scale=2)

        B1 = self.backup_node(
            backup_dir, 'node',
            node2, data_dir=node2.data_dir)

        self.delete_pb(backup_dir, 'node', backup_id=A1, options=['--wal'])

        self.validate_pb(backup_dir)

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_backup_with_empty_control_file(self):
        """
        take backup, truncate its control file,
        try to delete it via 'delete' command
        """
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'],
            set_replication=True)

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        node.slow_start()

        # full backup mode
        self.backup_node(
            backup_dir, 'node', node, options=['--stream'])
        # page backup mode
        self.backup_node(
            backup_dir, 'node', node, backup_type="delta", options=['--stream'])
        # page backup mode
        backup_id = self.backup_node(
            backup_dir, 'node', node, backup_type="delta", options=['--stream'])

        with open(
            os.path.join(backup_dir, 'backups', 'node', backup_id, 'backup.control'),
            'wt') as f:
                f.flush()
                f.close()

        show_backups = self.show_pb(backup_dir, 'node')
        self.assertEqual(len(show_backups), 3)

        self.delete_pb(backup_dir, 'node', backup_id=backup_id)

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_interleaved_incremental_chains(self):
        """complicated case of interleaved backup chains"""
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # Take FULL BACKUPs

        backup_id_a = self.backup_node(backup_dir, 'node', node)
        backup_id_b = self.backup_node(backup_dir, 'node', node)

        # Change FULL B backup status to ERROR
        self.change_backup_status(backup_dir, 'node', backup_id_b, 'ERROR')

        # FULLb  ERROR
        # FULLa  OK
        # Take PAGEa1 backup
        page_id_a1 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEa1 OK
        # FULLb  ERROR
        # FULLa  OK
        # Change FULL B backup status to OK
        self.change_backup_status(backup_dir, 'node', backup_id_b, 'OK')

        # Change PAGEa1 backup status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_a1, 'ERROR')

        # PAGEa1 ERROR
        # FULLb  OK
        # FULLa  OK
        page_id_b1 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEb1 OK
        # PAGEa1 ERROR
        # FULLb  OK
        # FULLa  OK
        # Now we start to play with first generation of PAGE backups
        # Change PAGEb1 status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'ERROR')

        # Change PAGEa1 status to OK
        self.change_backup_status(backup_dir, 'node', page_id_a1, 'OK')

        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK
        page_id_a2 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEa2 OK
        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK
        # Change PAGEa2 status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_a2, 'ERROR')

        # Change PAGEb1 status to OK
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'OK')

        # PAGEa2 ERROR
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK
        page_id_b2 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # Change PAGEa2 status to OK
        self.change_backup_status(backup_dir, 'node', page_id_a2, 'OK')

        # PAGEb2 OK
        # PAGEa2 OK
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        self.backup_node(backup_dir, 'node', node)
        self.backup_node(backup_dir, 'node', node, backup_type='page')

        # PAGEc1 OK
        # FULLc  OK
        # PAGEb2 OK
        # PAGEa2 OK
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Delete FULLb
        self.delete_pb(
            backup_dir, 'node', backup_id_b)

        self.assertEqual(len(self.show_pb(backup_dir, 'node')), 5)

        print(self.show_pb(
            backup_dir, 'node', as_json=False, as_text=True))

        # Clean after yourself
        self.del_test_dir(module_name, fname)

    # @unittest.skip("skip")
    def test_delete_multiple_descendants(self):
        """
        PAGEb3
          |                 PAGEa3
        PAGEb2               /
          |       PAGEa2    /
        PAGEb1       \     /
          |           PAGEa1
        FULLb           |
                      FULLa  should be deleted
        """
        fname = self.id().split('.')[3]
        node = self.make_simple_node(
            base_dir=os.path.join(module_name, fname, 'node'),
            initdb_params=['--data-checksums'])

        backup_dir = os.path.join(self.tmp_path, module_name, fname, 'backup')
        self.init_pb(backup_dir)
        self.add_instance(backup_dir, 'node', node)
        self.set_archiving(backup_dir, 'node', node)
        node.slow_start()

        # Take FULL BACKUPs
        backup_id_a = self.backup_node(backup_dir, 'node', node)

        backup_id_b = self.backup_node(backup_dir, 'node', node)

        # Change FULLb backup status to ERROR
        self.change_backup_status(backup_dir, 'node', backup_id_b, 'ERROR')

        page_id_a1 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # Change FULLb backup status to OK
        self.change_backup_status(backup_dir, 'node', backup_id_b, 'OK')

        # Change PAGEa1 backup status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_a1, 'ERROR')

        # PAGEa1 ERROR
        # FULLb  OK
        # FULLa  OK

        page_id_b1 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEb1 OK
        # PAGEa1 ERROR
        # FULLb  OK
        # FULLa  OK

        # Change PAGEa1 backup status to OK
        self.change_backup_status(backup_dir, 'node', page_id_a1, 'OK')

        # Change PAGEb1 backup status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'ERROR')

        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        page_id_a2 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEa2 OK
        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Change PAGEb1 backup status to OK
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'OK')

        # Change PAGEa2 backup status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_a2, 'ERROR')

        # PAGEa2 ERROR
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        page_id_b2 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEb2 OK
        # PAGEa2 ERROR
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Change PAGEb2 and PAGEb1  status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_b2, 'ERROR')
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'ERROR')

        # PAGEb2 ERROR
        # PAGEa2 ERROR
        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        page_id_a3 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEa3 OK
        # PAGEb2 ERROR
        # PAGEa2 ERROR
        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Change PAGEa3 status to ERROR
        self.change_backup_status(backup_dir, 'node', page_id_a3, 'ERROR')

        # Change PAGEb2 status to OK
        self.change_backup_status(backup_dir, 'node', page_id_b2, 'OK')

        page_id_b3 = self.backup_node(
            backup_dir, 'node', node, backup_type='page')

        # PAGEb3 OK
        # PAGEa3 ERROR
        # PAGEb2 OK
        # PAGEa2 ERROR
        # PAGEb1 ERROR
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Change PAGEa3, PAGEa2 and PAGEb1 status to OK
        self.change_backup_status(backup_dir, 'node', page_id_a3, 'OK')
        self.change_backup_status(backup_dir, 'node', page_id_a2, 'OK')
        self.change_backup_status(backup_dir, 'node', page_id_b1, 'OK')

        # PAGEb3 OK
        # PAGEa3 OK
        # PAGEb2 OK
        # PAGEa2 OK
        # PAGEb1 OK
        # PAGEa1 OK
        # FULLb  OK
        # FULLa  OK

        # Check that page_id_a3 and page_id_a2 are both direct descendants of page_id_a1
        self.assertEqual(
            self.show_pb(backup_dir, 'node', backup_id=page_id_a3)['parent-backup-id'],
            page_id_a1)

        self.assertEqual(
            self.show_pb(backup_dir, 'node', backup_id=page_id_a2)['parent-backup-id'],
            page_id_a1)

        # Delete FULLa
        self.delete_pb(backup_dir, 'node', backup_id_a)

        self.assertEqual(len(self.show_pb(backup_dir, 'node')), 4)

        # Clean after yourself
        self.del_test_dir(module_name, fname)
