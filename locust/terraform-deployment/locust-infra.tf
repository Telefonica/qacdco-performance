provider "azurerm" {
  features {}
}

variable "workers" {
  type = number
  default = 2
}

variable "vm_master_size" {
  type = string
  default = "Standard_E2ds_v5"
}

variable "vm_worker_size" {
    type = string
    default = "Standard_D2ds_v5"
}

variable "resource_group" {
  type = string
  default = "test-locust"
}

resource "azurerm_resource_group" "test-locust" {
  name     = "${var.resource_group}"
  location = "eastus2"
}

resource "azurerm_virtual_network" "worker-network" {
  name                = "worker-network"
  resource_group_name = "${azurerm_resource_group.test-locust.name}"
  location            = "eastus2"
  address_space       = ["172.20.0.0/16"]
}

resource "azurerm_subnet" "worker-subnet" {
  name                 = "worker-subnet"
  resource_group_name  = "${azurerm_resource_group.test-locust.name}"
  virtual_network_name = azurerm_virtual_network.worker-network.name
  address_prefixes     = ["172.20.0.0/24"]
}

resource "azurerm_public_ip" "worker-public-ip" {
  count               = var.workers
  name                = "worker-public-ip${count.index}"
  resource_group_name = "${azurerm_resource_group.test-locust.name}"
  location            = "eastus2"
  allocation_method   = "Static"
  sku                 = "Basic"
}

resource "azurerm_network_interface" "worker-interface" {
  count               = var.workers
  name                = "worker-nic${count.index}"
  location            = "eastus2"
  resource_group_name = "${azurerm_resource_group.test-locust.name}"

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.worker-public-ip.*.id, count.index)
  }
}

resource "azurerm_linux_virtual_machine" "worker-vm" {
  count                 = var.workers
  name                  = "locustWorker-vm${count.index}"
  resource_group_name   = "${azurerm_resource_group.test-locust.name}"
  location              = "eastus2"
  size                  = "Standard_D2ds_v5"
  admin_username        = "adminuser"
  network_interface_ids = [element(azurerm_network_interface.worker-interface.*.id, count.index)]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }
}

resource "azurerm_public_ip" "master-public-ip" {
  name                = "master-public-ip"
  resource_group_name = "${azurerm_resource_group.test-locust.name}"
  location            = "eastus2"
  allocation_method   = "Static"
  sku                 = "Basic"
}

resource "azurerm_network_interface" "master-interface" {
  name                = "master-nic"
  location            = "eastus2"
  resource_group_name = "${azurerm_resource_group.test-locust.name}"

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.worker-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.master-public-ip.id
  }
}

resource "azurerm_linux_virtual_machine" "master-vm" {
  name                  = "locustMaster-vm"
  resource_group_name   = "${azurerm_resource_group.test-locust.name}"
  location              = "eastus2"
  size                  = var.vm_master_size
  admin_username        = "adminuser"
  network_interface_ids = [azurerm_network_interface.master-interface.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }
}

resource "null_resource" "master_provisioner" {
  triggers = {
    instance_id = azurerm_linux_virtual_machine.master-vm.id
  }

  provisioner "file" {
      source      = "/app"
      destination = "/home/adminuser/locust"
  }

  provisioner "remote-exec" {
    inline = [
      "bash /home/adminuser/locust/terraform-deployment/locust-infra-setup.sh master"
    ]
  }

  connection {
    type = "ssh"
    host = azurerm_linux_virtual_machine.master-vm.public_ip_address
    user = "adminuser"
    private_key = file("~/.ssh/id_rsa")
  }
}

resource "null_resource" "worker_provisioner" {
  count = var.workers
  depends_on = [null_resource.master_provisioner]

  triggers = {
    instance_id = azurerm_linux_virtual_machine.worker-vm.*.id[count.index]
  }

  provisioner "file" {
      source      = "/app"
      destination = "/home/adminuser/locust"
  }

  provisioner "remote-exec" {
    inline = [
      "bash /home/adminuser/locust/terraform-deployment/locust-infra-setup.sh worker"
    ]
  }

  connection {
    type = "ssh"
    host = azurerm_public_ip.worker-public-ip.*.ip_address[count.index]
    user = "adminuser"
    private_key = file("~/.ssh/id_rsa")
  }
}

