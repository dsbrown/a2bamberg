from fabric.api import env, local, run
 
def vagrant():
	# change from the default user to 'vagrant'
	env.user = 'vagrant'
	# connect to the port-forwarded ssh
	env.hosts = ['127.0.0.1:2204']
 
	# use vagrant ssh key
	result = local('vagrant ssh-config | grep IdentityFile', capture=True)
	env.key_filename = result.split('\"')[1]
 
def test():
	run('ls -alsh')
	run('nosetests')