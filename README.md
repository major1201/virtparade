VirtParade
===

An easy-use tool helps you create kvm virtual machines gracefully with simple configurations on Linux servers.

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

1. Check `/etc/virtparade/config.yml`
2. Build your first instance(if it is not exist)
3. Create disks: if the disk is based on image(have the `image` property), copy and resize the image, expand the filesystem, convert image format. If it is the first disk and is based on image, mount the disk to a temp directory and run init scripts.
4. Generate libvirt instance XML file from the Jinja2 template file: `/etc/virtparade/instance.xml`
5. Define and start the instance
6. Show instance VNC port
7. Build your second instance
8. ...

Init scripts:

1. Run the main script: `/etc/virtparade/script.d/${your_image_name}/main.sh ${mountdir}`
2. Run the network script multiple times(depend on how many addresses you have defined in `/etc/virtparade/config.yml` -> instances.network.addresses): `/etc/virtparade/script.d/${your_image_name}/network.sh ${mountdir} ${index} ${ip} ${prefix} ${gateway}`
3. Run the dns script multiple times(depend on how many dns addresses you have defined in `/etc/virtparade/config.yml` -> instances.network.dns): `/etc/virtparade/script.d/${your_image_name}/dns.sh ${mountdir} ${index} ${dns_address}`

## Configuration

See config sample in `virtparade-config-sample`.

/etc/virtparade/config.yml

```yaml
debug: true

images:                                 # required; image definitions
  centos7:                              # required; image name
    path: /opt/images/centos7.qcow2     # required; image path
    format: qcow2                       # required; image format, supported formats: raw, qcow, qcow2, vhdx, vmdk
    root_dev: /dev/sda1                 # required; image expand partition, you can use `virt-filesystems -a image_path --filesystems -l` to select a device
    need_expand_filesystem: true        # optional; default: false; whether to `virt-resize` a image or not, depending you image file
    run_script: true                    # optional; default: true; whether to image profile scripts in ./script.d/${image_name} or not
  coreos:
    path: /opt/images/coreos_production_qemu_image.img
    format: qcow2
    root_dev: /dev/sda9
    mount:                              # optional; specify guestmount --mount argument
      - /dev/sda9                       #   according to guestmount man page, format should be:
      - /dev/sda3:/usr:ro               #     dev[:mnt[:opts[:fstype]] Mount dev on mnt (if omitted, /)

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
      - type: block                     # optional; default: file; current support type: file, block
        block: /dev/sda2                # required; block devide path
    cdroms:                             # optional; insert cdroms to the virtual machine with iso file
      - type: file                      # optional; default: file; file or block
        path: /opt/images/centos7.iso   # required; file or block path
    network:                            # required; network definitions
      addresses:                        # required; network address definitions
        - ip: 10.246.214.218            # optional; ip address
          prefix: 24                    # optional; cidr
          gateway: 10.246.214.1         # optional; network gateway, only on could be specified through all addresses
          network_bridge: br-mgmt       # required; network bridge on host
      dns:                              # optional; network dns addresses
        - 192.168.102.81
    autostart: true                     # optional; default: false; auto start on host boot
```

Write your own image init script in `/etc/virtparade/script.d`

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

Immediately stop after `guestmount`ing the system disk(the first disk), it's useful when you want to write/test your init script or debug the image.

```bash
sudo virtparade mount mycentos7
```

## Contributing

Just fork the repository and open a pull request with your changes.

## License

MIT
