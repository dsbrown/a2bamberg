Vagrant.configure("2") do |config|
  config.vm.define :tube do |web|
    web.vm.box = "ubuntu12.04"
    web.vm.hostname = "tube"
    web.vm.network :forwarded_port, guest: 80, host: 8080
    web.vm.network :forwarded_port, guest: 5000, host: 5000
  end
end