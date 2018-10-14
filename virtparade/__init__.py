# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import os
import tempfile
import shutil
from collections import Iterable
from .utils import strings, num, setting, logger, objects, system, jinja2


class VirtParadeError(RuntimeError):
    pass


class VirtParade:
    supported_formats = ['raw', 'qcow', 'qcow2', 'vhdx', 'vmdk']

    def __init__(self, conf_dir='/etc/virtparade'):
        self.conf_dir = conf_dir
        self.images = {}
        self.instances = None

        debug = setting.conf.get('debug')
        self.debug = debug if isinstance(debug, bool) else False
        self.parse_config()

    @staticmethod
    def _check_string(val, emsg='error: string'):
        if strings.is_blank(val):
            raise VirtParadeError(emsg)

    @staticmethod
    def _check_int(val, _min=None, _max=None, emsg='error: int'):
        v = num.safe_int(val)
        if _min is not None and v < _min:
            raise VirtParadeError(emsg)
        if _max is not None and v > _max:
            raise VirtParadeError(emsg)

    @staticmethod
    def _check_iterator(val, emsg='error: iterator'):
        if not isinstance(val, Iterable):
            raise VirtParadeError(emsg)

    @staticmethod
    def _check_dict(val, emsg='error: dict'):
        if not isinstance(val, dict):
            raise VirtParadeError(emsg)

    def parse_config(self):
        # images
        setting_images = setting.conf.get('images')
        self._check_dict(setting_images, 'config: images should be dict')
        for name, image in setting_images.items():
            image['name'] = name
            for key in ('path', 'format', 'root_dev'):
                self._check_string(image.get(key), emsg='config: please specify image %s' % key)
            if not os.path.isfile(image['path']):
                raise VirtParadeError('image: image(%s) not exist' % image['path'])
            if not objects.contains(image['format'], *self.supported_formats):
                raise VirtParadeError('image: unknown image format: %s' % image['format'])
        self.images = setting_images

        # instances
        setting_instances = setting.conf.get('instances')
        if setting_instances is None:
            raise VirtParadeError('config: instances not defined')
        for instance in setting_instances:
            # check: name
            for key in ['name']:
                self._check_string(instance.get(key), emsg='config: please specify instance %s' % key)
            # check: vcpu, memory
            for key in ('vcpu', 'memory'):
                self._check_int(instance.get(key), 1, 128, emsg='config: %s should >= 1 and <= 128' % key)
            # check: disk
            disks = instance.get('disks')
            self._check_iterator(disks, emsg='config: disks should be iterable')
            if len(disks) == 0:
                raise VirtParadeError('config: please specify at least one disk')
            for i, disk in enumerate(disks):
                for key in ['path', 'format']:
                    self._check_string(disk.get(key), emsg='config: please specify disk %s' % key)
                if not objects.contains(disk['format'], *self.supported_formats):
                    raise VirtParadeError('disk: unknown disk format: %s' % disk['format'])
                if disk.get('image') is not None:
                    image = self.images.get(disk.get('image'))
                    if image is None:
                        raise VirtParadeError('config: undefined image: %s' % disk.get('image'))
                    disk['image'] = image
                if disk.get('size') is not None or disk.get('image') is None:  # sys disk size is optional, if disk image is defined
                    self._check_int(disk.get('size'), 1, emsg='config: disk size (int) should > 0')
                disk['dev'] = "vd%c" % chr(97 + i)
            # check: cdrom image
            cdrom_image = instance.get('cdrom_image')
            if cdrom_image is not None:
                self._check_string(cdrom_image, 'config: cdrom_image should not be blank')
                image = self.images.get(cdrom_image)
                if image is None:
                    raise VirtParadeError('config: undefined image: %s' % cdrom_image)
                instance['cdrom_image'] = image
            # check: network
            network = instance.get('network')
            self._check_dict(network, 'config: network should be a dict')
            addresses = network.get('addresses')
            self._check_iterator(addresses, 'config: addresses should be iterable')
            for address in addresses:
                for key in ('ip', 'network_bridge'):
                    self._check_string(address.get(key), emsg='config: please specify %s' % key)
                self._check_int(address.get('prefix'), 1, 32, emsg='config: prefix should be in (1, 32)')
                # gateway is optional
                if address.get('gateway') is not None:
                    self._check_string(address.get('gateway'), emsg='config: gateway format error')
            # dns is optional
            dns = network.get('dns')
            if dns is not None:
                self._check_iterator(dns, emsg='config: dns should be iterable')
                for i in dns:
                    self._check_string(i, emsg='config: dns should not be blank')

        self.instances = setting_instances

    @staticmethod
    def get_instances():
        stdout, stderr, rc = system.exec_command('virsh list --all --name')
        if rc != 0:
            raise VirtParadeError('get_instances error: %s' % stderr)
        return list(filter(strings.is_not_blank, stdout.split('\n')))

    def convert_image(self, from_img, from_fmt, to_img, to_fmt):
        cmd = 'qemu-img convert -p -f %s -O %s %s %s' % (from_fmt, to_fmt, from_img, to_img)
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('convert image error, rc: %i' % rc)

    def resize_image(self, image, size):
        cmd = 'qemu-img resize %s %iG' % (image, size)
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('resize image error, rc: %i' % rc)

    def expand_filesystem(self, src, expand_dev, dest, rm_src=True):
        """
        expand the image filesystem

        virt-resize doesn't support in-place expand, so dest image file is required
        :param src: source image
        :param expand_dev: expand partition device, you can run `virt-filesystems -a image --filesystems -l` to decide which part to expand
        :param dest: dest image
        :param rm_src: remove source image after expanded the image or not
        :return:
        """
        shutil.copy(src, dest)
        cmd = 'virt-resize --expand %s %s %s' % (expand_dev, src, dest)
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('expand filesystem error, rc: %i' % rc)
        if rm_src:
            os.remove(src)

    def create_image(self, path, size, image_format):
        cmd = 'qemu-img create -f %s %s %iG' % (image_format, path, size)
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('create image error, rc: %i' % rc)

    def guestmount(self, image, image_format, mountpoint):
        cmd = 'guestmount --format=%s -a %s --rw -i %s' % (image_format, image, mountpoint)
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('guestmount error, rc: %i' % rc)

    def guestunmount(self, mountpoint, rm_mountpoint=False):
        cmd = 'guestunmount %s' % mountpoint
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('guestunmount error, rc: %i' % rc)
        if rm_mountpoint:
            os.rmdir(mountpoint)

    def virsh_define(self, xml_file):
        cmd = 'virsh define %s' % xml_file
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('virsh define error, rc: %i' % rc)

    def virsh_start(self, name):
        cmd = 'virsh start %s' % name
        logger.info('+ %s' % cmd)
        _, _, rc = system.exec_command_std(cmd) if self.debug else system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('virsh start error, rc: %i' % rc)

    @staticmethod
    def virsh_getvncport(name):
        cmd = 'virsh vncdisplay %s' % name
        logger.info('+ %s' % cmd)
        stdout, _, rc = system.exec_command(cmd)
        if rc != 0:
            raise VirtParadeError('virsh vncdisplay error!')
        return stdout

    def mkinstances(self, *names, step_to=None):
        """
        make instances
        :param names: choose inatance name to make, if left empty, all the instances would be run
        :param step_to: choose from ('mount'). mount: instances would be mounted only
        :return:
        """
        exist_instances = self.get_instances()
        for inst in self.instances:
            if len(names) > 0 and not objects.contains(inst['name'], *names):
                continue

            logger.info('Processing instance %s...' % inst['name'])

            if objects.contains(inst['name'], *exist_instances):
                # instance already exists
                logger.warning('instance %s already exists, skipping.' % inst['name'])
                continue

            continue_flag = False
            for disk in inst['disks']:
                if os.path.exists(disk['path']):
                    logger.warning('disk file already exists: %s, skipping.' % disk['path'])
                    continue_flag = True
                    break
            if continue_flag:
                continue

            # create disks
            for i, disk in enumerate(inst['disks']):
                image = disk.get('image')
                if image is None:
                    if step_to == 'mount':
                        logger.info('no disk mounted')
                        return

                    logger.info('creating general disk: %s, size: %iG, format: %s' % (disk['dev'], disk['size'], disk['format']))
                    self.create_image(disk['path'], disk['size'], disk['format'])
                    continue

                logger.info('creating disk: %s' % disk['dev'])

                if disk.get('size') is None:
                    shutil.copy(image['path'], disk['path'])
                else:
                    tempdir = tempfile.mkdtemp(prefix='virtparade-')
                    try:
                        logger.debug('disk exchange temp directory: %s' % tempdir)

                        # create temp image for resizing
                        disk_sys_orig = os.path.join(tempdir, 'image-orig.' + image['format'])
                        shutil.copy(image['path'], disk_sys_orig)

                        # resize the temp image
                        self.resize_image(disk_sys_orig, disk['size'])

                        # expand filesystem
                        self.expand_filesystem(disk_sys_orig, image['root_dev'], disk['path'])
                    finally:
                        shutil.rmtree(tempdir, True)

                # convert image format if necessary
                if image['format'] != disk['format']:
                    logger.info('converting disk %s format from %s to %s' % (disk['dev'], image['format'], disk['format']))
                    temp = tempfile.mktemp(prefix=os.path.basename(disk['path']), dir=os.path.dirname(disk['path']))
                    self.convert_image(disk['path'], image['format'], temp, disk['format'])
                    os.remove(disk['path'])
                    shutil.move(temp, disk['path'])

                if i == 0:  # mount first disk only

                    # guestmount
                    mountdir = tempfile.mkdtemp(prefix='virtparade-')
                    logger.info('mounting sys disk to %s' % mountdir)
                    self.guestmount(disk['path'], disk['format'], mountdir)
                    if step_to == 'mount':
                        logger.info('sys disk mounted to %s' % mountdir)
                        return
                    try:
                        # run init script
                        init_script_dir = os.path.join(self.conf_dir, 'script.d', image['name'])
                        main_script = os.path.join(init_script_dir, 'main.sh')
                        network_script = os.path.join(init_script_dir, 'network.sh')
                        dns_script = os.path.join(init_script_dir, 'dns.sh')

                        if os.path.isfile(main_script):
                            logger.info('running main script:')
                            cmd = '%s %s' % (os.path.join(init_script_dir, 'main.sh'), mountdir)
                            logger.info('+ %s' % cmd)
                            if self.debug:
                                system.exec_command_std(cmd)
                            else:
                                system.exec_command(cmd)
                        else:
                            logger.warning('main script not found, skipping.')

                        if os.path.isfile(network_script):
                            logger.info('running network script:')
                            for j, address in enumerate(inst['network']['addresses']):
                                cmd = '%s %s %s %s %s %s' % (os.path.join(init_script_dir, 'network.sh'), mountdir, j, address['ip'],
                                                             address['prefix'], strings.strip_to_empty(address.get('gateway')))
                                logger.info('+ %s' % cmd)
                                if self.debug:
                                    system.exec_command_std(cmd)
                                else:
                                    system.exec_command(cmd)
                        else:
                            logger.warning('network script not found, skipping.')

                        if os.path.isfile(dns_script):
                            if inst['network'].get('dns') is not None:
                                logger.info('running dns script:')
                                for j, dns in enumerate(inst['network'].get('dns')):
                                    cmd = '%s %s %s %s' % (os.path.join(init_script_dir, 'dns.sh'), mountdir, j, dns)
                                    logger.info('+ %s' % cmd)
                                    if self.debug:
                                        system.exec_command_std(cmd)
                                    else:
                                        system.exec_command(cmd)
                        else:
                            logger.warning('dns script not found, skipping.')
                    finally:
                        # guestunmount
                        logger.info('unmounting %s' % mountdir)
                        self.guestunmount(mountdir, rm_mountpoint=True)

            # generate xml
            tempxml = tempfile.mktemp(suffix='.xml', prefix='virtparade-')
            logger.info('generating libvirt xml file to %s' % tempxml)
            try:
                jinja2.parse_j2_file_to_file(
                    template_file=os.path.abspath(os.path.join(self.conf_dir, 'instance.xml')),
                    output_file=tempxml,
                    **inst
                )

                # define and start instance
                logger.info('staring host %s...' % inst['name'])
                self.virsh_define(tempxml)
                self.virsh_start(inst['name'])

                # virsh vncdisplay
                vnc_port = self.virsh_getvncport(inst['name'])
                logger.info('VNC for %s is: %s' % (inst['name'], vnc_port))
            finally:
                os.remove(tempxml)

            logger.info('done creating host: %s' % inst['name'])
