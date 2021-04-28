import logging
import re
from typing import Type, Optional
from datetime import timedelta, datetime
from threading import RLock
from telnetlib import Telnet

from showergel.metadata import to_datetime

log = logging.getLogger(__name__)

# Liquidsoap's message before it closes the connection because of inactivity
LIQUIDSOAP_CLOSING = "Connection timed out.. Bye!"

class TelnetConnector:
    """
    Connects Showergel to Liquidsoap over Telnet. All method calls are thread-safe.

    This requires the Liquidsoap script to enable ``server.telnet``, with
    settings matching Showergel's configuration. For example, if the ``.liq`` sets

    .. code-block:: ocaml
        set("server.telnet",true)
        set("server.telnet.bind_addr","192.168.1.10")
        set("server.telnet.port",4444)
    
    Then Showergel configuration should contain:

    .. code-block:: toml
        [liquidsoap]
        method = "telnet"
        host = "192.168.1.10"
        port = 4444
    
    You can also set ``timeout``, in seconds (defaults to 10).
    """
    
    UPTIME_PATTERN = re.compile(r"([0-9]+)d ([0-9]+)h ([0-9]+)m ([0-9]+)s")
    METADATA_PATTERN = re.compile(r"^([^=]+)=\"(.*)\"$")

    def __init__(self, config:dict):
        self._lock = RLock()
        self.host = config['liquidsoap.host']
        self.port = config['liquidsoap.port']
        if 'liquidsoap.timeout' in config:
            self.timeout = int(config['liquidsoap.timeout'])
        else:
            self.timeout = 10

        self._connection = Telnet()
        self._connect()

        self.soap_objects = {}
        self._first_output_name = None
        self._soaps_updated_at = None
        self.uptime()
        self._latest_active_source = None

    def _connect(self, reconnect=False):
        self._lock.acquire()
        if reconnect:
            self._connection.close()
            self._connection = Telnet()
        log.info("Attempting to contact Liquidsoap over telnet @%s:%s",
            self.host, self.port)
        try:
            self._connection.open(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            log.info("Connected.")
        except ConnectionRefusedError:
            log.warning("Cannot connect to Liquidsoap. Please check it is running, or check Showergel's configuration.")
        self._lock.release()

    def _command(self, command:str) -> str:
        self._lock.acquire()
        response = None
        remaining_attempts = 2
        while remaining_attempts > 0:
            # log.debug("Telnet command: %s", command)
            remaining_attempts -= 1
            try:
                if not self._connection.sock:
                    raise BrokenPipeError()
                self._connection.write(command.encode('utf8') + b'\n')
                line = self._connection.read_until(b'END').decode('utf8')
                response = line.rstrip("END").strip("\r\n")
                if response == LIQUIDSOAP_CLOSING:
                    raise EOFError()
                # log.debug("Telnet response: %r", response)
                break
            except (EOFError, BrokenPipeError, ConnectionResetError):
                if remaining_attempts:
                    self._connect(reconnect=True)
                else:
                    log.critical("Failed to open connection to %s:%s", self.host, self.port)
        self._lock.release()
        return response

    def _update_soaps(self):
        self.soap_objects = {}
        raw = self._command("list")
        if raw:
            for line in raw.split("\r\n"):
                splitted = line.split(" : ")
                self.soap_objects[splitted[0]] = splitted[1]
        self._first_output_name = None
        for soap_name, soap_type in self.soap_objects.items():
            if soap_type.startswith('output.'):
                self._first_output_name = soap_name
                break

    def uptime(self) -> Type[timedelta]:
        """
        Observing a decreasing uptime is interpreted as an instance reboot ;
        in that case we update the list of soap objects cached internally.

        :return timedelta: the connected Liquidsoap instance's uptime
        """
        self._lock.acquire()
        raw_uptime = self._command("uptime")
        if raw_uptime:
            parsed = self.UPTIME_PATTERN.match(raw_uptime)
        else:
            parsed = None
        if parsed:
            uptime = timedelta(
                days    = int(parsed.group(1)),
                hours   = int(parsed.group(2)),
                minutes = int(parsed.group(3)),
                seconds = int(parsed.group(4)),
            )
            if not self._soaps_updated_at or uptime < self._soaps_updated_at:
                self._update_soaps()
                self._soaps_updated_at = uptime
        else:
            uptime = timedelta()
            log.error("Cannot parse uptime: %r", raw_uptime)

        self._lock.release()
        return uptime

    def current(self) -> dict:
        """
        :return dict: metadata of what's currently playing
        """
        uptime = self.uptime()
        current_rid = self._command("request.on_air")
        if current_rid:
            raw = self._command("request.metadata " + current_rid)
            if raw:
                metadata = self._metadata_to_dict(raw)
            else:
                metadata = {}
        else:
            metadata = self._find_active_source()
            metadata.update(self._read_output_metadata())

        if 'on_air' in metadata:
            metadata['on_air'] = to_datetime(metadata['on_air']).isoformat()

        metadata['uptime'] = str(uptime)
        return metadata

    @classmethod
    def _metadata_to_dict(cls, raw) -> dict:
        metadata = {}
        for line in raw.split("\n"):
            parsed = cls.METADATA_PATTERN.match(line)
            if parsed:
                metadata[parsed.group(1)] = parsed.group(2)
            else:
                log.warning("Can't parse metadata item: %r", line)
        return metadata

    def _find_active_source(self) -> dict:
        """
        May return an empty dict when nothing is found
        """
        metadata = {}
        active_source = None
        status = None
        self._lock.acquire()
        if self._latest_active_source:
            # the most common case: it's still playing
            status = self._get_active_status(self._latest_active_source)
            if status:
                active_source = self._latest_active_source
                log.debug("re-using _latest_active_source")
        if not active_source:
            for src in self.soap_objects:
                status = self._get_active_status(src)
                if status:
                    active_source = src
                    break
        if active_source:
            self._latest_active_source = active_source
            metadata['source'] = active_source
            metadata['status'] = status

        self._lock.release()
        return metadata

    STATUS_CHECK = {
        'input.http': lambda s: s.startswith("connected"),
        'input.https': lambda s: s.startswith("connected"),
        'input.harbor': lambda s: s.startswith("source client connected"),
        'input.harbor.ssl': lambda s: s.startswith("source client connected"),
    }

    def _get_active_status(self, source:str) -> Optional[str]:
        """
        :param source:str: source name
        :return str: result of source's ``status`` command / ``None`` if source is not active.
        """
        source_type = self.soap_objects[source]
        if source_type in self.STATUS_CHECK:
            status = self._command(source + ".status")
            try:
                if self.STATUS_CHECK[source_type](status):
                    return status
                else:
                    return None
            except Exception as exc:
                log.debug(exc)
        else:
            log.debug("Don't know how to check %s", source_type)
        return None

    def _read_output_metadata(self) -> dict:
        """
        Some inputs don't have a ``.metadata`` command. When they're playing,
        the only way to fetch current metadata is to ask an output.
        """
        if self._first_output_name:
            all_metadata = self._command(self._first_output_name + '.metadata')
            separator = "--- 1 ---\n"
            if all_metadata:
                index = all_metadata.find(separator)
                if index >= 0:
                    index += len(separator)
                    return self._metadata_to_dict(all_metadata[index:])
        return {}

    def skip(self):
        if self._first_output_name:
            self._command(self._first_output_name + '.skip')

    def remaining(self) -> Optional[float]:
        if self._first_output_name:
            raw = self._command(self._first_output_name + '.remaining')
            if raw:
                try:
                    return float(raw)
                except ValueError:
                    pass
        return None


class EmptyConnector(TelnetConnector):
    def __init__(self):
        self.started_at = datetime.now()

    def uptime(self):
        return datetime.now() - self.started_at

    def skip(self):
        pass

    def remaining(self):
        return None

    def current(self):
        return {
            'on_air': self.started_at.isoformat(),
            'uptime': str(self.uptime()),
            'source': "unknown",
            'status': "please configure Showergel's [liquidsoap] section",
        }


class Connection:
    """
    This is both a Liquidsoap connector factory and a singleton holder.
    **Call ``Connection.setup(config=...)`` when starting showergel**.

    see TelnetConnector, showergel.demo.FakeLiquidsoapConnector,
    showergel.demo.DemoLiquidsoapConnector
    """
    _instance = None

    @classmethod
    def setup(cls, config:dict=None):
        if config:
            method = config.get('liquidsoap.method')
            if method == 'none':
                cls._instance = EmptyConnector()
            elif method == 'demo':
                from showergel.demo import DemoLiquidsoapConnector
                cls._instance = DemoLiquidsoapConnector()
            elif method == 'telnet':
                cls._instance = TelnetConnector(config)
            else:
                log.warning("Unknown method %s. Only 'demo' or 'telnet' are supported.", method)
                log.warning("Falling back to FakeLiquidsoapConnector: current playout info will be incorrect.")

        if cls._instance is None:
            from showergel.demo import FakeLiquidsoapConnector
            cls._instance = FakeLiquidsoapConnector()

    @classmethod
    def get(cls) -> Type[TelnetConnector]:
        if cls._instance is None:
            raise RuntimeError("Please call Connection.setup(config=...) first")
        return cls._instance


# test tool against a real Liquidsoap instance:
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    conn = TelnetConnector({
        "liquidsoap.host": "192.168.1.33",
        "liquidsoap.port": "1234",
        'metadata_log.extra_fields': [],
    })
    import time
    while True:
        print(conn.current())
        time.sleep(1.)
