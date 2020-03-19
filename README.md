<!--
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** template-svce, twitter_handle, email
-->

<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
![Build][build-shield]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/EOEPCA/template-svce">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">template-service</h3>

  <p align="center">
    Template for developing an EOEPCA Service
    <br />
    <a href="https://github.com/EOEPCA/template-svce"><strong>Explore the docs »</strong></a>
    <br />
    <a href="https://github.com/EOEPCA/template-svce">View Demo</a>
    ·
    <a href="https://github.com/EOEPCA/template-svce/issues">Report Bug</a>
    ·
    <a href="https://github.com/EOEPCA/template-svce/issues">Request Feature</a>
  </p>
</p>

## Steps to use this template
- Replace all "um-service-template" in .travis.yml with your repository's name
- Replace the ports in .travis.yml and Dockerfile to fit your service's ports
- Edit docs to fit your repository
- Replace code and requirements.txt in src by your own! Make sure to use pytest, or replace it in the .travis.yml to use the correct testing suite 
- Un-comment the "notifications" segment in .travis.yml, and input the correct data for slack and/or emails you want to notify

- setup the following variables (in travis webpage, for this project) to ensure travis automated CI works (https://travis-ci.com/github/EOEPCA/<project>/settings):
    1. GH_REPOS_NAME (this repo's name)
    2. GH_USER_NAME (GitHub name for the responsible of this module)
    3. GH_USER_EMAIL (GitHub email for the responsible of this module)
    4. DOCKER_USERNAME (Username of a user with write privileges on EOEPCA in dockerhub) MAKE SURE TO MAKE THIS VARIABLE HIDDEN IN LOGS
    5. DOCKER_PASSWORD (password for the username) MAKE SURE TO MAKE THIS VARIABLE HIDDEN IN LOGS

- Edit readme to fit your repository, and delete this part!

## Table of Contents

- [Steps to use this template](#steps-to-use-this-template)
- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Testing](#testing)
- [Documentation](#documentation)
- [Usage](#usage)
  - [Running the template service](#running-the-template-service)
  - [Upgrading Gradle Wrapper](#upgrading-gradle-wrapper)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Here's a blank template to get started:
**To avoid retyping too much info. Do a search and replace with your text editor for the following:**
`template-svce`, `twitter_handle`, `email`

### Built With

- [Javalin framework](https://javalin.io/)
- [Log4j2](https://logging.apache.org/log4j/2.x/) + [YAML](https://yaml.org/)
- [Junit 5](https://junit.org/junit5/)

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

- [Vagrant](https://www.vagrantup.com/docs/installation/)
- [EOEPCA Development Environment](https://github.com/EOEPCA/dev-env)

### Installation

1. Get into EOEPCA's development environment

```sh
vagrant ssh
```

3. Clone the repo

```sh
git clone https://github.com/EOEPCA/template-svce.git
```

4. Change local directory

```sh
cd template-service
```

### Testing

- `./gradlew build` runs only the unit tests
- `./gradlew integrationTest` runs only the integration tests (it compiles all source code beforehand). It does not package or deploy a build.
  This is assumed to have been done in a prior build pipeline step.

## Documentation

The component documentation can be found at https://eoepca.github.io/template-svce/.

<!-- USAGE EXAMPLES -->

## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

### Running the template service

Just execute the run task in Gradle

```sh
./gradlew run
```

### Upgrading Gradle Wrapper

Change the version number in the `build.gradle` wrapper task then run:

```sh
./gradlew wrapper --gradle-version=4.10.2 --distribution-type=bin
```

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/EOEPCA/template-svce/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the Apache-2.0 License. See `LICENSE` for more information.

## Contact

[EOEPCA mailbox](eoepca.systemteam@telespazio.com)

Project Link: [https://github.com/EOEPCA/um-pylibrary-template](https://github.com/EOEPCA/um-pylibrary-template)

## Acknowledgements

- README.md is based on [this template](https://github.com/othneildrew/Best-README-Template) by [Othneil Drew](https://github.com/othneildrew).


[contributors-shield]: https://img.shields.io/github/contributors/EOEPCA/um-pylibrary-template.svg?style=flat-square
[contributors-url]: https://github.com/EOEPCA/um-pylibrary-template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/EOEPCA/um-pylibrary-template.svg?style=flat-square
[forks-url]: https://github.com/EOEPCA/um-pylibrary-template/network/members
[stars-shield]: https://img.shields.io/github/stars/EOEPCA/um-pylibrary-template.svg?style=flat-square
[stars-url]: https://github.com/EOEPCA/um-pylibrary-template/stargazers
[issues-shield]: https://img.shields.io/github/issues/EOEPCA/um-pylibrary-template.svg?style=flat-square
[issues-url]: https://github.com/EOEPCA/um-pylibrary-template/issues
[license-shield]: https://img.shields.io/github/license/EOEPCA/um-pylibrary-template.svg?style=flat-square
[license-url]: https://github.com/EOEPCA/um-pylibrary-template/blob/master/LICENSE
[build-shield]: https://www.travis-ci.com/EOEPCA/um-pylibrary-template.svg?branch=master