from fabric.api import env, local, run, cd
from test_rest_api import test_list
 
def vagrant():
	'''Vagrant setup fixture'''
	# change from the default user to 'vagrant'
	env.user = 'vagrant'

	# connect to the port-forwarded ssh
	port = local('vagrant ssh-config | grep Port', capture=True).split(' ')[1]
	env.hosts = ['127.0.0.1:{}'.format(port)]

	# use vagrant ssh key
	result = local('vagrant ssh-config | grep IdentityFile', capture=True)
	env.key_filename = result.split('\"')[1]
 

def nose():
	with cd('/vagrant/tube'):
		run('nosetests')