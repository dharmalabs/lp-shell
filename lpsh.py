#!/usr/bin/env python
import urllib2, pickle, sys, os, getpass, argparse, simplejson as json

"""
  CLI to LP workspaces using REST API:
  http://www.liquidplanner.com/api-guide

  *Needs love to improve error handling and additional features.
  
  http://www.gnu.org/licenses/gpl-3.0.html
  GNU General Public License version 3

  Dharmatech
  358 S. 700 E., Suite B - 350
  SLC, UT 84102

  p: 801.541.8671
  e: jason@dharmatech.org 

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License as
  published by the Free Software Foundation; either version 3 of
  the License, or (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

def base_url():
  return 'https://app.liquidplanner.com/api'

def read_config():
  pkl = os.path.join(os.path.expanduser('~'), '.lp.pkl')
  try: config = pickle.load(open(pkl))
  except: config = False

  return config

def write_config(u, p, wid=None):
  pkl = os.path.join(os.path.expanduser('~'), '.lp.pkl')
  config = read_config()
  if not config: config = {}
  config['username'] = u
  config['password'] = p
  config['wid'] = wid
  pickle.dump(config, open(pkl, 'w'))
  os.chmod(pkl, 0600)

def pp(data):
  keys = data.keys()
  keys.sort()
  for key in keys: print "%s : %s" % (key, data[key])

def cmd_a_view(args):
  uri = base_url() + '/account'
  pp(get_response(uri))

def cmd_a_switch(args):
  write_config(args.username, args.password)

def cmd_t_view(args):
  config = read_config()
  uri = base_url() + '/workspaces/%s/tasks' % config['wid']
  print get_response(uri)
  #pp(get_response(uri))

def cmd_tl_view(args):
  config = read_config()
  # uri = base_url() + '/workspaces/%s/tasklists' % config['wid']
  # if args.id: uri = base_url() + '/workspaces/%s/tasks/%s' % (config['wid'], args.id)
  uri = base_url() + '/help/workspaces/'
  response = get_response(uri)
  print response
  #for item in response['children']:
  #  print "%s : %s" % (item['id'], item['name'])

  # print get_response(uri)
  #pp(get_response(uri))

def cmd_w_list(args):
  config = read_config()
  if config['wid'] == None:
    uri = base_url() + '/workspaces'
    response = get_response(uri)
    for d in response:
      print "%s : %s" % (d['id'], d['name'])
  else:
    uri = base_url() + '/workspaces/%s' % config['wid']
    pp(get_response(uri))

def cmd_w_view(args):
  config = read_config()
  uri = '/workspaces/%s' % config['wid']
  pp(get_response(uri))

def cmd_w_chatter(args):
  config = read_config()
  uri = base_url() + '/workspaces/%s/chatter' % config['wid']
  if args.me:
    uri += '?for_me=true'
  
  response = get_response(uri)
  for item in response:
    print "%s : %s" % (item['updated_by'], item['comment'])
  # pp(get_response(uri))

def cmd_w_set(args):
  config = read_config()
  config['wid'] = args.id
  write_config(config['username'], config['password'], wid=config['wid'])

def get_response(uri):
  config = read_config()
  u = config['username']
  p = config['password']
  req = urllib2.Request(uri,
    headers = {
      'Authorization': 'Basic %s' % (u + ':' + p).encode('base64').rstrip(),
      'Content-Type': 'application/json',
      'Accept': '*/*',
      'User-Agent': 'lp.py/0.1',
    },
  )
  f = urllib2.urlopen(req)

  return json.loads(f.read())

def main(argv):
  if not read_config():
    print "Unable to find/load configuration file, let's create one."
    u = raw_input('What is your LP username?: ')
    p = getpass.getpass('...and your password?: ')
    write_config(u, p)

  parser = argparse.ArgumentParser(description='Retrieves information from LP')
  subparsers = parser.add_subparsers(help='commands')

  # account
  a_group = subparsers.add_parser('a', help='account')
  a_subparsers = a_group.add_subparsers()
  a_group_view = a_subparsers.add_parser('view', help='view account')
  a_group_view.set_defaults(func=cmd_a_view)
  a_group_switch = a_subparsers.add_parser('switch', help='switch accounts')
  a_group_switch.add_argument('username')
  a_group_switch.add_argument('password')
  a_group_switch.set_defaults(func=cmd_a_switch)

  # tasks
  t_group = subparsers.add_parser('t', help='task(s)')
  t_subparsers = t_group.add_subparsers()
  t_group_view = t_subparsers.add_parser('view', help='view tasks')
  t_group_view.add_argument('id', nargs='?')
  t_group_view.set_defaults(func=cmd_t_view)

  # tasklist
  tl_group = subparsers.add_parser('tl', help='tasklist(s)')
  tl_subparsers = tl_group.add_subparsers()
  tl_group_view = tl_subparsers.add_parser('view', help='view taskslist(s)')
  tl_group_view.add_argument('id', nargs='?')
  tl_group_view.set_defaults(func=cmd_tl_view)

  # workspace
  w_group = subparsers.add_parser('w', help='workspace')
  w_subparsers = w_group.add_subparsers()
  w_group_list = w_subparsers.add_parser('list', help='list workspace(s)')
  w_group_list.add_argument('id', nargs='?')
  w_group_list.set_defaults(func=cmd_w_list)
  w_group_set = w_subparsers.add_parser('set', help='set active workspace')
  w_group_set.add_argument('id')
  w_group_set.set_defaults(func=cmd_w_set)
  w_group_chatter = w_subparsers.add_parser('chatter', help='recent workspace chatter')
  w_group_chatter.add_argument('--me', action='store_true')
  w_group_chatter.set_defaults(func=cmd_w_chatter)

  opts = parser.parse_args()
  opts.func(opts)

if __name__ == "__main__": main(sys.argv[1:])
