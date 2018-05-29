import errno
import os
import platform
import subprocess
from subprocess import PIPE
import time
import socket
from shutil import which
from tempfile import TemporaryDirectory


try:
    from subprocess import DEVNULL
    _HAS_NATIVE_DEVNULL = True
except ImportError:
    DEVNULL = -3
    _HAS_NATIVE_DEVNULL = False

class Service(object):

    def __init__(self, executable = None, port=0, log_file=DEVNULL, env=None,
                 start_error_message="", service_args = None, headless = True):
        if not executable:
            for chrome_exe in ["chrome", "google-chrome-stable"]
                executable = which(chrome_exe)
                if executable: break
            if not executable:
                raise ChromeException("Could not find chrome executable in system path!")
        
        self.path = executable
        
        self.tmpdir = TemporaryDirectory()
        
        self.port = port
        if self.port == 0:
            self.port = free_port()
        
        self.service_args = service_args or []
        self.service_args += ['--disable-background-networking',
                              '--disable-client-side-phishing-detection',
                              '--disable-default-apps', '--disable-hang-monitor',
                              '--disable-infobars', '--disable-popup-blocking',
                              '--disable-prompt-on-repost', '--disable-sync',
                              '--disable-web-resources', '--enable-automation',
                              '--enable-logging', '--password-store=basic',
                              '--force-fieldtrials=SiteIsolationExtensions/Control',
                              '--ignore-certificate-errors', '--log-level=0',
                              '--metrics-recording-only', '--no-first-run',
                              '--test-type=browser', '--use-mock-keychain']
        self.service_args += ['--user-data-dir='  + self.tmpdir.name]
        self.service_args += ['--remote-debugging-port=' + str(self.port)]
        self.service_args += ['--headless'] if headless else []

        if not _HAS_NATIVE_DEVNULL and log_file == DEVNULL:
            log_file = open(os.devnull, 'wb')

        self.start_error_message = start_error_message
        self.log_file = log_file
        self.env = env or os.environ
        
        self.tmpdir = TemporaryDirectory()
        
        self.start()

    @property
    def url(self):
        """
        Gets the url of the Service
        """
        return "http://%s" % join_host_port('127.0.0.1', self.port)

    def start(self):
        """
        Starts the Service.

        :Exceptions:
         - ChromeException : Raised either when it can't start the service
           or when it can't connect to the service
        """
        try:
            cmd = [self.path]
            cmd.extend(self.service_args)
            self.process = subprocess.Popen(cmd, env=self.env,
                                            close_fds=platform.system() != 'Windows',
                                            stdout=self.log_file,
                                            stderr=self.log_file,
                                            stdin=PIPE)
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise ChromeException(
                    "'%s' executable needs to be in PATH. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            elif err.errno == errno.EACCES:
                raise ChromeException(
                    "'%s' executable may have wrong permissions. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            else:
                raise
        except Exception as e:
            raise ChromeException(
                "The executable %s needs to be available in the path. %s\n%s" %
                (os.path.basename(self.path), self.start_error_message, str(e)))
        count = 0
        while True:
            self.assert_process_still_running()
            if self.is_connectable():
                break
            count += 1
            time.sleep(1)
            if count == 30:
                raise ChromeException("Can not connect to the Service %s" % self.path)

    def assert_process_still_running(self):
        return_code = self.process.poll()
        if return_code is not None:
            raise ChromeException(
                'Service %s unexpectedly exited. Status code was: %s'
                % (self.path, return_code)
            )

    def is_connectable(self):
        return is_connectable(self.port)

    def stop(self):
        """
        Stops the service.
        """
        if self.log_file != PIPE and not (self.log_file == DEVNULL and _HAS_NATIVE_DEVNULL):
            try:
                self.log_file.close()
            except Exception:
                pass

        if self.process is None:
            return

        try:
            if self.process:
                for stream in [self.process.stdin,
                               self.process.stdout,
                               self.process.stderr]:
                    try:
                        stream.close()
                    except AttributeError:
                        pass
                self.process.terminate()
                self.process.wait()
                self.process.kill()
                self.process = None
        except OSError:
            pass
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.__del__()

    def __del__(self):
        # `subprocess.Popen` doesn't send signal on `__del__`;
        # so we attempt to close the launched process when `__del__`
        # is triggered.
        try:
            self.stop()
        except Exception:
            pass
        
        try:
            self.tmpdir.cleanup()
        except Exception:
            pass


class ChromeException(Exception):
    """
    Base webdriver exception.
    """

    def __init__(self, msg=None, screen=None, stacktrace=None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += "Stacktrace:\n%s" % stacktrace
        return exception_msg


def free_port():
    """
    Determines a free port using sockets.
    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(('0.0.0.0', 0))
    free_socket.listen(5)
    port = free_socket.getsockname()[1]
    free_socket.close()
    return port


def is_connectable(port, host="localhost"):
    """
    Tries to connect to the server at port to see if it is running.
    :Args:
     - port - The port to connect.
    """
    socket_ = None
    try:
        socket_ = socket.create_connection((host, port), 1)
        result = True
    except socket.error:
        result = False
    finally:
        if socket_:
            socket_.close()
    return result


def join_host_port(host, port):
    """Joins a hostname and port together.
    This is a minimal implementation intended to cope with IPv6 literals. For
    example, _join_host_port('::1', 80) == '[::1]:80'.
    :Args:
        - host - A hostname.
        - port - An integer port.
    """
    if ':' in host and not host.startswith('['):
        return '[%s]:%d' % (host, port)
    return '%s:%d' % (host, port)
