from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("run_xiaohongshu.py")
SPEC = importlib.util.spec_from_file_location("run_xiaohongshu", SCRIPT)
runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(runtime)


class RuntimeTests(unittest.TestCase):
    def test_resolved_config_discovers_standard_external_client(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "repo"
            home = base / "home"
            client = home / ".growth-lab" / "clients" / "xiaohongshu-mcp"
            legacy = home / ".xhs-autopilot" / "xiaohongshu-mcp"
            root.mkdir()
            client.mkdir(parents=True)
            legacy.mkdir(parents=True)
            service = client / "xiaohongshu-mcp-windows-amd64.exe"
            login = client / "xiaohongshu-login-windows-amd64.exe"
            cookie = legacy / "cookies.json"
            service.touch()
            login.touch()
            cookie.touch()
            values = runtime.resolved_config(root, {"USERPROFILE": str(home)})
        self.assertEqual(values["XHS_MCP_BINARY"], str(service))
        self.assertEqual(values["XHS_MCP_LOGIN_BINARY"], str(login))
        self.assertEqual(values["XHS_MCP_COOKIES_PATH"], str(cookie))

    def test_child_environment_removes_duplicate_path_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            child = runtime.normalized_child_env(
                {"Path": "preferred", "PATH": "duplicate", "OTHER": "value"},
                Path(temp_dir) / "cookies.json",
            )
        self.assertEqual([key for key in child if key.casefold() == "path"], ["Path"])
        self.assertEqual(child["Path"], "preferred")
        self.assertEqual(child["OTHER"], "value")

    def test_login_timeout_restarts_owned_service_only_once(self) -> None:
        manager = mock.Mock()
        manager.endpoint = "http://127.0.0.1:18063"
        manager.service_process = mock.Mock()
        with mock.patch.object(
            runtime,
            "login_status",
            side_effect=[runtime.LoginCheckTimeout("cold"), True],
        ) as status:
            self.assertTrue(runtime.check_login_with_one_restart(manager, 45, 20))
        self.assertEqual(status.call_count, 2)
        manager.stop_service.assert_called_once_with()
        manager.start_service.assert_called_once_with(20)

    def test_login_timeout_does_not_stop_unknown_service(self) -> None:
        manager = mock.Mock()
        manager.endpoint = "http://127.0.0.1:18063"
        manager.service_process = None
        with mock.patch.object(
            runtime, "login_status", side_effect=runtime.LoginCheckTimeout("cold")
        ):
            with self.assertRaisesRegex(runtime.RuntimeError, "已有小红书服务"):
                runtime.check_login_with_one_restart(manager, 45, 20)
        manager.stop_service.assert_not_called()

    def test_missing_login_permission_stops_before_visible_login(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = root / "service.exe"
            login = root / "login.exe"
            service.touch()
            login.touch()
            config = {
                "XHS_MCP_BINARY": str(service),
                "XHS_MCP_LOGIN_BINARY": str(login),
                "XHS_MCP_COOKIES_PATH": str(root / "cookies.json"),
            }
            manager = mock.Mock()
            manager.endpoint = runtime.DEFAULT_ENDPOINT
            with mock.patch.object(runtime, "resolved_config", return_value=config), mock.patch.object(
                runtime, "RuntimeManager", return_value=manager
            ), mock.patch.object(runtime, "check_login_with_one_restart", return_value=False), mock.patch.object(
                runtime, "emit"
            ) as emit:
                result = runtime.main(
                    [
                        "topic",
                        "--out",
                        str(root / "result.json"),
                        "--runtime-service-timeout",
                        "5",
                    ]
                )
        self.assertEqual(result, 2)
        manager.run_visible_login.assert_not_called()
        self.assertIn("--allow-visible-login", emit.call_args_list[-1].args[1])

    def test_visible_login_refuses_unknown_running_service(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = root / "service.exe"
            login = root / "login.exe"
            service.touch()
            login.touch()
            manager = runtime.RuntimeManager(
                runtime.DEFAULT_ENDPOINT,
                service,
                login,
                root / "cookies.json",
                os.environ,
                root / "logs",
            )
            with mock.patch.object(runtime, "service_healthy", return_value=True):
                with self.assertRaisesRegex(runtime.RuntimeError, "不是本协调器启动"):
                    manager.run_visible_login(30)

    def test_login_success_resumes_original_collector_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            service = root / "service.exe"
            login = root / "login.exe"
            service.touch()
            login.touch()
            config = {
                "XHS_MCP_BINARY": str(service),
                "XHS_MCP_LOGIN_BINARY": str(login),
                "XHS_MCP_COOKIES_PATH": str(root / "cookies.json"),
            }
            manager = mock.Mock()
            manager.endpoint = runtime.DEFAULT_ENDPOINT
            completed = mock.Mock(returncode=0)
            with mock.patch.object(runtime, "resolved_config", return_value=config), mock.patch.object(
                runtime, "RuntimeManager", return_value=manager
            ), mock.patch.object(runtime, "check_login_with_one_restart", return_value=True), mock.patch.object(
                subprocess, "run", return_value=completed
            ) as run:
                result = runtime.main(
                    [
                        "topic",
                        "--limit",
                        "3",
                        "--out",
                        str(root / "result.json"),
                        "--runtime-service-timeout",
                        "5",
                    ]
                )
        self.assertEqual(result, 0)
        command = run.call_args.args[0]
        self.assertIn("--runtime-authenticated", command)
        self.assertEqual(command[-5:], ["topic", "--limit", "3", "--out", str(root / "result.json")])
        manager.stop_service.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
