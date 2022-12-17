def command_read(commands):

    for command in commands:
        if command.find('delay') != -1:
            print '::' + command
            pass
        else:
            print command


# command_list = ['command', 'takeoff', 'delay 5', 'land']
# command_read(command_list)