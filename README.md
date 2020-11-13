[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
![Build][build-shield]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">um-pep-engine</h3>
  <p align="center">
    Policy Enforcement Point
  </p>
</p>

<!-- GETTING STARTED -->

## Getting Started

This Policy Enforcement Point is a variation of the EOEPCA's PEP Building Block [EOEPCA Project Repository](https://github.com/EOEPCA/)
To get a local copy up and running follow these steps.

### Prerequisites

Required software:

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org//)

### Installation

1. Clone the repo

```sh
git clone https://github.com/ec-nextgeoss/um-pep-engine.git
```

2. Change local directory

```sh
cd um-pep-engine
```
## Dependencies
The PEP is written and tested for python 3.6.9, and has all dependencies listed in src/requirements.txt

## Configuration

The PEP gets all its configuration from the file located under `config/config.json`.
The parameters that are accepted, and their meaning, are as follows:
- **realm**: 'realm' parameter answered for each UMA ticket. Default is "eoepca"
- **auth_server_url**: complete url (with "https") of the Authorization server (Gluu).
- **proxy_endpoints**: array of back-end services for which the PEP acts as a proxy. Each JSON Object defined inside this field has the following subfields:
  - **base_url**: URL prefix for the requests (i.e. <pep>/<base_url>/<path> redirects to <resource_server_endpoint>/<path>
  - **resource_server_endpoint**: Complete url (with "https" and any port) of the Resource Server to protect with this PEP.
- **service_host**: Host for the proxy to listen on. For example, "0.0.0.0" will listen on all interfaces
- **service_port**: Port for the proxy to listen on. By default, **5566**. Keep in mind you will also have to edit the docker file if you intend to use a different port.
- **s_margin_rpt_valid**: An integer representing how many seconds of "margin" do we want when checking RPT. For example, using **5** will make sure the provided RPT is valid now AND AT LEAST in the next 5 seconds.
- **check_ssl_certs**: Toggle on/off (bool) to check certificates in all requests. This should be forced to True in a production environment
- **use_threads**: Toggle on/off (bool) the usage of threads for the proxy. Recommended to be left as True.
- **debug_mode**: Toggle on/off (bool) a debug mode of Flask. In a production environment, this should be false.
- **client_id**: string indicating a client_id for an already registered and configured client. Use the same client_id used in ID4EO where you configure the resources.
- **client_secret**: string indicating the client secret for the client_id. Use the one that corresponds to the client_id used for ID4EO

## Usage & functionality

For simplicity, docker is the best approach to run. First build the image (make sure you are in the folder where Dockerfile is):

```sh
docker build -t nextgeoss-pep .
```

Then simply run:
```sh
docker run -p 5566:5566 -d nextgeoss-pep
```

If by any reason you are unable to bind port 5566, you can use a different one:

```sh
docker run -p <desired-port>:5566 -d nextgeoss-pep
```

If this is running in a development environment without proper DNS setup, add the following to your docker run command:
```sh
--add-host <auth-server-dns>:<your-ip>
```

When launched, the PEP will answer to all requests that start with the configured path. These answers will come in the form of UMA tickets (if there are no RPT provided, or an invalid one is used).
In case the request is accompained by an "Authorization: Bearer <valid_RPT>", the PEP will make a request to the resource server, for the resource located exactly at the path requested (minus the configured at config), and return the resource's server answer.

Examples, given the example values of:
- path configured: "/pep"
- PEP is at pep.domain.com/pep
- Resource server is at remote.server.com

| Token | Request to PEP | PEP Action | PEP answer |
|-------|---------|------------|--------------|
| No RPT | pep.domain.com | None (request does not get to PEP endpoint) | None (the PEP doesn't see this request) |
| No RPT | pep.domain.com/pep/thing | Generate ticket for "/thing" | 401 + ticket |
| Valid RPT for "/thing" | pep.domain.com/pep/thing | Request to remote.server.com/thing | Contents of remote.server.com/thing |
| Valid RPT for "/thing" | pep.domain.com/pep/different | Generate ticket for "/different" | 401 + ticket |
| INVALID RPT for "/thing" | pep.domain.com/pep/thing | Generate ticket for "/thing" | 401 + ticket |
| No RPT | pep.domain.com/pep/thing/with/large/path | Generate ticket for "/thing/with/large/path" | 401 + ticket |
| Valid RPT for "/thing/with/large/path" | pep.domain.com/pep/thing/with/large/path | Request to remote.server.com/thing/with/large/path | Contents of remote.server.com/thing/with/large/path |

<!-- LICENSE -->

## License

Distributed under the Apache-2.0 License. See `LICENSE` for more information.


[contributors-shield]: https://img.shields.io/github/contributors/EOEPCA/um-pep-engine.svg?style=flat-square
[contributors-url]: https://github.com/EOEPCA/um-pep-engine/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/EOEPCA/um-pep-engine.svg?style=flat-square
[forks-url]: https://github.com/EOEPCA/um-pep-engine/network/members
[stars-shield]: https://img.shields.io/github/stars/EOEPCA/um-pep-engine.svg?style=flat-square
[stars-url]: https://github.com/EOEPCA/um-pep-engine/stargazers
[issues-shield]: https://img.shields.io/github/issues/EOEPCA/um-pep-engine.svg?style=flat-square
[issues-url]: https://github.com/EOEPCA/um-pep-engine/issues
[license-shield]: https://img.shields.io/github/license/EOEPCA/um-pep-engine.svg?style=flat-square
[license-url]: https://github.com/EOEPCA/um-pep-engine/blob/master/LICENSE
[build-shield]: https://www.travis-ci.com/EOEPCA/um-pep-engine.svg?branch=master
