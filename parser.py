from os import replace
import yaml
import textwrap

game = {}
location = {}
triggers = {'end': False}


def load(filename):
	with open(filename, 'r') as f:
		try:
			return yaml.safe_load(f)
		except yaml.YAMLError as exc:
			print(exc)
			exit(1)

def parse_location(string):
	parts = string.split('/')
	return game['locations'][parts[0]]['rooms'][parts[1]]

def main():
	global game
	global location
	global triggers

	game = load('test.yml')
	location = parse_location(game['start'])

	print('\u001b[32;1m', end='')
	print(f"The name is the loaded game is '{game['name']}'")
	print('\u001b[0m', end='')
	print('\u001b[32m', end='')
	print(textwrap.fill(location['message']))

	# The main game loop will run until the end trigger has been set to true
	while True:
		if triggers['end'] == True:
			return

		cmd = input('\u001b[33mWhat would you like to do? \u001b[0m').lower()
		print('\u001b[32m', end='')

		# TODO: change this to allow multiple keywords for chagne location/room
		if 'enter' in cmd:
			loc = get_exit_from_input(cmd)
			if loc is not None:
				location = parse_location(loc)
				print(textwrap.fill(location['message']))
			else:
				print('\u001b[31mI dont know what you are referring to')
		else:
			object = get_object_from_input(cmd)
			if object is not None:
				action = get_action_from_input(cmd, object)
				if action is not None:
					val = location['objects'][object]['actions'][action]
					if isinstance(val, str):
						print(textwrap.fill(val))
					else:
						if 'message' in val:
							print(textwrap.fill(val['message']))
						elif 'if' in val:
							printed = False
							for condition in val['if']:
								triggered = False
								conditions, typ = parse_condition(condition)
								if typ == "&&":
									for cond in conditions:
										if cond[0] == '!':
											if cond[1:] in triggers:
												if triggers[cond[1:]] == True:
													triggered = True
													break
											else:
												triggered = True
										else:
											if cond in triggers:
												if triggers[cond] == False:
													triggered = True
													break
											else:
												triggered = True
									if triggered == False:
										print(textwrap.fill(val['if'][condition]))
										printed = True
										break
								if typ == "||":
									for cond in conditions:
										if cond[0] == '!':
											if cond[1:] in triggers:
												if triggers[cond[1:]] == True:
													print(textwrap.fill(val['if'][condition]))
													printed = True
													break
										else:
											if cond in triggers:
												if triggers[cond] == True:
													print(textwrap.fill(val['if'][condition]))
													printed = True
													break
								if printed:
									break
							if not printed:
								print(textwrap.fill(val['else']))
						else:
							print('ERROR WRONGLY FORMATTED GAME FILE')
							return

						if 'trigger' in val:
							if isinstance(val['trigger'], str):
								triggers[val['trigger']] = True
							else:
								for trigger in val['trigger']:
									triggers[trigger] = True
				else:
					print('\u001b[31mSorry you cant do that')
			else:
				print('\u001b[31mI dont know what you are referring to')

# Parse condition from string to multiple triggers
# typ is either or or and, and denotes whether the triggers need to all be fufilled or just one
# String representation would look like "&& TRIGGER TRIGGER TRIGGER" or "TRIGGER"
# First two characters are the type of condition and then follows a space seperated list of conditions unless its a single condition
def parse_condition(condition):
	res = condition.split(' ')
	val = (res[1:], res[0]) if len(res) != 1 else (res, "&&")
	return val

def get_object_from_input(cmd):
	for i in location['objects']:
		names = get_name_and_alias(location['objects'][i], i)
		for name in names:
			if name in cmd:
				return i.replace(' ', '_')

def get_action_from_input(cmd, object):
	for i in location['objects'][object]['actions']:
		names = get_name_and_alias(location['objects'][object]['actions'][i], i)
		for name in names:
			if name in cmd:
				return i.replace(' ', '_')

def get_exit_from_input(cmd):
	for i in location['exits']:
		names = get_name_and_alias(location['exits'][i], i)
		for name in names:
			if name in cmd:
				if isinstance(location['exits'][i.replace(' ', '_')], str):
					return location['exits'][i.replace(' ', '_')]
				return location['exits'][i.replace(' ', '_')]['exit']
		
def get_name_and_alias(obj, name):
	if not isinstance(obj, str):
		if 'alias' in obj:
			return [name.replace('_', ' ')] + list(map(lambda x: x.replace('_', ' '), obj['alias']))
	return [name.replace('_', ' ')]

if __name__ == '__main__':
	main()
