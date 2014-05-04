#!/usr/bin/env python

from ConfigParser import RawConfigParser
import MySQLdb as mdb
import sys
try:
    import json
except ImportError:
    import simplejson as json

def grouplist(conn):
    inventory ={}
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
	 if len(result) > 0:
           inventory[group]['vars']=result

    cur.close()
    print json.dumps(inventory, indent=4)

def hostinfo(conn, name):
    result=retvars(conn,'host',name)
    print json.dumps(result, indent=4)

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

if __name__ == '__main__':
    config = RawConfigParser()
    config.read(['/etc/ansible/inventory_conf.ini','inventory_conf.ini'])
    try:
      con = mdb.connect(config.get('ansible','host'), config.get('ansible','user'), config.get('ansible','password'), config.get('ansible','db'));
    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      sys.exit(1)

    if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
        grouplist(con)
    elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
        hostinfo(con, sys.argv[2])
    else:
        print "Usage: %s --list or --host <hostname>" % sys.argv[0]
        sys.exit(1)

    con.close()
