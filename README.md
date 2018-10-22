VirtParade
===

An easy-use tool help you create kvm virtual machines gracefully with simple configuration on Linux servers.

## Requirements

- python >= 3.4
- virsh (libvirt-client)
- qemu-img
- virt-resize (libguestfs-tools-c)
- guestmount (libguestfs-tools-c)
- guestunmount (libguestfs-tools-c)

## Installation

From PyPi:

```bash
pip3 install virtparade
```

Manual

```bash
python3 setup.py install
```

Copy sample config directory to `/etc`

```bash
cp -a ./virtparade-config-sample /etc/virtparade
```

## VirtParade running roadmap

1. check `/etc/virtparade/config.yml`
2. Build your first instance(if it is not exist)
3. Create disks: if the disk is based on image(have the "image" property), copy and resize the image, expand the filesystem, convert image format. If it is the first disk and is based on image, mount the disk to a temp directory and run init scripts.
4. Generate libvirt instance XML file from `/etc/virtparade/instance.xml`
5. Define and start the instance
6. Show instance VNC port
7. Build you seconde instance
8. ...

Init scripts:

1. Run the main script: `/etc/virtparade/script.d/${your_image_name}/main.sh ${mountdir}`
2. Run the network script multiple times(depend on how many addresses you defined in `/etc/virtparade/config.yml` -> instances.network.addresses): `/etc/virtparade/script.d/${your_image_name}/network.sh ${mountdir} ${index} ${ip} ${prefix} ${gateway}`
3. Run the dns script multiple times(depend on how many dns addresses you defined in `/etc/virtparade/config.yml` -> instances.network.dns): `/etc/virtparade/script.d/${your_image_name}/dns.sh ${mountdir} ${index} ${dns_address}`

## Configuration

See config sample in `virtparade-config-sample`.

/etc/virtparade/config.yml

```yaml
images:                                 # required; image definitions
  centos7:                              # required; image name
    path: /opt/images/centos7.qcow2     # required; image path
    format: qcow2                       # required; image format, supported formats: raw, qcow, qcow2, vhdx, vmdk, you can check your image format via `qemu-img info centos7.qcow2`
    root_dev: /dev/sda1                 # required; image expand partition, you can use `virt-filesystems -a image_path --filesystems -l` to select a device
  ubuntu1604:
    path: /opt/images/ubuntu1604.qcow2
    format: qcow2
    root_dev: /dev/sda1
  freebsd_iso:
    path: /opt/images/freebsd.iso
    format: raw
    root_dev: /dev/sda

instances:                              # required; instance definitions
  - name: mycentos7                     # required; instance name
    vcpu: 4                             # required; vcpu number
    memory: 4                           # required; memory size(GiB)
    disks:                              # required; disks definitions, at least on disk should be assigned
      - path: /data/test1.vmdk          # required; dest disk path
        format: vmdk                    # required; disk format, supported formats are same to image format
        image: centos7                  # optional; the disk would be created based on image name defined earlier
        size: 40                        # required, except when image is specified; unit: GiB
      - path: /data/test1-disk.qcow2    # optional; disk2
        format: qcow2
        size: 40
    cdrom_image: freebsd_iso            # optional; insert a cdrom to the virtual machine with iso file defined in images
    network:                            # required; network definitions
      addresses:                        # required; network address definitions
        - ip: 10.246.214.218            # required; ip address
          prefix: 24                    # required; cidr
          gateway: 10.246.214.1         # optional; network gateway, only on could be specified through all addresses
          network_bridge: br-mgmt       # required; network bridge on host
      dns:                              # optional; network dns addresses
        - 192.168.102.81
```

Write you own image init script in `/etc/virtparade/script.d`

## Run VirtParade

Show help

```bash
virtparade --help
```

Test configuration

```bash
virtparade test
```

Build instances

```bash
sudo virtparade run --all                  # build all instances
sudo virtparade run mycentos7 myubuntu1604 # build specfied instances
```

Immediately stop after guestmount the system disk(the first disk), it's useful when you want to write/test you init script or debug the image.

```bash
sudo virtparade mount mycentos7
```

## Contributing

Just fork the repositry and open a pull request with your changes.

## License

MIT