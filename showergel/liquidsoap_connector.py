import logging
import re
from typing import Type, Optional, List
from datetime import timedelta, datetime
from threading import RLock
from telnetlib import Telnet
from time import sleep

import arrow

log = logging.getLogger(__name__)

from telnetlib import Telnet, theNULL, IAC, DO, DONT, WILL, WONT, SE, SB, NOOPT, _TelnetSelector, selectors
class FasterTelnet(Telnet):
    """This is needed for Python versions affected by https://bugs.python.org/issue46740
    """

    def fill_rawq(self):
        """Fill raw queue from exactly one recv() system call.

        Block if no data is immediately available.  Set self.eof when
        connection is closed.

        """
        if self.irawq >= len(self.rawq):
            self.rawq = b''
            self.irawq = 0
        buf = self.sock.recv(4096)
        self.msg("recv %r", buf)
        self.eof = (not buf)
        self.rawq = buf

    def process_rawq(self):
        """Transfer from raw queue to cooked queue.

        Set self.eof when connection is closed.  Don't block unless in
        the midst of an IAC sequence.

        """
        buf = [b'', b'']
        try:
            while self.rawq:
                if not self.iacseq:
                    slice = self._next_nonIAC_slice()
                    if slice:
                        buf[self.sb] = buf[self.sb] + slice
                    else:
                        c = self.rawq_getchar()
                        if c == theNULL:
                            continue
                        elif c == b"\021":
                            continue
                        else:
                            self.iacseq += c
                elif len(self.iacseq) == 1:
                    c = self.rawq_getchar()
                    # 'IAC: IAC CMD [OPTION only for WILL/WONT/DO/DONT]'
                    if c in (DO, DONT, WILL, WONT):
                        self.iacseq += c
                        continue

                    self.iacseq = b''
                    if c == IAC:
                        buf[self.sb] = buf[self.sb] + c
                    else:
                        if c == SB: # SB ... SE start.
                            self.sb = 1
                            self.sbdataq = b''
                        elif c == SE:
                            self.sb = 0
                            self.sbdataq = self.sbdataq + buf[1]
                            buf[1] = b''
                        if self.option_callback:
                            # Callback is supposed to look into
                            # the sbdataq
                            self.option_callback(self.sock, c, NOOPT)
                        else:
                            # We can't offer automatic processing of
                            # suboptions. Alas, we should not get any
                            # unless we did a WILL/DO before.
                            self.msg('IAC %d not recognized' % ord(c))
                elif len(self.iacseq) == 2:
                    c = self.rawq_getchar()
                    cmd = self.iacseq[1:2]
                    self.iacseq = b''
                    opt = c
                    if cmd in (DO, DONT):
                        self.msg('IAC %s %d',
                            cmd == DO and 'DO' or 'DONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.sock.sendall(IAC + WONT + opt)
                    elif cmd in (WILL, WONT):
                        self.msg('IAC %s %d',
                            cmd == WILL and 'WILL' or 'WONT', ord(opt))
                        if self.option_callback:
                            self.option_callback(self.sock, cmd, opt)
                        else:
                            self.sock.sendall(IAC + DONT + opt)
        except EOFError: # raised by self.rawq_getchar()
            self.iacseq = b'' # Reset on EOF
            self.sb = 0
        self.cookedq = self.cookedq + buf[0]
        self.sbdataq = self.sbdataq + buf[1]

    def _next_nonIAC_slice(self):
        """Return next non-IAC characters from raw queue.
        Assumes the caller checked the raw queue is not empty.
        """
        next_i = self.irawq
        max_i = len(self.rawq)
        while next_i < max_i:
            c = self.rawq[next_i]
            if c == theNULL[0] or c == 0x11 or c == IAC[0]:
                break
            next_i += 1

        if next_i == self.irawq:
            return None
        else:
            slice = self.rawq[self.irawq:next_i]
            self.irawq = next_i
            if next_i == max_i:
                self.rawq = b''
                self.irawq = 0
            return slice

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

        self._connection = FasterTelnet()
        self._connect()

        self.commands = []
        self.soap_objects = {}
        self._first_output_name = None
        self._soaps_updated_at = None
        self.connected_liquidsoap_version = None
        self.uptime()
        self._latest_active_source = None

    def _connect(self, reconnect=False):
        self._lock.acquire()
        if reconnect:
            self._connection.close()
            self._connection = FasterTelnet()
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

    def _decode(self, raw:str) -> List[str]:
        """
        We split Liquidsoap's raw response before unidecoding it because
        sometimes a line might contain incorrect Unicode - this is typically
        caused byweird metadata (embedded images, etc.). In that case, the
        line is just ignored.
        """
        response = []
        for line in raw.split(b"\n"):
            try:
                response.append(line.strip(b"\r").decode('utf8'))
            except UnicodeDecodeError as error:
                # leave logging for experiments, otherwise it can quickly fill the log
                #log.debug("Error while decoding %r", line)
                #log.debug("%s", error)
                pass
        return response

    def command(self, command:str) -> Optional[List[str]]:
        """
        Run a Liquidsoap command, and return its result.
        """
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
                raw = self._connection.read_until(b'END\r\n').rstrip(b"END\r\n").strip(b"\r\n")
                if raw == b"Connection timed out.. Bye!":
                    raise EOFError()
                response = self._decode(raw)
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
        self.commands = []
        raw = self.command("help")
        if raw:
            for line in raw:
                if line.startswith("|"):
                    command = line[2:]
                    if not command.startswith('help ') and command not in (
                        'exit', 'list', 'quit', 'uptime', 'version'
                    ):
                        self.commands.append(command)

        self.soap_objects = {}
        raw = self.command("list")
        if raw:
            for line in raw:
                splitted = line.split(" : ")
                try:
                    self.soap_objects[splitted[0]] = splitted[1]
                except IndexError:
                    # might happen with LS>2.0.3 #37
                    log.error("can't split %s", line)
                    break

        self._first_output_name = None
        for soap_name, soap_type in self.soap_objects.items():
            if soap_type.startswith('output.'):
                self._first_output_name = soap_name
                break

        self.connected_liquidsoap_version = self.command("version")[0]

    def uptime(self) -> Type[timedelta]:
        """
        Observing a decreasing uptime is interpreted as an instance reboot ;
        in that case we update the list of soap objects cached internally.

        :return timedelta: the connected Liquidsoap instance's uptime
        """
        self._lock.acquire()
        raw_uptime = self.command("uptime")
        if raw_uptime:
            parsed = self.UPTIME_PATTERN.match(raw_uptime[0])
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
        **Note**: `request.on_air` seems to provide an RID usable with
        `request.metadata RID`, but it may also provide *multiple* RIDs (like
        `4 9`), including one that is not playing. So we only rely on the first
        output's `metadata` command.

        :return dict: metadata of what's currently playing
        """
        uptime = self.uptime()
        # FIXME this is really inefficient - linked to #37
        metadata = self._find_active_source()
        output_metadata = self._read_output_metadata()
        metadata.update(output_metadata)

        if 'on_air' in metadata:
            metadata['on_air'] = arrow.get(metadata['on_air'], tzinfo='local').isoformat()

        metadata['uptime'] = str(uptime)
        return metadata

    @classmethod
    def _metadata_to_dict(cls, raw) -> dict:
        metadata = {}
        for line in raw:
            if line:
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
            status = self.command(source + ".status")
            try:
                if self.STATUS_CHECK[source_type](status[0]):
                    return status
                else:
                    return None
            except Exception as exc:
                log.debug(exc)
        return None

    def _read_output_metadata(self) -> dict:
        """
        Some inputs don't have a ``.metadata`` command. When they're playing,
        the only way to fetch current metadata is to ask an output.
        """
        if self._first_output_name:
            all_metadata = self.command(self._first_output_name + '.metadata')
            if all_metadata:
                try:
                    index = all_metadata.index("--- 1 ---")
                    return self._metadata_to_dict(all_metadata[index+1:])
                except ValueError:
                    pass
        return {}

    def skip(self):
        if self._first_output_name:
            self.command(self._first_output_name + '.skip')

    def remaining(self) -> Optional[float]:
        if self._first_output_name:
            raw = self.command(self._first_output_name + '.remaining')
            if raw:
                try:
                    return float(raw[0])
                except (ValueError, IndexError):
                    pass
        return None


class EmptyConnector(TelnetConnector):
    def __init__(self):
        self.connected_liquidsoap_version = "[can't connect - missing configuration]"
        self.started_at = datetime.utcnow()
        self.commands = []

    def command(self, command:str) -> str:
        return ""

    def uptime(self):
        return datetime.utcnow() - self.started_at

    def skip(self):
        pass

    def remaining(self):
        return None

    def current(self):
        return {
            'on_air': datetime.utcnow().isoformat(),
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
        "liquidsoap.host": "127.0.0.1",
        "liquidsoap.port": "1234",
        'metadata_log.extra_fields': [],
    })
    import time
    print(f"connected to {conn.connected_liquidsoap_version}")
    while True:
        print(conn.current())
        time.sleep(1.)
