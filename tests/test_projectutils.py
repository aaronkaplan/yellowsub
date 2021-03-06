import inspect
from builtins import RuntimeError
from unittest import TestCase
from lib.utils.projectutils import ProjectUtils
import os
import sys
import logging


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

    def __delete_loggers(self):
        logger_names = [name for name in logging.root.manager.loggerDict.keys() if name.startswith("yellowsub")]
        for name in logger_names:
            del logging.root.manager.loggerDict[name]

    def test_get_logger(self):
        logger_name = "testlogger"
        self.__delete_loggers()
        with self.assertRaises(RuntimeError):
            ProjectUtils.get_logger(logger_name)
        pass

    def test____setup_root_logger(self):
        config = ""
        with self.assertRaises(AttributeError):
            ProjectUtils._ProjectUtils__setup_root_logger(config)

        config = {}
        with self.assertRaises(RuntimeError):
            ProjectUtils._ProjectUtils__setup_root_logger(config)

        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [
                {'handler': {
                    'type': 'StreamHandler',
                    'output': '/tmp/yellowsub.INFO.log',
                    'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]}}
        with self.assertRaises(NotImplementedError):
            ProjectUtils._ProjectUtils__setup_root_logger(config)

        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.INFO.log',
                    'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]}}
        self.__delete_loggers()
        ProjectUtils._ProjectUtils__setup_root_logger(config)

        root_logger = logging.getLogger("yellowsub")
        self.assertEqual(root_logger.hasHandlers(), True)
        self.assertEqual(root_logger.getEffectiveLevel(), 10)

        root_logger_handlers = root_logger.handlers
        h = root_logger_handlers[0]
        self.assertEqual(h.level, 20)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.INFO.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        h = root_logger_handlers[1]
        self.assertEqual(h.level, 30)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.WARN.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

    def test_configure_logger(self):
        config = ""
        with self.assertRaises(TypeError):
            ProjectUtils.configure_logger(config)

        config = {}
        with self.assertRaises(RuntimeError):
            ProjectUtils.configure_logger(config)

        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [{'handler': {
                'type': 'TimedRotatingFileHandler',
                'output': '/tmp/yellowsub.INFO.log',
                'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]
        },
            'processors': {'MispAttributeSearcher': {'misp_uri': 'https://192.168.5.108/',
                                                     'misp_api_key': 'Uprq61Xgv9n3Fwl2DqUbPpnLEksex9mKuSy55QN0',
                                                     'logging': {'loglevel': 'DEBUG',
                                                                 'handlers': [{'handler': {
                                                                     'type': 'TimedRotatingFileHandler',
                                                                     'output': '/tmp/yellowsub.mispattributesearcher'
                                                                               '.INFO.log',
                                                                     'loglevel': 'INFO'}},
                                                                     {'handler': {
                                                                         'type': 'TimedRotatingFileHandler',
                                                                         'output': '/tmp/yellowsub'
                                                                                   '.mispattributesearcher.WARN.log',
                                                                         'loglevel': 'WARN'}}]}}}}

        # DG_Comment: test if called with a processor class that is not part of the config
        with self.assertRaises(RuntimeError):
            ProjectUtils.configure_logger(config, "testClass", "testID")

        # DG_Comment: test creation of root yellowsub logger if no processor class is provided
        self.__delete_loggers()
        ProjectUtils.configure_logger(config, None, None)

        # TODO: DG_Comment: this has to parametrized and put into an internal testing method as the same code is used
        #                  both for this as well as testing the root logger setup private method.
        root_logger = logging.getLogger("yellowsub")
        self.assertEqual(root_logger.hasHandlers(), True)
        self.assertEqual(root_logger.getEffectiveLevel(), 10)

        root_logger_handlers = root_logger.handlers
        h = root_logger_handlers[0]
        self.assertEqual(h.level, 20)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.INFO.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        h = root_logger_handlers[1]
        self.assertEqual(h.level, 30)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.WARN.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        # DG_Comment: Test if logger is properly created if processor class is provided but there is no specific logger
        #               defined at the processor level in the config
        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [{'handler': {
                'type': 'TimedRotatingFileHandler',
                'output': '/tmp/yellowsub.INFO.log',
                'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]
        },
            'processors': {'MispAttributeSearcher': {'misp_uri': 'https://192.168.5.108/',
                                                     'misp_api_key': ''}}}
        self.__delete_loggers()
        ProjectUtils.configure_logger(config, "MispAttributeSearcher", "testId")

        # TODO: DG_Comment: this has to parametrized and put into an internal testing method as the same code is used
        #                  both for this as well as testing the root logger setup private method.
        root_logger = logging.getLogger("yellowsub")
        self.assertEqual(root_logger.hasHandlers(), True)
        self.assertEqual(root_logger.getEffectiveLevel(), 10)

        root_logger_handlers = root_logger.handlers
        h = root_logger_handlers[0]
        self.assertEqual(h.level, 20)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.INFO.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        h = root_logger_handlers[1]
        self.assertEqual(h.level, 30)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.WARN.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        # DG_Comment:    test if the processor specific logger is configured properly

        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [{'handler': {
                'type': 'TimedRotatingFileHandler',
                'output': '/tmp/yellowsub.INFO.log',
                'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]
        },
            'processors': {'MispAttributeSearcher': {'misp_uri': 'https://192.168.5.108/',
                                                     'misp_api_key': 'Uprq61Xgv9n3Fwl2DqUbPpnLEksex9mKuSy55QN0',
                                                     'logging': {'loglevel': 'DEBUG',
                                                                 'handlers': [{'handler': {
                                                                     'type': 'TimedRotatingFileHandler',
                                                                     'output': '/tmp/yellowsub.mispattributesearcher'
                                                                               '.INFO.log',
                                                                     'loglevel': 'INFO'}},
                                                                     {'handler': {
                                                                         'type': 'TimedRotatingFileHandler',
                                                                         'output': '/tmp/yellowsub'
                                                                                   '.mispattributesearcher.WARN.log',
                                                                         'loglevel': 'WARN'}}]}}}}

        self.__delete_loggers()
        ProjectUtils.configure_logger(config, "MispAttributeSearcher", "testId")

        processor_logger = logging.getLogger("yellowsub.MispAttributeSearcher.testId")
        self.assertEqual(processor_logger.hasHandlers(), True)
        self.assertEqual(processor_logger.getEffectiveLevel(), 10)

        processor_logger_handlers = processor_logger.handlers
        h = processor_logger_handlers[0]
        self.assertEqual(h.level, 20)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.mispattributesearcher.INFO.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        h = processor_logger_handlers[1]
        self.assertEqual(h.level, 30)
        self.assertEqual(type(h).__name__, "TimedRotatingFileHandler")
        self.assertEqual(h.formatter._fmt, "%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s")
        self.assertEqual(h.stream.name, "/tmp/yellowsub.mispattributesearcher.WARN.log")
        # TODO: DG_Comment: should also check rotating interval. I have not figured out a way to do this.

        # DG_Comment:    test creation of specific processor level logger with unimplemented handler
        config = {'logging': {
            'loglevel': 'DEBUG',
            'facility': 'yellowsub',
            'handlers': [{'handler': {
                'type': 'TimedRotatingFileHandler',
                'output': '/tmp/yellowsub.INFO.log',
                'loglevel': 'INFO'}},
                {'handler': {
                    'type': 'TimedRotatingFileHandler',
                    'output': '/tmp/yellowsub.WARN.log',
                    'loglevel': 'WARN'}}]
        },
            'processors': {'MispAttributeSearcher': {'misp_uri': 'https://192.168.5.108/',
                                                     'misp_api_key': 'Uprq61Xgv9n3Fwl2DqUbPpnLEksex9mKuSy55QN0',
                                                     'logging': {'loglevel': 'DEBUG',
                                                                 'handlers': [{'handler': {
                                                                     'type': 'StreamHandler',
                                                                     'output': '/tmp/yellowsub.mispattributesearcher'
                                                                               '.INFO.log',
                                                                     'loglevel': 'INFO'}},
                                                                     {'handler': {
                                                                         'type': 'TimedRotatingFileHandler',
                                                                         'output': '/tmp/yellowsub'
                                                                                   '.mispattributesearcher.WARN.log',
                                                                         'loglevel': 'WARN'}}]}}}}

        self.__delete_loggers()
        with self.assertRaises(NotImplementedError):
            ProjectUtils.configure_logger(config, "MispAttributeSearcher", "testId")


if __name__ == '__main__':
    class_names = [(name, cls) for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass) if
                   name.startswith("Test") and name != "TestCase"]

    for name, cls in class_names:
        t = cls()
        functions = [(name, f) for name, f in inspect.getmembers(cls, predicate=inspect.isfunction) if
                     name.startswith("test_")]
        for n, f in functions:
            getattr(t, n)()
