# SDN Data Plane Generator

This tool will generate a data plane (hosts and switches) from a [DOT Language][6] topology definition, if specified this will also sniff the packets from each switch network interface and will send those packets to a central analyzer.

## Getting Started

The hosts are created as Docker containers using [Containernet][1] and a default Docker image which can be changed as required.

## Prerequisites

* SDN Controller (just tested with [ONOS][7])

* [Containernet][1], please refer to Containernet [Installation][3] for detailed instructions on how to install it.

* Additional is also required to install [pydot][2].

The easiest way is using [`pip`][5].

```
$ pip install pydot
```

## How to Run

An example [topology.dot](topology.dot) file is included, so you can use just running:

```
$ python create_topology.py
```

## Built With

* [Containernet][1] - Mininet fork that allows to use Docker containers as hosts in emulated networks
* [pydot][2] - Python library used to parse DOT files

## Authors
* **Jose Reyes** - [@letitbeat][4]
## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

[1]: https://github.com/containernet/containernet
[2]: https://github.com/pydot/pydot
[3]: https://github.com/containernet/containernet#installation
[4]: https://github.com/letitbeat
[5]: https://github.com/pypa/pip
[6]: https://en.wikipedia.org/wiki/DOT_%28graph_description_language%29
[7]: https://onosproject.org/software/

