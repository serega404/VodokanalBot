import fcntl
import signal
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import requests

import parser
import start_telegram


class RunSafetyTests(unittest.TestCase):
    def test_next_run_delivers_new_posts_after_skipped_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bot.lock"
            db_path = str(Path(directory) / "db.json")
            old = parser.Post("01.01", "old")
            new = parser.Post("01.01", "new")
            parser.save_database([old], db_path)
            sent = []
            with patch.object(parser, "fetch_posts", return_value=[old, new]), patch.object(
                start_telegram, "main", side_effect=lambda: parser.publish_new_posts(
                    sent.append, None, "http://source", db_path=db_path
                )
            ):
                with path.open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    start_telegram.run_once(path)
                    self.assertEqual([], sent)
                    self.assertEqual([old.key], parser.load_database(db_path))
                start_telegram.run_once(path)
                self.assertEqual([new.text], sent)
                self.assertEqual([old.key, new.key], parser.load_database(db_path))

    def test_unresponsive_telegram_times_out(self):
        class SlowHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                time.sleep(0.2)
                self.send_response(200)
                self.end_headers()
                try:
                    self.wfile.write(b'{"result": {"message_id": 42}}')
                except BrokenPipeError:
                    pass

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler) as server:
            class LocalTelegramSession(requests.Session):
                def get(self, url, **kwargs):
                    return super().get(f"http://127.0.0.1:{server.server_port}", **kwargs)

            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                with LocalTelegramSession() as session, patch.object(
                    start_telegram, "TELEGRAM_TIMEOUT", (0.05, 0.05), create=True
                ):
                    session.trust_env = False
                    with self.assertRaises(requests.exceptions.Timeout):
                        start_telegram.send_telegram_message(session, "test")
            finally:
                server.shutdown()
                worker.join(timeout=2)

    def test_interrupted_database_save_preserves_previous_data(self):
        def interrupt_save(value, file, **kwargs):
            file.write("[")
            raise SystemExit("time limit")

        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "db.json")
            parser.save_database([parser.Post("01.01", "previous")], path)
            with patch.object(parser.json, "dump", side_effect=interrupt_save):
                with self.assertRaisesRegex(SystemExit, "time limit"):
                    parser.save_database([parser.Post("01.01", "new")], path)
            self.assertEqual(["01.01$previous"], parser.load_database(path))

    def test_unresponsive_source_times_out(self):
        class SlowHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                time.sleep(0.2)
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                with requests.Session() as session, patch.object(
                    parser, "SOURCE_TIMEOUT", (0.05, 0.05), create=True
                ):
                    session.trust_env = False
                    with self.assertRaises(requests.exceptions.Timeout):
                        parser.fetch_posts(session, f"http://127.0.0.1:{server.server_port}")
            finally:
                server.shutdown()
                worker.join(timeout=2)

    def test_overlapping_run_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bot.lock"
            with path.open("a") as lock, patch.object(start_telegram, "main") as main:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                start_telegram.run_once(path)
                main.assert_not_called()

    def test_completed_run_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(start_telegram, "main") as main:
            path = Path(directory) / "bot.lock"
            start_telegram.run_once(path)
            start_telegram.run_once(path)
            self.assertEqual(2, main.call_count)

    def test_failed_run_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            start_telegram, "main", side_effect=[RuntimeError("source failed"), None]
        ) as main:
            path = Path(directory) / "bot.lock"
            with self.assertRaisesRegex(RuntimeError, "source failed"):
                start_telegram.run_once(path)
            start_telegram.run_once(path)
            self.assertEqual(2, main.call_count)

    def test_overdue_run_stops_and_allows_next_run(self):
        previous_handler = signal.getsignal(signal.SIGALRM)
        with tempfile.TemporaryDirectory() as directory, patch.object(
            start_telegram, "RUN_TIMEOUT_SECONDS", 1, create=True
        ):
            path = Path(directory) / "bot.lock"
            with patch.object(start_telegram, "main", side_effect=lambda: time.sleep(2)):
                with self.assertRaisesRegex(SystemExit, "time limit"):
                    start_telegram.run_once(path)
            self.assertEqual(previous_handler, signal.getsignal(signal.SIGALRM))
            self.assertEqual(0, signal.alarm(0))
            with patch.object(start_telegram, "main") as main:
                start_telegram.run_once(path)
                main.assert_called_once_with()
