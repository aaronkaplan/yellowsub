import inspect
from unittest import TestCase
from lib.utils.projectutils import ProjectUtils
import os
import sys


class TestProjectUtils(TestCase):

    def test_get_config_path_env_var_resolved(self):
        initial_env_yellowsub_test = os.getenv("YELLOWSUB_TEST")

        os.environ["YELLOWSUB_TEST"] = "1"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "true"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "TRUE"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "0"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config.yml")

        os.environ["YELLOWSUB_TEST"] = "false"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config.yml")

        os.environ["YELLOWSUB_TEST"] = "FALSE"
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config.yml")

        os.unsetenv("YELLOWSUB_TEST")
        self.assertEqual(ProjectUtils.get_config_path_env_var_resolved(), "/etc/config.yml")

        if initial_env_yellowsub_test is not None:
            os.environ["YELLOWSUB_TEST"] = initial_env_yellowsub_test

    def test_get_project_path_as_str(self):
        p = os.path.dirname(os.path.realpath(__file__))
        project_p = p[:p.find("yellowsub") + len("yellowsub")] + "/"

        self.assertEqual(ProjectUtils.get_project_path_as_str(), project_p)

    def test_get_config_path_as_str(self):
        initial_env_yellowsub_test = os.getenv("YELLOWSUB_TEST")

        p = os.path.dirname(os.path.realpath(__file__))
        project_p = p[:p.find("yellowsub") + len("yellowsub")] + "/"

        os.environ["YELLOWSUB_TEST"] = "1"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "true"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "TRUE"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config_test.yml")

        os.environ["YELLOWSUB_TEST"] = "0"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config.yml")

        os.environ["YELLOWSUB_TEST"] = "false"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config.yml")

        os.environ["YELLOWSUB_TEST"] = "FALSE"
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config.yml")

        os.unsetenv("YELLOWSUB_TEST")
        self.assertEqual(ProjectUtils.get_config_path_as_str(), project_p + "etc/config.yml")

        if initial_env_yellowsub_test is not None:
            os.environ["YELLOWSUB_TEST"] = initial_env_yellowsub_test

    def test____setup_root_logger(self):
        pass

    def test_configure_logger(self):
        pass

    def test_get_logger(self):
        pass


if __name__ == '__main__':
    class_names = [(name, cls) for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass) if
                   name.startswith("Test") and name != "TestCase"]

    for name, cls in class_names:
        t = cls()
        functions = [(name, f) for name, f in inspect.getmembers(cls, predicate=inspect.isfunction) if
                     name.startswith("test_")]
        for n, f in functions:
            getattr(t, n)()
