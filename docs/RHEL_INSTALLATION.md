# Rocky Linux and RHEL-compatible installation

Install the operating-system fontconfig configuration used by the bundled
Graphviz renderer:

```bash
sudo dnf install fontconfig
```

For the portable archive, verify the SHA-256 inventory, extract it, then run:

```bash
./nmap-flow-analyzer-1.6.0-rc1-rhel-x64/nmap-flow-analyzer doctor
```

For the RPM:

```bash
sudo rpm -ivh nmap-flow-analyzer-1.6.0-rc1-rhel-x64.rpm
nmap-flow-analyzer preflight
```

Remove it with `sudo rpm -e nmap-flow-analyzer`. Use only RHEL artifacts built
and tested in the Rocky Linux 9 gate.
