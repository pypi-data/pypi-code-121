import select
import six
from collections import defaultdict

def is_poll_available():
    return hasattr(select, "poll")


if is_poll_available():
    class Waiter(object):
        def __init__(self, rfds, wfds, xfds):
                poller = select.poll()
                self.fds = {x.fileno(): x for x in (rfds + wfds + xfds)}
                flags_per_fd = defaultdict(int)
                for rfd in rfds:
                    flags_per_fd[rfd] = flags_per_fd[rfd] | select.POLLIN | select.POLLPRI
                for wfd in wfds:
                    flags_per_fd[wfd] = flags_per_fd[wfd] | select.POLLOUT
                for xfd in xfds:
                    flags_per_fd[xfd] = flags_per_fd[xfd] | select.POLLHUP | select.POLLERR

                for fd, flags in six.iteritems(flags_per_fd):
                    poller.register(fd, flags)
                self.poller = poller

        def wait(self, timeout):
            rfdsout, wfdsout, xfdsout = [], [], []
            for (fd, bitmask) in self.poller.poll(timeout):
                if bitmask & select.POLLIN or bitmask & select.POLLPRI:
                    rfdsout.append(self.fds[fd])
                if bitmask & select.POLLOUT:
                    wfdsout.append(self.fds[fd])
                if bitmask & select.POLLHUP or bitmask & select.POLLERR:
                    xfdsout.append(self.fds[fd])
            return rfdsout, wfdsout, xfdsout

else:
    class Waiter(object):
        def __init__(self, rfds, wfds, xfds):
            self.rfds, self.wfds, self.xfds = rfds, wfds, xfds

        def wait(self, timeout):
            return select.select(self.rfds, self.wfds, self.xfds, timeout)

