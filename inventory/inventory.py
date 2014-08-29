#!/usr/bin/env python

from ConfigParser import RawConfigParser
import MySQLdb as mdb
import sys, os, time

try:
    import json
except ImportError:
    import simplejson as json

def getgroups(conn):
    inventory ={ }
    inventory['_meta']={ 'hostvars' : {} }
    inventory['all']= { 'hosts': [] }
    cur = conn.cursor()
    cur.execute("SELECT IF(group.name is null,'all',group.name) AS `group`,host.name FROM host LEFT JOIN host_group ON host_group.host_id=host.id LEFT JOIN `group` ON host_group.group_id=group.id")

    for row in cur.fetchall():
        group, name = row
        if not group in inventory:
            inventory[group] = {
                'hosts' : []
            }
        inventory[group]['hosts'].append(name)
	if not name in inventory['all']['hosts']:
	  inventory['all']['hosts'].append(name)

    return inventory

def getroles(conn, type, inventory):
  result = {}
  cur = conn.cursor()
  if type == 'host':
    cur.execute("SELECT host.name,role.name AS role FROM host_roles INNER JOIN role ON role.id=host_roles.role_id INNER JOIN host ON host.id=host_roles.host_id")
  elif type == 'group':
    cur.execute("SELECT group.name,role.name AS role FROM group_roles INNER JOIN role ON role.id=group_roles.role_id INNER JOIN `group` ON group.id=group_roles.group_id")

  rows=cur.fetchall()
  if type == 'group':
     for row in rows:
       if row[0] in inventory:
         if not 'roles' in inventory[row[0]]:
            inventory[row[0]]['roles']=[]
         inventory[row[0]]['roles'].append(row[1])

  if type == 'host':
     for row in rows:
       if not row[0] in inventory['_meta']['hostvars']:
         inventory['_meta']['hostvars'][row[0]]={}
       if not 'roles' in inventory['_meta']['hostvars']:
            inventory['_meta']['hostvars'][row[0]]['roles']=[]
       inventory['_meta']['hostvars'][row[0]]['roles'].append(row[1])

  return inventory

def getvars(conn, type, inventory):
  result = {}
  cur = conn.cursor()
  if type == 'host':
    cur.execute("SELECT host.name,single_var.name,value FROM host_vars INNER JOIN host ON host_id=host.id INNER JOIN single_var ON single_var_id=single_var.id")

  elif type == 'group':
    cur.execute("SELECT group.name,single_var.name,value FROM group_vars INNER JOIN `group` ON group.id=group_vars.group_id INNER JOIN single_var ON single_var_id=single_var.id")

  rows=cur.fetchall()
  if type == 'group':
    for row in rows:
       if row[0] in inventory:
         if not 'vars' in inventory[row[0]]:
           inventory[row[0]]['vars']={}
         inventory[row[0]]['vars'][row[1]]=row[2]
  if type == 'host':
     for row in rows:
       if not row[0] in inventory['_meta']['hostvars']:
         inventory['_meta']['hostvars'][row[0]]={}
       inventory['_meta']['hostvars'][row[0]][row[1]]=row[2]

  cur.execute("SELECT tablename,env FROM roletable")
  tables=cur.fetchall()
  for table in tables:
    if type == 'host':
      cur.execute('SELECT host.name,' + table[0] + '.* FROM ' + table[0] + ' INNER join host ON host.id=host_id')
    elif type == 'group':
      cur.execute('SELECT group.name,' + table[0] + '.* FROM ' + table[0] + ' INNER join `group` ON group.id=group_id')

    if type == 'group' and table[1] == 'multi':
      tablespace=table[0]+'_global'
    else:
      tablespace=table[0]

    rows=cur.fetchall()
    columns=cur.description
    for row in rows:
      tmp={}
      for (index,column) in enumerate(row):
        if index >= 4 and column != None:
         tmp[columns[index][0]] = column
      if type == 'group':
        if row[0] in inventory:
          if not 'vars' in inventory[row[0]]:
           inventory[row[0]]['vars']={}
          if not tablespace in inventory[row[0]]['vars']:
            inventory[row[0]]['vars'][tablespace]=[]
          inventory[row[0]]['vars'][tablespace].append(tmp)
      if type == 'host':
        if not row[0] in inventory['_meta']['hostvars']:
          inventory['_meta']['hostvars'][row[0]]={}
        if not tablespace in inventory['_meta']['hostvars'][row[0]]:
          inventory['_meta']['hostvars'][row[0]][tablespace]=[]
        inventory['_meta']['hostvars'][row[0]][tablespace].append(tmp)
    
  return inventory


def getjson(config):
        try:
                con = mdb.connect(config.get('ansible','host'), config.get('ansible','user'), config.get('ansible','password'), config.get('ansible','db'));
        except mdb.Error, e:
                print "Error %d: %s" % (e.args[0],e.args[1])
                sys.exit(1)

        inventory=getgroups(con)
        inventory=getvars(con,'group',inventory)
        inventory=getroles(con,'group',inventory)
        inventory=getroles(con,'host',inventory)
        inventory=getvars(con,'host',inventory)
        con.close()
        return inventory


def writecache(config,tmpfile):
  inventory=json.dumps(getjson(config), indent=3)
  cache=open(tmpfile, 'w')
  cache.write(inventory)
  cache.close()

def printcache(tmpfile):
	cache=open(tmpfile, 'r')
	print cache.read()


if __name__ == '__main__':
  config = RawConfigParser()
  config.read([os.path.dirname(os.path.abspath(__file__))+'/inventory_conf.ini'])
  tmpfile=config.get('ansible','tmpfile')

  if os.path.isfile(tmpfile):
    ago=time.time()-3600
    if os.path.getmtime(tmpfile)<ago:
      writecache(config,tmpfile)
  else:
    writecache(config,tmpfile)

  printcache(tmpfile)
