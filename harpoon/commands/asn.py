#! /usr/bin/env python
import os
import sys
import json
import requests
import pyasn
from harpoon.commands.base import Command
from harpoon.lib.utils import bracket, unbracket

class CommandAsn(Command):
    """
    # ASN command

    **Get ASN information from different sources**

    * Offline ASN info: `harpoon asn info ASN15134`
    * ASN Info from peering db (https://peeringdb.com/) : `harpoon asn db 1228` (-j for raw output)
    * List subnets for an ASN: `harpoon asn subnet 15348`

    Example:
    ```
    $ harpoon asn db 18182
    Name: So-net Entertainment Taiwan Limited
    Website: http://www.so-net.net.tw
    Created: 2011-06-15T06:16:44Z
    ```
    """
    name = "asn"
    description = "Gather information on an ASN"
    config = None
    asn_name = os.path.join(os.path.expanduser('~'), '.config/harpoon/asnnames.csv')
    asncidr = os.path.join(os.path.expanduser('~'), '.config/harpoon/asncidr.dat')

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(help='Subcommand')
        parser_a = subparsers.add_parser('info', help='Information on an ASn number')
        parser_a.add_argument('ASN', help='ASN Number')
        parser_a.set_defaults(subcommand='info')
        parser_b = subparsers.add_parser('db', help='ASN information from peeringdb (https://peeringdb.com/)')
        parser_b.add_argument('ASN', help='ASN Number')
        parser_b.add_argument('--json', '-j', help='Show raw json', action='store_true')
        parser_b.set_defaults(subcommand='db')
        parser_c = subparsers.add_parser('subnet', help='List of subnets for an ASN number')
        parser_c.add_argument('ASN', help='ASN Number')
        parser_c.set_defaults(subcommand='subnet')
        self.parser = parser

    def asnname(self, asn):
        """
        Search for the ASN name based on its number
        Input: asnnumber (integer)
        returns: string
        Returns an empty string if not found
        """
        # Search for name
        f = open(self.asn_name, 'r')
        line = f.readline()
        while line != '':
            s = line.split('|')
            if s[0] == str(asn):
                f.close()
                return s[1].strip()
            line = f.readline()
        f.close()
        return ''

    def run(self, conf, args, plugins):
        if hasattr(args, 'ASN'):
            if args.ASN.lower().startswith("asn"):
                asn = int(args.ASN[3:])
            elif args.ASN.lower().startswith("as"):
                asn = int(args.ASN[2:])
            else:
                asn = int(args.ASN)
        else:
            self.parser.print_help()
            sys.exit(0)
        if 'subcommand' in args:
            if args.subcommand == 'info':
                info = self.asnname(asn)
                if len(info):
                    print("ASN%i - %s" % (asn, info))
                else:
                    print("Unknown ASN")
            elif args.subcommand == "subnet":
                asndb = pyasn.pyasn(self.asncidr)
                subnets = asndb.get_as_prefixes(asn)
                for s in subnets:
                    print(s)
            elif args.subcommand == "db":
                r = requests.get('https://peeringdb.com/api/net?asn=%i' % asn)
                if r.status_code == 200:
                    if args.json:
                        print(json.dumps(r.json(), sort_keys=False, indent=4))
                    else:
                        data = r.json()['data'][0]
                        print('Name: %s' % data['name'])
                        if data['aka'] != '':
                            print("aka: %s" % data['aka'])
                        if data['notes'] != '':
                            print("Notes: %s" % data['notes'])
                        if data['website'] != '':
                            print("Website: %s" % data['website'])
                        print("Created: %s" % data['created'])
                else:
                    print("ASN not found")
            else:
                self.parser.print_help()
        else:
            self.parser.print_help()
