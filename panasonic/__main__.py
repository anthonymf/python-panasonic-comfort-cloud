import argparse
import json
import panasonic

from enum import Enum

def print_result(obj, indent = 0):
    for key in obj:
        value = obj[key]

        if isinstance(value, dict):
            print(" "*indent + key)
            print_result(value, indent + 4)
        elif isinstance(value, Enum):
            print(" "*indent + "{0: <{width}}: {1}".format(key, value.name, width=25-indent))
        else:
            print(" "*indent + "{0: <{width}}: {1}".format(key, value, width=25-indent))

def main():
    """ Start Panasonic Comfort Cloud command line """

    parser = argparse.ArgumentParser(
        description='Read or change status of Panasonic Climate devices')

    parser.add_argument(
        'username',
        help='Username for Panasonic Comfort Cloud')

    parser.add_argument(
        'password',
        help='Password for Panasonic Comfort Cloud')

    parser.add_argument(
        '-t', '--token',
        help='File to store token in',
        default='~/.panasonic-token')

    commandparser = parser.add_subparsers(
        help='commands',
        dest='command')
 
    commandparser.add_parser(
        'list',
        help="Get a list of all devices")

    get_parser = commandparser.add_parser(
        'get',
        help="Get status of a device")

    get_parser.add_argument(
        dest='device',
        type=int,
        help='Device number #')

    set_parser = commandparser.add_parser(
        'set',
        help="Set status of a device")

    set_parser.add_argument(
        dest='device',
        type=int,
        help='Device number #'
    )

    set_parser.add_argument(
        '-p', '--power',
        choices=[
            panasonic.constants.Power.On.name,
            panasonic.constants.Power.Off.name],
        help='Power mode')

    set_parser.add_argument(
        '-t', '--temperature',
        type=float,
        help="Temperature")

    set_parser.add_argument(
        '-f', '--fanSpeed',
        choices=[
            panasonic.constants.FanSpeed.Auto.name,
            panasonic.constants.FanSpeed.Low.name,
            panasonic.constants.FanSpeed.LowMid.name,
            panasonic.constants.FanSpeed.Mid.name,
            panasonic.constants.FanSpeed.HighMid.name,
            panasonic.constants.FanSpeed.High.name],
        help='Fan speed')

    set_parser.add_argument(
        '-m', '--mode',
        choices=[
            panasonic.constants.OperationMode.Auto.name,
            panasonic.constants.OperationMode.Cool.name,
            panasonic.constants.OperationMode.Dry.name,
            panasonic.constants.OperationMode.Heat.name,
            panasonic.constants.OperationMode.Fan.name],
        help='Operation mode')

    set_parser.add_argument(
        '-e', '--eco',
        choices=[
            panasonic.constants.EcoMode.Auto.name,
            panasonic.constants.EcoMode.Quiet.name,
            panasonic.constants.EcoMode.Powerful.name],
        help='Eco mode')    

    # set_parser.add_argument(
    #     '--airswingauto',
    #     choices=[
    #         panasonic.constants.AirSwingAutoMode.Disabled.name,
    #         panasonic.constants.AirSwingAutoMode.AirSwingLR.name,
    #         panasonic.constants.AirSwingAutoMode.AirSwingUD.name,
    #         panasonic.constants.AirSwingAutoMode.Both.name],
    #     help='Automation of air swing')

    set_parser.add_argument(
        '-y', '--airSwingVertical',
        choices=[
            panasonic.constants.AirSwingUD.Auto.name,
            panasonic.constants.AirSwingUD.Down.name,
            panasonic.constants.AirSwingUD.DownMid.name,
            panasonic.constants.AirSwingUD.Mid.name,
            panasonic.constants.AirSwingUD.UpMid.name,
            panasonic.constants.AirSwingUD.Up.name],
        help='Vertical position of the air swing')

    set_parser.add_argument(
        '-x', '--airSwingHorizontal',
        choices=[
            panasonic.constants.AirSwingLR.Auto.name,
            panasonic.constants.AirSwingLR.Left.name,
            panasonic.constants.AirSwingLR.LeftMid.name,
            panasonic.constants.AirSwingLR.Mid.name,
            panasonic.constants.AirSwingLR.RightMid.name,
            panasonic.constants.AirSwingLR.Right.name],
        help='Horizontal position of the air swing')

    dump_parser = commandparser.add_parser(
        'dump',
        help="Dump data of a device")

    dump_parser.add_argument(
        dest='device',
        type=int,
        help='Device number #')    

    args = parser.parse_args()

    session = panasonic.Session(args.username, args.password, args.token, False)
    session.login()
    try:
        if args.command == 'list':
            print("list of devices and its device id #")
            for idx, device in enumerate(session.get_devices()):
                print("  #{} - group: '{}', name: '{}', model: '{}'".format(idx + 1, device['group'], device['name'], device['model']))

        if args.command == 'get':
            if int(args.device) <= 0 or int(args.device) > len(session.get_devices()):
                raise Exception("Device not found, acceptable device id is from {} to {}".format(1, len(session.get_devices())))

            device = session.get_devices()[int(args.device) - 1]            
            print("reading from device '{}' ({})".format(device['name'], device['id']))

            print_result( session.get_device(device['id']) )

        if args.command == 'set':
            if int(args.device) <= 0 or int(args.device) > len(session.get_devices()):
                raise Exception("Device not found, acceptable device id is from {} to {}".format(1, len(session.get_devices())))

            device = session.get_devices()[int(args.device) - 1]
            print("writing to device '{}' ({})".format(device['name'], device['id']))

            kwargs = {}

            if args.power is not None:
                kwargs['power'] = panasonic.constants.Power[args.power]

            if args.temperature is not None:
                kwargs['temperature'] = args.temperature
                
            if args.fanSpeed is not None:
                kwargs['fanSpeed'] = panasonic.constants.FanSpeed[args.fanSpeed]
            
            if args.mode is not None:
                kwargs['mode'] = panasonic.constants.OperationMode[args.mode]

            if args.airSwingHorizontal is not None:
                kwargs['airSwingHorizontal'] = panasonic.constants.AirSwingLR[args.airSwingHorizontal]

            if args.airSwingVertical is not None:
                kwargs['airSwingVertical'] = panasonic.constants.AirSwingUD[args.airSwingVertical]

            session.set_device(device['id'], **kwargs)

        if args.command == 'dump':
            if int(args.device) <= 0 or int(args.device) > len(session.get_devices()):
                raise Exception("Device not found, acceptable device id is from {} to {}".format(1, len(session.get_devices())))

            device = session.get_devices()[int(args.device) - 1]
            
            print_result(session.dump(device['id']))
    
    except panasonic.ResponseError as ex:
        print(ex.text)


# pylint: disable=C0103
if __name__ == "__main__":
    main()