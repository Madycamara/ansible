#!/usr/bin/env python

from ConfigParser import RawConfigParser
import MySQLdb as mdb
import sys, os, time

try:
    import json
except ImportError:
    import simplejson as json

def grouplist(conn):
    inventory ={ }
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


    for group in inventory:
         result=retvars(conn,'group',group)
         inventory[group]['vars']=result
         roles=retroles(conn,'group',group)
         if len(roles) > 0:
           inventory[group]['vars']['roles_group']=roles

    inventory['_meta']={ 'hostvars' : {} }
    for host in inventory['all']['hosts']:
      inventory['_meta']['hostvars'][host]=hostinfo(conn,host,False)

    cur.close()
    return json.dumps(inventory, indent=4)

def hostinfo(conn, name, printout=True):
  result=retvars(conn,'host',name)
  roles=retroles(conn,'host',name)
  result['roles']=roles
  if printout == True:
     print json.dumps(result, indent=4)
  else:
    return result

def retroles(conn, type, name):
  result = {}
  cur = conn.cursor()
  if type == 'host':
    cur.execute("SELECT role.name AS role FROM host_roles INNER JOIN role ON role.id=host_roles.role_id INNER JOIN host ON host.id=host_roles.host_id WHERE host.name=%s", name)
  elif type == 'group':
    cur.execute("SELECT role.name AS role FROM group_roles INNER JOIN role ON role.id=group_roles.role_id INNER JOIN `group` ON group.id=group_roles.group_id WHERE group.name=%s", name)

  rows=cur.fetchall()
  for row in rows:
    result[row[0]]='true'
    #result.append(row[0])

  return result

def retvars(conn, type, name):
  result = {}
  cur = conn.cursor()
  if type == 'host':
    cur.execute("SELECT single_var.name,value FROM host_vars INNER JOIN host ON host_id=host.id INNER JOIN single_var ON single_var_id=single_var.id WHERE host.name=%s", name)
  elif type == 'group':
    cur.execute("SELECT single_var.name,value FROM group_vars INNER JOIN `group` ON group.id=group_vars.group_id INNER JOIN single_var ON single_var_id=single_var.id WHERE group.name=%s", name)

  rows=cur.fetchall()
  for row in rows:
    result[row[0]]=row[1]

  cur.execute("SELECT tablename,env FROM roletable")
  tables=cur.fetchall()
  for table in tables:
    if type == 'host':
      cur.execute('SELECT ' + table[0] + '.* FROM ' + table[0] + ' INNER join host ON host.id=host_id WHERE host.name=%s', name)
    elif type == 'group':
      cur.execute('SELECT ' + table[0] + '.* FROM ' + table[0] + ' INNER join `group` ON group.id=group_id WHERE group.name=%s',name)

    if type == 'group' and table[1] == 'multi':
      tablespace=table[0]+'_global'
    else:
      tablespace=table[0]

    rows=cur.fetchall()
    if len(rows) > 0:
      result[tablespace]=[]
    columns=cur.description
    for row in rows:
      tmp={}
      for (index,column) in enumerate(row):
        if index >= 3 and column != None:
         tmp[columns[index][0]] = column
      result[tablespace].append(tmp)
    
  return result

def writecache(con,tmpfile):
	json=grouplist(con)
	cache=open(tmpfile, 'w')
	cache.write(json)
	cache.close()

def printcache(tmpfile):
	cache=open(tmpfile, 'r')
	print cache.read()


if __name__ == '__main__':
    tmpfile='/tmp/ansible_cache.json'
    config = RawConfigParser()
    config.read([os.path.dirname(os.path.abspath(__file__))+'/inventory_conf.ini'])
    try:
      con = mdb.connect(config.get('ansible','host'), config.get('ansible','user'), config.get('ansible','password'), config.get('ansible','db'));
    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      sys.exit(1)

    if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
	if os.path.isfile(tmpfile):
		ago=time.time()-3600
		if os.path.getmtime(tmpfile)<ago:
			writecache(con,tmpfile)
	else:
		writecache(con,tmpfile)

	printcache(tmpfile)
    elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
        hostinfo(con, sys.argv[2])
    else:
        print "Usage: %s --list or --host <hostname>" % sys.argv[0]
        sys.exit(1)

    con.close()
