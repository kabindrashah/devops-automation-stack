Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "devops-stack"

  config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "forwarded_port", guest: 80,   host: 8080   # app via Nginx
  config.vm.network "forwarded_port", guest: 3000, host: 3000   # Grafana
  config.vm.network "forwarded_port", guest: 9090, host: 9090   # Prometheus

  config.vm.provider "virtualbox" do |vb|
    vb.name   = "devops-automation-stack"
    vb.memory = 3072
    vb.cpus   = 2
  end

  # Ansible runs inside the VM, so it also works from Windows without WSL.
  config.vm.provision "ansible_local" do |ansible|
    ansible.provisioning_path = "/vagrant"
    ansible.playbook = "ansible/site.yml"
  end
end
