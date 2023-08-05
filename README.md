# The toolchain – Clotilde and Overseer and Revolori

Please cite our accompanying paper when making use of the toolchain:

**Zieglmeier, Valentin**: "The Inverse Transparency Toolchain: A Fully Integrated and Quickly Deployable Data Usage Logging Infrastructure." *Software Impacts* 17 (Sept. 2023), Article 100554.
DOI: [10.1016/j.simpa.2023.100554](https://doi.org/10.1016/j.simpa.2023.100554).
[*[BibTeX]*](https://mediatum.ub.tum.de/export/1717184/bibtex)


## About

The Inverse Transparency Toolchain—consisting of Overseer, Clotilde, and Revolori—is a flexible solution for research, teaching, and prototyping in the context of inverse transparency.

## Deploying with Docker

To build and run the toolchain, use Docker Compose: [documentation and instructions](/run/README.md)

## Tools

- **Overseer – Log Store**: Logs and stores data usages.
    + [Documentation](/overseer-log-store/README.md)
- **Clotilde – Transparency UI**: Makes logged usages of data visible to data owners.
    + [Documentation](/clotilde-web-console/README.md)
- **Revolori – SSO Provider**: User management and authentication.
    + [Documentation](/revolori-sso-provider/README.md)

## Credits

- Clotilde
    + [@vauhochzett](https://github.com/vauhochzett/)
    + [@JCHHeilmann](https://github.com/JCHHeilmann)
    + Patipon Riebpradit
- Overseer
    + [@vauhochzett](https://github.com/vauhochzett/)
    + [@felixschorer](https://github.com/felixschorer)
    + Yiyu Gu
- Revolori
    + [@vauhochzett](https://github.com/vauhochzett/)
    + Stefan Knilling
    + Stefan Madzharov
    + [@hohmannr](https://github.com/hohmannr)
- Automated Docker deployment
    + [@vauhochzett](https://github.com/vauhochzett/)
    + [@hohmannr](https://github.com/hohmannr)
