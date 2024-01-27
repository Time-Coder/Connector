# Connector -- A lightweight network programming tool for Python

**Connector** is a lightweight network programming tool for Python 3. **Connector** will greatly simplify Client/Server mode's network programming. **Connector** can help a lot in any situations that need message exchanging. All message communication will become very easy. In detail, it can do following things: 

1. Share/Send variables between different threads/processes/programs/computers.
2. Put/Get files/folders to/from different programs on different computers.
3. RPC (Remote Procedure Call)

**Connector** only provide 2 classes for user to use: ``Server`` and ``Client``. And these two classes make everything easy. Let's getting start!

In addition, You can:

* find full documentation at: [https://connector.readthedocs.io/en/latest](https://connector.readthedocs.io/en/latest)
* find PyPI index at: [https://pypi.org/project/tcp-connector](https://pypi.org/project/tcp-connector)

## Release Note

### 0.0.7
* Reconstruct and optimize all code.

### 0.0.5
* Support finding default IP on Linux by introducing `netifaces` module;
* Support sending lambda function by changing module `cloudpick` to `dill`;
* Use uuid for session id;
* Remove unneeded queue after a session finished.

### 0.0.4
* First stable release